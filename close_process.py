import subprocess

def close_process_by_name(process_name):
    """
    关闭所有指定名称的进程
    :param process_name: 进程名（如 notepad.exe）
    :return: None
    """
    try:
        subprocess.run(['taskkill', '/F', '/IM', process_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Closed all {process_name} processes")
    except subprocess.CalledProcessError as e:
        print(f"Failed to close {process_name}: {e}")

# 示例用法
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python close_process.py <process_name.exe>")
    else:
        process_name = sys.argv[1]
        close_process_by_name(process_name)
