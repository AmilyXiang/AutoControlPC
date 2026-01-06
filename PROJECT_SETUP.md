# 项目使用指南 - AutoControlPC

## 目录

1. [项目下载后的第一步](#项目下载后的第一步)
2. [环境配置](#环境配置)
3. [验证安装](#验证安装)
4. [运行示例](#运行示例)
5. [Windows特殊配置](#windows特殊配置)
6. [常见问题](#常见问题)

## 项目下载后的第一步

### 步骤 1：检查Python版本
```powershell
python --version
```
需要 **Python 3.8 或更高版本**

### 步骤 2：创建虚拟环境
```powershell
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 步骤 3：安装依赖
```powershell
pip install -r requirements.txt
```

## 环境配置

### Python 依赖说明

项目的 `requirements.txt` 包含以下关键包：

| 包名 | 版本 | 用途 |
|-----|------|------|
| pyautogui | 0.9.53 | UI自动化（鼠标键盘） |
| Pillow | ≥9.0.0 | 图像处理和截图 |
| numpy | ≥1.20.0 | 数值计算 |
| opencv-python | ≥4.5.0 | 图标检测 |
| PaddleOCR | 2.8.0.3 | 文本识别 |
| pygame | ≥2.0.0 | 音频播放 |
| pydub | ≥0.25.1 | 音频处理 |
| simpleaudio | ≥1.0.4 | 简单音频播放 |
| sounddevice | ≥0.4.6 | 音频录音 |
| soundfile | ≥0.12.1 | 音频文件读写 |
| pywin32 | ≥306 | Windows操作（仅Windows） |

## 验证安装

### 检查所有依赖是否正确安装
```python
# 运行此脚本验证环境
python -c "
import pyautogui
import PIL
import cv2
import numpy
import paddleocr
import pygame
import pydub
import simpleaudio
import sounddevice
import soundfile
print('✓ 所有依赖安装成功！')
"
```

### 检查音频设备列表
```python
import sounddevice as sd
print('可用的音频设备：')
print(sd.query_devices())
```

## 运行示例

### 示例 1：单机P2P通信测试（推荐首选）
这是测试P2P网络功能的最简单方式，无需两台PC。

```powershell
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

**预期输出：**
```
[P2P] 接收服务器启动 (端口: 9998)
[P2P] 已连接到对端 127.0.0.1:9998
[P2P] 发送消息: ready
✓ 接收端收到消息 #1: ready
✓ 测试成功！
```

### 示例 2：音频播放测试
```powershell
python run_testcase.py testcase/audio_play_record_test1.xml
```

### 示例 3：网易音乐播放测试
```powershell
python run_testcase.py testcase/netease_music.xml
```

## Windows特殊配置

### 1. pywin32 后处理（重要！）
安装 `requirements.txt` 后，**必须**运行以下命令：

```powershell
python -m pywin32_postinstall -install
```

如果提示权限不足，以管理员身份运行PowerShell：
```powershell
# 右键PowerShell -> 以管理员身份运行
python -m pywin32_postinstall -install
```

### 2. FFmpeg安装（可选，仅音频处理需要）
某些音频操作可能需要 FFmpeg：

**选项A：使用Chocolatey（推荐）**
```powershell
# 需要管理员权限
choco install ffmpeg
```

**选项B：手动安装**
1. 下载：https://ffmpeg.org/download.html
2. 解压到 `C:\ffmpeg`
3. 添加到系统PATH环境变量

验证安装：
```powershell
ffmpeg -version
```

### 3. 处理PowerShell执行策略错误
如果遇到 "因为在此系统上禁止运行脚本"：

```powershell
# 使用 .bat 激活虚拟环境（推荐）
.venv\Scripts\activate.bat
```

或者临时允许执行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 常见问题

### Q1：如何找到音频设备ID？
**A：** 运行以下Python代码：
```python
import sounddevice as sd
devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"{i}: {device['name']}")
```

然后在XML中使用对应的ID：
```xml
<step type="audio" action="play" content="audio.wav" device="0" />
```

### Q2：网络错误 "SendTo failed" 或 "Connection refused"
**A：** 这通常是因为对端还未启动。解决方案：
1. 确保两台PC都在同一网络
2. 确认防火墙允许Python程序
3. 运行本地P2P测试验证网络模块：
   ```powershell
   python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
   ```

### Q3：PaddleOCR首次运行很慢
**A：** 这是正常的。PaddleOCR需要下载预训练模型（~500MB）：
1. 首次运行时会自动下载到 `~/.paddleocr/`
2. 后续运行会直接使用缓存，速度很快
3. 或者手动预下载：
   ```python
   from paddleocr import PaddleOCR
   ocr = PaddleOCR(use_angle_cls=True, lang='ch')
   ```

### Q4：pyautogui 在运行时卡顿
**A：** 这通常是因为 pyautogui 的安全功能。可以调整：
```python
import pyautogui
pyautogui.FAILSAFE = False  # 禁用移动到角落退出
pyautogui.PAUSE = 0.01      # 减少命令间延迟
```

但不建议禁用FAILSAFE，建议保持1-2秒的PAUSE来确保稳定性。

### Q5：无法访问Windows窗口操作
**A：** Windows窗口操作需要pywin32正确配置。运行：
```powershell
python -m pywin32_postinstall -install
# 然后重启Python环境或重启计算机
```

### Q6：XML文件无法找到
**A：** 确保：
1. XML文件在 `testcase/` 文件夹中
2. 文件名正确（区分大小写在Linux上）
3. 使用正确的命令语法：
   ```powershell
   python run_testcase.py testcase/filename.xml [testcase_name]
   ```

## 项目文档导航

| 文件 | 用途 |
|-----|------|
| [README.md](README.md) | 项目总览和功能说明 |
| [QUICK_START.md](QUICK_START.md) | 5分钟快速开始教程 |
| [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md) | P2P网络通信详细文档 |
| [INSTALL.md](INSTALL.md) | 安装验证检查清单 |
| [GUIDE.md](GUIDE.md) | 文件和模块说明 |

## 下一步

1. **快速体验**：运行 `python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send`
2. **学习XML格式**：查看 `testcase/` 中的示例文件
3. **配置两PC**：参考 [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md)
4. **自定义测试**：编写自己的XML文件

## 获取帮助

- 查看相应的 `.md` 文档文件
- 检查 `testcase/` 中的示例
- 查看控制台的详细错误信息
- 参考源代码中的注释

---

**最后更新**：项目已完全准备好使用。下载后直接按照步骤1-3进行配置即可。
