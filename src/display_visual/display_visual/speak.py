"""Speak text on the G2, and control the interaction screen switch.

Unlike play_video/play_audio, play_tts takes the text itself rather than a
file path, so nothing has to be uploaded to the interaction board first.
This works without AgiBot's data_push tool.

Underneath it is the /voice/tts/text service (gdk_msgs/srv/TtsRequest).

Runs on the robot -- see face_video.py for why a container cannot load the
GDK binding the robot uses.
"""

import time

import rclpy
from rclpy.node import Node

DEFAULT_TEXT = 'Hello World'


class Speak(Node):

    def __init__(self):
        super().__init__('speak')
        self.declare_parameter('text', DEFAULT_TEXT)
        self.declare_parameter('language', '')        # '', 'chinese', 'english'
        self.declare_parameter('volume', -1)          # -1 leaves it alone
        self.declare_parameter('display', '')         # '', 'on', 'off'

        self._interaction = None
        self._initialised = False

    def connect(self):
        try:
            import agibot_gdk
        except ImportError as exc:
            self.get_logger().error(
                f'cannot import agibot_gdk: {exc}\n'
                'This node must run on the robot.')
            return False

        try:
            if agibot_gdk.gdk_init() != agibot_gdk.GDKRes.kSuccess:
                self.get_logger().error('gdk_init() failed')
                return False
        except Exception as exc:
            self.get_logger().error(f'gdk_init() raised: {exc}')
            return False

        self._initialised = True
        self._gdk = agibot_gdk
        self._interaction = agibot_gdk.Interaction()
        time.sleep(1.0)
        self.get_logger().info('GDK initialised')
        return True

    def release(self):
        if self._initialised:
            try:
                self._gdk.gdk_release()
            except Exception as exc:
                self.get_logger().warning(f'gdk_release() failed: {exc}')

    def run(self):
        # Optional: screen on/off
        display = self.get_parameter('display').value
        if display in ('on', 'off'):
            try:
                self._interaction.set_display_switch(display == 'on')
                self.get_logger().info(f'display {display}')
            except Exception as exc:
                self.get_logger().warning(f'set_display_switch failed: {exc}')

        # Optional: language
        lang = self.get_parameter('language').value
        if lang:
            table = {
                'chinese': getattr(self._gdk.Language, 'kLanguageChinese', None),
                'english': getattr(self._gdk.Language, 'kLanguageEnglish', None),
            }
            value = table.get(lang.lower())
            if value is None:
                self.get_logger().warning(
                    f"unknown language '{lang}' -- use chinese or english")
            else:
                try:
                    self._interaction.set_language(value)
                    self.get_logger().info(f'language: {lang}')
                except Exception as exc:
                    self.get_logger().warning(f'set_language failed: {exc}')

        # Optional: volume
        volume = int(self.get_parameter('volume').value)
        if volume >= 0:
            try:
                self._interaction.set_volume(volume)
                self.get_logger().info(f'volume: {volume}')
            except Exception as exc:
                self.get_logger().warning(f'set_volume failed: {exc}')

        # The actual speech
        text = self.get_parameter('text').value
        if not text:
            self.get_logger().warning('empty text -- nothing to say')
            return False

        self.get_logger().info(f'speaking: {text!r}')
        try:
            self._interaction.play_tts(text)
        except Exception as exc:
            self.get_logger().error(f'play_tts failed: {exc}')
            return False

        self.get_logger().info('TTS accepted')
        return True


def main(args=None):
    rclpy.init(args=args)
    node = Speak()
    try:
        if node.connect():
            node.run()
            time.sleep(1.0)   # let the request reach the voice service
    except KeyboardInterrupt:
        pass
    finally:
        node.release()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
