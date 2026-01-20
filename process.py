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
        print(f"已关闭所有 {process_name} 进程")
    except subprocess.CalledProcessError as e:
        print(f"关闭 {process_name} 失败：{e}")

def run_bat_file(bat_path):
    """
    运行指定的bat批处理文件
    :param bat_path: bat文件路径
    :return: None
    """
    if not os.path.isfile(bat_path):
        print(f"[BAT] 文件不存在: {bat_path}")
        return
    try:
        subprocess.run([bat_path], shell=True, check=True)
        print(f"[BAT] 已运行: {bat_path}")
    except subprocess.CalledProcessError as e:
        print(f"[BAT] 运行失败: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("用法: python process.py <close/runbat> <参数>")
    else:
        cmd = sys.argv[1]
        arg = sys.argv[2]
        if cmd == 'close':
            close_process_by_name(arg)
        elif cmd == 'runbat':
            run_bat_file(arg)
        else:
            print("未知命令，只支持close和runbat")
