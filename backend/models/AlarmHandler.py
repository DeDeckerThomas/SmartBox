from models.Speaker import Speaker
from models.HCSR05 import HCSR05


class AlarmHandler():
    def __init__(self, ultrasonic_sensor):
        self.speaker = Speaker('Main')
        self.ultrasonic_sensor = ultrasonic_sensor
        self.isbusy = False

    def run_alarm(self, alarm):
        self.isbusy = True
        self.speaker.play_streaming_link(
            'http://icecast.vrtcdn.be/mnm-high.mp3')
        value = self.ultrasonic_sensor.get_distance()
        while value > 30:
            value = self.ultrasonic_sensor.get_distance()
            print(value)
        self.speaker.stop_playing()
        self.isbusy = False

    def restart_other_alarms(self):
        for alarm in self.alarms:
            alarm.start()

    @property
    def alarms(self):
        """The alarms property."""
        return self._alarms

    @alarms.setter
    def alarms(self, value):
        self._alarms = value
