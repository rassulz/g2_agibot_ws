"""Open and close the G2's end effector.

This node MOVES HARDWARE. It refuses to do so unless started with
``-p enable:=true``; without that it prints exactly what it would send and
exits, which is the intended way to check a command before running it.

Named gestures are the simplest way in -- rock, paper, scissors:

    ros2 run omni_hand hand_grasp -p side:=right -p gesture:=rock
    ros2 run omni_hand hand_grasp -p side:=right -p gesture:=rock,paper,scissors

Several names, comma separated, play in order with `hold` seconds between.

The poses come from AgiBot's own SDK solver, not from guesswork -- see
hand_model.py. O10 also answers to the other fifteen names it ships with
('ok', 'like', 'num3', 'clasping', ...); pass one to see the full list. A
1-DOF gripper manages rock and paper but not scissors.

Otherwise one knob covers grasping:

    grip = 0.0   fully open
    grip = 1.0   full grasp
    grip = 0.4   40% of the way from open to grasp

The endpoints are AgiBot's own reference poses (hand_model.POSES); `grip`
interpolates between them, so a partial value is a real intermediate hand
shape rather than a guess. For anything else, pass `positions` directly.

Before sending, the node checks that an effector is actually fitted, that its
error code is clear and that the arm is not in e-stop; then clamps every value
to the documented joint limits and reports what it clamped. It ramps from the
hand's measured position in `steps` increments rather than jumping.

Uses move_ee_pos(), which AgiBot documents as incompatible with the servo
interface -- do not run this alongside a servo controller.

    # look first (no motion, no --enable needed)
    ros2 run omni_hand hand_grasp -p side:=right -p grip:=1.0

    # then actually move
    ros2 run omni_hand hand_grasp -p side:=right -p grip:=1.0 -p enable:=true
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


class HandGrasp(Node):

    def __init__(self):
        super().__init__('hand_grasp')
        self.declare_parameter('side', 'right')       # 'left' or 'right'
        self.declare_parameter('gesture', '')         # rock/paper/scissors
        self.declare_parameter('hold', 2.0)           # seconds per gesture
        self.declare_parameter('grip', 0.0)           # 0 = open, 1 = grasp
        # Declared by type: an empty default cannot be type-inferred, and
        # leaving it uninitialised is how "not given" is expressed.
        self.declare_parameter(
            'positions', rclpy.Parameter.Type.DOUBLE_ARRAY)  # overrides grip
        self.declare_parameter('model', '')           # '' = auto-detect
        self.declare_parameter('steps', 5)            # ramp increments
        self.declare_parameter('step_delay', 0.15)    # seconds between steps
        self.declare_parameter('enable', False)       # required to move

        self._gdk = None
        self._robot = None
        self._initialised = False

    # --- lifecycle -------------------------------------------------------

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
        time.sleep(2.0)
        self.get_logger().info('GDK initialised')
        return True

    def release(self):
        if self._initialised:
            try:
                self._gdk.gdk_release()
            except Exception as exc:
                self.get_logger().warning(f'gdk_release() failed: {exc}')

    # --- checks ----------------------------------------------------------

    def resolve_model(self, side):
        """Which effector is fitted on `side`, or None if it cannot move.

        An explicit `model` parameter skips detection -- useful if the robot
        misreports -- but the safety checks below still run.
        """
        log = self.get_logger()
        override = self.get_parameter('model').value

        try:
            status = self._robot.get_whole_body_status()
        except Exception as exc:
            log.error(
                f'get_whole_body_status() failed: {exc}\n'
                'Motion control is not answering; nothing was sent.')
            return None

        if status.get(f'{side}_arm_estop'):
            log.error(f'{side} arm is in ESTOP -- refusing to command the hand')
            return None

        err = status.get(f'{side}_end_error', 0)
        if err:
            log.error(
                f'{side} end effector reports error code {err} -- '
                'refusing to command it. Run hand_identify for detail.')
            return None

        detected = status.get(f'{side}_end_model', '') or ''
        if override:
            if detected and detected != override:
                log.warning(
                    f'robot reports {detected!r} on the {side} side but '
                    f'model:={override!r} was given; using the override')
            return override

        if not detected:
            log.error(
                f'no end effector reported on the {side} side. '
                'Check the cable, and that the robot booted in a scene that '
                'configures this hand (mode_switch --list).')
            return None

        if detected not in hand_model.MODELS:
            log.error(
                f'{side} reports model {detected!r}, which this package does '
                'not have a joint table for. Add it to hand_model.py, or pass '
                'positions directly with model:=<name>.')
            return None

        return detected

    def current_positions(self, side, count):
        """The hand's measured joint positions, or None if unreadable."""
        try:
            state = self._robot.get_end_state().get(f'{side}_end_state')
        except Exception as exc:
            self.get_logger().warning(f'get_end_state() failed: {exc}')
            return None
        joints = (state or {}).get('end_states') or []
        if len(joints) != count:
            return None
        return [j.get('position', 0.0) for j in joints]

    # --- the command -----------------------------------------------------

    def targets(self, model, side):
        """The requested poses as [(label, positions)], before clamping.

        Three ways to ask, most specific first: a named gesture (or several,
        comma separated, played in order), explicit positions, or the `grip`
        slider.
        """
        log = self.get_logger()

        names = [
            n.strip().lower()
            for n in str(self.get_parameter('gesture').value or '').split(',')
            if n.strip()]
        if not names:
            return self._single(model, side)

        known = hand_model.gesture_names(model, side)
        out = []
        for name in names:
            pose = hand_model.gesture(model, side, name)
            if pose is None:
                log.error(
                    f'{model} cannot make {name!r}. Known: '
                    f'{", ".join(known)}')
                return None
            out.append((name, pose))
        return out

    def _single(self, model, side):
        log = self.get_logger()
        # Uninitialised type-declared parameters read back as None on some
        # distros and raise on others; both mean "not given".
        try:
            custom = list(self.get_parameter('positions').value or [])
        except Exception:
            custom = []
        expected = hand_model.MODELS[model]

        if custom:
            if len(custom) != expected:
                log.error(
                    f'{model} takes {expected} positions, got {len(custom)}')
                return None
            return [('positions', custom)]

        grip = float(self.get_parameter('grip').value)
        if not 0.0 <= grip <= 1.0:
            log.error(f'grip must be in [0, 1], got {grip}')
            return None

        opened = hand_model.pose(model, side, 'open')
        closed = hand_model.pose(model, side, 'grip')
        if opened is None or closed is None:
            log.error(
                f'no reference poses for {model}/{side}; '
                'pass positions explicitly')
            return None
        return [('grip=%.2f' % grip,
                 [o + (c - o) * grip for o, c in zip(opened, closed)])]

    def send(self, model, side, positions):
        states = self._gdk.JointStates()
        states.group = hand_model.GROUP[side]
        states.target_type = model
        entries = []
        for value in positions:
            joint = self._gdk.JointState()
            joint.position = float(value)
            entries.append(joint)
        states.states = entries
        states.nums = len(entries)
        self._robot.move_ee_pos(states)

    def run(self):
        log = self.get_logger()
        side = self.get_parameter('side').value
        if side not in ('left', 'right'):
            log.error(f"side must be 'left' or 'right', got {side!r}")
            return

        model = self.resolve_model(side)
        if model is None:
            return

        wanted = self.targets(model, side)
        if wanted is None:
            return

        joints = hand_model.joint_names(model, side) or [model]
        enabled = bool(self.get_parameter('enable').value)
        hold = float(self.get_parameter('hold').value)

        plan = []
        for label, want in wanted:
            goal, adjusted = hand_model.clamp(model, side, want)
            plan.append((label, goal))

            log.info(f'{label}: {side} {model} '
                     f'({hand_model.MODELS[model]} DOF)')
            for name, value in zip(joints, goal):
                log.info(f'  {name:<32} -> {value:7.4f}')
            for name, requested, applied in adjusted:
                log.warning(
                    f'clamped {name}: {requested:.4f} -> {applied:.4f} '
                    '(limit)')

        if not enabled:
            log.warning(
                'DRY RUN -- nothing sent. Re-run with -p enable:=true to '
                'move the hand.')
            return

        for index, (label, goal) in enumerate(plan):
            log.info(f'-> {label}')
            if not self._goto(model, side, goal):
                return
            if index < len(plan) - 1:
                time.sleep(hold)

        log.info('done')

    def _goto(self, model, side, goal):
        """Ramp from the measured position to `goal`. False if it failed."""
        log = self.get_logger()
        start = self.current_positions(side, len(goal))
        steps = max(1, int(self.get_parameter('steps').value))
        delay = float(self.get_parameter('step_delay').value)

        if start is None:
            log.warning(
                'could not read current position; sending the target in one '
                'step instead of ramping')
            start, steps = goal, 1

        try:
            for step in range(1, steps + 1):
                blend = step / steps
                waypoint = [a + (b - a) * blend for a, b in zip(start, goal)]
                self.send(model, side, waypoint)
                if step < steps:
                    time.sleep(delay)
        except Exception as exc:
            log.error(f'move_ee_pos() failed: {exc}')
            return False
        return True


def main(args=None):
    rclpy.init(args=args)
    node = HandGrasp()
    try:
        if not node.connect():
            return
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.release()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
