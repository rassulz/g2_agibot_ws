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
