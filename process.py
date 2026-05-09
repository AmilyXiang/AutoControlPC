import subprocess
import os

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

def run_bat_file(bat_path):
    """
    运行指定的bat批处理文件
    :param bat_path: bat文件路径
    :return: None
    """
    if not os.path.isfile(bat_path):
        print(f"[BAT] File not found: {bat_path}")
        return
    try:
        subprocess.run([bat_path], shell=True, check=True)
        print(f"[BAT] Executed: {bat_path}")
    except subprocess.CalledProcessError as e:
        print(f"[BAT] Execution failed: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python process.py <close/runbat> <arg>")
    else:
        cmd = sys.argv[1]
        arg = sys.argv[2]
        if cmd == 'close':
            close_process_by_name(arg)
        elif cmd == 'runbat':
            run_bat_file(arg)
        else:
            print("Unknown command, only close and runbat are supported")
