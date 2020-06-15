import os
import time
import subprocess
import signal


class Speaker:
    def __init__(self, name):
        self.name = name

    def play_streaming_link(self, link):
        self.process = subprocess.Popen(
            f'mpg123 {link}', stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    def stop_playing(self):
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

    @property
    def name(self):
        """The name property."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def __del__(self):
        self.stop_playing()
