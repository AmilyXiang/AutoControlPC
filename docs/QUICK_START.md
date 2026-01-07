# AutoControlPC 快速开始指南

## ⚡ 5分钟快速上手

### 第1步：环境准备

```bash
# 1. 克隆或下载项目
cd AutoControlPC

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证安装
python -c "import pyautogui; print('✓ 安装成功')"
```

### 第2步：运行第一个自动化流程

创建文件 `my_first_test.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testcases>
    <testcase name="我的第一个测试">
        <!-- 打开记事本 -->
        <step type="keyboard" action="press_key" content="win" />
        <step type="wait" action="sleep" content="1" />
        <step type="keyboard" action="type_text" content="notepad" />
        <step type="keyboard" action="press_key" content="enter" />
        <step type="wait" action="sleep" content="2" />
        
        <!-- 最大化窗口 -->
        <step type="window" action="maximize_top" content="" />
        <step type="wait" action="sleep" content="1" />
        
        <!-- 输入文本 -->
        <step type="keyboard" action="type_text" content="Hello AutoControlPC!" />
        <step type="wait" action="sleep" content="2" />
    </testcase>
</testcases>
```

运行：
```bash
python run_testcase.py my_first_test.xml "我的第一个测试"
```

### 第3步：测试P2P网络

创建文件 `my_network_test.py`：

```python
from p2p_network import P2PNetwork
from network_event import NetworkEvent
import time
import threading

# 创建接收端
receiver = P2PNetwork(local_port=9998)
receiver._start_server()

# 创建发送端
sender = P2PNetwork(local_port=9999)
sender.init('127.0.0.1', 9998)

time.sleep(1)

# 在后台接收消息
def receive():
    msg = receiver.receive(timeout=5)
    if msg:
        print(f"✓ 收到消息: {msg['event']}")
    else:
        print("✗ 接收超时")

threading.Thread(target=receive, daemon=True).start()

# 发送消息
print("发送消息...")
sender.send(NetworkEvent.READY, {'status': 'test'})

time.sleep(2)
sender.stop()
receiver.stop()
```

运行：
```bash
python my_network_test.py
```

## 📋 XML testcase 常用操作

### 键盘操作

```xml
<!-- 按键 -->
<step type="keyboard" action="press_key" content="enter" />

<!-- 输入文本 -->
<step type="keyboard" action="type_text" content="hello" />

<!-- 组合键 -->
<step type="keyboard" action="hotkey" content="ctrl+c" />
```

### 鼠标操作

```xml
<!-- 移动鼠标 -->
<step type="mouse" action="move_mouse" content="100,200" />

<!-- 点击 -->
<step type="mouse" action="click" content="left" />

<!-- 右键 -->
<step type="mouse" action="click" content="right" />
```

### 等待

```xml
<!-- 等待2秒 -->
<step type="wait" action="sleep" content="2" />
```

### 窗口操作

```xml
<!-- 最大化最上层窗口 -->
<step type="window" action="maximize_top" content="" />
```

### 音频操作

```xml
<!-- 播放音频 -->
<step type="audio" action="play" content="music.wav" device="0" />

<!-- 异步播放（不阻塞） -->
<step type="audio" action="play_async" content="music.wav" device="0" />

<!-- 录音 -->
<step type="audio" action="record" content="output.wav" device="0" duration="5" />

<!-- 异步录音 -->
<step type="audio" action="record_async" content="output.wav" device="0" duration="5" />
```

### 网络操作

```xml
<!-- 初始化网络（连接到对端） -->
<step type="network" action="init" content="192.168.1.100:9998" local_port="9998" />

<!-- 初始化网络（仅启动服务器） -->
<step type="network" action="init" content="" local_port="9998" />

<!-- 发送消息 -->
<step type="network" action="send" content="call_start" data="{&quot;phone&quot;: &quot;188&quot;}" />

<!-- 接收消息（阻塞等待） -->
<step type="network" action="receive" content="call_answer" timeout="30" />

<!-- 停止网络 -->
<step type="network" action="stop" content="" />
```

## 🎯 常见场景

### 场景1：自动化UI测试

```bash
python run_testcase.py testcase/my_ui_test.xml
```

### 场景2：音频播放和录制

```bash
python run_testcase.py testcase/audio_test.xml
```

### 场景3：两台PC Call/Answer通话

PC-1和PC-2都装上AutoControlPC后：

```bash
python p2p_testcase_coordinator.py \
  127.0.0.1 9999 \
  192.168.1.101 9999 \
  testcase/p2p_network_demo.xml "Call端流程" \
  testcase/p2p_network_demo.xml "Answer端流程"
```

## 🔍 查看可用网络事件

```bash
python network_event.py
```

输出：
```
可用的网络事件类型:
  init                 = init
  stop                 = stop
  ready                = ready
  call_start           = call_start
  call_answer          = call_answer
  call_end             = call_end
  ...
```

## 🐛 调试技巧

### 查看详细日志

在 `run_testcase.py` 中添加：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 查看可用音频设备

```bash
python audio_recorder.py list
```

### 查看鼠标位置

```python
import pyautogui
print(pyautogui.position())
```

## 📞 需要帮助？

1. 查看完整文档：[P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md)
2. 查看示例用例：`testcase/` 目录
3. 检查报错日志

## ✅ 验证清单

- [ ] Python 3.8+ 已安装
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] 能运行 `python run_testcase.py testcase/p2p_network_demo.xml`
- [ ] 网络测试成功
- [ ] 创建了第一个自定义 testcase

完成以上步骤，你就可以开始使用AutoControlPC了！🎉
