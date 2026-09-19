"""View the G2's head stereo-left camera.

The camera is reachable two ways. This node uses the ROS bridge:

    /gdk/camera/head_stereo_left      sensor_msgs/CompressedImage (JPEG)

The native GDK equivalent is agibot_gdk.Camera() with
CameraType.kHeadStereoLeft, which only runs on the robot. The ROS topic
works from a workstation, so it is the one used here.

Requires the robot in base-fastdds mode.

QoS: camera topics are best_effort. Subscribing with the default reliable
QoS silently yields no frames.

Modes
    info  -- print size/rate only, no decoding, no dependencies
    save  -- write frames to disk as .jpg (the payload is already JPEG,
             so this needs no OpenCV either)
    show  -- decode and display in a window; needs cv2 and a display
"""

import os
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage

DEFAULT_TOPIC = '/gdk/camera/head_stereo_left'

SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
)


class StereoViewer(Node):

    def __init__(self):
        super().__init__('stereo_viewer')
        self.declare_parameter('topic', DEFAULT_TOPIC)
        self.declare_parameter('mode', 'show')          # info | save | show
        self.declare_parameter('output_dir', '/tmp/g2_frames')
        self.declare_parameter('save_every', 1)         # save 1 frame in N
        self.declare_parameter('max_frames', 0)         # 0 = unlimited

        self._mode = self.get_parameter('mode').value
        self._topic = self.get_parameter('topic').value
        self._count = 0
        self._saved = 0
        self._bytes = 0
        self._cv2 = None

        if self._mode == 'show':
            try:
                import cv2
                import numpy as np
                self._cv2, self._np = cv2, np
            except ImportError as exc:
                self.get_logger().error(
                    f'mode=show needs OpenCV and numpy ({exc}). '
                    "Use mode:=save or mode:=info instead.")
                raise SystemExit(1)

        if self._mode == 'save':
            os.makedirs(self.get_parameter('output_dir').value, exist_ok=True)

        self.create_subscription(
            CompressedImage, self._topic, self._on_frame, SENSOR_QOS)
        self.create_timer(2.0, self._report)

        self.get_logger().info(f'mode={self._mode}  topic={self._topic}')

    def _on_frame(self, msg):
        self._count += 1
        self._bytes += len(msg.data)

        if self._mode == 'save':
            every = max(1, int(self.get_parameter('save_every').value))
            if self._count % every:
                return
            out = self.get_parameter('output_dir').value
            name = os.path.join(out, f'frame_{self._saved:05d}.jpg')
            # msg.data is already a JPEG byte stream -- no decode needed.
            with open(name, 'wb') as fh:
                fh.write(bytes(msg.data))
            self._saved += 1
            limit = int(self.get_parameter('max_frames').value)
            if limit and self._saved >= limit:
                self.get_logger().info(f'saved {self._saved} frames to {out}')
                raise SystemExit(0)

        elif self._mode == 'show':
            buf = self._np.frombuffer(bytes(msg.data), dtype=self._np.uint8)
            frame = self._cv2.imdecode(buf, self._cv2.IMREAD_COLOR)
            if frame is None:
                self.get_logger().warning('could not decode frame')
                return
            self._cv2.imshow('G2 head_stereo_left', frame)
            if self._cv2.waitKey(1) & 0xFF == ord('q'):
                raise SystemExit(0)

    def _report(self):
        if self._count == 0:
            self.get_logger().warning(
                'no frames. Check: robot in base-fastdds mode, '
                'FASTRTPS_DEFAULT_PROFILES_FILE set, ROS_DOMAIN_ID=4, '
                'and that this topic is best_effort.')
            return
        fps = self._count / 2.0
        kbs = self._bytes / 1024 / 2.0
        extra = f'  saved={self._saved}' if self._mode == 'save' else ''
        self.get_logger().info(f'{fps:.1f} fps  {kbs:.0f} KiB/s{extra}')
        self._count = 0
        self._bytes = 0

    def destroy_node(self):
        if self._cv2 is not None:
            try:
                self._cv2.destroyAllWindows()
            except Exception:
                pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = StereoViewer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
