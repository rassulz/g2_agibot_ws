"""Play a video on the G2's facial interaction screen.

The interaction API is NOT bridged to ROS 2 -- there is no mapping for it in
gdk/config/ros_bridge_config.json. It is reached through the native GDK
Python binding instead:

    agibot_gdk.Interaction().play_video(video_path, loop_count)

Underneath this is the /display/video_display service
(gdk_msgs/srv/VideoDisplayReq), whose result codes are:
    0 success   1 busy   2 file does not exist

WHERE THIS RUNS
    On the robot. `agibot_gdk` there is built cpython-312-aarch64, matching
    the robot's Python 3.12. The x86_64 build shipped for workstations is
    cpython-310, so this node cannot run in the kilted container (Python
    3.12 / x86_64) -- the ABI matches neither. Deploy via git and run it on
    the robot.

WHERE THE VIDEO MUST BE
    `video_path` is resolved by the interaction board, not by this process.
    A path that exists on your workstation means nothing. Copy the file onto
    the robot and pass a path the interaction board can read; a result of
    "file does not exist" is the usual sign it cannot.
"""

import os

import rclpy
from rclpy.node import Node

DEFAULT_VIDEO = '/home/agi/videos/Hello World.mp4'
DEFAULT_LOOP = 1          # 0 = loop forever


class FaceVideo(Node):

    def __init__(self):
        super().__init__('face_video')
        self.declare_parameter('video_path', DEFAULT_VIDEO)
        self.declare_parameter('loop', DEFAULT_LOOP)
        self.declare_parameter('action', 'start')      # start | stop
        self.declare_parameter('turn_display_on', True)

        self._interaction = None

    # -- GDK -----------------------------------------------------------
    def _connect(self):
        """Import and initialise the native GDK interaction interface."""
        try:
            import agibot_gdk
        except ImportError as exc:
            self.get_logger().error(
                f'cannot import agibot_gdk: {exc}\n'
                'This node must run on the robot. The workstation build is '
                'cpython-310/x86_64 and will not load under Python 3.12.')
            return False

        try:
            self._interaction = agibot_gdk.Interaction()
        except Exception as exc:
            self.get_logger().error(
                f'could not create Interaction(): {exc}\n'
                'Check that aorta is reachable (AORTA_DISCOVERY_URI).')
            return False

        return True

    # -- actions -------------------------------------------------------
    def start(self):
        path = self.get_parameter('video_path').value
        loop = int(self.get_parameter('loop').value)

        if os.path.isabs(path) and not os.path.exists(path):
            # Not fatal: the interaction board may see a path we cannot.
            self.get_logger().warn(
                f'{path} is not visible from this process. That is fine if '
                'the interaction board can reach it, but a "file does not '
                'exist" failure below means it cannot.')

        if self.get_parameter('turn_display_on').value:
            try:
                self._interaction.set_display_switch(True)
                self.get_logger().info('display switched on')
            except Exception as exc:
                self.get_logger().warn(f'set_display_switch failed: {exc}')

        forever = ' (looping forever)' if loop == 0 else f' (x{loop})'
        self.get_logger().info(f'playing {path}{forever}')

        try:
            self._interaction.play_video(path, loop)
        except Exception as exc:
            self.get_logger().error(
                f'play_video failed: {exc}\n'
                'Likely causes: the interaction board cannot read that path, '
                'the file is not .mp4, or the display is already busy.')
            return False

        self.get_logger().info('video command accepted')
        return True

    def stop(self):
        """Stop playback by switching the display off."""
        try:
            self._interaction.set_display_switch(False)
        except Exception as exc:
            self.get_logger().error(f'could not stop playback: {exc}')
            return False
        self.get_logger().info('display switched off')
        return True


def main(args=None):
    rclpy.init(args=args)
    node = FaceVideo()
    try:
        if not node._connect():
            return
        action = node.get_parameter('action').value
        if action == 'stop':
            node.stop()
        elif action == 'start':
            node.start()
        else:
            node.get_logger().error(
                f"unknown action '{action}' -- expected 'start' or 'stop'")
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
