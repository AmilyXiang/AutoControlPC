# move interface
# include move_plain, long_press, short_press, press_down, press_up, wait_move, origin, human_adjust
import time

from .moveserial import SerialInterface
from . import setting

class MoveInterface:
    def __init__(self, serial_interface):
        self.ser = serial_interface
        self.settings = setting.Settings()
        self.ser.send_command("G21")  # 设置单位为毫米
        self.ser.send_command("G90")  # 设置为绝对坐标模式
        self.ser.send_command("G92 X0 Y0 Z0")  # 设置当前坐标为原点
        # 设置最大速度
        self.ser.send_command(f"$110={self.settings.xyz_speed_max}")
        self.ser.send_command(f"$111={self.settings.xyz_speed_max}")
        self.ser.send_command(f"$112={self.settings.xyz_speed_max}")
        # 设置最大加速度
        self.ser.send_command(f"$120={self.settings.xyz_accelerate_max}")
        self.ser.send_command(f"$121={self.settings.xyz_accelerate_max}")
        self.ser.send_command(f"$122={self.settings.xyz_accelerate_max}")
        self.ser.send_command(f"F{self.settings.speed}")  # 设置默认速度
        self.ser.receive_response()
        self.X = 0
        self.Y = 0
        self.Z = 0

    def move_plain(self, x, y, z, f=None):
        if f is None:
            f = self.settings.speed
        command = f"G01 X{x} Y{y} Z{z} F{f}"
        self.ser.send_command(command)
        self.X = x
        self.Y = y  
        self.Z = z

    def long_press(self):
        # 实现长按逻辑
        self.press_down()  # 按下
        time.sleep(self.settings.long_press_time)  # 等待长按时间
        self.press_up()  # 抬起

    def short_press(self):
        # 实现短按逻辑
        self.press_down()  # 按下
        time.sleep(self.settings.short_press_time)  # 短按时间，可以根据需要调整
        self.press_up()  # 抬起

    def press_down(self):
        # 实现按下逻辑
        self.move_plain(self.X, self.Y, self.Z - self.settings.press_depth)  # 假设按下动作是Z轴下降按压深度单位
        self.wait_move()  # 等待移动完成

    def press_up(self):
        # 实现抬起逻辑
        self.move_plain(self.X, self.Y, self.Z + self.settings.press_depth)  # 假设抬起动作是Z轴上升按压深度单位
        self.wait_move()  # 等待移动完成

    def wait_move(self):
        pass # 实现等待移动完成的逻辑，可以通过查询设备状态或者简单的时间等待来实现

    def origin(self):
        command = f"G01 X0 Y0 Z0 F{self.settings.speed}"  # 回原点指令
        self.ser.send_command(command)
        self.X = 0
        self.Y = 0
        self.Z = 0

    def human_adjust(self):
        pass  # 实现人工调整的逻辑
