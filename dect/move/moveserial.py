# serial interface
# include open, close, write, read
import serial 
import time
from . import setting

class SerialInterface:
    def __init__(self, port=None, baudrate=None, timeout=None):
        self.settings = setting.Settings()
        if port is None:
            port = self.settings.com_port
        if baudrate is None:
            baudrate = self.settings.baud_rate
        if timeout is None:
            timeout = self.settings.timeout
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.wait_for_response = self.settings.wait_for_response

    def send_command(self, command):
        if self.ser.is_open:
            full_command = (command + "\n").encode('utf-8')
            self.ser.write(full_command)
            print(f"SEND: {command}")

    def receive_response(self):
        responses = []
        while self.wait_for_response:
            line = self.ser.readline().decode('utf-8').strip()
            if not line:
                time.sleep(0.1)
                line = self.ser.readline().decode('utf-8').strip()
                if not line:
                    break  # 没有更多数据
            responses.append(line)
        for resp in responses:
            print(f"RECEIVE: {resp}")

    def close(self):
        self.ser.close()
