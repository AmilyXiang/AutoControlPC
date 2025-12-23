"""
自动控制器
集成鼠标和键盘控制，提供高级自动化功能
"""

from mouse_controller import MouseController
from keyboard_controller import KeyboardController
import time


class AutoController:
    """自动化控制器，集成鼠标和键盘操作"""
    
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
    
    def wait(self, duration=1.0):
        """等待指定时间
        
        Args:
            duration: 等待时间（秒）
        """
        time.sleep(duration)
    
    def move_and_click(self, x, y, button='left', wait_before=0.2, wait_after=0.2):
        """移动到目标位置并点击
        
        Args:
            x: 目标X坐标
            y: 目标Y坐标
            button: 按钮类型 'left', 'right', 'middle'
            wait_before: 点击前等待时间（秒）
            wait_after: 点击后等待时间（秒）
        """
        self.mouse.move_to(x, y, duration=0.3)
        self.wait(wait_before)
        self.mouse.click(x, y, button)
        self.wait(wait_after)
    
    def type_text_slowly(self, text, char_interval=0.05, pre_wait=0.2, post_wait=0.2):
        """缓慢输入文本（用于提高兼容性）
        
        Args:
            text: 要输入的文本
            char_interval: 每个字符之间的间隔（秒）
            pre_wait: 输入前等待时间（秒）
            post_wait: 输入后等待时间（秒）
        """
        self.wait(pre_wait)
        self.keyboard.type_text(text, interval=char_interval)
        self.wait(post_wait)
    
    def input_at_position(self, x, y, text):
        """在指定位置点击后输入文本
        
        Args:
            x: 点击的X坐标
            y: 点击的Y坐标
            text: 要输入的文本
        """
        self.move_and_click(x, y)
        self.keyboard.type_text(text, interval=0.05)
    
    def take_screenshot_info(self):
        """获取当前鼠标位置信息（用于调试）"""
        pos = self.mouse.get_position()
        return f"Current mouse position: ({pos[0]}, {pos[1]})"


# 简化API，使用全局实例
_controller = AutoController()

# 导出常用函数
def move_mouse(x, y, duration=0.5):
    """移动鼠标"""
    _controller.mouse.move_to(x, y, duration)

def click_mouse(x=None, y=None, button='left', count=1):
    """点击鼠标"""
    _controller.mouse.click(x, y, button, count)

def left_click(x=None, y=None):
    """左键点击"""
    _controller.mouse.left_click(x, y)

def right_click(x=None, y=None):
    """右键点击"""
    _controller.mouse.right_click(x, y)

def double_click(x=None, y=None):
    """双击"""
    _controller.mouse.double_click(x, y)

def type_text(text, interval=0.05):
    """输入文本"""
    _controller.keyboard.type_text(text, interval)

def press_key(key_name):
    """按下键"""
    _controller.keyboard.press_key(key_name)

def release_key(key_name):
    """释放键"""
    _controller.keyboard.release_key(key_name)

def tap_key(key_name, count=1):
    """点击键"""
    _controller.keyboard.tap_key(key_name, count)

def key_combination(*keys):
    """按键组合"""
    _controller.keyboard.key_combination(*keys)

def drag_to(start_x, start_y, end_x, end_y, duration=1.0):
    """拖动鼠标"""
    _controller.mouse.drag_to(start_x, start_y, end_x, end_y, duration)

def scroll_mouse(x, y, direction=1, amount=5):
    """滚动鼠标滚轮
    
    Args:
        x: 滚动位置X坐标
        y: 滚动位置Y坐标
        direction: 方向 1向上，-1向下
        amount: 滚动量
    """
    _controller.mouse.scroll(x, y, 0, direction * amount)

def wait(duration=1.0):
    """等待"""
    _controller.wait(duration)

def get_mouse_position():
    """获取鼠标位置"""
    return _controller.mouse.get_position()
