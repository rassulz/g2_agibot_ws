"""Scaffold for sending joint commands to the G2.

THIS WILL MOVE THE ROBOT. Nothing is published unless --enable is passed,
and even then only the joints you name are addressed.

/gdk/joint_control expects gdk_msgs/JointPositionServo:

    std_msgs/Header header
    float64          control_period
    string[]         joint_names
    float64[]        joint_positions
    float64[]        joint_velocities

Read the current values from /gdk/joint_state first and move in small
increments from where the joint already is. Confirm the workspace is clear
and someone is on the e-stop before enabling.
"""

import argparse
import sys

import rclpy
from rclpy.node import Node
from gdk_msgs.msg import JointPositionServo

CONTROL_TOPIC = '/gdk/joint_control'
CONTROL_PERIOD = 0.01   # seconds; /gdk/joint_state runs at 100 Hz


class CommandScaffold(Node):

    def __init__(self, enabled):
        super().__init__('command_scaffold')
        self._enabled = enabled
        self._pub = self.create_publisher(JointPositionServo, CONTROL_TOPIC, 10)

        if not enabled:
            self.get_logger().info(
                'dry run -- nothing will be published. '
                'Pass --enable to actually command the robot.')

    def send(self, names, positions, velocities=None):
        msg = JointPositionServo()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.control_period = CONTROL_PERIOD
        msg.joint_names = list(names)
        msg.joint_positions = [float(p) for p in positions]
        msg.joint_velocities = [float(v) for v in (velocities or
                                                   [0.0] * len(names))]

        if not self._enabled:
            self.get_logger().info(f'[dry run] would send: {msg.joint_names} '
                                   f'-> {msg.joint_positions}')
            return

        self.get_logger().warning(f'SENDING: {msg.joint_names} '
                               f'-> {msg.joint_positions}')
        self._pub.publish(msg)


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enable', action='store_true',
                        help='actually publish (THE ROBOT WILL MOVE)')
    parsed, remaining = parser.parse_known_args(
        args if args is not None else sys.argv[1:])

    rclpy.init(args=remaining)
    node = CommandScaffold(parsed.enable)
    try:
        # Fill in a real target before using this.
        node.send([], [])
        rclpy.spin_once(node, timeout_sec=1.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
