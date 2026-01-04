
import xml.etree.ElementTree as ET
import os
import time


import pyautogui
import sys
import numpy as np


# OCR工具实例
from ocr_tool import OcrTool
ocr = OcrTool(['en', 'ch_sim'], gpu=False)

def execute_step(step):
    step_type = step.get('type')
    action = step.get('action')
    content = step.get('content')
    print(f"执行: type={step_type}, action={action}, content={content}")
    if step_type == 'keyboard':
        if action == 'press_key':
            pyautogui.press(content)
        elif action == 'type_text':
            pyautogui.typewrite(content, interval=0.1)
    elif step_type == 'mouse':
        if action == 'move_mouse':
            x, y = map(int, content.split(','))
            pyautogui.moveTo(x, y, duration=0.5)
        elif action == 'click':
            if content == 'left':
                pyautogui.click()
            elif content == 'right':
                pyautogui.click(button='right')
    elif step_type == 'check':
        if action == 'input_method':
            # OCR识别右下角输入法状态
            from PIL import ImageGrab
            import auto_controller as ac
            # 获取屏幕尺寸
            screen = ImageGrab.grab()
            w, h = screen.size
            # 截取右下角区域（如宽200高80像素，可根据实际调整）
            region = screen.crop((w-200, h-80, w, h))
            status = ocr.find_text_position('英', region)
            status_cn = ocr.find_text_position('中', region)
            print(f"[CHECK] OCR识别右下角：'英'={status}, '中'={status_cn}")
            # 期望为“英语(美国)”时，右下角应为“英”
            need_switch = False
            if content == '英语(美国)':
                if not status:
                    print("[CHECK] 当前不是英文输入状态，尝试切换...")
                    need_switch = True
            elif content == '中文(简体，中国)':
                if not status_cn:
                    print("[CHECK] 当前不是中文输入状态，尝试切换...")
                    need_switch = True
            if need_switch:
                for i in range(5):
                    pyautogui.hotkey('ctrlleft', 'space')
                    time.sleep(2.0)
                    screen = ImageGrab.grab()
                    region = screen.crop((w-200, h-80, w, h))
                    status = ocr.find_text_position('英', region)
                    status_cn = ocr.find_text_position('中', region)
                    print(f"[CHECK] 切换后OCR：'英'={status}, '中'={status_cn}")
                    if (content == '英语(美国)' and status) or (content == '中文(简体，中国)' and status_cn):
                        print("[CHECK] 输入法切换成功！")
                        break
                else:
                    print("[CHECK] 输入法切换失败，当前OCR状态未达期望")
            else:
                print("[CHECK] 当前输入法已是期望值，无需切换")
    elif step_type == 'wait':
        if action == 'sleep':
            time.sleep(float(content))
    elif step_type == 'ocr':
        if action == 'find_and_click':
            # 增加等待，确保界面已刷新
            time.sleep(2)
            from PIL import ImageGrab
            import auto_controller as ac
            screenshot = ImageGrab.grab()
            pos = ocr.find_text_position(content, screenshot)
            if pos:
                print(f"[OCR] 找到'{content}'，点击位置: {pos}")
                ac.move_mouse(pos[0], pos[1], duration=0.5)
                ac.left_click()
            else:
                print(f"[OCR] 未找到'{content}'，跳过点击")
                # 打印所有识别到的文本和置信度
                print("[OCR] 本次截图所有识别结果：")
                results = ocr.reader.readtext(np.array(screenshot))
                for bbox, text, conf in results:
                    print(f"  文本: '{text}'  置信度: {conf:.2f}")
                # 保存截图
                screenshot.save(f"ocr_debug_{content}.png")
                print(f"[OCR] 已保存调试截图: ocr_debug_{content}.png")
    time.sleep(0.3)

def execute_testcases(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    import glob
    for testcase in root.findall('testcase'):
        print(f"\n开始执行用例: {testcase.get('name')}")
        for step in testcase.findall('step'):
            execute_step(step)
        print(f"用例 '{testcase.get('name')}' 执行完毕\n")
        # 删除执行过程中生成的图片等文件
        patterns = ["last_rainbow_screenshot.png", "after_cui_ji_click.png", "after_call_click.png"]
        for pat in patterns:
            for f in glob.glob(pat):
                try:
                    os.remove(f)
                    print(f"已删除文件: {f}")
                except Exception as e:
                    print(f"删除文件失败: {f}, 原因: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python run_testcase.py <xml文件路径>")
        print("示例: python run_testcase.py testcase/rainbow_main.xml")
        sys.exit(1)
    xml_file = sys.argv[1]
    if not os.path.isfile(xml_file):
        print(f"未找到指定的xml文件: {xml_file}")
        sys.exit(2)
    execute_testcases(xml_file)
