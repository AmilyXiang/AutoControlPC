"""
鼠标控制模块
提供鼠标移动、点击、滚动等操作
"""

from pynput.mouse import Controller, Button
import time


class MouseController:
    """鼠标控制类"""
    
    def __init__(self):
        self.mouse = Controller()
    
    def get_position(self):
        """获取当前鼠标位置"""
        return self.mouse.position
    
    def move_to(self, x, y, duration=0.5):
        """移动鼠标到指定位置
        
        Args:
            x: 目标X坐标
            y: 目标Y坐标
            duration: 移动耗时（秒），0表示立即移动
        """
        if duration > 0:
            current_x, current_y = self.mouse.position
            steps = int(duration * 60)  # 假设60fps
            for i in range(steps):
                progress = (i + 1) / steps
                new_x = current_x + (x - current_x) * progress
                new_y = current_y + (y - current_y) * progress
                self.mouse.position = (new_x, new_y)
                time.sleep(1/60)
        else:
            self.mouse.position = (x, y)
    
    def move_relative(self, dx, dy, duration=0.5):
        """相对当前位置移动鼠标
        
        Args:
            dx: X轴偏移量
            dy: Y轴偏移量
            duration: 移动耗时（秒）
        """
        current_x, current_y = self.mouse.position
        self.move_to(current_x + dx, current_y + dy, duration)
    
    def click(self, x=None, y=None, button='left', count=1, interval=0.1):
        """点击鼠标
        
        Args:
            x: 点击的X坐标，为None时在当前位置点击
            y: 点击的Y坐标，为None时在当前位置点击
            button: 按钮类型 'left', 'right', 'middle'
            count: 点击次数
            interval: 点击之间的间隔（秒）
        """
        if x is not None and y is not None:
            self.move_to(x, y, duration=0.2)
        
        btn = Button.left if button == 'left' else Button.right if button == 'right' else Button.middle
        
        for _ in range(count):
            self.mouse.click(btn, 1)
            if count > 1:
                time.sleep(interval)
    
    def left_click(self, x=None, y=None, count=1, interval=0.1):
        """左键点击"""
        self.click(x, y, 'left', count, interval)
    
    def right_click(self, x=None, y=None):
        """右键点击"""
        self.click(x, y, 'right', 1, 0.1)
    
    def double_click(self, x=None, y=None, interval=0.1):
        """双击"""
        self.click(x, y, 'left', 2, interval)
    
    def scroll(self, x, y, dx=0, dy=1):
        """滚动滚轮
        
        Args:
            x: 滚动位置的X坐标
            y: 滚动位置的Y坐标
            dx: 水平滚动（不是所有鼠标都支持）
            dy: 垂直滚动（正数向上，负数向下）
        """
        self.mouse.position = (x, y)
        self.mouse.scroll(dx, dy)
    
    def drag_to(self, start_x, start_y, end_x, end_y, duration=1.0, button='left'):
        """从一个位置拖动到另一个位置
        
        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 拖动耗时（秒）
            button: 按钮类型 'left', 'right', 'middle'
        """
        self.move_to(start_x, start_y, duration=0.2)
        
        btn = Button.left if button == 'left' else Button.right if button == 'right' else Button.middle
        
        with self.mouse.pressed(btn):
            self.move_to(end_x, end_y, duration=duration)
