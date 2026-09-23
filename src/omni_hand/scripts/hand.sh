#!/usr/bin/env bash
# Send gestures to a running usb_hand and print each answer.
#
#   hand.sh rock
#   hand.sh rock paper scissors
#   hand.sh ok like num3        any O10 factory gesture

source "$(dirname "${BASH_SOURCE[0]}")/hand_env.sh"
exec python3 "$WS/src/omni_hand/omni_hand/hand_cmd.py" "$@"
