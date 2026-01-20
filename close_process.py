import subprocess

def close_process_by_name(process_name):
    """
    关闭所有指定名称的进程
    :param process_name: 进程名（如 notepad.exe）
    :return: None
    """
    try:
        subprocess.run(['taskkill', '/F', '/IM', process_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"已关闭所有 {process_name} 进程")
    except subprocess.CalledProcessError as e:
        print(f"关闭 {process_name} 失败：{e}")

# 示例用法
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("用法: python close_process.py <进程名.exe>")
    else:
        process_name = sys.argv[1]
        close_process_by_name(process_name)
