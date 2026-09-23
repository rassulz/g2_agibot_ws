#!/usr/bin/env bash
# Start the OmniHand USB driver (usb_hand). It MOVES the hand.
#
#   hand_start.sh             drive the hand
#   hand_start.sh --dry-run   answer gestures without moving
#
# Anything after that goes to the node as ROS parameters, e.g. speed:
#   hand_start.sh -p steps:=5 -p step_delay:=0.05     ~0.25 s ramp per phase
#   hand_start.sh -p steps:=1                         the motors' own speed
#
# Runs outside hal: the robot's e-stop does not stop it. Ctrl+C stops it.

source "$(dirname "${BASH_SOURCE[0]}")/hand_env.sh"

if pgrep -f '^python3 .*omni_hand/usb_hand.py' > /dev/null; then
    echo "usb_hand is already running -- two drivers on one serial port" \
         "would fight. Stop the other one first."
    exit 1
fi

ENABLE=true
if [ "$1" = "--dry-run" ]; then
    ENABLE=false
    shift
fi

exec python3 "$WS/src/omni_hand/omni_hand/usb_hand.py" \
    --ros-args -p enable:=$ENABLE "$@"
