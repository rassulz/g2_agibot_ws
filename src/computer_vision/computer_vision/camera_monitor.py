"""Subscribe to the G2 head camera and report what is arriving.

The head/hand colour streams are published as CompressedImage (JPEG); only
the depth stream is a raw Image. Camera topics are best_effort, so the QoS
below must match or no frames are delivered.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage

DEFAULT_TOPIC = '/gdk/camera/head_color'

SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
)


class CameraMonitor(Node):

    def __init__(self):
        super().__init__('camera_monitor')
        self.declare_parameter('topic', DEFAULT_TOPIC)
        topic = self.get_parameter('topic').value

        self._count = 0
        self._bytes = 0
        self.create_subscription(
            CompressedImage, topic, self._on_frame, SENSOR_QOS)
        self.create_timer(1.0, self._report)

        self.get_logger().info(f'listening on {topic}')

    def _on_frame(self, msg):
        self._count += 1
        self._bytes += len(msg.data)

    def _report(self):
        if self._count == 0:
            self.get_logger().warn(
                'no frames -- check the robot is in base-fastdds mode '
                'and that QoS is best_effort')
            return
        self.get_logger().info(
            f'{self._count} fps, {self._bytes / 1024:.0f} KiB/s')
        self._count = 0
        self._bytes = 0


def main(args=None):
    rclpy.init(args=args)
    node = CameraMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
