"""Watch the G2's motion-control state in detail.

Subscribes /gdk/motion_control_status (gdk_msgs/MotionControlStatus) and
reports the control mode, error state, end-effector frames and any
self-collision pairs the controller is reporting.

Read-only.
"""

import rclpy
from rclpy.node import Node
from gdk_msgs.msg import MotionControlStatus

STATUS_TOPIC = '/gdk/motion_control_status'

MODE_NAMES = {
    MotionControlStatus.MODE_STOP: 'STOP',
    MotionControlStatus.MODE_SERVO: 'SERVO',
    MotionControlStatus.MODE_PLANNING: 'PLANNING',
}


def _fmt_pose(p):
    return (f'xyz=({p.position.x:7.4f}, {p.position.y:7.4f}, {p.position.z:7.4f}) '
            f'q=({p.orientation.x:6.3f}, {p.orientation.y:6.3f}, '
            f'{p.orientation.z:6.3f}, {p.orientation.w:6.3f})')


class StatusMonitor(Node):

    def __init__(self):
        super().__init__('status_monitor')
        self.declare_parameter('period', 1.0)
        self.declare_parameter('show_frames', True)
        self.declare_parameter('show_wrenches', False)

        self._latest = None
        self._seen = 0
        self._last_mode = None

        self.create_subscription(
            MotionControlStatus, STATUS_TOPIC, self._on_status, 10)
        self.create_timer(self.get_parameter('period').value, self._report)

        self.get_logger().info(f'listening on {STATUS_TOPIC}')

    def _on_status(self, msg):
        self._latest = msg
        self._seen += 1

        # Mode transitions are worth logging the moment they happen.
        if msg.mode != self._last_mode:
            name = MODE_NAMES.get(msg.mode, f'UNKNOWN({msg.mode})')
            if self._last_mode is not None:
                prev = MODE_NAMES.get(self._last_mode, self._last_mode)
                self.get_logger().warn(f'mode change: {prev} -> {name}')
            else:
                self.get_logger().info(f'mode: {name}')
            self._last_mode = msg.mode

    def _report(self):
        msg = self._latest
        if msg is None:
            self.get_logger().warn(
                'no status received -- is the robot in base-fastdds mode?')
            return

        mode = MODE_NAMES.get(msg.mode, f'UNKNOWN({msg.mode})')
        self.get_logger().info(f'--- mode={mode}  msgs={self._seen} ---')
        self._seen = 0

        if msg.error_code != 0:
            self.get_logger().error(
                f'error_code={msg.error_code} {msg.error_msg}')

        if msg.collision_pairs_1:
            self.get_logger().error(
                f'SELF-COLLISION: {len(msg.collision_pairs_1)} pair(s)')
            for a, b in zip(msg.collision_pairs_1, msg.collision_pairs_2):
                self.get_logger().error(f'    {a} <-> {b}')

        if not self.get_parameter('show_frames').value:
            return

        for i, name in enumerate(msg.frame_names):
            if i < len(msg.frame_poses):
                self.get_logger().info(
                    f'  {name:<20} {_fmt_pose(msg.frame_poses[i])}')
            if self.get_parameter('show_wrenches').value and \
                    i < len(msg.frame_wrenchs):
                w = msg.frame_wrenchs[i].force
                self.get_logger().info(
                    f'  {"":<20} force=({w.x:7.3f}, {w.y:7.3f}, {w.z:7.3f}) N')


def main(args=None):
    rclpy.init(args=args)
    node = StatusMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
