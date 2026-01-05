# AutoControlPC

一个用于 Windows 自动化的 Python 项目，支持鼠标、键盘控制及 OCR 识别，适合批量 UI 自动化测试。

## 主要功能

- **鼠标控制**：移动、点击、拖拽、滚轮等操作
- **键盘控制**：输入文本、按键、组合键等
- **OCR识别**：基于 easyocr，支持模糊匹配，自动定位并点击屏幕文本
- **输入法检测**：通过 OCR 识别右下角“中/英”状态，自动切换输入法
- **图标检测**：基于OpenCV模板匹配，支持灰度图精准检测图标并自动移动鼠标
- **窗口操作**：支持最大化最上层窗口
- **测试用例驱动**：支持 XML 测试用例批量自动执行，支持自定义多种自动化动作

## 安装

1. 创建虚拟环境
	```bash
	python -m venv .venv
	.venv\Scripts\activate
	```
2. 安装依赖
	```bash
	pip install -r requirements.txt
	```

## 文件结构

- run_testcase.py         通用测试用例执行器，自动解析并执行 XML 测试步骤
- ocr_tool.py             OCR工具，支持模糊匹配和区域识别
- auto_controller.py      鼠标键盘自动化控制器
- keyboard_controller.py  键盘底层控制
- mouse_controller.py     鼠标底层控制
- testcase/               测试用例 XML 文件目录
- requirements.txt        依赖包列表
- GUIDE.md                项目文件说明
- README.md               项目简介与用法

## 快速开始

1. 编写 XML 测试用例（见 testcase/rainbow_main.xml 示例）
2. 运行自动化脚本：
	```bash
	python run_testcase.py testcase/rainbow_main.xml
	```


## 用例示例

```xml
<!-- OCR查找并点击 -->
<step type="ocr" action="find_and_click" content="Audio" />
<!-- 输入法检测与切换 -->
<step type="check" action="input_method" content="英语(美国)" />
<!-- 最大化最上层窗口 -->
<step type="window" action="maximize_top" />
<!-- 图标检测并移动鼠标到第一个匹配位置 -->
<step type="icon" action="find_and_move" content="png/1.jpg" />
```

> 程序结束后会自动清理所有 debug_match_*.png 调试图片。

## 说明

- 输入法检测采用 OCR 识别右下角“中/英”状态，自动切换。
- OCR 支持模糊匹配，提升识别容错率。
- 图标检测采用灰度模板匹配，适合像素级一致的静态图标。
- 支持窗口最大化等常用窗口操作。
- 可扩展更多自动化步骤和断言。
- 所有 debug_match_*.png 调试图片会在自动化流程结束后自动清理。
ac.type_text('notepad', interval=0.1)
time.sleep(0.3)

# Press Enter
ac.tap_key('enter')
time.sleep(1)

# Move mouse and click
ac.move_mouse(500, 400, duration=0.5)
time.sleep(0.2)
ac.left_click()

# Type some text
ac.type_text('Hello AutoControlPC!', interval=0.05)
```

### OCR-Based Automation

The library includes advanced OCR capabilities to find and interact with UI elements:

```python
from PIL import ImageGrab
import auto_controller as ac
import easyocr

# Take screenshot
screenshot = ImageGrab.grab()

# Find text position using OCR
# (See run_rainbow_ocr.py for complete example)
```

## Core Modules

### auto_controller.py
Main API providing simplified functions:
- `move_mouse(x, y, duration=0)` - Move mouse to coordinates
- `left_click(duration=0)` - Click left mouse button
- `type_text(text, interval=0.05)` - Type text with delays between characters
- `key_combination(keys)` - Press key combinations (e.g., 'ctrl+c')
- `tap_key(key)` - Tap a single key
- `get_mouse_position()` - Get current mouse position
- `scroll_mouse(clicks, direction='down')` - Scroll mouse wheel

### mouse_controller.py
Low-level mouse operations via `MouseController` class

### keyboard_controller.py
Keyboard operations with support for 50+ special keys:
- Function keys (F1-F12)
- Modifiers (Shift, Ctrl, Alt, Win)
- Navigation (Up, Down, Left, Right, Enter, etc.)

### advanced_features.py
Advanced features:
- Action recording and playback
- Script building utilities

## Example Scripts

### run_rainbow_ocr.py
Automated workflow demonstrating:
1. Launch Rainbow application via Win+R
2. Input text "cui ji"
3. Find "Cui Ji" button using OCR
4. Click the button
5. Find and click "Call" button
6. Find and click "Audio" button

Run with:
```bash
python run_rainbow_ocr.py
```

## Requirements

- Python 3.12+
- Windows OS
- pynput 1.7.6
- opencv-python
- Pillow (PIL)
- numpy
- easyocr
- torch (dependency of easyocr)

See `requirements.txt` for complete list.

## Key Features

### Mouse Operations
- Smooth movement with configurable duration
- Left/right click, double-click
- Drag operations
- Scroll wheel support
- Position querying

### Keyboard Operations
- Text input with inter-character delays (prevents typing too fast)
- Single key taps
- Key combinations (Ctrl+C, Alt+Tab, Win+D, etc.)
- Special key support (50+ keys)

### OCR Integration
- Find text on screen using EasyOCR
- Case-sensitive and case-insensitive matching
- Partial text matching
- Automatic center coordinate calculation
- Multiple matching strategies

## Testing

Run tests with:
```bash
python test.py
```

## File Structure

```
AutoControlPC/
├── auto_controller.py          # Main API
├── mouse_controller.py          # Mouse operations
├── keyboard_controller.py       # Keyboard operations
├── advanced_features.py         # Advanced features
├── run_rainbow_ocr.py          # Example automation script
├── test.py                      # Test suite
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Usage Tips

1. **Timing**: Add `time.sleep()` delays between operations to allow UI to respond
2. **Focus**: Click on the target window first to ensure it has focus
3. **OCR**: First-run OCR initialization downloads models (~100MB), takes 30-60 seconds
4. **Coordinates**: Use `mouse_tracker.py` equivalent to find target coordinates
5. **Errors**: Catch KeyboardInterrupt to allow stopping long-running scripts

## Troubleshooting

### OCR Model Download
- First-run OCR may take 30-60 seconds as it downloads models
- Models are cached after first run for faster subsequent execution

### Keyboard Input Issues
- Ensure target application has focus
- Use longer delays between key presses for slow applications
- Some applications may require special handling

### Mouse Precision
- Use `duration` parameter in `move_mouse()` for smooth movement
- Some applications may require delays after moving mouse before clicking

## License

AutoControlPC - Windows PC Automation Library

## Author

Developed for automated testing and task automation on Windows platforms.
