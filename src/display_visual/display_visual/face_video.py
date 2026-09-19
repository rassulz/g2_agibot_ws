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
    The interaction board is a SEPARATE DEVICE from the Jetson. `video_path`
    is resolved on the board's own filesystem, so a path that exists on the
    Jetson -- or on your workstation -- means nothing here.

    Media reaches the board only through AgiBot's `data_push` tool, which
    uploads into the board's /home/agi/. Run it on the workstation, wired
    directly to the robot:

        ./data_push ~/media_pack        # -> board:/home/agi/media_pack/
        play_video('/home/agi/media_pack/demo.mp4', 1)

    data_push is not shipped in the GDK install or on the robot; the docs
    say to request it from AgiBot operations
    (see http://10.42.1.101:8849/site/ -> appendices -> data_push).

    Until the file is on the board, these calls time out rather than
    reporting a missing file.
"""

import os
import time

import rclpy
from rclpy.node import Node

# Path on the INTERACTION BOARD, not on the Jetson. See the module docstring.
DEFAULT_VIDEO = '/home/agi/media_pack/demo.mp4'

# The Python API reference says loop_count=-1 means loop forever, while the
# comment in VideoDisplay.msg says 0 does. The two disagree; -1 follows the
# API this node actually calls. Use a positive count if unsure.
DEFAULT_LOOP = 1
LOOP_FOREVER = -1


class FaceVideo(Node):

    def __init__(self):
        super().__init__('face_video')
        self.declare_parameter('video_path', DEFAULT_VIDEO)
        self.declare_parameter('loop', DEFAULT_LOOP)
        self.declare_parameter('action', 'start')      # start | stop
        self.declare_parameter('turn_display_on', True)

        self._interaction = None
        self._initialised = False

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

        # The GDK core must be brought up before any interface object is
        # created. Without this, Interaction() constructs fine but every call
        # fails with "GDK is not initialized" followed by a request timeout.
        try:
            if agibot_gdk.gdk_init() != agibot_gdk.GDKRes.kSuccess:
                self.get_logger().error(
                    'gdk_init() failed. Check that the GDK services are '
                    'running and that ~/app/env.sh has been sourced.')
                return False
        except Exception as exc:
            self.get_logger().error(f'gdk_init() raised: {exc}')
            return False

        self._initialised = True

        try:
            self._interaction = agibot_gdk.Interaction()
        except Exception as exc:
            self.get_logger().error(
                f'could not create Interaction(): {exc}')
            return False

        time.sleep(1.0)   # let the interface finish coming up
        self.get_logger().info('GDK initialised')
        return True

    def release(self):
        """Tear the GDK down again. Safe to call if init never succeeded."""
        if not self._initialised:
            return
        try:
            import agibot_gdk
            agibot_gdk.gdk_release()
        except Exception as exc:
            self.get_logger().warning(f'gdk_release() failed: {exc}')

    # -- actions -------------------------------------------------------
    def start(self):
        path = self.get_parameter('video_path').value
        loop = int(self.get_parameter('loop').value)

        if os.path.isabs(path) and not os.path.exists(path):
            # Not fatal: the interaction board may see a path we cannot.
            self.get_logger().warning(
                f'{path} is not visible from this process. That is fine if '
                'the interaction board can reach it, but a "file does not '
                'exist" failure below means it cannot.')

        if self.get_parameter('turn_display_on').value:
            try:
                self._interaction.set_display_switch(True)
                self.get_logger().info('display switched on')
            except Exception as exc:
                self.get_logger().warning(f'set_display_switch failed: {exc}')

        if loop == 0:
            self.get_logger().warning(
                'loop=0 is ambiguous: the Python API documents -1 for endless '
                'playback, VideoDisplay.msg documents 0. Use -1 or a count.')
        forever = (' (looping forever)' if loop == LOOP_FOREVER
                   else f' (x{loop})')
        self.get_logger().info(f'playing {path}{forever}')

        try:
            self._interaction.play_video(path, loop)
        except Exception as exc:
            self.get_logger().error(
                f'play_video failed: {exc}\n'
                'Most likely the file is not on the interaction board. It is '
                'a separate device -- a path on the Jetson is not visible to '
                'it. Upload with AgiBot\'s data_push tool, which writes into '
                'the board\'s /home/agi/, then pass that path.')
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
        node.release()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
