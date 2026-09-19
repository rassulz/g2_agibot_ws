"""Show several G2 cameras side by side in one window, to compare them.

Subscribes to any number of CompressedImage camera topics, decodes each,
scales them to a common tile size and tiles them into a single window.
Every tile is labelled with its topic, native resolution and measured rate,
which is what you need in order to pick one.

/gdk/camera/head_depth is excluded by default: it is a raw sensor_msgs/Image,
not CompressedImage, so it needs a different subscriber.

Camera topics are best_effort; the subscriptions below match that.
"""

import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage

# head_stereo_left is the primary camera for this workspace; head_color is
# the rectilinear alternative. The other three the robot exposes
# (head_stereo_right, hand_left_color, hand_right_color) are available by
# passing -p topics:='[...]' but are not shown by default.
DEFAULT_TOPICS = [
    '/gdk/camera/head_stereo_left',
    '/gdk/camera/head_color',
]

SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
)

WINDOW = 'G2 cameras  --  q to quit'


class Stream:
    """Latest frame and running statistics for one camera."""

    def __init__(self, topic):
        self.topic = topic
        self.frame = None
        self.count = 0
        self.bytes = 0
        self.fps = 0.0
        self.kbs = 0.0
        self.shape = None
        self.last = time.time()

    def tick(self):
        now = time.time()
        dt = now - self.last
        if dt >= 1.0:
            self.fps = self.count / dt
            self.kbs = self.bytes / 1024 / dt
            self.count = 0
            self.bytes = 0
            self.last = now


class MultiViewer(Node):

    def __init__(self):
        super().__init__('multi_viewer')
        self.declare_parameter('topics', DEFAULT_TOPICS)
        self.declare_parameter('tile_width', 480)
        self.declare_parameter('columns', 2)
        self.declare_parameter('rate', 15.0)

        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            self.get_logger().error(f'needs OpenCV and numpy: {exc}')
            raise SystemExit(1)
        self._cv2, self._np = cv2, np

        topics = list(self.get_parameter('topics').value)
        self._streams = {}
        for topic in topics:
            stream = Stream(topic)
            self._streams[topic] = stream
            # default argument binds the loop variable per subscription
            self.create_subscription(
                CompressedImage, topic,
                lambda msg, s=stream: self._on_frame(msg, s),
                SENSOR_QOS)

        period = 1.0 / float(self.get_parameter('rate').value)
        self.create_timer(period, self._render)
        self.create_timer(3.0, self._report)

        self.get_logger().info(f'watching {len(topics)} cameras')
        for topic in topics:
            self.get_logger().info(f'  {topic}')

    def _on_frame(self, msg, stream):
        buf = self._np.frombuffer(bytes(msg.data), dtype=self._np.uint8)
        frame = self._cv2.imdecode(buf, self._cv2.IMREAD_COLOR)
        if frame is None:
            return
        stream.frame = frame
        stream.shape = (frame.shape[1], frame.shape[0])   # w, h
        stream.count += 1
        stream.bytes += len(msg.data)
        stream.tick()

    def _tile(self, stream, width):
        """Scale one stream to `width`, letterboxed, with a caption."""
        cv2, np = self._cv2, self._np
        height = int(width * 3 / 4)
        canvas = np.zeros((height, width, 3), dtype=np.uint8)

        if stream.frame is None:
            cv2.putText(canvas, 'waiting...', (12, height // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 1)
        else:
            src_h, src_w = stream.frame.shape[:2]
            scale = min(width / src_w, height / src_h)
            new = cv2.resize(stream.frame,
                             (int(src_w * scale), int(src_h * scale)))
            y = (height - new.shape[0]) // 2
            x = (width - new.shape[1]) // 2
            canvas[y:y + new.shape[0], x:x + new.shape[1]] = new

        name = stream.topic.replace('/gdk/camera/', '')
        res = f'{stream.shape[0]}x{stream.shape[1]}' if stream.shape else '-'
        caption = f'{name}   {res}   {stream.fps:.0f} fps   {stream.kbs / 1024:.1f} MB/s'

        cv2.rectangle(canvas, (0, 0), (width, 22), (0, 0, 0), -1)
        cv2.putText(canvas, caption, (6, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
        cv2.rectangle(canvas, (0, 0), (width - 1, height - 1), (45, 45, 45), 1)
        return canvas

    def _render(self):
        cv2, np = self._cv2, self._np
        width = int(self.get_parameter('tile_width').value)
        cols = max(1, int(self.get_parameter('columns').value))

        tiles = [self._tile(s, width) for s in self._streams.values()]
        if not tiles:
            return

        # pad the last row so hstack gets equal-length rows
        while len(tiles) % cols:
            tiles.append(np.zeros_like(tiles[0]))

        rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
        cv2.imshow(WINDOW, np.vstack(rows))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise SystemExit(0)

    def _report(self):
        live = [s for s in self._streams.values() if s.frame is not None]
        if not live:
            self.get_logger().warning(
                'no frames yet -- robot in base-fastdds mode? profile set?')
            return
        for s in live:
            self.get_logger().info(
                f'{s.topic.replace("/gdk/camera/", ""):<20} '
                f'{s.shape[0]}x{s.shape[1]:<6} {s.fps:5.1f} fps  '
                f'{s.kbs / 1024:5.2f} MB/s')

    def destroy_node(self):
        try:
            self._cv2.destroyAllWindows()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MultiViewer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
