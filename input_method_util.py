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
    buf = ctypes.create_unicode_buffer(9)
    res = ctypes.windll.user32.GetKeyboardLayoutNameW(buf)
    if res:
        layout = buf.value
        return layout_map.get(layout, f"未知({layout})")
    else:
        return "无法获取输入法布局"

if __name__ == '__main__':
    print("当前输入法:", get_keyboard_layout_name())
