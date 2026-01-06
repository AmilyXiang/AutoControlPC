# 📋 AutoControlPC - 快速使用指南

> 项目已完成清理，所有文件都是必需的。开箱即用！

## 🚀 极速开始（3步，5分钟）

### 步骤1：安装依赖
```bash
pip install -r requirements.txt
```

### 步骤2：Windows额外配置（仅Windows）
```bash
python -m pywin32_postinstall -install
```

### 步骤3：运行第一个测试
```bash
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

看到 `✓ 测试成功！` 就表示一切正常 ✅

---

## 📚 文档导航

| 文档 | 用途 | 新手 | 开发 | 网络 |
|-----|------|------|------|------|
| **START_HERE.md** | 5分钟快速开始 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **README.md** | 项目功能说明 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **QUICK_START.md** | 详细上手教程 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **PROJECT_SETUP.md** | 安装配置指南 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| **P2P_NETWORK_GUIDE.md** | 网络通信详解 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **GUIDE.md** | 模块参考 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 常用命令

```bash
# 验证安装（可选）
python -c "import sys; print(f'Python {sys.version}')"

# 运行P2P测试（单机）
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send

# 运行音频测试
python run_testcase.py testcase/audio_play_record_test1.xml

# 查看可用音频设备
python -c "import sounddevice as sd; print(sd.query_devices())"
```

---

## 📁 项目结构

```
AutoControlPC/
├── run_testcase.py              # 主程序
├── [16个Python模块]
├── [7个文档文件]
├── requirements.txt
├── testcase/                    # 7个示例测试用例
├── png/                         # 图标素材
└── testAudioFile/               # 音频文件
```

---

## ✨ 项目特点

- ✅ **开箱即用** - 下载后直接使用
- ✅ **精简高效** - 删除了所有过时文件
- ✅ **完整功能** - UI自动化、音频、P2P网络
- ✅ **清晰文档** - 7份精炼文档
- ✅ **丰富示例** - 7个XML测试用例
- ✅ **支持多PC** - P2P双向通信

---

## 🎓 推荐学习路径

### 新手（1小时）
1. 打开 **START_HERE.md** (3分钟)
2. 运行第一个测试 (1分钟)  
3. 阅读 **README.md** (5分钟)
4. 浏览 **QUICK_START.md** (10分钟)
5. 查看 `testcase/` 示例 (10分钟)
6. 尝试修改XML (20分钟)

### 开发者（2小时）
1. 完成新手路径 (1小时)
2. 阅读 **GUIDE.md** (30分钟)
3. 查看源代码 (20分钟)
4. 尝试扩展功能 (10分钟)

### 网络用户（3小时）
1. 完成新手路径 (1小时)
2. 阅读 **P2P_NETWORK_GUIDE.md** (30分钟)
3. 配置两PC环境 (30分钟)
4. 测试双向通信 (30分钟)

---

## 🔍 常见问题

**Q: 如何找音频设备ID？**
```python
import sounddevice as sd
print(sd.query_devices())
```
在XML中使用：`device="0"` (替换为你的设备ID)

**Q: 怎样创建自己的测试？**
1. 复制 `testcase/p2p_network_demo.xml`
2. 编辑其中的 `<step>` 内容
3. 运行测试：`python run_testcase.py your_file.xml`

**Q: 两PC怎么通信？**
查看 [P2P_NETWORK_GUIDE.md](P2P_NETWORK_GUIDE.md) 的步骤3-5

**Q: 网络连接失败？**
1. 确保两台PC在同一网络
2. 检查防火墙是否阻止了Python
3. 确认对端IP地址正确（使用 `ipconfig`）

---

## 📊 项目统计

| 指标 | 数值 |
|-----|------|
| Python模块 | 16个 |
| 文档文件 | 7个 |
| 代码行数 | 3000+ |
| 支持的操作 | 13+ |
| 网络事件 | 13+ |
| 测试用例 | 7个 |

---

## 🎉 现在就开始

```bash
# 最简单的方式
pip install -r requirements.txt
python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send
```

或者打开 **START_HERE.md** 了解更多。

---

**项目已清理完成，所有文件都是精选必需的。随时可以使用！** 🚀

