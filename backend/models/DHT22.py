from RPi import GPIO
from repositories.DataRepository import DataRepository
import time


class DHT22:
    def __init__(self, data_pin):
        self.data_pin = data_pin
        self.__humidity = 0

    def read(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.data_pin, GPIO.OUT)
        GPIO.output(self.data_pin, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(self.data_pin, GPIO.LOW)
        time.sleep(0.001)
        GPIO.setup(self.data_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        timings = []
        previous_state = 0
        timestamp = 0
        unchanged_count = 0
        while unchanged_count < 100:
            current_state = GPIO.input(self.data_pin)
            if current_state+1 == previous_state:
                timings.append(time.time()-timestamp)
                timestamp = time.time()
                unchanged_count = 0
            else:
                unchanged_count += 1
            previous_state = current_state

        bits = self.__convert_timings_to_bits(timings)

        bytes_list = self.__convert_bits_to_bytes(bits)
        try:
            if self.__checksum(bytes_list):
                self.__temperature = ((bytes_list[2] << 8)+bytes_list[3])/10.00
                self.__humidity = ((bytes_list[0] << 8)+bytes_list[1])/10.00
        except:
            self.read()

    def get_humidity(self):
        self.read()
        return self.__humidity

    def get_temperature(self):
        return self.__temperature

    def __convert_timings_to_bits(self, timings):
        bits = [1 if timing > 0.000100 else 0 for timing in timings]
        return bits[2:]

    def __convert_bits_to_bytes(self, bits):
        bytes_list = []
        byte = 0
        for i in range(0, len(bits)):
            byte <<= 1
            if bits[i] == 1:
                byte |= 1
            elif bits[i] == 0:
                byte |= 0
            if ((i + 1) % 8 == 0):
                bytes_list.append(byte)
                byte = 0
        return bytes_list

    def __checksum(self, bytes_list):
        return bytes_list[0] + bytes_list[1] + bytes_list[2] + bytes_list[3] & 255 == bytes_list[4]
