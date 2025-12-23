"""
高级功能模块 - 提供录制、回放、OCR识别等高级功能
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any
import auto_controller as ac


class ActionRecorder:
    """操作录制器 - 记录鼠标和键盘操作"""
    
    def __init__(self):
        self.actions = []
        self.start_time = None
        self.recording = False
    
    def start_recording(self):
        """开始记录操作"""
        self.actions = []
        self.start_time = time.time()
        self.recording = True
        print("开始录制操作...")
    
    def stop_recording(self):
        """停止记录操作"""
        self.recording = False
        print(f"录制完成，共记录 {len(self.actions)} 个操作")
        return self.actions
    
    def record_mouse_move(self, x: int, y: int, duration: float = 0):
        """记录鼠标移动"""
        if self.recording:
            self.actions.append({
                'type': 'mouse_move',
                'x': x,
                'y': y,
                'duration': duration,
                'timestamp': time.time() - self.start_time
            })
    
    def record_mouse_click(self, button: str = 'left', x: int = None, y: int = None):
        """记录鼠标点击"""
        if self.recording:
            self.actions.append({
                'type': 'mouse_click',
                'button': button,
                'x': x,
                'y': y,
                'timestamp': time.time() - self.start_time
            })
    
    def record_key_press(self, key: str):
        """记录按键"""
        if self.recording:
            self.actions.append({
                'type': 'key_press',
                'key': key,
                'timestamp': time.time() - self.start_time
            })
    
    def record_text_input(self, text: str):
        """记录文本输入"""
        if self.recording:
            self.actions.append({
                'type': 'text_input',
                'text': text,
                'timestamp': time.time() - self.start_time
            })
    
    def record_wait(self, duration: float):
        """记录等待操作"""
        if self.recording:
            self.actions.append({
                'type': 'wait',
                'duration': duration,
                'timestamp': time.time() - self.start_time
            })
    
    def save_to_file(self, filename: str):
        """保存操作序列到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'recorded_at': datetime.now().isoformat(),
                'action_count': len(self.actions),
                'actions': self.actions
            }, f, indent=2, ensure_ascii=False)
        print(f"已保存到 {filename}")
    
    def load_from_file(self, filename: str):
        """从JSON文件加载操作序列"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.actions = data['actions']
        print(f"已加载 {len(self.actions)} 个操作")
        return self.actions


class ActionPlayer:
    """操作回放器 - 回放记录的操作"""
    
    def __init__(self):
        self.actions = []
    
    def load_actions(self, actions: List[Dict[str, Any]]):
        """加载操作列表"""
        self.actions = actions
    
    def load_from_file(self, filename: str):
        """从文件加载操作"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.actions = data['actions']
    
    def play(self, speed: float = 1.0, loop: int = 1):
        """播放操作序列
        
        Args:
            speed: 播放速度（1.0为正常速度，>1.0为加速）
            loop: 循环次数
        """
        for loop_count in range(loop):
            print(f"开始回放 (循环 {loop_count + 1}/{loop})...")
            
            prev_timestamp = 0
            for action in self.actions:
                # 计算时间间隔
                time_diff = (action.get('timestamp', 0) - prev_timestamp) / speed
                if time_diff > 0:
                    time.sleep(time_diff)
                
                # 执行操作
                action_type = action.get('type')
                
                if action_type == 'mouse_move':
                    ac.move_mouse(action['x'], action['y'], action.get('duration', 0))
                
                elif action_type == 'mouse_click':
                    ac.click_mouse(
                        action.get('x'),
                        action.get('y'),
                        action.get('button', 'left')
                    )
                
                elif action_type == 'key_press':
                    ac.tap_key(action['key'])
                
                elif action_type == 'text_input':
                    ac.type_text(action['text'], interval=0.05)
                
                elif action_type == 'wait':
                    ac.wait(action.get('duration', 0.5) / speed)
                
                prev_timestamp = action.get('timestamp', 0)
            
            print(f"循环 {loop_count + 1} 完成")
    
    def play_interactive(self):
        """交互式播放，可以暂停"""
        print("开始交互式回放 (按 Ctrl+C 暂停)...")
        
        try:
            prev_timestamp = 0
            for idx, action in enumerate(self.actions):
                # 计算时间间隔
                time_diff = action.get('timestamp', 0) - prev_timestamp
                if time_diff > 0:
                    time.sleep(time_diff)
                
                # 执行操作
                action_type = action.get('type')
                
                if action_type == 'mouse_move':
                    ac.move_mouse(action['x'], action['y'], action.get('duration', 0))
                
                elif action_type == 'mouse_click':
                    ac.click_mouse(
                        action.get('x'),
                        action.get('y'),
                        action.get('button', 'left')
                    )
                
                elif action_type == 'key_press':
                    ac.tap_key(action['key'])
                
                elif action_type == 'text_input':
                    ac.type_text(action['text'], interval=0.05)
                
                elif action_type == 'wait':
                    ac.wait(action.get('duration', 0.5))
                
                # 显示进度
                print(f"执行第 {idx + 1}/{len(self.actions)} 个操作: {action_type}")
                
                prev_timestamp = action.get('timestamp', 0)
            
            print("回放完成")
        
        except KeyboardInterrupt:
            print("\n回放已暂停")


class ScriptBuilder:
    """脚本构建器 - 使用链式调用构建自动化脚本"""
    
    def __init__(self):
        self.actions = []
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """移动鼠标"""
        self.actions.append(('move_mouse', (x, y, duration)))
        return self
    
    def click(self, x: int = None, y: int = None, button: str = 'left', count: int = 1):
        """点击鼠标"""
        self.actions.append(('click', (x, y, button, count)))
        return self
    
    def type_text(self, text: str, interval: float = 0.05):
        """输入文本"""
        self.actions.append(('type_text', (text, interval)))
        return self
    
    def press_key(self, key: str):
        """按键"""
        self.actions.append(('press_key', (key,)))
        return self
    
    def key_combo(self, *keys):
        """按键组合"""
        self.actions.append(('key_combo', keys))
        return self
    
    def wait(self, duration: float = 1.0):
        """等待"""
        self.actions.append(('wait', (duration,)))
        return self
    
    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: float = 1.0):
        """拖拽"""
        self.actions.append(('drag', (x1, y1, x2, y2, duration)))
        return self
    
    def scroll(self, x: int, y: int, direction: int = 1, amount: int = 5):
        """滚动"""
        self.actions.append(('scroll', (x, y, direction, amount)))
        return self
    
    def execute(self):
        """执行脚本"""
        print(f"执行脚本，共 {len(self.actions)} 个操作...")
        
        for idx, (action_type, args) in enumerate(self.actions):
            try:
                if action_type == 'move_mouse':
                    ac.move_mouse(*args)
                elif action_type == 'click':
                    ac.click_mouse(*args)
                elif action_type == 'type_text':
                    ac.type_text(*args)
                elif action_type == 'press_key':
                    ac.tap_key(*args)
                elif action_type == 'key_combo':
                    ac.key_combination(*args)
                elif action_type == 'wait':
                    ac.wait(*args)
                elif action_type == 'drag':
                    ac.drag_to(*args)
                elif action_type == 'scroll':
                    ac.scroll_mouse(*args)
                
                print(f"  [{idx + 1}/{len(self.actions)}] {action_type} 完成")
            
            except Exception as e:
                print(f"  ✗ 操作失败: {e}")
                return False
        
        print("脚本执行完成")
        return True
    
    def save_as_code(self, filename: str):
        """保存为Python代码"""
        code = [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            "\"\"\"",
            "自动生成的自动化脚本",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\"\"\"",
            "",
            "import auto_controller as ac",
            "",
            "def main():",
            "    \"\"\"执行自动化操作\"\"\"",
        ]
        
        for action_type, args in self.actions:
            if action_type == 'move_mouse':
                code.append(f"    ac.move_mouse({args[0]}, {args[1]}, {args[2]})")
            elif action_type == 'click':
                code.append(f"    ac.click_mouse({args[0]}, {args[1]}, '{args[2]}', {args[3]})")
            elif action_type == 'type_text':
                code.append(f"    ac.type_text('{args[0]}', interval={args[1]})")
            elif action_type == 'press_key':
                code.append(f"    ac.tap_key('{args[0]}')")
            elif action_type == 'key_combo':
                keys = ', '.join(f"'{k}'" for k in args)
                code.append(f"    ac.key_combination({keys})")
            elif action_type == 'wait':
                code.append(f"    ac.wait({args[0]})")
            elif action_type == 'drag':
                code.append(f"    ac.drag_to({args[0]}, {args[1]}, {args[2]}, {args[3]}, {args[4]})")
            elif action_type == 'scroll':
                code.append(f"    ac.scroll_mouse({args[0]}, {args[1]}, {args[2]}, {args[3]})")
        
        code.extend([
            "",
            "if __name__ == '__main__':",
            "    main()",
        ])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(code))
        
        print(f"已保存脚本到 {filename}")
