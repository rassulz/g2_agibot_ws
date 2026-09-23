"""End-effector tables for the G2: joint names, limits and reference poses.

Pure data -- no ROS, no GDK import, so it can be read or unit-tested anywhere.

The G2 reports which end effector is fitted in
``get_whole_body_status()['left_end_model' | 'right_end_model']``. That string
is also the ``target_type`` that ``move_ee_pos()`` expects, so the same key
drives identification and command.

Sources, both from GDK 3.2.3:
  * joint names  -- ~/.cache/agibot/app/gdk/config/end_reflection.json
  * limits/poses -- site/contents/reference/Python/robot/ (move_ee_pos)

Limits are version-bound. AgiBot's docs say so explicitly; re-check them
against the GDK on the robot before trusting them with hardware.
"""

# Joint counts move_ee_pos() enforces. A wrong count is rejected by the
# service, not silently padded.
MODELS = {
    'omnipicker': 1,
    'dahuan': 1,
    'ctek90d': 1,
    'o10_t2': 10,
    'o12_t2': 12,
}

# Single-DOF grippers: (open, closed). Everything between is a partial grip.
GRIPPER_RANGE = {
    'omnipicker': (-0.785, 0.0),
    'dahuan': (0.0, 0.025),
    'ctek90d': (-0.91, 0.0),
}

# name, min, max -- in the order move_ee_pos() expects.
O10_LEFT = [
    ('idx31_hand_l_thumb_roll_joint',  -1.1213740444063567,  0.029670597283903602),
    ('idx32_hand_l_thumb_abad_joint',  -0.04537856055185257, 1.642354826126664),
    ('idx33_hand_l_thumb_mcp_joint',   -0.8415977653116657,  0.0),
    ('idx36_hand_l_index_abad_joint',   0.0,                 0.16406094968746698),
    ('idx37_hand_l_index_pip_joint',    0.0,                 1.4835298641951802),
    ('idx39_hand_l_middle_pip_joint',   0.0,                 1.4835298641951802),
    ('idx41_hand_l_ring_abad_joint',   -0.16929693744344995, 0.0),
    ('idx42_hand_l_ring_pip_joint',     0.0,                 1.4835298641951802),
    ('idx44_hand_l_pinky_abad_joint',  -0.1850049007113989,  0.0),
    ('idx45_hand_l_pinky_pip_joint',    0.0,                 1.4835298641951802),
]

O10_RIGHT = [
    ('idx71_hand_r_thumb_roll_joint',  -0.029670597283903602, 1.1213740444063567),
    ('idx72_hand_r_thumb_abad_joint',  -1.642354826126664,    0.04537856055185257),
    ('idx73_hand_r_thumb_mcp_joint',    0.0,                  0.8415977653116657),
    ('idx76_hand_r_index_abad_joint',  -0.16406094968746698,  0.0),
    ('idx77_hand_r_index_pip_joint',    0.0,                  1.4835298641951802),
    ('idx79_hand_r_middle_pip_joint',   0.0,                  1.4835298641951802),
    ('idx81_hand_r_ring_abad_joint',    0.0,                  0.16929693744344995),
    ('idx82_hand_r_ring_pip_joint',     0.0,                  1.4835298641951802),
    ('idx84_hand_r_pinky_abad_joint',   0.0,                  0.1850049007113989),
    ('idx85_hand_r_pinky_pip_joint',    0.0,                  1.4835298641951802),
]

O12_LEFT = [
    ('idx31_hand_l_thumb_roll_joint',  -0.9425,  0.0),
    ('idx32_hand_l_thumb_abad_joint',   0.0,     1.3875),
    ('idx33_hand_l_thumb_mcp_joint',   -0.8273,  0.0),
    ('idx34_hand_l_thumb_pip_joint',   -1.2915,  0.0),
    ('idx36_hand_l_index_abad_joint',  -0.2618,  0.2618),
    ('idx37_hand_l_index_mcp_joint',    0.0,     1.3526),
    ('idx38_hand_l_index_pip_joint',    0.0,     1.5307),
    ('idx40_hand_l_middle_abad_joint', -0.2618,  0.2618),
    ('idx41_hand_l_middle_mcp_joint',   0.0,     1.3579),
    ('idx42_hand_l_middle_pip_joint',   0.0,     1.8151),
    ('idx44_hand_l_ring_mcp_joint',     0.0,     1.5359),
    ('idx47_hand_l_pinky_mcp_joint',    0.0,     1.5359),
]

O12_RIGHT = [
    ('idx71_hand_r_thumb_roll_joint',   0.0,     0.9425),
    ('idx72_hand_r_thumb_abad_joint',  -1.3875,  0.0),
    ('idx73_hand_r_thumb_mcp_joint',   -0.8273,  0.0),
    ('idx74_hand_r_thumb_pip_joint',   -1.2915,  0.0),
    ('idx76_hand_r_index_abad_joint',  -0.2618,  0.2618),
    ('idx77_hand_r_index_mcp_joint',    0.0,     1.3526),
    ('idx78_hand_r_index_pip_joint',    0.0,     1.5307),
    ('idx80_hand_r_middle_abad_joint', -0.2618,  0.2618),
    ('idx81_hand_r_middle_mcp_joint',   0.0,     1.3579),
    ('idx82_hand_r_middle_pip_joint',   0.0,     1.8151),
    ('idx84_hand_r_ring_mcp_joint',     0.0,     1.5359),
    ('idx87_hand_r_pinky_mcp_joint',    0.0,     1.5359),
]

JOINTS = {
    ('o10_t2', 'left'): O10_LEFT,
    ('o10_t2', 'right'): O10_RIGHT,
    ('o12_t2', 'left'): O12_LEFT,
    ('o12_t2', 'right'): O12_RIGHT,
}

# Reference poses straight from AgiBot's docs ("典型状态值").
POSES = {
    ('o10_t2', 'left'): {
        'open': [0.0] * 10,
        'grip': [-0.2, 1.45, -0.75, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0],
    },
    ('o10_t2', 'right'): {
        'open': [0.0] * 10,
        'grip': [0.2, -1.45, 0.75, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0],
    },
    ('o12_t2', 'left'): {
        'open': [-0.53, 0.42, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'grip': [-0.77, 0.5, -0.4, -0.36, -0.12, 0.69, 0.46, 0.0, 0.72, 0.5,
                 0.63, 0.63],
    },
    ('o12_t2', 'right'): {
        'open': [0.53, -0.42, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'grip': [0.77, -0.5, -0.4, -0.36, 0.12, 0.69, 0.46, 0.0, 0.72, 0.5,
                 0.63, 0.63],
    },
}

GROUP = {'left': 'left_tool', 'right': 'right_tool'}


def is_dexterous(model):
    """True for the multi-finger OmniHands, False for single-DOF grippers."""
    return model in ('o10_t2', 'o12_t2')


def joint_names(model, side):
    """Joint names in command order, or [] for a single-DOF gripper."""
    return [n for n, _, _ in JOINTS.get((model, side), [])]


def pose(model, side, name):
    """A named reference pose ('open'/'grip'), or None if undefined.

    Grippers are handled here too so callers do not special-case them:
    GRIPPER_RANGE holds (open, closed) for the 1-DOF models.
    """
    if model in GRIPPER_RANGE:
        opened, closed = GRIPPER_RANGE[model]
        return [opened] if name == 'open' else [closed]
    table = POSES.get((model, side))
    return list(table[name]) if table and name in table else None


def clamp(model, side, positions):
    """Clamp to the documented limits.

    Returns (clamped, adjustments) where adjustments lists
    (joint_name, requested, applied) for every value that had to move --
    so a caller can report what it changed instead of silently altering
    the command.
    """
    if model in GRIPPER_RANGE:
        lo, hi = sorted(GRIPPER_RANGE[model])
        table = [(model, lo, hi)]
    else:
        table = JOINTS.get((model, side))
        if table is None:
            return list(positions), []

    out, adjusted = [], []
    for (name, lo, hi), want in zip(table, positions):
        got = min(max(want, lo), hi)
        out.append(got)
        if got != want:
            adjusted.append((name, want, got))
    return out, adjusted


# --- gestures ---------------------------------------------------------------
#
# The SDK_* tables below are generated by tools/dump_gestures.py from the
# AgiLink OmniHand SDK 1.1.8 kinematics solver -- AgiBot's own poses, not
# guesses. Do not hand-edit them. Everything after SDK_GESTURES is written
# by hand.
#
# The solver is pure maths: OmniHand2025Solver.set_hand_gesture() returns
# actuator counts, and actuator_input_to_active_joint_pos() turns those into
# joint angles. No hand and no CAN bus are involved, so the numbers can be
# lifted out offline and sent through the robot's own move_ee_pos() instead.
#
# The joint order matches end_reflection.json, confirmed by reading the poses
# rather than assuming: 'num1' straightens only the index, 'num4' straightens
# all four fingers, 'like' straightens only the thumb. Abduction is positive
# on the left hand and negative on the right, which is also what the limits
# in JOINTS say.
#
# O10 ships 18 gestures, O12 only 5 -- so O12 has no scissors and one is
# derived below.

SDK_O10_LEFT = {
    'all_zero': [
        -0, -0.0001, -0.0007, -0, 0.0146, 0.0146, 0, 0.0146, 0, 0.0146],
    'clasping': [
        -0.5001, 0.8, -0.2004, 0.16, 0.6063, 0.6063, -0.17, 0.6063, -0.17,
        0.6063],
    'fist1': [
        -0.4302, 0.2999, -0.6606, -0, 1.4763, 1.4763, 0, 1.4763, 0, 1.4763],
    'fist2': [
        -0.5001, 0.9996, -0.7501, -0, 1.4763, 1.4763, 0, 1.4763, 0, 1.4763],
    'hand_heart1': [
        0.03, 1.3598, -0.0007, -0, 0.6558, 0.6558, 0, 0.6558, 0, 0.6558],
    'hand_heart2': [
        -0.3002, 0.0998, -0.6606, -0, 1.0954, 1.0954, 0, 1.0954, 0, 1.0954],
    'hand_heart3': [
        -0, 1.56, -0.4596, -0, 0.0146, 0.0146, 0, 0.0146, 0, 0.0146],
    'ily': [
        -0.3302, -0.0001, -0.0007, 0.1, 0.0146, 1.4763, -0.07, 1.4763,
        -0.11, 0.0146],
    'like': [
        -0.2701, -0.0001, -0.0007, -0, 1.4763, 1.4763, 0, 1.4763, 0, 1.4763],
    'num1': [
        -0.3201, 1.1197, -0.7895, 0.06, 0.0146, 1.4763, 0, 1.4763, 0, 1.4763],
    'num2': [
        -0.4801, 1.4997, -0.7895, 0.16, 0.0146, 0.0146, 0, 1.4763, 0, 1.4763],
    'num3': [
        -0.6402, 1.4799, -0.8095, 0.16, 0.0146, 0.0146, -0.09, 0.0146,
        -0.09, 1.4763],
    'num4': [
        -0.6402, 1.4799, -0.8095, 0.16, 0.0146, 0.0146, -0.07, 0.0146,
        -0.15, 0.0146],
    'num6': [
        -0.4001, -0.0001, -0.0007, -0, 1.4763, 1.4763, -0.05, 1.4763, -0.17,
        0.0146],
    'num8': [
        -0.4001, -0.0001, -0.0007, -0, 0.0146, 1.4763, 0, 1.4763, 0, 1.4763],
    'ok': [
        0.03, 1.5096, -0.7006, 0.16, 0.8471, 0.202, -0.07, 0.1458, -0.107,
        0.0958],
    'one_handed_finger_heart': [
        -0.8002, 0.3997, -0.4696, -0, 0.8182, 1.4763, 0, 1.4763, 0, 1.4763],
    'paper': [
        -0.5801, 0.2099, -0.0007, -0, 0.0146, 0.0146, 0, 0.0146, 0, 0.0146],
}

SDK_O10_RIGHT = {
    'all_zero': [
        -0.0002, -0.0003, 0.0003, 0, 0.0146, 0.0146, 0, 0.0146, 0, 0.0146],
    'clasping': [
        0.4998, -0.8004, 0.2001, -0.16, 0.6063, 0.6063, 0.17, 0.6063, 0.17,
        0.6063],
    'fist1': [
        0.4299, -0.3003, 0.6605, 0, 1.4763, 1.4763, 0, 1.4763, 0, 1.4763],
    'fist2': [0.4998, -1.0001, 0.75, 0, 1.4763, 1.4763, 0, 1.4763, 0, 1.4763],
    'hand_heart1': [
        -0.03, -1.3603, 0.0003, 0, 0.6558, 0.6558, 0, 0.6558, 0, 0.6558],
    'hand_heart2': [
        0.2999, -0.1002, 0.6605, 0, 1.0954, 1.0954, 0, 1.0954, 0, 1.0954],
    'hand_heart3': [
        -0.0002, -1.5604, 0.4593, 0, 0.0146, 0.0146, 0, 0.0146, 0, 0.0146],
    'ily': [
        0.3299, -0.0003, 0.0003, -0.1, 0.0146, 1.4763, 0.07, 1.4763, 0.11,
        0.0146],
    'like': [0.2699, -0.0003, 0.0003, 0, 1.4763, 1.4763, 0, 1.4763, 0, 1.4763],
    'num1': [
        0.3198, -1.1201, 0.7894, -0.06, 0.0146, 1.4763, 0, 1.4763, 0, 1.4763],
    'num2': [
        0.4799, -1.5001, 0.7894, -0.16, 0.0146, 0.0146, 0, 1.4763, 0, 1.4763],
    'num3': [
        0.6399, -1.4803, 0.8094, -0.16, 0.0146, 0.0146, 0.09, 0.0146, 0.09,
        1.4763],
    'num4': [
        0.6399, -1.4803, 0.8094, -0.16, 0.0146, 0.0146, 0.07, 0.0146, 0.15,
        0.0146],
    'num6': [
        0.3998, -0.0003, 0.0003, 0, 1.4763, 1.4763, 0.05, 1.4763, 0.17,
        0.0146],
    'num8': [0.3998, -0.0003, 0.0003, 0, 0.0146, 1.4763, 0, 1.4763, 0, 1.4763],
    'ok': [
        -0.03, -1.51, 0.7004, -0.16, 0.8471, 0.202, 0.07, 0.1458, 0.107,
        0.0958],
    'one_handed_finger_heart': [
        0.7999, -0.4001, 0.4693, 0, 0.8182, 1.4763, 0, 1.4763, 0, 1.4763],
    'paper': [
        0.5798, -0.2103, 0.0003, 0, 0.0146, 0.0146, 0, 0.0146, 0, 0.0146],
}

SDK_O12_LEFT = {
    'all_zero': [0, 0, 0, 0, -0, 0, 0, -0, 0, 0, 0, 0],
    'fist': [
        0, 0, 0, -1.1994, 0.0001, 1.3461, 1.4165, 0.0001, 1.3461, 1.4208,
        1.5056, 1.5056],
    'ok': [0, 0, 0, -0.9483, 0, 0.4993, 0.6419, -0, 0, 0, 0, 0],
    'pack': [0.1381, 0, -0.83, 0, -0, 0, 0, -0, 0, 0, 0, 0],
    'paper': [0, 0, -0.3296, -0.3741, -0, 0, 0, -0, 0, 0, 0, 0],
}

SDK_O12_RIGHT = {
    'all_zero': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'fist': [
        0.4995, -0.1731, 0, -1.1994, -0.0001, 1.3461, 1.4165, -0.0001,
        1.3461, 1.4208, 1.5056, 1.5056],
    'ok': [0.3, -0.5186, 0, -0.9483, -0, 0.4993, 0.6419, 0, 0, 0, 0, 0],
    'pack': [0.5795, -0.8502, -0.1572, 0, -0.26, 0.6316, 0, 0, 0, 0, 0, 0],
    'paper': [0.3399, 0, -0.3296, -0.3741, 0, 0, 0, 0, 0, 0, 0, 0],
}

SDK_GESTURES = {
    ('o10_t2', 'left'): SDK_O10_LEFT,
    ('o10_t2', 'right'): SDK_O10_RIGHT,
    ('o12_t2', 'left'): SDK_O12_LEFT,
    ('o12_t2', 'right'): SDK_O12_RIGHT,
}

# O12's solver has no V sign, so build one from its own fist: keep the thumb
# curl and the ring/pinky flexion, straighten index and middle, and spread
# them with the abduction joints (O12 has one on both fingers, so the V is
# real). Mirrored on the right, matching how every SDK pose mirrors.
_O12_SPREAD = 0.2618        # the documented abduction limit


def _o12_scissors(side):
    fist = SDK_GESTURES[('o12_t2', side)]['fist']
    spread = _O12_SPREAD if side == 'left' else -_O12_SPREAD
    return (fist[:4]
            + [spread, 0.0, 0.0]
            + [-spread, 0.0, 0.0]
            + fist[10:12])


for _side in ('left', 'right'):
    SDK_GESTURES[('o12_t2', _side)]['scissors'] = _o12_scissors(_side)

# What rock, paper and scissors mean per model.
#
# O10 ships two fists, and for this game fist2 is the right one: doc/pic
# shows fist1 with the thumb standing out sideways, while fist2 tucks it
# across the palm into a compact fist. scissors is num2, which doc/pic shows
# as a textbook V.
#
# O12's thumb on the left-hand fist comes back all zeros from the solver
# while the right is curled -- looks like an SDK quirk, so check the left
# hand visually before trusting it.
RPS = {
    'o10_t2': {'rock': 'fist2', 'paper': 'paper', 'scissors': 'num2'},
    'o12_t2': {'rock': 'fist', 'paper': 'paper', 'scissors': 'scissors'},
}

GESTURE_NAMES = ('rock', 'paper', 'scissors')

# Poses of our own, for what the SDK does not ship. Same joint order.
#
# neutral: a hand at rest. None of the 18 factory poses is one -- all_zero
# is a flat hand, the same as paper, and clasping is half of a two-hand
# pose with the fingers splayed. So: the fingers curled a little, in a
# cascade from index to pinky (0.4 -> 0.7 rad, 23-40 deg) the way a
# relaxed hand hangs, no spread, and the thumb loosely beside the index
# rather than across the palm. It stays well clear of the game poses --
# at least 0.69 rad of finger flexion from paper, 1.08 from rock and 1.15
# from scissors -- so nobody reads it as a move.
CUSTOM_GESTURES = {
    ('o10_t2', 'left'): {
        'neutral': [-0.3, 0.35, -0.2, 0.0, 0.4, 0.5, 0.0, 0.6, 0.0, 0.7],
    },
    ('o10_t2', 'right'): {
        'neutral': [0.3, -0.35, 0.2, 0.0, 0.4, 0.5, 0.0, 0.6, 0.0, 0.7],
    },
}


def gesture_names(model, side):
    """Everything `gesture()` accepts for this effector."""
    if model in GRIPPER_RANGE:
        return ['rock', 'paper']
    return sorted(
        set(GESTURE_NAMES) | set(SDK_GESTURES.get((model, side), {}))
        | set(CUSTOM_GESTURES.get((model, side), {})))


def gesture(model, side, name):
    """A named pose, or None if this effector cannot make it.

    Accepts rock/paper/scissors and, on the OmniHands, any SDK gesture name
    too -- 'ok', 'like', 'num3', 'clasping' and the rest.

    Single-DOF grippers manage rock (closed) and paper (open); scissors
    needs fingers, so it returns None rather than something that would look
    like a shrug.
    """
    name = name.strip().lower()
    if model in GRIPPER_RANGE:
        opened, closed = GRIPPER_RANGE[model]
        if name == 'paper':
            return [opened]
        if name == 'rock':
            return [closed]
        return None

    custom = CUSTOM_GESTURES.get((model, side), {})
    if name in custom:
        return list(custom[name])
    table = SDK_GESTURES.get((model, side))
    if table is None:
        return None
    key = RPS.get(model, {}).get(name, name)
    return list(table[key]) if key in table else None


# --- move planning (O10) ----------------------------------------------------
#
# The thumb folds over the fingers, so moving everything at once can drive a
# finger into the thumb. Found on the hand itself: going from rock to
# scissors, index and middle have to come out from under the thumb. The rule
# that covers every rock/paper/scissors transition:
#
#   fingers closing -> fingers first, then the thumb wraps over them
#   fingers opening -> the thumb moves out of the way first, then the fingers
#
# Indices are positions in JOINTS[('o10_t2', side)], which is also the order
# the AgiLink SDK uses for get/set_all_active_joint_angles().

O10_THUMB = (0, 1, 2)                 # roll, abad, mcp
O10_FINGERS = (3, 4, 5, 6, 7, 8, 9)   # abad and pip joints of the four fingers
O10_FLEX = (4, 5, 7, 9)               # the pip joints: how far the hand is closed


def o10_phases(start, goal):
    """Split an O10 move into [(label, pose), ...] reached one after another.

    Each pose is a full 10-joint target; the last one is always `goal`.
    """
    closing = sum(goal[i] - start[i] for i in O10_FLEX) > 0
    thumb_done = [goal[i] if i in O10_THUMB else start[i]
                  for i in range(len(goal))]
    fingers_done = [goal[i] if i in O10_FINGERS else start[i]
                    for i in range(len(goal))]
    if closing:
        return [('fingers', fingers_done), ('thumb', list(goal))]
    return [('thumb', thumb_done), ('fingers', list(goal))]


def sdk_gesture(model, name):
    """The AgiLink SDK gesture key behind `name` ('rock' -> 'fist2'), or None."""
    name = name.strip().lower()
    key = RPS.get(model, {}).get(name, name)
    table = SDK_GESTURES.get((model, 'left'), {})
    return key if key in table else None
