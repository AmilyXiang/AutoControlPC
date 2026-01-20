import sys
import os
import pyperclip
import csv
import time

def save_clipboard_to_txt(filename):
    # 支持动态时间变量 {now}
    if '{now}' in filename:
        now_str = time.strftime('%Y%m%d_%H%M%S')
        filename = filename.replace('{now}', now_str)
    content = pyperclip.paste()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"已保存剪贴板内容到 {filename}")

def save_clipboard_to_csv(filename):
    # 支持动态时间变量 {now}
    if '{now}' in filename:
        now_str = time.strftime('%Y%m%d_%H%M%S')
        filename = filename.replace('{now}', now_str)
    content = pyperclip.paste()
    # 按行分割，每行再按逗号分割
    rows = [row.split(',') for row in content.splitlines()]
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"已保存剪贴板内容到 {filename} (csv格式)")

def main():
    if len(sys.argv) < 3:
        print("用法: python clipboard_save.py <txt/csv> <输出文件名>")
        return
    fmt = sys.argv[1].lower()
    filename = sys.argv[2]
    if fmt == 'txt':
        save_clipboard_to_txt(filename)
    elif fmt == 'csv':
        save_clipboard_to_csv(filename)
    else:
        print("暂不支持该格式，只支持txt和csv")

if __name__ == '__main__':
    main()
