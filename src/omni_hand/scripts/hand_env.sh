# Shared environment for the OmniHand USB tools. Sourced, not run.
#
# The node and the gesture client must share one ROS 2 environment or they
# cannot see each other, so both scripts source this file and nothing else.

WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

for distro in kilted jazzy humble; do
    if [ -f "/opt/ros/$distro/setup.bash" ]; then
        source "/opt/ros/$distro/setup.bash"
        break
    fi
done

# The AgiLink SDK wheel, unpacked rather than installed -- see usb_hand.py.
export PYTHONPATH="${OMNIHAND_SDK:-$HOME/omnihand_pkg}:$PYTHONPATH"
