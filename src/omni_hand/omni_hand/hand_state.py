"""Report the state of the G2's hand and arm joints.

Read-only. Joint commands go to /gdk/joint_control as JointPositionServo;
see command_scaffold.py in this package, which is deliberately inert.
"""

import rclpy
from rclpy.node import Node
from gdk_msgs.msg import JointState

JOINT_STATE_TOPIC = '/gdk/joint_state'

# Joint names follow the pattern idxNN_<segment>_jointM, e.g. idx01_body_joint1.
DEFAULT_MATCH = 'hand'


class HandState(Node):

    def __init__(self):
        super().__init__('hand_state')
        self.declare_parameter('match', DEFAULT_MATCH)
        self.declare_parameter('period', 1.0)
        self._match = self.get_parameter('match').value

        self._latest = None
        self.create_subscription(
            JointState, JOINT_STATE_TOPIC, self._on_state, 10)
        self.create_timer(
            self.get_parameter('period').value, self._report)

        self.get_logger().info(
            f'watching joints matching "{self._match}" on {JOINT_STATE_TOPIC}')

    def _on_state(self, msg):
        self._latest = msg

    def _report(self):
        msg = self._latest
        if msg is None:
            self.get_logger().warning('no joint state received yet')
            return

        rows = [
            (n, p, v, e)
            for n, p, v, e in zip(
                msg.name, msg.position, msg.velocity, msg.effort)
            if self._match in n
        ]
        if not rows:
            self.get_logger().warning(
                f'no joint matched "{self._match}"; '
                f'available: {", ".join(msg.name[:6])} ...')
            return

        self.get_logger().info(f'--- {len(rows)} joints ---')
        for name, pos, vel, eff in rows:
            self.get_logger().info(
                f'  {name:<24} pos={pos:8.4f} rad  '
                f'vel={vel:7.3f}  eff={eff:8.3f}')


def main(args=None):
    rclpy.init(args=args)
    node = HandState()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
