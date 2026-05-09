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
    print(f"  [OK] {text}")

def print_error(text):
    """打印错误信息"""
    print(f"  [FAIL] {text}")

def print_warning(text):
    """打印警告信息"""
    print(f"  [WARN] {text}")

def check_file_exists(path, name):
    """检查文件是否存在"""
    if Path(path).exists():
        print_success(f"{name}")
        return True
    else:
        print_error(f"{name} - not found")
        return False

def main():
    """主验证函数"""
    print_header("AutoControlPC Project Integrity Check")
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    all_ok = True
    
    # 1. 检查Python版本
    print_header("1. Python Version Check")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    else:
        print_error(f"Python version too low {version.major}.{version.minor}, need 3.8+")
        all_ok = False
    
    # 2. 检查核心模块
    print_header("2. Core Module Check")
    core_modules = [
        ("run_testcase.py", "Test case execution engine"),
        ("auto_controller.py", "UI automation controller"),
        ("keyboard_controller.py", "Keyboard control"),
        ("mouse_controller.py", "Mouse control"),
        ("audio_player.py", "Audio playback"),
        ("audio_recorder.py", "Audio recording"),
        ("ocr_tool.py", "OCR text recognition"),
        ("icon_detector.py", "Icon detection"),
        ("window_util.py", "Window operations"),
        ("input_method_util.py", "Input method detection"),
        ("advanced_features.py", "Advanced features"),
    ]
    
    for filename, desc in core_modules:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 3. 检查网络模块
    print_header("3. Network Module Check")
    network_modules = [
        ("p2p_network.py", "P2P network implementation"),
        ("network_event.py", "Network event definitions"),
        ("p2p_testcase_coordinator.py", "Test coordinator"),
    ]
    
    for filename, desc in network_modules:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 4. 检查工具和测试
    print_header("4. Tools and Test Scripts")
    tools = [
        ("parse_testcase.py", "Test case parser"),
        ("test.py", "Basic test"),
    ]
    
    for filename, desc in tools:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 5. 检查文档
    print_header("5. Documentation Check")
    docs = [
        ("README.md", "Project readme"),
        ("PROJECT_SETUP.md", "Installation setup"),
        ("QUICK_START.md", "Quick start"),
        ("P2P_NETWORK_GUIDE.md", "Network guide"),
        ("INSTALL.md", "Install check"),
        ("GUIDE.md", "File guide"),
        ("PROJECT_FILES_CHECKLIST.md", "File checklist"),
    ]
    
    for filename, desc in docs:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 6. 检查配置文件
    print_header("6. Config File Check")
    configs = [
        ("requirements.txt", "Python dependencies"),
        ("setup.py", "Package config"),
    ]
    
    for filename, desc in configs:
        if not check_file_exists(filename, f"{desc} ({filename})"):
            all_ok = False
    
    # 7. 检查测试用例
    print_header("7. Test Case Check")
    testcases_dir = Path("testcase")
    
    if testcases_dir.exists():
        testcases = list(testcases_dir.glob("*.xml"))
        if testcases:
            print_success(f"Found {len(testcases)} test cases")
                for tc in sorted(testcases):
                    print(f"    - {tc.name}")
        else:
            print_warning("testcase folder is empty")
    else:
        print_error("testcase folder not found")
        all_ok = False
    
    # 8. 检查素材文件夹
    print_header("8. Asset Folder Check")
    folders = [
        ("png", "Icon assets"),
        ("testAudioFile", "Test audio"),
    ]
    
    for folder, desc in folders:
        if check_file_exists(folder, f"{desc} ({folder}/)"):
            count = len(list(Path(folder).glob("*")))
            print(f"    ├─ Contains {count} files")
        else:
            all_ok = False
    
    # 9. 检查Python依赖
    print_header("9. Python Dependency Check")
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
            print_success(f"{display_name} installed")
        except ImportError:
            print_error(f"{display_name} not installed")
            missing_packages.append(display_name)
            all_ok = False
    
    # Windows 特定检查
    if sys.platform == "win32":
        try:
            import win32api
            print_success("pywin32 installed (Windows)")
        except ImportError:
            print_warning("pywin32 not installed (Windows-specific, only needed for window ops)")
            missing_packages.append("pywin32")
    
    # 10. 总结
    print_header("Verification Summary")
    
    if all_ok and not missing_packages:
        print_success("All checks passed! Project is ready to use.")
        print("\n[INFO] Next steps:")
        print("  1. Run: python run_testcase.py testcase/p2p_network_demo.xml P2P_SinglePC_Send")
        print("  2. Read: README.md and QUICK_START.md")
        print("  3. Learn: Check XML examples in testcase/")
        return 0
    else:
        print_error("Issues found, please fix and retry")
        
        if missing_packages:
            print("\n[FAIL] Missing the following Python packages:")
            for pkg in missing_packages:
                print(f"  - {pkg}")
            print("\nFix:")
            print("  pip install -r requirements.txt")
            
            if sys.platform == "win32" and "pywin32" in missing_packages:
                print("  python -m pywin32_postinstall -install")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
