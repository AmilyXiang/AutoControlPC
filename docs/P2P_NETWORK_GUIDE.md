# P2P对等网络测试系统指南

## 核心概念

### 什么是P2P对等网络？

两个PC完全对等，**都是服务器，都是客户端**：
- 可以发送消息
- 可以接收消息
- 无需区分服务器端和客户端

### 事件系统

所有网络通信都基于**事件**，统一定义在 `network_event.py` 中：

| 事件 | 说明 | 示例 |
|------|------|------|
| `init` | 初始化网络 | XML中使用 `network init` |
| `stop` | 停止网络 | XML中使用 `network stop` |
| `ready` | 就绪信号 | 表示已准备好 |
| `call_start` | 开始呼叫 | Call端发送 |
| `call_ringing` | 来电铃声 | Answer端收到 |
| `call_answer` | 接听电话 | Answer端发送 |
| `call_end` | 结束通话 | 任意端发送 |
| `audio_start` | 开始音频 | 音频操作 |
| `message` | 通用消息 | 自定义消息 |
| `data` | 通用数据 | 自定义数据 |

## XML中使用网络

### 网络操作语法

```xml
<!-- 初始化网络 -->
<step type="network" action="init" content="peer_host:peer_port" local_port="9998" />

<!-- 发送事件 -->
<step type="network" action="send" content="event_name" data="{...}" />

<!-- 接收事件（阻塞等待） -->
<step type="network" action="receive" content="event_name" timeout="30" />

<!-- 停止网络 -->
<step type="network" action="stop" content="" />
```

### 参数说明

#### network init
```xml
<step type="network" action="init" content="192.168.1.101:9998" local_port="9998" />
```
- `content`: 对端地址和端口 (格式: `ip:port`)，为空时仅启动本地服务器
- `local_port`: 本地监听端口（默认9998）

#### network send
```xml
<step type="network" action="send" content="call_start" data="{&quot;from&quot;: &quot;pc1&quot;}" />
```
- `content`: 事件名称
- `data`: JSON格式的数据（可选）

#### network receive
```xml
<step type="network" action="receive" content="call_answer" timeout="30" />
```
- `content`: 等待的事件名称（为空表示接收任何事件）
- `timeout`: 等待超时时间（秒，默认30）

#### network stop
```xml
<step type="network" action="stop" content="" />
```
- 无需参数

## 快速开始

### 步骤1：启动两个PC的remote_executor服务器

**PC-1：**
```bash
python remote_executor.py
```

**PC-2：**
```bash
python remote_executor.py
```

### 步骤2：同步运行Call和Answer流程

```bash
python p2p_testcase_coordinator.py \
  127.0.0.1 9999 \
  192.168.1.101 9999 \
  testcase/p2p_network_demo.xml "Call端流程" \
  testcase/p2p_network_demo.xml "Answer端流程"
```

## 执行流程示意

### Call端（PC-1）和Answer端（PC-2）

```
时间线：

t0:  PC-1 init network (连接到PC-2:9998)
     PC-2 init network (监听9998，等待连接)

t1:  PC-2 send "ready"
     PC-1 receive "ready" 

t2:  PC-1 execute call UI
     PC-1 send "call_start" 
     
t3:  PC-2 receive "call_start"
     PC-2 execute answer UI
     PC-2 send "call_answer"

t4:  PC-1 receive "call_answer"
     PC-1和PC-2同时进行音频播放和录音

t5:  PC-1 send "call_end"
     PC-2 receive "call_end"

t6:  两端都 network stop
```

## 实际应用示例

### 完整的Call/Answer场景

**testcase/p2p_call_answer.xml:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testcases>
    <!-- Call端 -->
    <testcase name="Call端">
        <!-- 1. 初始化网络，连接到Answer端 -->
        <step type="network" action="init" content="192.168.1.101:9998" local_port="9998" />
        <step type="wait" action="sleep" content="2" />
        
        <!-- 2. 等待Answer端就绪 -->
        <step type="network" action="receive" content="ready" timeout="10" />
        
        <!-- 3. 执行拨号UI -->
        <step type="keyboard" action="type_text" content="1881234567" />
        <step type="keyboard" action="press_key" content="enter" />
        <step type="wait" action="sleep" content="1" />
        
        <!-- 4. 发送call信号 -->
        <step type="network" action="send" content="call_start" data="{&quot;phone&quot;: &quot;1881234567&quot;}" />
        
        <!-- 5. 等待Answer端接听 -->
        <step type="network" action="receive" content="call_answer" timeout="30" />
        
        <!-- 6. 执行通话（播放+录音） -->
        <step type="audio" action="play_async" content="testAudioFile/test_audio.wav" device="0" />
        <step type="audio" action="record_async" content="testAudioFile/call_recorded.wav" device="0" duration="10" />
        <step type="wait" action="sleep" content="11" />
        
        <!-- 7. 发送挂断信号 -->
        <step type="network" action="send" content="call_end" data="{&quot;duration&quot;: 10}" />
        
        <!-- 8. 停止网络 -->
        <step type="network" action="stop" content="" />
    </testcase>
    
    <!-- Answer端 -->
    <testcase name="Answer端">
        <!-- 1. 初始化网络（仅启动服务器） -->
        <step type="network" action="init" content="" local_port="9998" />
        <step type="wait" action="sleep" content="1" />
        
        <!-- 2. 发送就绪信号 -->
        <step type="network" action="send" content="ready" />
        
        <!-- 3. 等待来电 -->
        <step type="network" action="receive" content="call_start" timeout="30" />
        
        <!-- 4. 执行接听UI -->
        <step type="keyboard" action="press_key" content="enter" />
        <step type="wait" action="sleep" content="1" />
        
        <!-- 5. 发送接听信号 -->
        <step type="network" action="send" content="call_answer" data="{&quot;status&quot;: &quot;answered&quot;}" />
        
        <!-- 6. 执行通话（播放+录音） -->
        <step type="audio" action="play_async" content="testAudioFile/test_audio.wav" device="0" />
        <step type="audio" action="record_async" content="testAudioFile/answer_recorded.wav" device="24" duration="10" />
        <step type="wait" action="sleep" content="11" />
        
        <!-- 7. 等待Call端挂断 -->
        <step type="network" action="receive" content="call_end" timeout="30" />
        
        <!-- 8. 停止网络 -->
        <step type="network" action="stop" content="" />
    </testcase>
</testcases>
```

**运行命令：**
```bash
python p2p_testcase_coordinator.py \
  127.0.0.1 9999 \
  192.168.1.101 9999 \
  testcase/p2p_call_answer.xml "Call端" \
  testcase/p2p_call_answer.xml "Answer端"
```

## 网络拓扑

```
┌─────────────────┐
│     PC-1        │
│ port: 9998      │  ← remote_executor.py
│ (Call端)        │  ← p2p_network服务器+客户端
└─────────────────┘
         ↔ P2P通信
         ↔ (TCP双向)
         ↔
┌─────────────────┐
│     PC-2        │
│ port: 9998      │  ← remote_executor.py
│ (Answer端)      │  ← p2p_network服务器+客户端
└─────────────────┘
```

## 调试技巧

### 查看可用事件
```bash
python network_event.py
```

### 测试P2P网络连接
```bash
# PC-1启动接收端
python p2p_network.py receiver 9998

# PC-2启动发送端
python p2p_network.py sender 192.168.1.100 9998 9999
```

### 查看网络连接
```bash
# Windows
netstat -ano | findstr :9998

# Linux
netstat -tlnp | grep 9998
```

## 常见问题

**Q: 如何添加自定义事件？**
A: 在 `network_event.py` 中添加到 `NetworkEvent` 枚举和 `EVENTS` 字典。

**Q: 能否传递复杂的JSON数据？**
A: 可以，在 `data` 属性中传递JSON字符串，注意转义引号。

**Q: 超时时间设置多长合适？**
A: 根据网络和业务逻辑，通常30-60秒。如果PC操作比较复杂，可以加长。

**Q: 消息会丢失吗？**
A: 不会。接收方会在内存队列中缓存接收到的消息，接收方调用 `receive` 时会从队列中获取。

## 总结

| 操作 | XML写法 | 说明 |
|------|---------|------|
| 初始化 | `<step type="network" action="init" content="ip:port" />` | 连接到对端或启动服务器 |
| 发送 | `<step type="network" action="send" content="event_name" />` | 发送事件给对端 |
| 接收 | `<step type="network" action="receive" content="event_name" />` | 等待对端事件（阻塞） |
| 停止 | `<step type="network" action="stop" content="" />` | 关闭网络连接 |
