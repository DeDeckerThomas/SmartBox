from RPi import GPIO
from subprocess import check_output
from threading import Thread
from datetime import datetime
from repositories.DataRepository import DataRepository
import time


class LCD(Thread):

    def __init__(self, E, RS, data_bits):
        Thread.__init__(self)
        self.E = E
        self.RS = RS
        self.data_bits = data_bits
        self.__initGPIO()

    @property
    def E(self):
        return self._E

    @E.setter
    def E(self, value):
        self._E = value

    @property
    def RS(self):
        return self._RS

    @RS.setter
    def RS(self, value):
        self._RS = value

    @property
    def data_bits(self):
        return self._data_bits

    @data_bits.setter
    def data_bits(self, value):
        self._data_bits = value

    def run(self):
        status = "IP"
        self.init_lcd()
        self.hide_cursor(True)
        previous_time = ''
        while True:
            current_time = self.get_time()
            if current_time != previous_time:
                self.first_row()
                self.write_message(current_time)
                self.second_row()
                if status == "IP":
                    status = "INFO"
                    self.write_message(self.get_ip().ljust(16))
                elif status == "INFO":
                    status = "IP"
                    self.write_message(
                        'T:'+str(round(DataRepository.get_latest_value(1).get('Value'), 1))+'ßC')
                    self.write_message(' ')
                    self.write_message(
                        'H:' + str(round(DataRepository.get_latest_value(2).get('Value'), 1))+'%')
            previous_time = current_time

    def __initGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RS, GPIO.OUT)
        GPIO.setup(self.E, GPIO.OUT)
        for pin in self.data_bits:
            GPIO.setup(pin, GPIO.OUT)

    def __send_instruction(self, value):
        GPIO.output(self.RS, GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(self.E, GPIO.HIGH)
        time.sleep(0.001)
        self.__set_data_bits(value)
        time.sleep(0.001)
        GPIO.output(self.E, GPIO.LOW)
        time.sleep(0.01)

    def __send_character(self, value):
        GPIO.output(self.RS, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(self.E, GPIO.HIGH)
        time.sleep(0.001)
        self.__set_data_bits(value)
        time.sleep(0.001)
        GPIO.output(self.E, GPIO.LOW)
        time.sleep(0.01)

    def __set_data_bits(self, value):
        mask = 0x80
        for i in range(8):
            bit = value & (mask >> i)
            GPIO.output(self.data_bits[i], 1 if bit > 0 else 0)

    def init_lcd(self):
        self.__send_instruction(56)
        self.__send_instruction(15)
        self.clear_lcd()

    def clear_lcd(self):
        self.__send_instruction(1)

    def writeA(self):
        self.__send_character(ord("A"))

    def first_row(self):
        self.__send_instruction(128)

    def second_row(self):
        self.__send_instruction(192)

    def displayOn(self):
        self.__send_instruction(12)

    def write_message(self, message):
        for i in range(0, len(message)):
            if i == 16:
                self.second_row()
            self.__send_character(ord(message[i]))

    def hide_cursor(self, hide):
        if hide:
            self.__send_instruction(12)
        else:
            self.__send_instruction(15)

    def get_ip(self):
        """Get IP address
        This function returns the local IPv4 address of the wlan0 interface.
        """
        ips = check_output(['hostname', '--all-ip-addresses'])
        ips = ips.decode(encoding='utf-8').rstrip('\n').split(' ')
        return ips[1]

    def get_time(self):
        return datetime.now().strftime("%H:%M %d/%m/%Y")
