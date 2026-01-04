"""
window_util.py
窗口操作工具：最大化当前最上层窗口。
"""
import win32gui
import win32con

def maximize_top_window():
    # 获取最前面的窗口句柄
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return True
    return False

if __name__ == '__main__':
    if maximize_top_window():
        print("已最大化最上层窗口。")
    else:
        print("未找到最上层窗口。")
