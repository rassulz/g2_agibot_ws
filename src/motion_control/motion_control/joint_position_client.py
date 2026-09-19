"""Request/response client for planned joint moves on the G2.

THIS WILL MOVE THE ROBOT when --enable is passed. Without it the request is
printed and nothing is published.

Unlike /gdk/joint_control (JointPositionServo, a continuous servo stream),
/gdk/joint_pos_request is a one-shot planned move:

    publish  /gdk/joint_pos_request   gdk_msgs/JointPositionRequst
    receive  /gdk/joint_pos_response  gdk_msgs/CommonResponse

Requests carry a uuid; the response echoes it back, so concurrent requests
can be told apart. `lifetime` bounds how long the request stays valid.

Before enabling: confirm the workspace is clear, someone is on the e-stop,
and read current positions from /gdk/joint_state so the target is a small
step from where the joint already is.
"""

import argparse
import sys
import uuid as uuidlib

import rclpy
from rclpy.node import Node
from gdk_msgs.msg import JointPositionRequst, CommonResponse

REQUEST_TOPIC = '/gdk/joint_pos_request'
RESPONSE_TOPIC = '/gdk/joint_pos_response'

DEFAULT_LIFETIME = 5.0      # seconds the request remains valid
RESPONSE_TIMEOUT = 10.0     # seconds to wait before giving up


class JointPositionClient(Node):

    def __init__(self, enabled):
        super().__init__('joint_position_client')
        self._enabled = enabled
        self._pending = {}

        self._pub = self.create_publisher(
            JointPositionRequst, REQUEST_TOPIC, 10)
        self.create_subscription(
            CommonResponse, RESPONSE_TOPIC, self._on_response, 10)

        if not enabled:
            self.get_logger().info(
                'dry run -- nothing will be published. '
                'Pass --enable to actually command the robot.')

    def send(self, names, positions, velocities=None,
             lifetime=DEFAULT_LIFETIME, detail=''):
        """Publish a planned joint move. Returns the request uuid."""
        req = JointPositionRequst()
        req.header.stamp = self.get_clock().now().to_msg()
        req.lifetime = float(lifetime)
        req.joint_names = list(names)
        req.joint_positions = [float(p) for p in positions]
        req.joint_velocities = [float(v) for v in (velocities or
                                                   [0.0] * len(names))]
        req.uuid = str(uuidlib.uuid4())
        req.detail = detail

        if not self._enabled:
            self.get_logger().info(
                f'[dry run] would request {req.joint_names} -> '
                f'{req.joint_positions} (uuid={req.uuid})')
            return req.uuid

        self._pending[req.uuid] = req
        self.get_logger().warn(
            f'SENDING {req.joint_names} -> {req.joint_positions} '
            f'(uuid={req.uuid})')
        self._pub.publish(req)
        return req.uuid

    def _on_response(self, msg):
        if msg.uuid not in self._pending:
            return   # someone else's request
        self._pending.pop(msg.uuid)

        if msg.result == CommonResponse.SUCCESS:
            self.get_logger().info(f'SUCCESS (uuid={msg.uuid})')
        else:
            self.get_logger().error(
                f'FAILED (uuid={msg.uuid}): {msg.reason}')

    def wait_for_responses(self, timeout=RESPONSE_TIMEOUT):
        deadline = self.get_clock().now().nanoseconds + int(timeout * 1e9)
        while self._pending and \
                self.get_clock().now().nanoseconds < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
        for pending in self._pending:
            self.get_logger().error(f'no response for uuid={pending}')


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enable', action='store_true',
                        help='actually publish (THE ROBOT WILL MOVE)')
    parsed, remaining = parser.parse_known_args(
        args if args is not None else sys.argv[1:])

    rclpy.init(args=remaining)
    node = JointPositionClient(parsed.enable)
    try:
        # Fill in a real target before using this.
        node.send([], [], detail='example request')
        node.wait_for_responses()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
