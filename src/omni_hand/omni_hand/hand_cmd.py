"""Send gestures to a running usb_hand and print its answer to each.

    python3 src/omni_hand/omni_hand/hand_cmd.py rock
    python3 src/omni_hand/omni_hand/hand_cmd.py rock paper scissors
    python3 src/omni_hand/omni_hand/hand_cmd.py --pause 5 rock paper

Several gestures are played in order, holding each one for --pause seconds
(default 1) before the next.

Waits until usb_hand is actually subscribed before publishing, so the
command is not lost to discovery latency the way a bare
`ros2 topic pub --once` can be, then waits for the /omni_hand/status reply.
Exits non-zero if a gesture was refused, stopped, or not answered.
"""

import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from std_msgs.msg import String

CONNECT_TIMEOUT = 5.0     # seconds to find usb_hand
GESTURE_TIMEOUT = 20.0    # two ramped phases take ~4 s at the slowest
DEFAULT_PAUSE = 1.0       # seconds to hold a gesture before the next


def main(args=None):
    names = remove_ros_args(sys.argv)[1:]
    pause = DEFAULT_PAUSE
    if names[:1] == ['--pause']:
        try:
            pause = float(names[1])
        except (IndexError, ValueError):
            print('--pause needs a number of seconds')
            return 2
        names = names[2:]
    if not names:
        print(__doc__.strip())
        return 2

    rclpy.init(args=args)
    node = Node('hand_cmd')
    pub = node.create_publisher(String, 'omni_hand/gesture', 10)
    replies = []
    node.create_subscription(
        String, 'omni_hand/status', lambda msg: replies.append(msg.data), 10)

    code = 0
    try:
        deadline = time.time() + CONNECT_TIMEOUT
        while time.time() < deadline and not (
                pub.get_subscription_count()
                and node.count_publishers('/omni_hand/status')):
            rclpy.spin_once(node, timeout_sec=0.1)
        if not pub.get_subscription_count():
            print('usb_hand is not running -- start it with hand_start.sh')
            return 1

        for i, name in enumerate(names):
            if i:
                time.sleep(pause)     # hold the previous gesture
            replies.clear()
            pub.publish(String(data=name))
            deadline = time.time() + GESTURE_TIMEOUT
            while not replies and time.time() < deadline:
                rclpy.spin_once(node, timeout_sec=0.1)
            answer = replies[0] if replies else \
                f'{name}: no answer in {GESTURE_TIMEOUT:.0f} s'
            print(answer, flush=True)
            if not answer.startswith(('done ', 'dry run ')):
                code = 1
                break
    except KeyboardInterrupt:
        code = 130
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
    return code


if __name__ == '__main__':
    sys.exit(main())
