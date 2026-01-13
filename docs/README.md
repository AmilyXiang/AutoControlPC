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

查看 [PROJECT_SETUP.md](PROJECT_SETUP.md) 获取详细的安装检查清单和故障排除指南。

## 项目结构

```
AutoControlPC/
├── run_testcase.py              # XML测试用例执行引擎
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
├── testcase/                     # 测试用例目录
│   ├── netease_music.xml         # 音乐播放测试
│   └── p2p_network_demo.xml      # P2P通信测试
├── png/                          # 图标素材目录
├── QUICK_START.md                # 快速开始教程
├── INSTALL.md                    # 安装检查清单
├── P2P_NETWORK_GUIDE.md          # P2P详细文档
├── requirements.txt              # Python依赖
├── setup.py                      # 包配置文件
└── README.md                     # 本文件
```

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
    
    <!-- 等待1秒 -->
    <step type="wait" content="1" />
</testcase>
```

**音频操作参数说明**：
- `device_id` / `device`：指定音频设备ID（可通过 `python audio_player.py list` 查看）
- `time`：（仅限 play/play_async）播放时长（秒），不设置则播放到文件结束
- `duration`：（仅限 record/record_async）录音时长（秒）

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
    <!-- 点击坐标(100,100) -->
    <step type="mouse" action="click" x="100" y="100" />
    
    <!-- 输入文本 -->
    <step type="keyboard" action="input" content="Hello World" />
    
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
| keyboard | input | 输入文本 |
| keyboard | key | 按下单个按键 |
| mouse | click | 点击 (支持left/right/double) |
| mouse | move | 移动鼠标 |
| mouse | drag | 拖拽 |
| mouse | scroll | 滚动 |
| audio | play | 同步播放音频 |
| audio | play_async | 异步播放音频 |
| audio | record | 录音 |
| network | init | 初始化P2P连接 |
| network | send | 发送网络事件 |
| network | receive | 接收网络事件 |
| network | stop | 停止网络连接 |
| ocr | find_and_click | OCR定位并点击 |
| icon | find_and_move | 图标检测并移动鼠标 |
| window | maximize_top | 最大化顶部窗口 |
| wait | - | 延时等待 |

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
A：某些音频库需要额外配置。查看 [PROJECT_SETUP.md](PROJECT_SETUP.md) 的Windows特定步骤。

**Q：如何自定义网络事件？**
A：在 `network_event.py` 中的 NetworkEvent 枚举类中添加新事件，然后在XML中使用。

## 文档

- [QUICK_START.md](QUICK_START.md) - 5分钟快速上手
- [PROJECT_SETUP.md](PROJECT_SETUP.md) - 安装配置和故障排除
- [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md) - P2P网络详细文档
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
4. 参考 [PROJECT_SETUP.md](PROJECT_SETUP.md) 的常见问题部分
