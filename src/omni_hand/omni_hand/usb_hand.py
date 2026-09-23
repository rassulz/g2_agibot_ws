"""Drive the OmniHand O10 over its own USB port, and put it on ROS 2.

The robot's hal does not detect this hand on CAN, so it is invisible to the
GDK and to the robot's ROS 2 bridge. Its USB-C port still works: plugged into
the robot it shows up as a serial port, and the AgiLink OmniHand SDK talks to
it directly. This node is the ROS 2 side of that link.

    /omni_hand/gesture      std_msgs/String       in   rock | paper | scissors,
                                                       or any O10 SDK gesture
                                                       (ok, like, num3, ...)
    /omni_hand/joint_state  sensor_msgs/JointState out  measured joint angles
    /omni_hand/status       std_msgs/String       out  done <name> | refused ...

This node MOVES HARDWARE and does so outside hal: the robot's e-stop does not
stop it. Without -p enable:=true it only logs what it would do.

Every move is checked and paced the same way it was tested on the hand:
  * refuse if any joint reports stalled / overheat / over-current / motor or
    communication fault, before the move and between its phases
  * clamp the target to the documented joint limits
  * split the move so the thumb and fingers do not collide
    (hand_model.o10_phases), and ramp each phase from the measured pose
  * finish with the SDK's own set_hand_gesture() for the exact factory pose

One-time setup on the robot (nothing is installed system-wide):

    git clone https://github.com/AgibotTech/agillink_omnihand_sdk ~/agillink_omnihand_sdk
    cd ~/agillink_omnihand_sdk/linux/aarch64/python
    mkdir -p ~/omnihand_pkg && python3 -m zipfile -e \\
        omnihand-1.1.8-cp312-cp312-linux_aarch64.whl ~/omnihand_pkg
    sudo usermod -aG dialout agi          # serial port access; log in again

Run on the robot, from the workspace (the scripts set up ROS 2 and the SDK
path, the same way for both, so the two sides always see each other):

    src/omni_hand/scripts/hand_start.sh            # terminal 1: the driver
    src/omni_hand/scripts/hand.sh rock             # terminal 2: gestures

USB direct control is O10-only (SDK QUICK_START), so the model is fixed.
"""

import os
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

try:
    from omni_hand import hand_model
except ImportError:  # run straight from a git checkout, without colcon
    import sys
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from omni_hand import hand_model

MODEL = 'o10_t2'
DEFAULT_PORT = ('/dev/serial/by-id/'
                'usb-STMicroelectronics_STM32_Virtual_ComPort_'
                '386133553335-if00')
FAULT_FLAGS = ('stalled', 'overheat', 'over_current',
               'motor_except', 'commu_except')


class UsbHand(Node):

    def __init__(self):
        super().__init__('usb_hand')
        self.declare_parameter('port', DEFAULT_PORT)
        self.declare_parameter('side', 'left')        # 'left' or 'right'
        self.declare_parameter('steps', 10)           # ramp steps per phase
        self.declare_parameter('step_delay', 0.2)     # seconds per step
        self.declare_parameter('state_rate', 2.0)     # Hz, 0 = off
        self.declare_parameter('enable', False)       # required to move

        self._side = self.get_parameter('side').value
        self._names = hand_model.joint_names(MODEL, self._side)
        self._hand = None
        self._gestures = None

        self.create_subscription(
            String, 'omni_hand/gesture', self._on_gesture, 10)
        self._state_pub = self.create_publisher(
            JointState, 'omni_hand/joint_state', 10)
        self._status_pub = self.create_publisher(
            String, 'omni_hand/status', 10)

    # --- connection ------------------------------------------------------

    def connect(self):
        log = self.get_logger()
        if self._side not in ('left', 'right'):
            log.error(f"side must be 'left' or 'right', got {self._side!r}")
            return False

        port = self.get_parameter('port').value
        if not os.path.exists(port):
            log.error(f'{port} does not exist -- is the hand USB-C plugged '
                      'into the robot?')
            return False
        if not os.access(port, os.R_OK | os.W_OK):
            log.error(f'no permission on {port}. Once: '
                      'sudo usermod -aG dialout $USER, then log in again '
                      '(or sudo chmod 666 until the next replug).')
            return False

        try:
            from omnihand import HandType, OmniHand2025, OmniHand2025Gesture
        except ImportError as exc:
            log.error(f'cannot import the AgiLink SDK: {exc}\n'
                      'export PYTHONPATH=~/omnihand_pkg:$PYTHONPATH '
                      '(see the setup notes at the top of this file)')
            return False

        try:
            hand = OmniHand2025.create_hand_by_usb(
                hand_type=HandType.LEFT if self._side == 'left'
                else HandType.RIGHT,
                hand_device_id=1,
                uart_port=port)
        except Exception as exc:
            log.error(f'create_hand_by_usb() failed: {exc}')
            return False
        if hand is None or not hand.init():
            log.error('the hand did not answer over USB')
            return False

        self._hand = hand
        self._gestures = OmniHand2025Gesture
        faults = self._faults()
        log.info(f'connected to O10 ({self._side}) on {port}; '
                 f'faults: {faults or "none"}')
        if not self.get_parameter('enable').value:
            log.warning('DRY RUN -- gestures are logged, not sent. '
                        'Start with -p enable:=true to move the hand.')

        rate = float(self.get_parameter('state_rate').value)
        if rate > 0.0:
            self.create_timer(1.0 / rate, self._publish_state)
        return True

    # --- hand I/O --------------------------------------------------------

    def _refresh(self):
        # Despite its name, init() is what re-reads the hand: it sends 0x09
        # (all positions) and 0x0D (error code). The getters below return
        # the values it cached -- seen in the SDK's raw frame log.
        return self._hand.init()

    def _angles(self):
        return list(self._hand.get_all_active_joint_angles())

    def _faults(self):
        return [(joint + 1, flag)
                for joint, report in enumerate(self._hand.get_all_error_reports())
                for flag in FAULT_FLAGS if getattr(report, flag)]

    def _publish_state(self):
        if self._hand is None or not self._refresh():
            return
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self._names)
        msg.position = [float(a) for a in self._angles()]
        self._state_pub.publish(msg)

    def _status(self, text, error=False):
        # Separate call sites: rclpy refuses to log one line at two levels.
        if error:
            self.get_logger().error(text)
        else:
            self.get_logger().info(text)
        self._status_pub.publish(String(data=text))

    # --- gestures --------------------------------------------------------

    def _on_gesture(self, msg):
        name = msg.data.strip().lower()
        goal = hand_model.gesture(MODEL, self._side, name)
        if goal is None:
            known = ', '.join(hand_model.gesture_names(MODEL, self._side))
            self._status(f'refused {name!r}: unknown gesture. Known: {known}',
                         error=True)
            return

        goal, adjusted = hand_model.clamp(MODEL, self._side, goal)
        for joint, requested, applied in adjusted:
            self.get_logger().warning(
                f'clamped {joint}: {requested:.4f} -> {applied:.4f}')

        if not self._refresh():
            self._status(f'refused {name}: could not read the hand', True)
            return
        faults = self._faults()
        if faults:
            self._status(f'refused {name}: joint faults {faults}', True)
            return
        start = self._angles()
        if len(start) != len(goal):
            self._status(f'refused {name}: read {len(start)} joints, '
                         f'expected {len(goal)}', True)
            return

        phases = hand_model.o10_phases(start, goal)
        order = ' -> '.join(label for label, _ in phases)
        if not self.get_parameter('enable').value:
            self._status(f'dry run {name}: {order}, target '
                         f'{[round(a, 3) for a in goal]}')
            return

        self.get_logger().info(f'{name}: {order}')
        steps = max(1, int(self.get_parameter('steps').value))
        delay = float(self.get_parameter('step_delay').value)
        pose = start
        for label, target in phases:
            for k in range(1, steps + 1):
                self._hand.set_all_active_joint_angles(
                    [a + (b - a) * k / steps for a, b in zip(pose, target)])
                time.sleep(delay)
            pose = target
            if not self._refresh():
                self._status(f'stopped {name} after {label}: '
                             'could not read the hand', True)
                return
            faults = self._faults()
            if faults:
                self._status(f'stopped {name} after {label}: '
                             f'joint faults {faults}', True)
                return

        key = hand_model.sdk_gesture(MODEL, name)
        if key is not None:
            self._hand.set_hand_gesture(
                getattr(self._gestures, f'OMNIHAND_2025_GESTURE_{key.upper()}'))
            time.sleep(delay)
        self._refresh()
        error = max(abs(a - b) for a, b in zip(self._angles(), goal))
        faults = self._faults()
        if faults:
            self._status(f'done {name} with joint faults {faults}', True)
        else:
            self._status(f'done {name} (max error {error:.3f} rad)')
        self._publish_state()


def main(args=None):
    rclpy.init(args=args)
    node = UsbHand()
    try:
        if node.connect():
            rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass                  # Ctrl+C or SIGTERM: a normal way to stop
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
