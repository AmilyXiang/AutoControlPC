"""
测试脚本 - 验证AutoControlPC是否正常安装和工作
"""

import sys
import time


def test_imports():
    """测试是否能导入所有模块"""
    print("=" * 50)
    print("测试1：检查模块导入")
    print("=" * 50)
    
    try:
        print("导入 mouse_controller...", end=" ")
        from mouse_controller import MouseController
        print("✓ 成功")
    except ImportError as e:
        print(f"✗ 失败: {e}")
        return False
    
    try:
        print("导入 keyboard_controller...", end=" ")
        from keyboard_controller import KeyboardController
        print("✓ 成功")
    except ImportError as e:
        print(f"✗ 失败: {e}")
        return False
    
    try:
        print("导入 auto_controller...", end=" ")
        import auto_controller as ac
        print("✓ 成功")
    except ImportError as e:
        print(f"✗ 失败: {e}")
        return False
    
    print()
    return True


def test_mouse():
    """测试鼠标功能"""
    print("=" * 50)
    print("测试2：鼠标功能测试")
    print("=" * 50)
    
    from mouse_controller import MouseController
    mouse = MouseController()
    
    try:
        print("获取鼠标位置...", end=" ")
        pos = mouse.get_position()
        print(f"✓ 成功: {pos}")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False
    
    try:
        print("移动鼠标到(100, 100)...", end=" ")
        mouse.move_to(100, 100, duration=0.5)
        print("✓ 成功")
        time.sleep(0.5)
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False
    
    try:
        print("移动鼠标回原位置...", end=" ")
        mouse.move_to(pos[0], pos[1], duration=0.5)
        print("✓ 成功")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False
    
    print()
    return True


def test_keyboard():
    """测试键盘功能"""
    print("=" * 50)
    print("测试3：键盘功能测试")
    print("=" * 50)
    
    from keyboard_controller import KeyboardController
    keyboard = KeyboardController()
    
    try:
        print("测试特殊键识别 (Enter)...", end=" ")
        key = keyboard._get_key('enter')
        print(f"✓ 成功")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False
    
    try:
        print("测试特殊键识别 (Ctrl)...", end=" ")
        key = keyboard._get_key('ctrl')
        print(f"✓ 成功")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False
    
    try:
        print("测试单个字符识别 (a)...", end=" ")
        key = keyboard._get_key('a')
        print(f"✓ 成功")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False
    
    print()
    return True


def test_auto_controller():
    """测试自动化控制器"""
    print("=" * 50)
    print("测试4：自动化控制器测试")
    print("=" * 50)
    
    import auto_controller as ac
    
    try:
        print("测试 get_mouse_position()...", end=" ")
        pos = ac.get_mouse_position()
        print(f"✓ 成功: {pos}")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False
    
    try:
        print("测试 wait()...", end=" ")
        ac.wait(0.1)
        print("✓ 成功")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False
    
    print()
    return True


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " " * 48 + "║")
    print("║" + "  AutoControlPC - 系统测试".center(48) + "║")
    print("║" + " " * 48 + "║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    all_passed = True
    
    all_passed = test_imports() and all_passed
    all_passed = test_mouse() and all_passed
    all_passed = test_keyboard() and all_passed
    all_passed = test_auto_controller() and all_passed
    
    print("=" * 50)
    if all_passed:
        print("✓ 所有测试通过！AutoControlPC已准备就绪")
        print("=" * 50)
        print()
        print("后续步骤：")
        print("1. 查看 USAGE_GUIDE.md 了解如何使用")
        print("2. 运行 examples.py 查看使用示例")
        print("3. 在你的脚本中使用 auto_controller 模块")
        print()
        return 0
    else:
        print("✗ 某些测试失败，请检查安装是否正确")
        print("=" * 50)
        print()
        print("故障排除：")
        print("1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("2. 检查Python版本是否 >= 3.6")
        print("3. 检查是否有文件权限问题")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
