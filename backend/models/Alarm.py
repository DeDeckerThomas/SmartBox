from threading import Thread
from datetime import datetime
from models.AlarmHandler import AlarmHandler


class Alarm(Thread):
    def __init__(self, alarm_id, user_id, name, isactive, starttime, duration, ultrasonic_sensor, alarmhandler):
        Thread.__init__(self)
        self.alarm_id = alarm_id
        self.user_id = user_id
        self.name = name
        self.isactive = isactive
        self.starttime = starttime
        self.duration = duration
        self.alarmhandler = alarmhandler

    def get_time(self):
        return datetime.now().strftime("%H:%M:00")

    def run(self):
        current_time = self.get_time()
        while self.starttime != current_time or not(self.isactive):
            current_time = self.get_time()
        if not(self.alarmhandler.isbusy) and self.isactive:
            self.alarmhandler.run_alarm(self)

    @property
    def alarm_id(self):
        """The alarm_id property."""
        return self._alarm_id

    @alarm_id.setter
    def alarm_id(self, value):
        self._alarm_id = value

    @property
    def user_id(self):
        """The user_id property."""
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def name(self):
        """The name property."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def isactive(self):
        """The isactive property."""
        return self._isactive

    @isactive.setter
    def isactive(self, value):
        self._isactive = value

    @property
    def starttime(self):
        """The starttime property."""
        return self._starttime

    @starttime.setter
    def starttime(self, value):
        self._starttime = value

    @property
    def duration(self):
        """The duration property."""
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value

    @property
    def isplaying(self):
        """The isplaying property."""
        return self._isplaying

    @isplaying.setter
    def isplaying(self, value):
        self._isplaying = value
