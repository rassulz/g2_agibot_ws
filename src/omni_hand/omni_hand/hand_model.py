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
# Rock-paper-scissors, in the same joint order as JOINTS above.
#
# 'paper' is AgiBot's own open pose. 'rock' and 'scissors' are built here:
# the thumb copies AgiBot's grip pose (a curl they validated), and the finger
# flexors go to ~90% of their documented limit so a fist actually reads as a
# fist -- their reference grip only curls to about 1.0 rad, which looks more
# like holding a ball.
#
# For scissors the abduction joints spread index and middle apart. O12 has an
# abad joint on both fingers so it makes a real V; O10 has one only on the
# index, so the V is shallower. Which way positive abduction points is not
# stated in the docs -- if the V opens the wrong way, flip the sign of the
# abad entries. Nothing else about the pose depends on it.

_O10_L_THUMB_CURL = [-0.2, 1.45, -0.75]
_O10_R_THUMB_CURL = [0.2, -1.45, 0.75]
_O10_CURL = 1.35          # pip flexion, limit 1.4835

_O12_L_THUMB_CURL = [-0.77, 0.5, -0.4, -0.36]
_O12_R_THUMB_CURL = [0.77, -0.5, -0.4, -0.36]
_O12_MCP = 1.30           # limit 1.3526 (index) / 1.3579 (middle)
_O12_PIP = 1.40           # limit 1.5307 (index) / 1.8151 (middle)
_O12_RP = 1.40            # ring and pinky mcp, limit 1.5359
_O12_SPREAD = 0.2618      # index/middle abduction limit

GESTURES = {
    # O10 order: thumb roll/abad/mcp, index abad/pip, middle pip,
    #            ring abad/pip, pinky abad/pip
    ('o10_t2', 'left'): {
        'paper': [0.0] * 10,
        'rock': _O10_L_THUMB_CURL + [
            0.0, _O10_CURL, _O10_CURL, 0.0, _O10_CURL, 0.0, _O10_CURL],
        'scissors': _O10_L_THUMB_CURL + [
            0.164, 0.0, 0.0, 0.0, _O10_CURL, 0.0, _O10_CURL],
    },
    ('o10_t2', 'right'): {
        'paper': [0.0] * 10,
        'rock': _O10_R_THUMB_CURL + [
            0.0, _O10_CURL, _O10_CURL, 0.0, _O10_CURL, 0.0, _O10_CURL],
        'scissors': _O10_R_THUMB_CURL + [
            -0.164, 0.0, 0.0, 0.0, _O10_CURL, 0.0, _O10_CURL],
    },
    # O12 order: thumb roll/abad/mcp/pip, index abad/mcp/pip,
    #            middle abad/mcp/pip, ring mcp, pinky mcp
    ('o12_t2', 'left'): {
        'paper': POSES[('o12_t2', 'left')]['open'],
        'rock': _O12_L_THUMB_CURL + [
            0.0, _O12_MCP, _O12_PIP, 0.0, _O12_MCP, _O12_PIP,
            _O12_RP, _O12_RP],
        'scissors': _O12_L_THUMB_CURL + [
            _O12_SPREAD, 0.0, 0.0, -_O12_SPREAD, 0.0, 0.0,
            _O12_RP, _O12_RP],
    },
    ('o12_t2', 'right'): {
        'paper': POSES[('o12_t2', 'right')]['open'],
        'rock': _O12_R_THUMB_CURL + [
            0.0, _O12_MCP, _O12_PIP, 0.0, _O12_MCP, _O12_PIP,
            _O12_RP, _O12_RP],
        'scissors': _O12_R_THUMB_CURL + [
            -_O12_SPREAD, 0.0, 0.0, _O12_SPREAD, 0.0, 0.0,
            _O12_RP, _O12_RP],
    },
}

GESTURE_NAMES = ('rock', 'paper', 'scissors')


def gesture(model, side, name):
    """A named gesture, or None if this effector cannot make it.

    Single-DOF grippers can only manage rock (closed) and paper (open);
    scissors needs fingers, so it returns None rather than something that
    would look like a shrug.
    """
    if model in GRIPPER_RANGE:
        opened, closed = GRIPPER_RANGE[model]
        if name == 'paper':
            return [opened]
        if name == 'rock':
            return [closed]
        return None
    table = GESTURES.get((model, side))
    return list(table[name]) if table and name in table else None
