# 🚀 AutoControlPC - 开始使用指南

欢迎使用 AutoControlPC！这是一个完整的多PC自动化测试框架。项目已经过精简清理，所有文件都是必需的。

## ⚡ 30秒快速开始

```powershell
# 1. 安装依赖（仅需一次）
pip install -r requirements.txt

# 2. Windows额外配置（仅Windows）
python -m pywin32_postinstall -install

# 3. 运行你的第一个测试
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

看到 `✓ 测试成功！` 就表示一切正常。🎉

---

## 📚 完整文档导航

| 你想要... | 查看这个文件 |
|----------|-----------|
| 了解项目功能 | [README.md](README.md) |
| 安装和配置 | [PROJECT_SETUP.md](PROJECT_SETUP.md) |
| 5分钟教程 | [QUICK_START.md](QUICK_START.md) |
| 两PC网络配置 | [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md) |
| 检查文件清单 | [PROJECT_FILES_CHECKLIST.md](PROJECT_FILES_CHECKLIST.md) |
| 模块详细说明 | [GUIDE.md](GUIDE.md) |
| 验证安装 | [INSTALL.md](INSTALL.md) |

---

## 🎯 常见使用场景

### 场景1：我想测试P2P网络通信（推荐首选）

```powershell
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

✅ 优点：无需两台PC，10秒完成  
📝 示例文件：`testcase/p2p_network_demo.xml`  
📖 详情查看：[QUICK_START.md](QUICK_START.md)

### 场景2：我想测试音频播放和录音

```powershell
python run_testcase.py testcase/audio_play_record_test1.xml
```

需要指定测试用例名称（如果XML中有多个）：
```powershell
python run_testcase.py testcase/audio_play_record_test2.xml 用例名称
```

### 场景3：我有两台PC，想测试跨PC通信

参考 [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md) 中的步骤3-5。

### 场景4：我想创建自己的测试用例

1. **复制示例**
   ```powershell
   copy testcase/p2p_network_demo.xml testcase/my_test.xml
   ```

2. **编辑 XML 文件**（用你喜欢的文本编辑器）

3. **运行测试**
   ```powershell
   python run_testcase.py testcase/my_test.xml 用例名称
   ```

4. **参考示例**: `testcase/` 文件夹中的各个XML文件

---

## ⚙️ 系统要求

- **Python**: 3.8+（推荐3.10+）
- **操作系统**: Windows 7+ / Linux / macOS
- **内存**: 最少2GB（PaddleOCR需要）
- **网络**: 两PC场景需要网络连接

## 📦 依赖包

项目自动安装这些包（通过 `pip install -r requirements.txt`）：

```
pyautogui==0.9.53              # UI自动化
Pillow>=9.0.0                  # 图像处理
numpy>=1.20.0                  # 数值计算
opencv-python>=4.5.0           # 计算机视觉
PaddleOCR==2.8.0.3             # OCR识别
pygame>=2.0.0                  # 音频播放
pydub>=0.25.1                  # 音频处理
simpleaudio>=1.0.4             # 简单音频
sounddevice>=0.4.6             # 音频录音
soundfile>=0.12.1              # 音频文件
pywin32>=306                   # Windows操作（仅Windows）
```

---

## ✅ 验证安装完成

运行验证脚本检查所有文件和依赖：

```powershell
python project_verify.py
```

**预期输出**：所有项目都显示 ✅

---

## 🔧 常见配置

### 找到你的音频设备ID

```python
import sounddevice as sd
devices = sd.query_devices()
for i, d in enumerate(devices):
    print(f"{i}: {d['name']}")
```

在XML中使用：
```xml
<step type="audio" action="play" content="audio.wav" device="0" />
```

### 找到你的PC的IP地址

**Windows:**
```powershell
ipconfig
# 查找 "IPv4 地址"，通常形如 192.168.x.x
```

**Linux/macOS:**
```bash
ifconfig | grep "inet "
```

在XML中使用：
```xml
<step type="network" action="init" content="192.168.1.102:9998" local_port="9998" />
```

---

## 🐛 故障排除

| 问题 | 解决方案 |
|-----|---------|
| `ModuleNotFoundError` | 运行 `pip install -r requirements.txt` |
| Windows pywin32错误 | 运行 `python -m pywin32_postinstall -install` |
| 网络连接失败 | 检查两台PC是否在同一网络，防火墙设置 |
| 音频设备未找到 | 运行上面的设备检测脚本 |
| OCR速度慢 | 这是第一次运行，需要下载模型。后续会快得多 |
| 找不到XML文件 | 确保文件在 `testcase/` 文件夹中 |

更多问题查看 [PROJECT_SETUP.md](PROJECT_SETUP.md) 的完整故障排除部分。

---

## 🎓 学习路径

### 初学者（开始使用）
1. 运行验证脚本：`python project_verify.py`
2. 运行第一个测试：`python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send`
3. 阅读 [QUICK_START.md](QUICK_START.md)

### 中级（自定义测试）
1. 查看 `testcase/` 中的XML示例
2. 参考 [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md) 了解XML格式
3. 创建自己的测试用例

### 高级（扩展功能）
1. 阅读 [GUIDE.md](GUIDE.md) 了解模块结构
2. 修改 `network_event.py` 添加自定义事件
3. 扩展 `run_testcase.py` 添加新操作类型
4. 修改 `p2p_network.py` 自定义通信协议

---

## 📞 获取帮助

1. **查看相关文档** - 所有问题都有相应的文档
2. **检查示例** - `testcase/` 中的7个例子覆盖大部分场景
3. **查看错误信息** - Python会给出详细的错误说明
4. **查看源代码** - Python注释和代码很清晰

---

## 🎉 现在就开始！

```powershell
# 一键启动
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

**预期输出:**
```
[P2P] 接收服务器启动 (端口: 9998)
[P2P] 已连接到对端 127.0.0.1:9998
[P2P] 发送消息: ready
✓ 接收端收到消息 #1: ready
✓ 测试成功！
```

看到这个输出就说明 ✅ 一切就绪！

---

## 📊 项目统计

- **代码行数**: 3000+
- **支持的操作**: 13+
- **网络事件**: 13+
- **示例测试**: 7个
- **文档页数**: 30+

---

## 📜 许可证

MIT - 随意使用和修改

---

**祝你使用愉快！** 🚀

如有任何问题，先查看相应的 `.md` 文档文件。
