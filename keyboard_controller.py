"""
键盘控制模块
提供键盘按键、输入文本等操作
"""

from pynput.keyboard import Controller, Key
import time


class KeyboardController:
    """键盘控制类"""
    
    def __init__(self):
        self.keyboard = Controller()
    
    # 特殊键映射
    SPECIAL_KEYS = {
        'enter': Key.enter,
        'return': Key.enter,
        'tab': Key.tab,
        'backspace': Key.backspace,
        'delete': Key.delete,
        'escape': Key.esc,
        'esc': Key.esc,
        'space': Key.space,
        'home': Key.home,
        'end': Key.end,
        'pageup': Key.page_up,
        'pagedown': Key.page_down,
        'up': Key.up,
        'down': Key.down,
        'left': Key.left,
        'right': Key.right,
        'shift': Key.shift,
        'ctrl': Key.ctrl,
        'control': Key.ctrl,
        'alt': Key.alt,
        'altgr': Key.alt_gr,
        'win': Key.cmd,
        'cmd': Key.cmd,
        'capslock': Key.caps_lock,
        'numlock': Key.num_lock,
        'scrolllock': Key.scroll_lock,
        'print': Key.print_screen,
        'insert': Key.insert,
        'f1': Key.f1,
        'f2': Key.f2,
        'f3': Key.f3,
        'f4': Key.f4,
        'f5': Key.f5,
        'f6': Key.f6,
        'f7': Key.f7,
        'f8': Key.f8,
        'f9': Key.f9,
        'f10': Key.f10,
        'f11': Key.f11,
        'f12': Key.f12,
    }
    
    def type_text(self, text, interval=0.05):
        """输入文本
        
        Args:
            text: 要输入的文本
            interval: 每个字符之间的间隔（秒）
        """
        for char in text:
            self.keyboard.type(char)
            if interval > 0:
                time.sleep(interval)
    
    def press_key(self, key_name):
        """按下键（不释放）
        
        Args:
            key_name: 键名称，可以是单个字符或特殊键名
        """
        key = self._get_key(key_name)
        self.keyboard.press(key)
    
    def release_key(self, key_name):
        """释放键
        
        Args:
            key_name: 键名称
        """
        key = self._get_key(key_name)
        self.keyboard.release(key)
    
    def tap_key(self, key_name, count=1, interval=0.1):
        """点击键（按下后立即释放）
        
        Args:
            key_name: 键名称
            count: 点击次数
            interval: 点击之间的间隔（秒）
        """
        for _ in range(count):
            self.press_key(key_name)
            self.release_key(key_name)
            if count > 1:
                time.sleep(interval)
    
    def key_combination(self, *keys):
        """按下多个键的组合（如Ctrl+C）
        
        Args:
            *keys: 要组合的键列表
            
        Example:
            key_combination('ctrl', 'c')  # Ctrl+C
            key_combination('ctrl', 'alt', 'delete')  # Ctrl+Alt+Delete
        """
        key_objects = [self._get_key(k) for k in keys]
        
        for key in key_objects:
            self.keyboard.press(key)
        
        # 释放按键，顺序相反
        for key in reversed(key_objects):
            self.keyboard.release(key)
    
    def hold_key(self, key_name, duration=1.0):
        """按住键一段时间
        
        Args:
            key_name: 键名称
            duration: 持续时间（秒）
        """
        self.press_key(key_name)
        time.sleep(duration)
        self.release_key(key_name)
    
    def _get_key(self, key_name):
        """根据键名获取对应的Key对象
        
        Args:
            key_name: 键名称（字符或特殊键名）
            
        Returns:
            Key对象
        """
        key_name_lower = str(key_name).lower()
        
        if key_name_lower in self.SPECIAL_KEYS:
            return self.SPECIAL_KEYS[key_name_lower]
        elif len(key_name) == 1:
            return key_name
        else:
            raise ValueError(f"Unknown key: {key_name}")
