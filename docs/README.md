# AutoControlPC - 多PC自动化测试框架

一个功能强大的 Python 自动化框架，支持多PC协同测试。采用 **P2P（点对点）网络架构**实现两台PC的对等通信，无需中央服务器。支持 UI 自动化、音频操作、网络协调，适合复杂的场景自动化测试（如电话通话模拟、多端同步测试等）。

## 核心功能

### UI 自动化
- **鼠标控制**：移动、点击、拖拽、滚轮等操作
- **键盘控制**：输入文本、按键、组合键等
- **窗口操作**：最大化、置顶、查询窗口信息
- **OCR识别**：基于 PaddleOCR，自动定位并点击屏幕文本
- **图标检测**：基于OpenCV模板匹配，精准检测图标并交互

### 音频操作
- **多设备播放**：支持指定声卡设备播放音频（同步/异步），可设置播放时长
- **多设备录音**：支持指定声卡设备录音，支持异步录音和停止录音
- **声音检测**：基于 RMS/SNR 的音频有声/静音检测，支持断言验证
- **同步音频**：两台PC同时播放和录音，支持跨PC音频转接
- **播放控制**：可设置 `time` 参数限制播放时长，不设置则播放到文件结束

### 网络协调（P2P）
- **对等通信**：两台PC双向通信，无中央服务器
- **事件驱动**：基于 NetworkEvent 枚举的类型安全事件系统
- **自动重连**：网络中断时自动重新连接
- **消息队列**：线程安全的异步消息处理

### XML驱动测试
- **声明式用例**：XML格式定义测试步骤
- **多种操作**：键盘、鼠标、音频、网络、窗口、OCR、图标、延时
- **灵活配置**：设备选择、超时设置、数据传递
- **批量执行**：支持指定目录或通配符依次运行多个 XML 文件
- **HTML 测试报告**：执行完成后自动生成 `testreport/report.html`，含 PASS/FAIL 汇总和失败原因

### DECT自动化（相机 + 机械）
- **多设备支持**：通过 `device` 属性同时控制多套 DECT 设备（移动臂 + 摄像头）
- **集中配置**：设备串口、摄像头、分机号等统一在 `dect/config/devices.json` 管理
- **变量引用**：XML 用例中用 `{device.X.field}` 引用任意设备配置项
- **DECT按键操作**：支持拨号、摘机、挂机、回原点等动作
- **视觉识别**：YOLO + PaddleOCR 识别屏幕文字和图标
- **资源全局缓存**：相机、YOLO模型、PaddleOCR模型、串口连接在进程生命周期内只初始化一次，多个 XML case 之间自动复用，无需重复加载
- **摄像头共享**：多设备配置相同 `camera_index` 时自动共用，不会重复打开
- **调试图片自动保存**：每次抓图会保存到 `png/debug/capture_<timestamp>.png`
- **异常保护**：case 执行中途异常时，自动尝试所有设备机械回原点

## 快速开始

### 1. 安装依赖
```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

> **Windows 注意**：pywin32 安装后需要运行：
> ```bash
> python -m pywin32_postinstall -install
> ```

### 2. 运行第一个测试（5分钟）

查看 [QUICK_START.md](QUICK_START.md) 了解详细的入门教程。

最简单的例子：单机P2P测试
```bash
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

### 3. 配置两PC场景

详见 [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md)：
1. 获取两台PC的IP地址：`ipconfig` 或 `ifconfig`
2. 分别运行两个测试，配置正确的对端IP和端口
3. 网络事件会自动同步

## 安装验证

查看 [QUICK_GUIDE.md](QUICK_GUIDE.md) 获取安装检查清单和故障排除建议。

## 项目结构

```
AutoControlPC/
├── run_testcase.py              # XML测试用例执行引擎（支持单文件/目录/通配符）
├── test_report.py               # HTML 测试报告生成器
├── dect_controller.py           # DECT 控制器（多设备支持）
├── audio_voice_detector.py      # 音频有声/静音检测
├── network_event.py              # P2P网络事件定义
├── p2p_network.py                # P2P网络通信实现
├── p2p_testcase_coordinator.py   # 多PC测试协调器
├── auto_controller.py            # UI自动化核心
├── keyboard_controller.py        # 键盘控制
├── mouse_controller.py           # 鼠标控制
├── audio_player.py               # 音频播放（支持多设备）
├── audio_recorder.py             # 音频录音（支持多设备）
├── ocr_tool.py                   # OCR文本识别
├── icon_detector.py              # 图标检测
├── window_util.py                # 窗口操作
├── input_method_util.py          # 输入法检测
├── dect/                         # DECT 模块
│   ├── config/                   # 设备配置
│   │   ├── devices.json          # 多设备配置（串口、摄像头、分机号等）
│   │   └── settings.py           # DeviceConfig dataclass + 加载逻辑
│   ├── image/                    # 摄像头、视觉分析
│   └── move/                     # 运动控制
│       ├── setting.py            # 运动参数（速度、加速度、按压深度等）
│       └── layout/               # 按键坐标配置（8262.json, 8254.json 等）
├── testcase/                     # 测试用例目录
│   ├── DECT/                     # DECT 相关用例
│   ├── netease_music.xml         # 音乐播放测试
│   └── p2p_network_demo.xml      # P2P通信测试
├── testreport/                   # 测试报告输出目录
├── png/                          # 图标素材目录
├── docs/                         # 文档目录
├── requirements.txt              # Python依赖
└── setup.py                      # 包配置文件
```

## DECT 多设备配置

### 设备配置文件

设备硬件信息集中管理在 `dect/config/devices.json`：

```json
{
    "1": {
        "com_port": "COM3",
        "camera_index": 0,
        "ext_number": "20001"
    },
    "2": {
        "com_port": "COM5",
        "camera_index": 1,
        "ext_number": "20002"
    }
}
```

新增设备只需在此文件中添加一条记录。运动参数（速度、加速度、按压深度等）在 `dect/move/setting.py` 中配置。

### 多设备用例

通过 `device` 属性指定操作哪套设备（默认为 `"1"`）：

```xml
<testcase name="DECT_双设备通话测试">
    <!-- 初始化两套设备 -->
    <step type="dect" action="init" content="8262" device="1" />
    <step type="dect" action="init" content="8262" device="2" />

    <!-- 设备1 拨打 设备2 的分机号 -->
    <step type="dect" action="dial_number" content="{device.2.ext_number}" device="1" />
    <step type="dect" action="press_key" content="offhook" device="1" />

    <!-- 设备2 验证来电显示并接听 -->
    <step type="dect" action="verify_screen" content='{"text": "{device.1.ext_number}"}' device="2" />
    <step type="dect" action="press_key" content="offhook" device="2" />

    <!-- 双方挂机 -->
    <step type="dect" action="press_key" content="onhook" device="1" />
    <step type="dect" action="press_key" content="onhook" device="2" />

    <!-- 回原点并关闭 -->
    <step type="dect" action="origin" device="1" />
    <step type="dect" action="origin" device="2" />
    <step type="dect" action="close" device="1" />
    <step type="dect" action="close" device="2" />
</testcase>
```

### 变量引用语法

XML 用例中可使用 `{device.X.field}` 引用任意设备的配置项，适用于所有步骤类型：

| 变量 | 说明 |
|------|------|
| `{device.1.ext_number}` | 设备1的分机号 |
| `{device.2.com_port}` | 设备2的串口 |
| `{device.1.camera_index}` | 设备1的摄像头编号 |

变量在运行时自动替换，`devices.json` 中新增的字段无需改代码即可引用。

## DECT用例快速运行

```bash
# 运行单个用例文件
python run_testcase.py testcase/dect_8262_dial_test.xml

# 运行整个目录下的所有用例
python run_testcase.py testcase/DECT/

# 使用通配符
python run_testcase.py testcase/DECT/*.xml

# 运行目录下指定名称的用例
python run_testcase.py testcase/DECT/ MyCaseName
```

执行完成后自动生成报告：`testreport/report.html`

调试截图目录：`png/debug/`

### DECT 长按示例
```xml
<testcase name="DECT_LongPress_Test" description="DECT long press example">
      <step type="dect" action="init" content="8262" />

      <!-- Long press OK key for the configured long-press duration -->
      <step type="dect" action="press_key" content="ok" press_type="long" />

      <step type="dect" action="origin" />
      <step type="dect" action="close" />
</testcase>
```

`dect press_key` supports:
- `press_type="short"`：default short press
- `press_type="long"`：long press, duration controlled by `dect/move/setting.py`

### DECT 整串拨号示例
```xml
<testcase name="DECT_DialNumber_Test" description="DECT dial full number in one step">
      <step type="dect" action="init" content="8262" />

      <!-- Dial 10000 with 0.3s interval between each key -->
      <step type="dect" action="dial_number" content="10000" interval="0.3" />

      <!-- Verify the dialed number on screen -->
      <step type="dect" action="verify_screen" content='{"text": "10000"}' />

      <step type="dect" action="origin" />
      <step type="dect" action="close" />
</testcase>
```

`dect dial_number` supports:
- `content`：整串号码，支持字符 `0-9`、`*`、`#`
- `interval="0.5"`：按键间隔秒数，默认 0.5s

## XML测试用例示例

### 1. 音频操作（多设备）
```xml
<testcase name="AudioTest" description="多设备同时播放和录音">
    <!-- 播放音频到设备4，播放完整文件 -->
    <step type="audio" action="play" content="testAudioFile/sine_40.wav" device_id="4" />
    
    <!-- 异步播放到设备25，仅播放3秒 -->
    <step type="audio" action="play_async" content="testAudioFile/sine_40.wav" device_id="25" time="3" />
    
    <!-- 异步录音10秒（从设备24） -->
    <step type="audio" action="record_async" content="testAudioFile/recorded.wav" 
          device_id="24" duration="10" />
    
    <!-- 停止正在进行的录音 -->
    <step type="audio" action="stop_record" />
    
    <!-- 检测录音文件是否有声音（期望有声音，静音则报错） -->
    <step type="audio" action="check_voice" content="testAudioFile/recorded.wav" expect="true" />
    
    <!-- 检测录音文件应为静音（自定义阈值） -->
    <step type="audio" action="check_voice" content="testAudioFile/recorded.wav"
          expect="false" rms_threshold="0.005" snr_threshold="2.5" />
    
    <!-- 等待1秒 -->
    <step type="wait" content="1" />
</testcase>
```

**音频操作参数说明**：
- `device_id` / `device`：指定音频设备ID（可通过 `python audio_player.py list` 查看）
- `time`：（仅限 play/play_async）播放时长（秒），不设置则播放到文件结束
- `duration`：（仅限 record/record_async）录音时长（秒）
- `expect`：（仅限 check_voice）期望结果，`true` 表示期望有声音，`false` 表示期望静音；不设置则只打印结果不做断言
- `rms_threshold`：（仅限 check_voice）RMS能量阈值，默认 `0.001`
- `snr_threshold`：（仅限 check_voice）信噪比阈值，默认 `3.0`

### 2. P2P网络通信
```xml
<!-- PC-A：发起通话 -->
<testcase name="P2P_Caller" description="发起端">
    <!-- 初始化P2P，连接到PC-B (192.168.1.102:9999) -->
    <step type="network" action="init" content="192.168.1.102:9999" 
          local_port="9998" />
    
    <!-- 发送"准备就绪"事件 -->
    <step type="network" action="send" content="ready" 
          data="{&quot;status&quot;: &quot;online&quot;}" />
    
    <!-- 发送"开始播放音频"事件 -->
    <step type="network" action="send" content="audio_play_start" 
          data="{&quot;file&quot;: &quot;sine_40.wav&quot;}" />
    
    <!-- 播放音频 -->
    <step type="audio" action="play" content="testAudioFile/sine_40.wav" 
          device_id="4" />
    
    <!-- 发送"播放完成"事件 -->
    <step type="network" action="send" content="audio_play_end" 
          data="{&quot;file&quot;: &quot;sine_40.wav&quot;}" />
    
    <!-- 等待对端"录音停止"事件 -->
    <step type="network" action="receive" content="record_stopped" 
          timeout="30" />
    
    <!-- 关闭网络连接 -->
    <step type="network" action="stop" content="" />
</testcase>

<!-- PC-B：接听通话 -->
<testcase name="P2P_Receiver" description="接听端">
    <!-- 初始化P2P，监听本地9999端口 -->
    <step type="network" action="init" content="192.168.1.101:9998" 
          local_port="9999" />
    
    <!-- 等待"准备就绪"事件 -->
    <step type="network" action="receive" content="ready" timeout="30" />
    
    <!-- 等待"开始播放音频"事件 -->
    <step type="network" action="receive" content="audio_play_start" timeout="30" />
    
    <!-- 异步开始录音 -->
    <step type="audio" action="record_async" content="testAudioFile/record.wav" 
          device_id="24" duration="60" />
    
    <!-- 等待"播放完成"事件 -->
    <step type="network" action="receive" content="audio_play_end" timeout="30" />
    
    <!-- 停止录音 -->
    <step type="audio" action="stop_record" />
    
    <!-- 发送"录音停止"事件给对端 -->
    <step type="network" action="send" content="record_stopped" 
          data="{&quot;status&quot;: &quot;stopped&quot;}" />
</testcase>
```

**网络事件清单**：
- `ready` - 就绪信号
- `call_start` / `call_answer` - 通话相关
- `audio_play_start` / `audio_play_end` - 音频播放控制
- `record_stopped` - 录音停止通知

## 支持的操作类型
```xml
<testcase name="UITest" description="UI操作示例">
      <!-- 键盘按键 -->
      <step type="keyboard" action="press_key" content="enter" />
    
      <!-- 键盘输入文本 -->
      <step type="keyboard" action="type_text" content="Hello World" />
    
      <!-- 鼠标移动到坐标 -->
      <step type="mouse" action="move_mouse" content="100,100" />
    
      <!-- 鼠标左键点击 -->
      <step type="mouse" action="click" content="left" />
    
    <!-- OCR查找并点击 -->
    <step type="ocr" action="find_and_click" content="确定" />
    
    <!-- 最大化顶部窗口 -->
    <step type="window" action="maximize_top" />
    
    <!-- 图标检测 -->
    <step type="icon" action="find_and_move" content="png/button.jpg" />
    
    <!-- 等待2秒 -->
    <step type="wait" content="2" />
</testcase>
```

## 支持的操作类型

| 操作类型 | 动作 | 说明 |
|---------|-----|------|
| keyboard | press_key | 按下单个按键 |
| keyboard | type_text | 输入文本（支持 `{now}` 动态时间变量） |
| mouse | move_mouse | 移动鼠标到 `x,y` 坐标 |
| mouse | click | 点击鼠标（`left`/`right`） |
| audio | play | 同步播放音频 |
| audio | play_async | 异步播放音频 |
| audio | record | 同步录音 |
| audio | record_async | 异步录音 |
| audio | stop_record | 停止录音 |
| audio | check_voice | 检测音频是否有声音（支持 `expect` 断言） |
| network | init | 初始化P2P连接 |
| network | send | 发送网络事件 |
| network | receive | 接收网络事件（支持 `timeout`/`check`） |
| network | stop | 停止网络连接 |
| check | input_method | 检查并切换输入法状态 |
| process | close | 关闭指定进程 |
| process | runbat | 运行 bat 脚本 |
| clipboard | save | 保存剪贴板（txt/csv） |
| wait | sleep | 延时等待 |
| ocr | find_and_click | OCR定位并点击 |
| window | maximize_top | 最大化顶部窗口 |
| icon | find_and_move | 图标检测并移动鼠标 |
| dect | init | 初始化 DECT 控制器（支持 `device` 指定设备） |
| dect | press_key | DECT 按键操作（支持 `press_type`） |
| dect | dial_number | 整串号码拨号（支持 `interval` 和 `{device.X.field}` 变量） |
| dect | verify_screen | 验证 DECT 屏幕内容（支持拼接匹配） |
| dect | capture | 仅抓图并分析 |
| dect | origin | 机械回原点 |
| dect | close | 断开控制器（资源保留供下一个 case 复用） |

## 网络事件系统

P2P通信支持预定义事件和自定义事件。接收消息时可通过 `check` 属性验证 `data` 内容：

```xml
<!-- 发送事件（附加JSON数据） -->
<step type="network" action="send" content="call_start" 
      data="{&quot;from&quot;: &quot;PC-A&quot;, &quot;phone&quot;: &quot;188xxxx&quot;}" />

<!-- 接收事件（可选验证data） -->
<step type="network" action="receive" content="call_answer" timeout="30" />

<!-- 接收事件并验证data内容 -->
<step type="network" action="receive" content="call_answer" timeout="30"
      check="{&quot;status&quot;: &quot;confirmed&quot;}" />
```

**常见事件类型：**
- `ready` - 就绪信号
- `call_start` - 发起通话
- `call_answer` - 接听通话
- `audio_play_start` - 音频开始
- `audio_play_end` - 音频结束
- `record_stopped` - 录音停止
- 自定义事件 - 任何字符串都可以用作事件名称

## 使用场景

### 场景1：单机P2P通信测试
在一台PC上同时运行两个进程，测试P2P双向通信：
```bash
# 此测试自动在单个进程内完成收发
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

### 场景2：两PC电话模拟
- PC-A（主叫方）：发送CALL_START，等待CALL_ANSWER
- PC-B（被叫方）：等待CALL_START，发送CALL_ANSWER
- 配合音频设备实现模拟通话

### 场景3：多设备音频转接
- PC-A播放到设备0，同时录音从设备24
- PC-B播放到设备1，同时录音从设备25
- 物理连接设备形成音频环路进行跨PC测试

## 常见问题

**Q：如何找到我的音频设备ID？**
A：运行以下命令查看所有音频设备：
```python
import sounddevice as sd
print(sd.query_devices())
```
找到你的设备并注意其ID号（通常是0-31之间的整数）。

**Q：网络连接失败怎么办？**
A：检查以下项目：
1. 两台PC在同一网络上
2. 防火墙未阻止Python程序
3. 确认对端IP地址正确：`ipconfig` 查看IPv4地址
4. 确认端口号未被占用

**Q：如何在Windows上安装PyAudio依赖？**
A：某些音频库需要额外配置。可先查看 [QUICK_GUIDE.md](QUICK_GUIDE.md) 的 Windows 说明。

**Q：DECT拍照后的图片保存在哪里？**
A：运行 DECT 视觉步骤时，原始抓图会自动保存到 `png/debug/capture_<timestamp>.png`。

**Q：报错后机械会不会停在半路？**
A：框架会在 case 异常时自动尝试所有已初始化设备执行回原点动作，降低机构停留风险。

**Q：跑多个 DECT XML case 时，每个 init 都会重新加载模型吗？**
A：不会。相机、YOLO、PaddleOCR、串口等资源在进程内全局缓存，首次 `init` 加载后，后续 `init` 直接复用（~0s）。`close` 只是断开控制器引用，不销毁资源。进程退出时自动调用 `destroy_all()` 释放全部硬件。

**Q：`close` 前需要手动 `origin` 吗？**
A：是的。`close` 不再自动回原点，请在 `close` 前显式写 `<step type="dect" action="origin" />`。

**Q：如何自定义网络事件？**
A：在 `network_event.py` 中的 NetworkEvent 枚举类中添加新事件，然后在XML中使用。

## 文档

- [QUICK_START.md](QUICK_START.md) - 5分钟快速上手
- [QUICK_GUIDE.md](QUICK_GUIDE.md) - 安装配置和故障排除
- [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md) - P2P网络详细文档
- [DECT_INTEGRATION_PLAN.md](DECT_INTEGRATION_PLAN.md) - DECT集成说明
- [GUIDE.md](GUIDE.md) - 模块参考

## 系统要求

- Python 3.8+
- Windows 7+ / Linux / macOS
- 网络连通（两PC场景）
- 足够的系统权限（某些OCR和图标检测需要）

## 许可证

MIT

## 支持

遇到问题？
1. 查看相应文档
2. 检查示例testcase文件
3. 查看控制台错误输出
4. 参考 [QUICK_GUIDE.md](QUICK_GUIDE.md) 的常见问题部分
