#!/usr/bin/env python3
"""
AutoControlPC 项目完整性验证脚本
用于检查所有必需文件和依赖是否正确安装

使用方法：
  python project_verify.py
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    """打印成功信息"""
    print(f"  ✅ {text}")

def print_error(text):
    """打印错误信息"""
    print(f"  ❌ {text}")

def print_warning(text):
    """打印警告信息"""
    print(f"  ⚠️  {text}")

def check_file_exists(path, name):
    """检查文件是否存在"""
    if Path(path).exists():
        print_success(f"{name}")
        return True
    else:
        print_error(f"{name} - 未找到")
        return False

def main():
    """主验证函数"""
    print_header("AutoControlPC 项目完整性验证")
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    all_ok = True
    
    # 1. 检查Python版本
    print_header("1. Python版本检查")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    else:
        print_error(f"Python版本过低 {version.major}.{version.minor}，需要3.8+")
        all_ok = False
    
    # 2. 检查核心模块
    print_header("2. 核心模块检查")
    core_modules = [
        ("run_testcase.py", "测试用例执行引擎"),
        ("auto_controller.py", "UI自动化控制器"),
        ("keyboard_controller.py", "键盘控制"),
        ("mouse_controller.py", "鼠标控制"),
        ("audio_player.py", "音频播放"),
        ("audio_recorder.py", "音频录音"),
        ("ocr_tool.py", "OCR文本识别"),
        ("icon_detector.py", "图标检测"),
        ("window_util.py", "窗口操作"),
        ("input_method_util.py", "输入法检测"),
        ("advanced_features.py", "高级特性"),
    ]
    
    for filename, desc in core_modules:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 3. 检查网络模块
    print_header("3. 网络通信模块检查")
    network_modules = [
        ("p2p_network.py", "P2P网络实现"),
        ("network_event.py", "网络事件定义"),
        ("p2p_testcase_coordinator.py", "测试协调器"),
    ]
    
    for filename, desc in network_modules:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 4. 检查工具和测试
    print_header("4. 工具和测试脚本")
    tools = [
        ("parse_testcase.py", "用例解析工具"),
        ("test.py", "基础测试"),
    ]
    
    for filename, desc in tools:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 5. 检查文档
    print_header("5. 文档文件检查")
    docs = [
        ("README.md", "项目说明"),
        ("PROJECT_SETUP.md", "安装配置"),
        ("QUICK_START.md", "快速开始"),
        ("P2P_NETWORK_GUIDE.md", "网络文档"),
        ("INSTALL.md", "安装检查"),
        ("GUIDE.md", "文件说明"),
        ("PROJECT_FILES_CHECKLIST.md", "文件清单"),
    ]
    
    for filename, desc in docs:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 6. 检查配置文件
    print_header("6. 配置文件检查")
    configs = [
        ("requirements.txt", "Python依赖"),
        ("setup.py", "包配置"),
    ]
    
    for filename, desc in configs:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 7. 检查测试用例
    print_header("7. 测试用例检查")
    testcases_dir = Path("testcase")
    
    if testcases_dir.exists():
        testcases = list(testcases_dir.glob("*.xml"))
        if testcases:
            print_success(f"找到 {len(testcases)} 个测试用例")
            for tc in sorted(testcases):
                print(f"    • {tc.name}")
        else:
            print_warning("testcase 文件夹为空")
    else:
        print_error("testcase 文件夹不存在")
        all_ok = False
    
    # 8. 检查素材文件夹
    print_header("8. 素材文件夹检查")
    folders = [
        ("png", "图标素材"),
        ("testAudioFile", "测试音频"),
    ]
    
    for folder, desc in folders:
        if check_file_exists(folder, f"{desc} ({folder}/)"):
            count = len(list(Path(folder).glob("*")))
            print(f"    ├─ 包含 {count} 个文件")
        else:
            all_ok = False
    
    # 9. 检查Python依赖
    print_header("9. Python依赖检查")
    required_packages = [
        "pyautogui",
        "PIL",
        "cv2",
        "numpy",
        "paddleocr",
        "pygame",
        "pydub",
        "simpleaudio",
        "sounddevice",
        "soundfile",
    ]
    
    import_map = {
        "PIL": "Pillow",
        "cv2": "opencv-python",
    }
    
    missing_packages = []
    
    for package in required_packages:
        import_name = package
        display_name = import_map.get(package, package)
        
        try:
            __import__(import_name)
            print_success(f"{display_name} 已安装")
        except ImportError:
            print_error(f"{display_name} 未安装")
            missing_packages.append(display_name)
            all_ok = False
    
    # Windows 特定检查
    if sys.platform == "win32":
        try:
            import win32api
            print_success("pywin32 已安装 (Windows)")
        except ImportError:
            print_warning("pywin32 未安装 (Windows特定，仅窗口操作需要)")
            missing_packages.append("pywin32")
    
    # 10. 总结
    print_header("验证总结")
    
    if all_ok and not missing_packages:
        print_success("所有检查通过！项目已完全准备好使用。")
        print("\n📝 下一步建议：")
        print("  1. 运行：python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send")
        print("  2. 阅读：README.md 和 QUICK_START.md")
        print("  3. 学习：查看 testcase/ 中的XML示例")
        return 0
    else:
        print_error("检查发现问题，请修复后重试")
        
        if missing_packages:
            print("\n❌ 缺少以下Python包：")
            for pkg in missing_packages:
                print(f"  • {pkg}")
            print("\n修复方法：")
            print("  pip install -r requirements.txt")
            
            if sys.platform == "win32" and "pywin32" in missing_packages:
                print("  python -m pywin32_postinstall -install")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
