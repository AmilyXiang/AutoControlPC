import xml.etree.ElementTree as ET
import os
import time
import threading


import pyautogui
import sys
import numpy as np
from PIL import ImageGrab


# OCR工具实例
from ocr_tool import OcrTool
ocr = None


def get_ocr_tool():
    """按需初始化OCR，减少程序启动阻塞"""
    global ocr
    if ocr is None:
        print("[OCR] Initializing OCR engine...")
        ocr = OcrTool(['en', 'ch_sim'], gpu=False)
    return ocr


def grab_screen_or_raise(context):
    """统一截图入口，给出Jenkins可执行诊断信息"""
    try:
        return ImageGrab.grab()
    except OSError as e:
        raise RuntimeError(
            f"[{context}] Screenshot capture failed. Jenkins may be running in a non-interactive session "
            "(service session) or the desktop is locked. Please run the agent in a logged-in, unlocked desktop session."
        ) from e

# 设备管理器
from device_manager import get_device_id

# P2P网络支持
from p2p_network import get_network, init_network, stop_network
from network_event import NetworkEvent, EVENTS

import re
def _resolve_device_vars(text):
    """替换 {device.X.field} 变量为 devices.json 中的实际值"""
    if not text or '{device.' not in text:
        return text
    from dect.config.settings import get_device_config
    def _replacer(m):
        device_id, field = m.group(1), m.group(2)
        cfg = get_device_config(device_id)
        if hasattr(cfg, field):
            return str(getattr(cfg, field))
        raise ValueError(f"DeviceConfig has no field '{field}' (device={device_id})")
    return re.sub(r'\{device\.(\w+)\.(\w+)\}', _replacer, text)

# --- 异步音频线程追踪 ---
_async_audio_threads = []  # [(thread, error_holder), ...]

class _ThreadWithError:
    """包装线程目标函数，捕获异常供主线程检查。"""
    def __init__(self, target, args=()):
        self.error = None
        self._target = target
        self._args = args

    def run(self):
        try:
            self._target(*self._args)
        except Exception as e:
            self.error = e

def _check_async_audio_threads():
    """Join所有异步音频线程，如有失败则抛出AssertionError。"""
    global _async_audio_threads
    errors = []
    for t, holder in _async_audio_threads:
        t.join()
        if holder.error:
            errors.append(str(holder.error))
    _async_audio_threads = []
    if errors:
        raise AssertionError(f"[AUDIO] Async audio failed: {'; '.join(errors)}")


def _check_case_capabilities(testcase_elem):
    """检查用例 init step 上的 require_cap，型号不满足则返回首个缺失项。
    
    约定：require_cap 只标注在 action="init" 的 step 上。
    返回 None 表示全部满足；返回 (cap, model, device_id) 表示首个不满足的。
    """
    from dect.config.settings import get_device_config, model_has_capability
    for elem in testcase_elem.iter('step'):
        if elem.get('action') != 'init':
            continue
        cap = elem.get('require_cap')
        if cap:
            device_id = elem.get('device', '1')
            cfg = get_device_config(device_id)
            if not model_has_capability(cfg.model, cap):
                return (cap, cfg.model, device_id)
    return None


def execute_step(step):
    step_type = step.get('type')
    action = step.get('action')
    content = _resolve_device_vars(step.get('content'))
    print(f"Execute step: type={step_type}, action={action}, content={content}")

    if step_type == 'keyboard':
        if action == 'press_key':
            pyautogui.press(content)
        elif action == 'type_text':
            # 支持动态时间变量 {now}
            if '{now}' in content:
                now_str = time.strftime('%Y%m%d_%H%M%S')
                content = content.replace('{now}', now_str)
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
            device_str = step.get('device', '-1')
            device_idx = get_device_id(device_str)
            device_arg = device_idx if device_idx is not None and device_idx >= 0 else None
            time_duration = step.get('time')
            duration_arg = float(time_duration) if time_duration else None
            ok = play_audio(content, device_arg, duration_arg)
            print(f"[AUDIO] Play audio: {content} {'success' if ok else 'failed'}" + (f" (duration: {duration_arg}s)" if duration_arg else ""))
        elif action == 'play_async':
            # 异步播放，不阻塞后续步骤，失败时fail case
            from audio_player import play_audio
            device_str = step.get('device', '-1')
            device_idx = get_device_id(device_str)
            device_arg = device_idx if device_idx is not None and device_idx >= 0 else None
            time_duration = step.get('time')
            duration_arg = float(time_duration) if time_duration else None
            holder = _ThreadWithError(target=play_audio, args=(content, device_arg, duration_arg))
            thread = threading.Thread(target=holder.run, daemon=True)
            thread.start()
            _async_audio_threads.append((thread, holder))
            device_display = f"'{device_str}' (ID={device_idx})" if device_idx is not None else (device_str if device_str != '-1' else 'default')
            print(f"[AUDIO] Async play audio: {content}, device: {device_display}" + (f", duration: {duration_arg}s" if duration_arg else ""))
        elif action == 'record':
            # 同步录音
            from audio_recorder import record_audio
            device_str = step.get('device', '0')
            device_idx = get_device_id(device_str)
            if device_idx is None:
                device_idx = 0
            duration = float(step.get('duration', 5))
            output_file = content
            record_audio(device_idx, duration, output_file)
            print(f"[AUDIO] Recording completed: {output_file}")
        elif action == 'record_async':
            # 异步录音，不阻塞后续步骤，失败时fail case
            from audio_recorder import record_audio
            device_str = step.get('device', '0')
            device_idx = get_device_id(device_str)
            if device_idx is None:
                device_idx = 0
            duration = float(step.get('duration', 5))
            output_file = content
            holder = _ThreadWithError(target=record_audio, args=(device_idx, duration, output_file))
            thread = threading.Thread(target=holder.run, daemon=True)
            thread.start()
            _async_audio_threads.append((thread, holder))
            device_display = f"'{device_str}' (ID={device_idx})" if device_str != '0' else '0'
            print(f"[AUDIO] Async recording started, device: {device_display}, duration: {duration}s, output: {output_file}")
        elif action == 'stop_record':
            # 停止录音
            from audio_recorder import stop_record
            stop_record()
        elif action == 'check_voice':
            # 先检查异步音频线程是否有失败
            _check_async_audio_threads()
            # 检测音频文件是否有声音
            from audio_voice_detector import detect_silence
            audio_file = content
            rms_th = float(step.get('rms_threshold', 0.001))
            snr_th = float(step.get('snr_threshold', 3.0))
            result = detect_silence(audio_file, rms_threshold=rms_th, snr_threshold=snr_th)
            has_voice = not result['is_silence']
            print(f"[AUDIO] Voice check: {audio_file} -> {'voice detected' if has_voice else 'silence'} "
                f"(RMS={result['rms_mean']}, noise_floor={result['noise_floor']}, SNR={result['snr']})")
            expect = step.get('expect')
            if expect is not None:
                expect_voice = expect.lower() in ('true', '1', 'yes')
                if expect_voice != has_voice:
                    raise AssertionError(
                        f"Voice check assertion failed: expected {'voice' if expect_voice else 'silence'}, "
                        f"actual {'voice' if has_voice else 'silence'} (file={audio_file})")
                print(f"[AUDIO] Voice check assertion passed: expected {'voice' if expect_voice else 'silence'}")
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
                    print(f"[NETWORK] Initialize network: local_port={local_port}, peer={peer_host}:{peer_port}")
                    init_network(local_port, peer_host, peer_port)
                else:
                    print(f"[NETWORK] Initialize network: local_port={local_port} (server only)")
                    init_network(local_port=local_port)
                print(f"[NETWORK] [OK] Network initialization succeeded")
            except Exception as e:
                print(f"[NETWORK] [FAIL] Network initialization failed: {e}")
                raise RuntimeError(f"Network initialization failed, stop testing: {e}")
        
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
            print(f"[DEBUG] Sending message: event={event_name}, data={data}")
            print(f"[DEBUG] client_socket state: {network.client_socket}")
            success = network.send(event_name, data)
            print(f"[NETWORK] Send message: {event_name}, success={success}")
            
            if not success:
                print(f"[NETWORK] [FAIL] Message send failed")
                raise RuntimeError(f"Message send failed (event: {event_name}), stop testing")
        
        elif action == 'receive':
            # network receive: 接收消息（阻塞）
            # content: 事件名称 (例如: call_answer)，为空表示接收任何事件
            # 属性: timeout (等待超时秒数，默认30)
            # 属性: check (验证data内容的JSON条件，可选)
            event_name = content if content else None
            timeout = float(step.get('timeout', 30))
            check_str = step.get('check', '')
            
            # 解析check条件（可选的data验证条件）
            check_data = {}
            if check_str:
                try:
                    import json
                    check_data = json.loads(check_str)
                except Exception as e:
                    raise RuntimeError(f"Failed to parse JSON in 'check' attribute: {check_str}, error: {e}")
            
            network = get_network()
            print(f"[DEBUG] Waiting to receive: event={event_name}, timeout={timeout}s")
            message = network.receive(event_name, timeout)
            
            if message:
                event = message.get('event')
                data = message.get('data', {})
                timestamp = message.get('timestamp')
                
                # 验证data内容
                if check_data:
                    all_match = True
                    for key, expected_value in check_data.items():
                        actual_value = data.get(key)
                        if actual_value != expected_value:
                            all_match = False
                            print(f"[NETWORK] [WARN] Data validation failed: {key}, expected={expected_value}, actual={actual_value}")
                    
                    if not all_match:
                        raise RuntimeError(f"Received message validation failed: event={event}, expected_data={check_data}, actual_data={data}")
                
                print(f"[NETWORK] [OK] Receive succeeded")
                print(f"           Event: {event}")
                print(f"           Data: {data}")
                print(f"           Timestamp: {timestamp}")
            else:
                print(f"[NETWORK] [FAIL] Receive timeout or failure: event={event_name}, timeout={timeout}s")
                raise RuntimeError(f"Message receive failed or timed out (event: {event_name}), stop testing")
        
        elif action == 'stop':
            # network stop: 停止网络连接
            print(f"[NETWORK] Stop network connection")
            stop_network()
    elif step_type == 'check':
        if action == 'input_method':
            import auto_controller as ac
            ocr_tool = get_ocr_tool()
            screen = grab_screen_or_raise('CHECK')
            w, h = screen.size
            region = screen.crop((w-200, h-80, w, h))
            status = ocr_tool.find_text_position('英', region)
            print(f"[CHECK] OCR in bottom-right corner: '英'={status}")
            need_switch = False
            if content == '英语(美国)':
                if not status:
                    print("[CHECK] Current input method is not English, trying to switch...")
                    need_switch = True
                else:
                    print("[CHECK] Current input method is already English, no switch needed")
            elif content == '中文(简体，中国)':
                if status:
                    print("[CHECK] Current input method is English, switching to Chinese...")
                    need_switch = True
                else:
                    print("[CHECK] Current input method is already not English, no switch needed")
            if need_switch:
                for i in range(5):
                    pyautogui.hotkey('ctrl', 'space')
                    time.sleep(2.0)
                    screen = grab_screen_or_raise('CHECK')
                    region = screen.crop((w-200, h-80, w, h))
                    status = ocr_tool.find_text_position('英', region)
                    print(f"[CHECK] OCR after switch: '英'={status}")
                    if (content == '英语(美国)' and status) or (content == '中文(简体，中国)' and not status):
                        print("[CHECK] Input method switch succeeded")
                        break
                else:
                    print("[CHECK] Input method switch failed, OCR state did not meet expectation")
            else:
                print("[CHECK] Current input method already matches expectation, no switch needed")
    elif step_type == 'process':
        if action == 'close':
            # 关闭指定进程
            process_name = content
            from process import close_process_by_name
            close_process_by_name(process_name)
        elif action == 'runbat':
            # 运行bat批处理文件
            bat_path = content
            from process import run_bat_file
            run_bat_file(bat_path)
    elif step_type == 'clipboard':
        if action == 'save':
            # 保存剪贴板内容到文件
            fmt = step.get('format', 'txt')
            filename = content
            import clipboard_save
            if fmt == 'txt':
                clipboard_save.save_clipboard_to_txt(filename)
            elif fmt == 'csv':
                clipboard_save.save_clipboard_to_csv(filename)
            else:
                print(f"[CLIPBOARD] Unsupported format: {fmt}")
    elif step_type == 'wait':
        if action == 'sleep':
            time.sleep(float(content))
    elif step_type == 'ocr':
        if action == 'find_and_click':
            time.sleep(2)
            import auto_controller as ac
            ocr_tool = get_ocr_tool()
            screenshot = grab_screen_or_raise('OCR')
            pos = ocr_tool.find_text_position(content, screenshot)
            if pos:
                print(f"[OCR] Found '{content}', click position: {pos}")
                ac.move_mouse(pos[0], pos[1], duration=0.5)
                ac.left_click()
            else:
                print(f"[OCR] '{content}' not found, skip click")
                print("[OCR] All recognized results in current screenshot:")
                results = ocr_tool.reader.readtext(np.array(screenshot))
                for bbox, text, conf in results:
                    print(f"  Text: '{text}'  Confidence: {conf:.2f}")
                screenshot.save(f"ocr_debug_{content}.png")
                print(f"[OCR] Debug screenshot saved: ocr_debug_{content}.png")
    elif step_type == 'window':
        if action == 'maximize_top':
            from window_util import maximize_top_window
            ok = maximize_top_window()
            print(f"[WINDOW] Maximize top window: {'success' if ok else 'failed'}")
    elif step_type == 'icon':
        if action == 'find_and_move':
            from icon_detector import IconDetector
            from mouse_controller import MouseController
            detector = IconDetector(threshold=0.6)
            matches = detector.find_icons(content)
            if matches:
                x, y, score = matches[0]
                print(f"[ICON] Icon detected at ({x},{y}), confidence={score:.2f}, move mouse automatically")
                MouseController().move_to(x, y, duration=0.3)
            else:
                print(f"[ICON] Icon not detected: {content}")
    elif step_type == 'dect':
        from dect_controller import init_dect_controller, get_dect_controller, close_dect_controller
        device_id = step.get('device', '1')
        if action == 'init':
            # model 从 devices.json 读取; content 可选覆盖型号
            init_dect_controller(model=content or None, device_id=device_id)
        elif action == 'press_key':
            # content: 按键名 (例如: 1, hangup, ok)
            press_type = step.get('press_type', 'short')
            ctrl = get_dect_controller(device_id)
            ctrl.press_key(content, press_type=press_type)
        elif action == 'dial_number':
            # content: 整串号码 (例如: 10000, *123#)
            # 支持的字符: 0-9, *, #
            interval = float(step.get('interval', 0.5))
            ctrl = get_dect_controller(device_id)
            for ch in content:
                if ch in '0123456789*#':
                    ctrl.press_key(ch)
                    time.sleep(interval)
                else:
                    print(f"[DECT] dial_number: skip unsupported character '{ch}'")
            print(f"[DECT] dial_number: dialed '{content}' ({len([c for c in content if c in '0123456789*#'])} keys, interval={interval}s)")
        elif action == 'verify_screen':
            # content: JSON格式的期望结果 (例如: {"text": "10000", "signal": true})
            import json
            ctrl = get_dect_controller(device_id)
            expected = json.loads(content)
            success = ctrl.verify_screen(expected)
            if not success:
                raise AssertionError(f"DECT screen verification failed: expected {content}")
        elif action == 'press_and_verify':
            # content: 按键名, verify: JSON格式的期望结果
            # 按键后立即拍照验证，无间隔延时
            import json
            ctrl = get_dect_controller(device_id)
            press_type = step.get('press_type', 'short')
            verify_content = step.get('verify')
            if not verify_content:
                raise ValueError("press_and_verify requires 'verify' attribute with JSON expected result")
            expected = json.loads(verify_content)
            ctrl.press_and_verify(content, expected, press_type=press_type)
        elif action == 'capture':
            # 仅拍照分析，不验证
            ctrl = get_dect_controller(device_id)
            ctrl.capture_and_analyze()
        elif action == 'navigate':
            # content: 导航路径名（如 'service_menu', 'test_sw_info'）
            # 自动查询设备型号并获取对应的按键序列
            from dect.config.settings import get_device_config, get_navigation_path
            ctrl = get_dect_controller(device_id)
            cfg = get_device_config(device_id)
            path = get_navigation_path(cfg.model, content)
            interval = float(step.get('interval', 0.3))
            print(f"[DECT] navigate: {content} ({cfg.model}) -> {path}")
            for key in path:
                ctrl.press_key(key)
                time.sleep(interval)
        elif action == 'origin':
            ctrl = get_dect_controller(device_id)
            ctrl.origin()
        elif action == 'close':
            close_dect_controller(device_id)
    time.sleep(0.3)


def execute_if_block(elem):
    """Execute an <if> block: check screen condition, run child steps if matched.

    XML syntax:
        <if type="dect" check='{"lock": true}' device="1">
            <step ... />
            <else>
                <step ... />
            </else>
        </if>

    Returns number of child steps executed.
    """
    import json
    block_type = elem.get('type')
    if block_type != 'dect':
        print(f"[IF] Unsupported if-block type: {block_type}, skipping")
        return 0

    device_id = elem.get('device', '1')
    check_str = elem.get('check')
    if not check_str:
        print("[IF] Missing 'check' attribute on <if> block, skipping")
        return 0

    from dect_controller import get_dect_controller
    ctrl = get_dect_controller(device_id)
    result = ctrl.capture_and_analyze()

    expected = json.loads(check_str)
    condition_met = True
    for key, value in expected.items():
        if key == "text":
            texts = result.get("text", [])
            check_texts = [value] if isinstance(value, str) else list(value)
            for t in check_texts:
                joined = ' '.join(texts)
                if t not in texts and t not in joined:
                    condition_met = False
                    break
        else:
            if key not in result:
                condition_met = False
                break

    count = 0
    if condition_met:
        print(f"[IF] Condition met: {check_str} -> executing child steps")
        for child in elem:
            if child.tag == 'step':
                execute_step(child)
                count += 1
            elif child.tag == 'else':
                pass  # skip else block
    else:
        print(f"[IF] Condition NOT met: {check_str} -> executing <else> block")
        else_block = elem.find('else')
        if else_block is not None:
            for child in else_block.findall('step'):
                execute_step(child)
                count += 1
        else:
            print("[IF] No <else> block, skipping")
    return count


def execute_testcases(xml_path, testcase_name=None, report=None):
    from test_report import TestReport
    if report is None:
        report = TestReport(xml_path)
    tree = ET.parse(xml_path)
    root = tree.getroot()
    import glob
    xml_basename = os.path.basename(xml_path)
    for testcase in root.findall('testcase'):
        tc_name = testcase.get('name')
        # 如果指定了testcase_name，则只执行匹配的
        if testcase_name and tc_name != testcase_name:
            continue
        display_name = f"[{xml_basename}] {tc_name}"
        print(f"\nStart testcase: {display_name}")
        tc_start = time.time()
        steps_done = 0

        # capability gate: 开始前检查用例所有 require_cap，型号不支持则整个 case SKIP
        missing_cap = _check_case_capabilities(testcase)
        if missing_cap:
            cap_str, model_str, device_str = missing_cap
            print(f"[SKIP CASE] Testcase requires capability '{cap_str}' but model {model_str} (device {device_str}) lacks it")
            tc_duration = time.time() - tc_start
            report.add_result(display_name, 'SKIP', tc_duration, steps_done=0)
            continue

        try:
            for elem in testcase:
                if elem.tag == 'step':
                    execute_step(elem)
                    steps_done += 1
                elif elem.tag == 'if':
                    executed = execute_if_block(elem)
                    if executed:
                        steps_done += executed
            tc_duration = time.time() - tc_start
            report.add_result(display_name, 'PASS', tc_duration, steps_done=steps_done)
        except Exception as e:
            tc_duration = time.time() - tc_start
            report.add_result(display_name, 'FAIL', tc_duration, error=e, steps_done=steps_done)
            print(f"[ERROR] Testcase '{display_name}' execution failed: {e}")
            # 报错时尝试让所有 DECT 机械回原点
            try:
                from dect_controller import _controllers
                for did, ctrl in _controllers.items():
                    try:
                        ctrl.press_key("onhook")
                        print(f"[DECT] Error recovery: device {did} pressed onhook")
                    except Exception:
                        pass
                    try:
                        ctrl.origin()
                        print(f"[DECT] Error recovery: device {did} returned to origin")
                    except Exception:
                        pass
            except Exception:
                pass
        print(f"Testcase '{display_name}' finished\n")
        # 删除执行过程中生成的图片等文件
        patterns = ["last_rainbow_screenshot.png", "after_cui_ji_click.png", "after_call_click.png"]
        for pat in patterns:
            for f in glob.glob(pat):
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Failed to delete file: {f}, reason: {e}")
    return report


def run_and_report(xml_paths, testcase_name=None):
    """执行一组 XML 测试文件，汇总生成一份报告。"""
    from test_report import TestReport
    label = xml_paths[0] if len(xml_paths) == 1 else f"{len(xml_paths)} XML files"
    report = TestReport(label)
    for xml_path in xml_paths:
        print(f"\n{'='*50}")
        print(f"Load test file: {xml_path}")
        print(f"{'='*50}")
        execute_testcases(xml_path, testcase_name=testcase_name, report=report)

    # 生成 HTML 测试报告
    report_path = report.generate_html()
    total, passed, failed, skipped = report.summary()
    print(f"\n{'='*50}")
    print(f"Test report generated: {report_path}")
    print(f"Total: {total}  Passed: {passed}  Failed: {failed}  Skipped: {skipped}")
    print(f"{'='*50}")
    return report

def resolve_xml_paths(path_arg):
    """解析路径参数，支持单文件、目录、glob 通配符。"""
    import glob as _glob
    # 目录：取下面所有 .xml
    if os.path.isdir(path_arg):
        files = sorted(_glob.glob(os.path.join(path_arg, '*.xml')))
        if not files:
            print(f"No XML files found in directory: {path_arg}")
            sys.exit(2)
        return files
    # 通配符
    if '*' in path_arg or '?' in path_arg:
        files = sorted(_glob.glob(path_arg))
        if not files:
            print(f"Wildcard did not match any files: {path_arg}")
            sys.exit(2)
        return files
    # 单文件
    if os.path.isfile(path_arg):
        return [path_arg]
    print(f"Specified file or directory not found: {path_arg}")
    sys.exit(2)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_testcase.py <xml_file/dir/glob> [testcase_name]")
        print("Example: python run_testcase.py testcase/rainbow_main.xml")
        print("         python run_testcase.py testcase/DECT/")
        print("         python run_testcase.py testcase/DECT/*.xml")
        print("         python run_testcase.py testcase/DECT/ MyCaseName")
        sys.exit(1)
    xml_arg = sys.argv[1]
    testcase_name = sys.argv[2] if len(sys.argv) > 2 else None
    xml_paths = resolve_xml_paths(xml_arg)
    print(f"XML files to execute ({len(xml_paths)}): {xml_paths}")
    report = run_and_report(xml_paths, testcase_name)
    # 有失败用例时返回非零退出码
    _, _, failed, _ = report.summary()
    # 释放 DECT 硬件资源（串口、相机、模型）
    try:
        from dect_controller import destroy_all
        destroy_all()
    except Exception:
        pass
    # 清理调试图片
    import glob
    for f in glob.glob('debug_match_*.png'):
        try:
            os.remove(f)
        except Exception as e:
            print(f"Failed to delete debug image: {f}, reason: {e}")
    if failed > 0:
        sys.exit(1)
