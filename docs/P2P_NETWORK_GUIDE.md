# P2P对等网络测试系统指南

## 核心概念

### 什么是P2P对等网络？

两个PC完全对等，**都是服务器，都是客户端**：
- 可以发送消息
- 可以接收消息
- 无需区分服务器端和客户端

### 事件系统

所有网络通信都基于**事件**，统一定义在 `network_event.py` 中：

```python
INIT = "init"
STOP = "stop"
READY = "ready"
CALL_START = "call_start"
CALL_ANSWER = "call_answer"
CALL_END = "call_end"
AUDIO_START = "audio_start"
AUDIO_STOP = "audio_stop"
MESSAGE = "message"
DATA = "data"
```

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
<!-- 主动连接到对端 -->
<step type="network" action="init" content="192.168.1.101:9998" local_port="9998" />

<!-- 只监听，等待对端连接 -->
<step type="network" action="init" content="" local_port="9998" />
```
- `content`: 对端地址和端口 (格式: `ip:port`)，为空时仅启动本地服务器
- `local_port`: 本地监听端口（默认9998）

#### network send
```xml
<step type="network" action="send" content="call_start" data="{&quot;phone&quot;: &quot;188xx&quot;}" />
```
- `content`: 事件名称
- `data`: JSON格式的数据（可选）

#### network receive
```xml
<step type="network" action="receive" content="call_answer" timeout="30" />
```
- `content`: 等待的事件名称
- `timeout`: 等待超时时间（秒，默认30）

#### network stop
```xml
<step type="network" action="stop" content="" />
```

## 快速开始

### 单机P2P测试（推荐首选）

无需两台PC，直接测试网络功能：

```bash
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

### 两PC实际测试

#### PC-A（主叫方）

编辑 `testcase/pc_a_call.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testcases>
    <testcase name="Call">
        <!-- 连接到PC-B -->
        <step type="network" action="init" content="192.168.1.102:9998" local_port="9998" />
        <step type="wait" content="1" />
        
        <!-- 发送准备就绪 -->
        <step type="network" action="send" content="ready" data="{&quot;status&quot;: &quot;online&quot;}" />
        
        <!-- 发送通话请求 -->
        <step type="network" action="send" content="call_start" data="{&quot;caller&quot;: &quot;PC-A&quot;}" />
        
        <!-- 等待接听 -->
        <step type="network" action="receive" content="call_answer" timeout="30" />
        
        <!-- 播放音频 -->
        <step type="audio" action="play" content="testAudioFile/test.wav" device="0" />
        
        <!-- 发送结束信号 -->
        <step type="network" action="send" content="call_end" />
        
        <!-- 停止网络 -->
        <step type="network" action="stop" content="" />
    </testcase>
</testcases>
```

运行：
```bash
python run_testcase.py testcase/pc_a_call.xml Call
```

#### PC-B（被叫方）

编辑 `testcase/pc_b_answer.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testcases>
    <testcase name="Answer">
        <!-- 监听本地端口，等待连接 -->
        <step type="network" action="init" content="" local_port="9998" />
        
        <!-- 等待就绪信号 -->
        <step type="network" action="receive" content="ready" timeout="30" />
        
        <!-- 等待通话请求 -->
        <step type="network" action="receive" content="call_start" timeout="30" />
        
        <!-- 发送接听 -->
        <step type="network" action="send" content="call_answer" data="{&quot;receiver&quot;: &quot;PC-B&quot;}" />
        
        <!-- 播放音频 -->
        <step type="audio" action="play" content="testAudioFile/test.wav" device="0" />
        
        <!-- 等待结束信号 -->
        <step type="network" action="receive" content="call_end" timeout="30" />
        
        <!-- 停止网络 -->
        <step type="network" action="stop" content="" />
    </testcase>
</testcases>
```

运行：
```bash
python run_testcase.py testcase/pc_b_answer.xml Answer
```

## 执行流程

```
时间线：

t0:  PC-B 运行 init "" 9998 → 启动服务器，等待连接
     PC-A 运行 init "192.168.1.102:9998" 9998 → 连接到PC-B

t1:  PC-A send "ready"
     PC-B receive "ready" ✓

t2:  PC-A send "call_start"
     PC-B receive "call_start" ✓

t3:  PC-B send "call_answer"
     PC-A receive "call_answer" ✓

t4:  PC-A 和 PC-B 同时播放音频

t5:  PC-A send "call_end"
     PC-B receive "call_end" ✓

t6:  双方停止网络连接
```

## 常见场景

### 场景1：简单消息通信

PC-A → PC-B

```xml
<!-- PC-A -->
<step type="network" action="init" content="192.168.1.102:9998" local_port="9998" />
<step type="network" action="send" content="message" data="{&quot;text&quot;: &quot;Hello&quot;}" />
<step type="network" action="receive" content="message" timeout="10" />
<step type="network" action="stop" content="" />

<!-- PC-B -->
<step type="network" action="init" content="" local_port="9998" />
<step type="network" action="receive" content="message" timeout="30" />
<step type="network" action="send" content="message" data="{&quot;text&quot;: &quot;Hi&quot;}" />
<step type="network" action="stop" content="" />
```

### 场景2：多消息同步

```xml
<!-- PC-A -->
<step type="network" action="send" content="ready" />
<step type="network" action="send" content="start" />
<step type="network" action="receive" content="ready" />
<step type="network" action="receive" content="start" />

<!-- PC-B -->
<step type="network" action="receive" content="ready" />
<step type="network" action="receive" content="start" />
<step type="network" action="send" content="ready" />
<step type="network" action="send" content="start" />
```

## 故障排查

### 网络连接失败

检查：
1. 两台PC是否在同一网络
2. 防火墙是否阻止了Python
3. IP地址和端口是否正确

```bash
# Windows查看开放的端口
netstat -ano | findstr :9998

# Linux查看开放的端口
netstat -tlnp | grep 9998
```

### 消息接收超时

检查：
1. 对端是否已启动
2. 事件名称是否一致
3. 网络连接是否正常

### 端口已被占用

改用其他端口：

```xml
<step type="network" action="init" content="192.168.1.102:8888" local_port="8888" />
```

## 常见问题

**Q: PC-A和PC-B谁应该先运行？**
A: PC-B先运行（init为空），然后PC-A运行（init指定PC-B地址）。或者同时运行，网络库会自动重连。

**Q: 可以用其他端口吗？**
A: 可以，只要两端端口不冲突即可。

**Q: 消息会丢失吗？**
A: 不会。接收方会在内存队列缓存消息。

**Q: 支持自定义事件吗？**
A: 支持。在XML中send/receive任何字符串都可以，不一定要在network_event.py中定义。

## 总结

| 操作 | 说明 |
|------|------|
| `init "ip:port"` | 连接到对端 |
| `init ""` | 等待对端连接 |
| `send "event"` | 发送事件 |
| `receive "event"` | 等待事件 |
| `stop ""` | 关闭连接 |

---

**更多例子**: 查看 `testcase/p2p_network_demo.xml`

