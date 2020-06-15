from RPi import GPIO
# from repositories.DataRepository import DataRepository
import time


class HCSR05:
    def __init__(self, echo_pin, trigger_pin):
        self.echo_pin = echo_pin
        self.trigger_pin = trigger_pin
        self.__init_gpio()

    def __init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.setup(self.trigger_pin, GPIO.OUT)

    def get_distance(self):
        GPIO.output(self.trigger_pin, GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, GPIO.LOW)

        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        while GPIO.input(self.echo_pin) == 1:
            end_time = time.time()

        time_range = end_time - start_time
        distance = round(time_range * 17150, 2)
        # DataRepository.add_measurement(3, distance)
        return distance
