
# 项目文件说明（AutoControlPC）

## 主要自动化脚本
- **run_testcase.py**
  - 通用测试用例执行器。
  - 解析 testcase 文件夹下的 xml 测试用例，自动执行键盘、鼠标、OCR、输入法检查等步骤。
  - 输入法检测采用 OCR 识别右下角“中/英”状态，自动切换。
  - 支持自定义测试流程，便于批量自动化测试。

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

## 其他
- **requirements.txt**
  - Python 依赖包列表。
- **GUIDE.md**
  - 项目文件说明（本文件）。
- **README.md**
  - 项目简介与使用说明。

---
如需添加新测试用例，只需在 testcase 文件夹下新增 xml 文件，并用 run_testcase.py 指定执行即可。

---
如需添加新测试用例，只需在testcase文件夹下新增xml文件，并用run_testcase.py指定执行即可。
