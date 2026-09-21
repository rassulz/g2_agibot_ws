"""Dump the AgiLink OmniHand SDK's gesture poses as joint angles.

Regenerates the SDK_GESTURES tables in ../omni_hand/hand_model.py. The SDK's
kinematics solver is pure maths -- no hand, no CAN bus -- so this runs offline
on any machine.

    python3 -m venv /tmp/oh
    /tmp/oh/bin/pip install \
        ~/agillink_omnihand_sdk/linux/x64/python/omnihand-1.1.8-cp310-*.whl
    /tmp/oh/bin/python dump_gestures.py      # writes GESTURES_OUT (JSON)

Pick the wheel matching your Python: the SDK ships cp310 through cp314.

Note the binding disagrees with the SDK's own docs on two names: the O10
solver takes hand_type= and has actuator_input_to_active_joint_pos(), while
the O12 one takes is_left_hand= and has convert_actuator_to_joint().
"""
import json
from omnihand import OmniHand2025Gesture as G10, OmniHandPro2025Gesture as G12
from omnihand.omnihand_2025 import OmniHand2025Solver as S10
from omnihand.omnihand_pro_2025 import OmniHandPro2025Solver as S12

out = {}
for model, mk, Enum, conv in (
        ('o10_t2', lambda L: S10(hand_type=L), G10,
         lambda s, a: s.actuator_input_to_active_joint_pos(a)),
        ('o12_t2', lambda L: S12(is_left_hand=L), G12,
         lambda s, a: s.convert_actuator_to_joint(a))):
    for side, is_left in (('left', True), ('right', False)):
        d = {}
        for n in sorted(x for x in dir(Enum) if x.startswith('OMNI')):
            s = mk(is_left)
            try:
                s.show_log(False)
            except Exception:
                pass
            ai = s.set_hand_gesture(getattr(Enum, n))
            d[n.split('GESTURE_', 1)[-1].lower()] = [
                round(float(v), 4) for v in conv(s, ai)]
        out[model + '|' + side] = d
with open('GESTURES_OUT', 'w') as f:
    json.dump(out, f, indent=1)
