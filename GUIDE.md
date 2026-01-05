

# 项目文件说明（AutoControlPC）

## 主要自动化脚本
- **run_testcase.py**
  - 通用测试用例执行器。
  - 解析 testcase 文件夹下的 xml 测试用例，自动执行键盘、鼠标、OCR、输入法检查等步骤。
  - 输入法检测采用 OCR 识别右下角“中/英”状态，自动切换。
  - 支持自定义测试流程，便于批量自动化测试。
  - 新增支持窗口最大化、图标检测等自动化动作。
## 图标检测与窗口操作

- **icon_detector.py**
  - 基于OpenCV模板匹配，支持灰度图精准检测图标。
  - 提供 find_icons 方法，返回所有匹配位置。
  - 可在XML用例中通过 `<step type="icon" action="find_and_move" content="png/1.jpg" />` 自动检测并移动鼠标。
- **window_util.py**
  - 支持最大化当前最上层窗口。
  - 可在XML用例中通过 `<step type="window" action="maximize_top" />` 实现。

## OCR与输入法工具
- **ocr_tool.py**
  - 独立 OCR 工具，基于 easyocr，支持模糊匹配。
  - 提供 find_text_position 方法，支持屏幕任意区域文本识别与定位。
- **input_method_util.py**
  - 输入法布局码检测工具（已不推荐，建议用 OCR 方案）。

## 控制器模块
- **auto_controller.py**
  - 自动化控制器，统一封装鼠标和键盘操作。
  - 提供如 move_mouse、type_text、left_click 等常用自动化 API。
- **keyboard_controller.py**
  - 键盘控制底层实现。
  - 支持按键、输入文本、组合键等操作。
- **mouse_controller.py**
  - 鼠标控制底层实现。
  - 支持鼠标移动、点击、拖拽、滚轮等操作。

## 测试用例与配置
- **testcase/**
  - 存放所有自动化测试用例 xml 文件。
  - 例如 rainbow_main.xml 描述了完整的主流程自动化步骤。
  - 支持如下 step 类型：
    - `keyboard`：键盘输入、按键
    - `mouse`：鼠标移动、点击
    - `ocr`：OCR查找并点击
    - `check`：输入法检测与切换
    - `wait`：等待
    - `window`：窗口操作（如最大化）
    - `icon`：图标检测与自动移动鼠标

## 其他
- **requirements.txt**
  - Python 依赖包列表。
- **GUIDE.md**
  - 项目文件说明（本文件）。
- **README.md**
  - 项目简介与使用说明。


---
> 程序结束后会自动清理所有 debug_match_*.png 调试图片。
如需添加新测试用例，只需在 testcase 文件夹下新增 xml 文件，并用 run_testcase.py 指定执行即可。

---
如需添加新测试用例，只需在testcase文件夹下新增xml文件，并用run_testcase.py指定执行即可。
