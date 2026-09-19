"""Report which end effector the G2 has fitted, and its live joint state.

Read-only. This node never commands motion -- run it first, after plugging a
hand in, to confirm the robot actually sees it.

Two GDK calls do the work:
  get_whole_body_status()  -> left_end_model / right_end_model, error codes
  get_end_state()          -> per-joint position, current, temperature, errors

The model string it prints ('o10_t2', 'o12_t2', 'omnipicker', ...) is exactly
what hand_grasp.py needs as target_type, so start here.

Needs the GDK binding, so it runs on the robot or in the humble container --
see face_video.py for the ABI reason.
"""

import time

import rclpy
from rclpy.node import Node

try:
    from omni_hand import hand_model
except ImportError:  # run straight from a git checkout, without colcon
    import os
    import sys
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from omni_hand import hand_model


class HandIdentify(Node):

    def __init__(self):
        super().__init__('hand_identify')
        # 0.0 = report once and exit; >0 = re-read every N seconds.
        self.declare_parameter('period', 0.0)
        self.declare_parameter('verbose', True)

        self._gdk = None
        self._robot = None
        self._initialised = False

    def connect(self):
        try:
            import agibot_gdk
        except ImportError as exc:
            self.get_logger().error(
                f'cannot import agibot_gdk: {exc}\n'
                'Run this on the robot, or in the humble container.')
            return False

        try:
            if agibot_gdk.gdk_init() != agibot_gdk.GDKRes.kSuccess:
                self.get_logger().error('gdk_init() failed')
                return False
        except Exception as exc:
            self.get_logger().error(f'gdk_init() raised: {exc}')
            return False

        self._initialised = True
        self._gdk = agibot_gdk
        self._robot = agibot_gdk.Robot()
        time.sleep(2.0)          # the docs' own settling time before first call
        self.get_logger().info('GDK initialised')
        return True

    def release(self):
        if self._initialised:
            try:
                self._gdk.gdk_release()
            except Exception as exc:
                self.get_logger().warning(f'gdk_release() failed: {exc}')

    # --- reporting -------------------------------------------------------

    def report(self):
        log = self.get_logger()

        try:
            status = self._robot.get_whole_body_status()
        except Exception as exc:
            log.error(
                f'get_whole_body_status() failed: {exc}\n'
                'If this is a request timeout, the motion-control service is '
                'not answering -- check the robot is in a launch scene that '
                'starts it (mode_switch --list).')
            return False

        models = {
            'left': status.get('left_end_model', '') or '(none)',
            'right': status.get('right_end_model', '') or '(none)',
        }
        errors = {
            'left': status.get('left_end_error', 0),
            'right': status.get('right_end_error', 0),
        }

        log.info('--- end effectors ---')
        for side in ('left', 'right'):
            model = models[side]
            err = errors[side]
            dof = hand_model.MODELS.get(model)
            kind = (
                f'{dof} DOF' if dof
                else 'unknown to hand_model.py -- check GDK version')
            log.info(f'  {side:<5} {model:<12} {kind}')
            if err:
                log.error(f'  {side:<5} error code {err}')

        # Arm estop matters here: a hand on an e-stopped arm will not move.
        for side in ('left', 'right'):
            if status.get(f'{side}_arm_estop'):
                log.warning(f'{side} arm is in ESTOP')
            if status.get(f'{side}_arm_control'):
                log.warning(
                    f'{side} arm is under active control by something else')

        if not self.get_parameter('verbose').value:
            return True

        try:
            end_state = self._robot.get_end_state()
        except Exception as exc:
            log.warning(f'get_end_state() failed: {exc}')
            return True

        for side in ('left', 'right'):
            state = end_state.get(f'{side}_end_state')
            if not state:
                continue
            joints = state.get('end_states') or []
            if not joints:
                continue

            names = state.get('names') or hand_model.joint_names(
                models[side], side)
            log.info(
                f'--- {side} joints ({len(joints)}), '
                f'controlled={state.get("controlled")} ---')
            for i, joint in enumerate(joints):
                name = names[i] if i < len(names) else f'joint{i}'
                flags = []
                if not joint.get('enable', True):
                    flags.append('DISABLED')
                if joint.get('err_code'):
                    flags.append(f'err={joint["err_code"]}')
                log.info(
                    f'  [{i:2}] {name:<32} '
                    f'pos={joint.get("position", 0.0):7.4f} rad  '
                    f'cur={joint.get("current", 0.0):6.2f} A  '
                    f'{joint.get("temperature", 0.0):5.1f} C'
                    + ('  ' + ' '.join(flags) if flags else ''))

        return True


def main(args=None):
    rclpy.init(args=args)
    node = HandIdentify()
    try:
        if not node.connect():
            return
        period = node.get_parameter('period').value
        if period > 0.0:
            node.create_timer(period, node.report)
            rclpy.spin(node)
        else:
            node.report()
    except KeyboardInterrupt:
        pass
    finally:
        node.release()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
