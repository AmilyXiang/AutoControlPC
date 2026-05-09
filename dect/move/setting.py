# 3轴运动平台控制相关参数

class Settings:
    def __init__(self):
        self.wait_for_response = True
        self.speed = 2500
        self.xyz_speed_max = 3000
        self.xyz_accelerate_max = 100
        self.com_port = 'COM3'
        self.baud_rate = 115200
        self.timeout = 1    
        self.long_press_time = 2  # 长按时间阈值，单位为秒
        self.short_press_time = 0.2  # 短按时间，单位为秒
        self.press_depth = 2  # 按压深度，单位为毫米
