"""
mouse_position_test.py
实时打印鼠标位置，按 Ctrl+C 退出。
"""
from mouse_controller import MouseController
import time

if __name__ == '__main__':
    mc = MouseController()
    try:
        while True:
            pos = mc.get_position()
            print(f"当前鼠标位置: {pos}", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n已退出鼠标位置实时检测。")
