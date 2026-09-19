"""Console dashboard for the G2's motion-control state.

Combines /gdk/joint_state and /gdk/motion_control_status into one view,
refreshed in place.
"""

import rclpy
from rclpy.node import Node
from gdk_msgs.msg import JointState, MotionControlStatus

JOINT_STATE_TOPIC = '/gdk/joint_state'
MC_STATUS_TOPIC = '/gdk/motion_control_status'

MODE_NAMES = {0: 'STOP', 1: 'SERVO', 2: 'PLANNING'}


class StatusDisplay(Node):

    def __init__(self):
        super().__init__('status_display')
        self.declare_parameter('period', 1.0)
        self.declare_parameter('max_joints', 8)

        self._joints = None
        self._status = None

        self.create_subscription(
            JointState, JOINT_STATE_TOPIC, self._on_joints, 10)
        self.create_subscription(
            MotionControlStatus, MC_STATUS_TOPIC, self._on_status, 10)
        self.create_timer(self.get_parameter('period').value, self._render)

    def _on_joints(self, msg):
        self._joints = msg

    def _on_status(self, msg):
        self._status = msg

    def _render(self):
        lines = ['', '=' * 62, ' AgiBot G2 — status', '=' * 62]

        if self._status is None:
            lines.append(' motion control : (no data)')
        else:
            s = self._status
            mode = MODE_NAMES.get(s.mode, f'UNKNOWN({s.mode})')
            lines.append(f' mode           : {mode}')
            lines.append(f' error code     : {s.error_code}'
                         + (f'  {s.error_msg}' if s.error_msg else ''))
            if s.frame_names:
                lines.append(f' frames         : {len(s.frame_names)}')
            pairs = len(s.collision_pairs_1)
            if pairs:
                lines.append(f' COLLISION      : {pairs} pair(s)')
                for a, b in zip(s.collision_pairs_1, s.collision_pairs_2):
                    lines.append(f'                  {a} <-> {b}')

        if self._joints is None:
            lines.append(' joints         : (no data)')
        else:
            j = self._joints
            limit = self.get_parameter('max_joints').value
            lines.append(f' joints         : {len(j.name)}')
            faults = [n for n, e in zip(j.name, j.error_code) if e != 0]
            if faults:
                lines.append(f' JOINT FAULTS   : {", ".join(faults)}')
            for name, pos, vel in list(
                    zip(j.name, j.position, j.velocity))[:limit]:
                lines.append(f'   {name:<26} {pos:8.4f} rad  {vel:7.3f} rad/s')
            if len(j.name) > limit:
                lines.append(f'   ... {len(j.name) - limit} more')

        lines.append('=' * 62)
        print('\n'.join(lines), flush=True)


def main(args=None):
    rclpy.init(args=args)
    node = StatusDisplay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
