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
- **多设备播放**：支持指定声卡设备播放音频（同步/异步）
- **多设备录音**：支持指定声卡设备录音
- **同步音频**：两台PC同时播放和录音，支持跨PC音频转接

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
    <!-- 播放音频到设备0 -->
    <step type="audio" action="play" content="audio/sound.wav" device="0" />
    
    <!-- 异步播放到设备1 -->
    <step type="audio" action="play_async" content="audio/music.wav" device="1" />
    
    <!-- 从设备24录音10秒 -->
    <step type="audio" action="record" content="output/record.wav" 
          device="24" duration="10" />
    
    <!-- 等待1秒 -->
    <step type="wait" content="1" />
</testcase>
```

### 2. P2P网络通信
```xml
<!-- PC-A：发起通话 -->
<testcase name="P2P_Caller" description="发起端">
    <!-- 初始化P2P，连接到PC-B (192.168.1.102:9998) -->
    <step type="network" action="init" content="192.168.1.102:9998" 
          local_port="9998" />
    
    <!-- 发送"准备就绪"事件 -->
    <step type="network" action="send" content="ready" 
          data="{&quot;status&quot;: &quot;online&quot;}" />
    
    <!-- 发送"发起通话"事件 -->
    <step type="network" action="send" content="call_start" 
          data="{&quot;caller&quot;: &quot;Alice&quot;}" />
    
    <!-- 等待对端"接听"事件（超时30秒） -->
    <step type="network" action="receive" content="call_answer" 
          timeout="30" />
    
    <!-- 关闭网络连接 -->
    <step type="network" action="stop" content="" />
</testcase>

<!-- PC-B：接听通话 -->
<testcase name="P2P_Receiver" description="接听端">
    <!-- 初始化P2P，监听本地9999端口，不主动连接 -->
    <step type="network" action="init" content="" local_port="9999" />
    
    <!-- 等待"准备就绪"事件 -->
    <step type="network" action="receive" content="ready" timeout="30" />
    
    <!-- 等待"发起通话"事件 -->
    <step type="network" action="receive" content="call_start" timeout="30" />
    
    <!-- 发送"接听"事件 -->
    <step type="network" action="send" content="call_answer" 
          data="{&quot;receiver&quot;: &quot;Bob&quot;}" />
    
    <!-- 关闭网络连接 -->
    <step type="network" action="stop" content="" />
</testcase>
```

### 3. UI自动化
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

## 网络事件类型

P2P通信支持的预定义事件（可扩展）：

```python
class NetworkEvent(Enum):
    INIT = "init"              # 连接初始化
    STOP = "stop"              # 停止连接
    READY = "ready"            # 就绪信号
    CALL_START = "call_start"  # 发起通话
    CALL_ANSWER = "call_answer"# 接听通话
    CALL_END = "call_end"      # 通话结束
    AUDIO_START = "audio_start"# 音频开始
    AUDIO_STOP = "audio_stop"  # 音频停止
    VIDEO_START = "video_start"# 视频开始
    VIDEO_STOP = "video_stop"  # 视频停止
    MESSAGE = "message"        # 自定义消息
    DATA = "data"              # 数据传输
    CUSTOM = "custom"          # 用户自定义
```

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
