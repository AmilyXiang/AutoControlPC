import xml.etree.ElementTree as ET
import os
import time
import threading


import pyautogui
import sys
import numpy as np


# OCR工具实例
from ocr_tool import OcrTool
ocr = OcrTool(['en', 'ch_sim'], gpu=False)

# P2P网络支持
from p2p_network import get_network, init_network, stop_network
from network_event import NetworkEvent, EVENTS

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
    elif step_type == 'audio':
        if action == 'play':
            from audio_player import play_audio
            device_idx = int(step.get('device', -1))
            device_arg = device_idx if device_idx >= 0 else None
            time_duration = step.get('time')
            duration_arg = float(time_duration) if time_duration else None
            ok = play_audio(content, device_arg, duration_arg)
            print(f"[AUDIO] 播放音频: {content} {'成功' if ok else '失败'}" + (f" (时长: {duration_arg}s)" if duration_arg else ""))
        elif action == 'play_async':
            # 异步播放，不阻塞后续步骤
            from audio_player import play_audio
            device_idx = int(step.get('device', -1))
            device_arg = device_idx if device_idx >= 0 else None
            time_duration = step.get('time')
            duration_arg = float(time_duration) if time_duration else None
            thread = threading.Thread(target=play_audio, args=(content, device_arg, duration_arg), daemon=True)
            thread.start()
            print(f"[AUDIO] 异步播放音频: {content}，设备: {device_idx if device_idx >= 0 else '默认'}" + (f", 时长: {duration_arg}s" if duration_arg else ""))
        elif action == 'record':
            # 同步录音
            from audio_recorder import record_audio
            device_idx = int(step.get('device', 0))
            duration = float(step.get('duration', 5))
            output_file = content
            record_audio(device_idx, duration, output_file)
            print(f"[AUDIO] 录音完成: {output_file}")
        elif action == 'record_async':
            # 异步录音，不阻塞后续步骤
            from audio_recorder import record_audio
            device_idx = int(step.get('device', 0))
            duration = float(step.get('duration', 5))
            output_file = content
            thread = threading.Thread(target=record_audio, args=(device_idx, duration, output_file), daemon=True)
            thread.start()
            print(f"[AUDIO] 异步录音开始，设备: {device_idx}，时长: {duration}s，输出: {output_file}")
        elif action == 'stop_record':
            # 停止录音
            from audio_recorder import stop_record
            stop_record()
    elif step_type == 'network':
        if action == 'init':
            # network init: 初始化网络连接
            # content: peer_host:peer_port (例如: 192.168.1.101:9998)
            # 属性: local_port (本地监听端口，默认9998)
            local_port = int(step.get('local_port', 9998))
            
            try:
                if content and ':' in content:
                    parts = content.split(':')
                    peer_host = parts[0]
                    peer_port = int(parts[1])
                    print(f"[NETWORK] 初始化网络: 本地端口={local_port}, 对端={peer_host}:{peer_port}")
                    init_network(local_port, peer_host, peer_port)
                else:
                    print(f"[NETWORK] 初始化网络: 本地端口={local_port}（仅启动服务器）")
                    init_network(local_port=local_port)
                print(f"[NETWORK] ✓ 网络初始化成功")
            except Exception as e:
                print(f"[NETWORK] ✗ 网络初始化失败: {e}")
                raise RuntimeError(f"网络初始化失败，停止测试: {e}")
        
        elif action == 'send':
            # network send: 发送消息
            # content: 事件名称 (例如: call_start)
            # 属性: data (消息数据，JSON格式，可选)
            event_name = content
            data_str = step.get('data', '{}')
            
            try:
                import json
                data = json.loads(data_str)
            except:
                data = {'message': data_str}
            
            network = get_network()
            print(f"[DEBUG] 开始发送消息: 事件={event_name}, 数据={data}")
            print(f"[DEBUG] client_socket状态: {network.client_socket}")
            success = network.send(event_name, data)
            print(f"[NETWORK] 发送消息: {event_name}, 成功={success}")
            
            if not success:
                print(f"[NETWORK] ✗ 消息发送失败")
                raise RuntimeError(f"消息发送失败（事件: {event_name}），停止测试")
        
        elif action == 'receive':
            # network receive: 接收消息（阻塞）
            # content: 事件名称 (例如: call_answer)，为空表示接收任何事件
            # 属性: timeout (等待超时秒数，默认30)
            event_name = content if content else None
            timeout = float(step.get('timeout', 30))
            
            network = get_network()
            print(f"[DEBUG] 开始等待接收: 事件={event_name}, 超时={timeout}秒")
            message = network.receive(event_name, timeout)
            
            if message:
                print(f"[NETWORK] ✓ 接收成功: {message}")
            else:
                print(f"[NETWORK] ✗ 接收超时或失败: 事件={event_name}, 超时={timeout}秒")
                raise RuntimeError(f"消息接收失败或超时（事件: {event_name}），停止测试")
        
        elif action == 'stop':
            # network stop: 停止网络连接
            print(f"[NETWORK] 停止网络连接")
            stop_network()
    elif step_type == 'check':
        if action == 'input_method':
            from PIL import ImageGrab
            import auto_controller as ac
            screen = ImageGrab.grab()
            w, h = screen.size
            region = screen.crop((w-200, h-80, w, h))
            status = ocr.find_text_position('英', region)
            status_cn = ocr.find_text_position('中', region)
            print(f"[CHECK] OCR识别右下角：'英'={status}, '中'={status_cn}")
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
                print("[OCR] 本次截图所有识别结果：")
                results = ocr.reader.readtext(np.array(screenshot))
                for bbox, text, conf in results:
                    print(f"  文本: '{text}'  置信度: {conf:.2f}")
                screenshot.save(f"ocr_debug_{content}.png")
                print(f"[OCR] 已保存调试截图: ocr_debug_{content}.png")
    elif step_type == 'window':
        if action == 'maximize_top':
            from window_util import maximize_top_window
            ok = maximize_top_window()
            print(f"[WINDOW] 最大化最上层窗口: {'成功' if ok else '失败'}")
    elif step_type == 'icon':
        if action == 'find_and_move':
            from icon_detector import IconDetector
            from mouse_controller import MouseController
            detector = IconDetector(threshold=0.6)
            matches = detector.find_icons(content)
            if matches:
                x, y, score = matches[0]
                print(f"[ICON] 检测到图标，位置=({x},{y}), 置信度={score:.2f}，自动移动鼠标")
                MouseController().move_to(x, y, duration=0.3)
            else:
                print(f"[ICON] 未检测到图标: {content}")
    time.sleep(0.3)

def execute_testcases(xml_path, testcase_name=None):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    import glob
    for testcase in root.findall('testcase'):
        tc_name = testcase.get('name')
        # 如果指定了testcase_name，则只执行匹配的
        if testcase_name and tc_name != testcase_name:
            continue
        print(f"\n开始执行用例: {tc_name}")
        for step in testcase.findall('step'):
            execute_step(step)
        print(f"用例 '{tc_name}' 执行完毕\n")
        # 删除执行过程中生成的图片等文件
        patterns = ["last_rainbow_screenshot.png", "after_cui_ji_click.png", "after_call_click.png"]
        for pat in patterns:
            for f in glob.glob(pat):
                try:
                    os.remove(f)
                    # print(f"已删除文件: {f}")
                except Exception as e:
                    print(f"删除文件失败: {f}, 原因: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python run_testcase.py <xml文件路径> [testcase名称]")
        print("示例: python run_testcase.py testcase/p2p_network_demo.xml P2P_Sender")
        print("      python run_testcase.py testcase/rainbow_main.xml")
        sys.exit(1)
    xml_file = sys.argv[1]
    testcase_name = sys.argv[2] if len(sys.argv) > 2 else None
    if not os.path.isfile(xml_file):
        print(f"未找到指定的xml文件: {xml_file}")
        sys.exit(2)
    execute_testcases(xml_file, testcase_name)
    # 程序结束后清理所有 debug_match_*.png
    import glob
    for f in glob.glob('debug_match_*.png'):
        try:
            os.remove(f)
            print(f"已删除调试图片: {f}")
        except Exception as e:
            print(f"删除调试图片失败: {f}, 原因: {e}")
