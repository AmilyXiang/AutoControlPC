"""
input_method_util.py
输入法检测与切换工具，支持获取当前输入法名称。
"""
import ctypes

# 常见输入法布局映射表
layout_map = {
    "00000804": "中文(简体，中国)",
    "00000409": "英语(美国)",
    "00000408": "希腊语",
    "0000040C": "法语(法国)",
    "00000407": "德语(德国)",
    # 可根据需要补充更多
}

def get_keyboard_layout_name():
    """获取前台窗口的键盘布局"""
    # 获取前台窗口句柄
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    if not hwnd:
        return "无法获取前台窗口"
    
    # 获取前台窗口的线程ID
    thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
    if not thread_id:
        return "无法获取窗口线程"
    
    # 获取该线程的键盘布局
    hkl = ctypes.windll.user32.GetKeyboardLayout(thread_id)
    if not hkl:
        return "Failed to get keyboard layout"
    
    # 将HKL转换为布局ID（低16位）
    layout_id = format(hkl & 0xFFFF, '08X')
    
    return layout_map.get(layout_id, f"Unknown({layout_id})")

if __name__ == '__main__':
    print("Current input method:", get_keyboard_layout_name())
