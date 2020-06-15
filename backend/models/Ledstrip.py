import serial
import time
import os


class Ledstrip:
    def __init__(self, mac):
        self.mac = mac
        try:
            os.popen(f'sudo rfcomm connect hci0 {self.mac}')
            time.sleep(5)
        except Exception as ex:
            raise Exception('Bluetooth device not available.')

    def init_serial(self):
        """Initialization of serial communication
        This function setups the serial communication between the Raspberry Pi and Arduino Uno.
        """
        return serial.Serial('/dev/rfcomm0', 9600)

    def send_color(self, r, g, b, brightness):
        self.serial = self.init_serial()
        self.serial.write('COLOR'.encode(encoding='utf-8'))
        self.serial.read()
        time.sleep(0.5)
        self.serial.write(f'{r};{g};{b}'.encode(encoding='utf-8'))
        self.serial.read()
        time.sleep(2)
        self.serial.write('BRIGHTNESS'.encode(encoding='utf-8'))
        self.serial.read()
        time.sleep(1.5)
        self.serial.write(str(brightness).encode(encoding='utf-8'))
        self.serial.close()

    def send_pattern(self, pattern):
        self.serial = self.init_serial()
        self.serial.write('PATTERN'.encode(encoding='utf-8'))
        self.serial.read()
        self.serial.write(pattern.encode(encoding='utf-8'))
        self.serial.close()
