#!/usr/bin/env bash
# Start the OmniHand USB driver (usb_hand). It MOVES the hand.
#
#   hand_start.sh             drive the hand
#   hand_start.sh --dry-run   answer gestures without moving
#
# Runs outside hal: the robot's e-stop does not stop it. Ctrl+C stops it.

source "$(dirname "${BASH_SOURCE[0]}")/hand_env.sh"

if pgrep -f '^python3 .*omni_hand/usb_hand.py' > /dev/null; then
    echo "usb_hand is already running -- two drivers on one serial port" \
         "would fight. Stop the other one first."
    exit 1
fi

ENABLE=true
[ "$1" = "--dry-run" ] && ENABLE=false

exec python3 "$WS/src/omni_hand/omni_hand/usb_hand.py" \
    --ros-args -p enable:=$ENABLE
