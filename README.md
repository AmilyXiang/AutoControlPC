# AutoControlPC

A comprehensive Python automation library for controlling Windows PC with mouse and keyboard, featuring advanced OCR-based UI interaction capabilities.

## Features

- **Mouse Control**: Move, click, drag, scroll operations
- **Keyboard Control**: Type text, press keys, key combinations (Ctrl+C, Win+V, etc.)
- **OCR Recognition**: Find and interact with on-screen text using EasyOCR
- **Automation Scripts**: Pre-built scripts for complex workflows
- **Cross-platform**: Works with Python 3.12+ on Windows

## Installation

### 1. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
import auto_controller as ac
import time

# Press Win key to open run dialog
ac.tap_key('win')
time.sleep(0.5)

# Type text
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
