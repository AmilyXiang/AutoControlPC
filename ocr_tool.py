"""
ocr_tool.py
独立OCR工具，基于easyocr，支持截图识别和文本定位。
"""

import easyocr
from PIL import ImageGrab
import numpy as np
import cv2

class OcrTool:
    def __init__(self, lang_list=None, gpu=False):
        if lang_list is None:
            lang_list = ['en']
        self.reader = easyocr.Reader(lang_list, gpu=gpu)

    def find_text_position(self, target_text, screenshot=None, fuzzy=True):
        """
        查找目标文本在屏幕上的中心坐标。
        支持模糊匹配（Levenshtein距离<=2）。
        :param target_text: 目标字符串
        :param screenshot: PIL.Image，可选，未提供则自动截图
        :param fuzzy: 是否启用模糊匹配
        :return: (x, y) 或 None
        """
        if screenshot is None:
            screenshot = ImageGrab.grab()
        img_array = np.array(screenshot)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        results = self.reader.readtext(img_bgr)
        target_lower = target_text.lower()
        candidates = []

        def levenshtein(a, b):
            # 简单Levenshtein距离实现
            if len(a) < len(b):
                a, b = b, a
            if len(b) == 0:
                return len(a)
            previous_row = range(len(b) + 1)
            for i, c1 in enumerate(a):
                current_row = [i + 1]
                for j, c2 in enumerate(b):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

        for (bbox, text, confidence) in results:
            text_stripped = text.strip()
            text_lower = text_stripped.lower()
            match = False
            # 精确或包含匹配
            if target_lower in text_lower or text_lower in target_lower:
                match = True
            # 模糊匹配
            elif fuzzy and levenshtein(target_lower, text_lower) <= 2:
                match = True
            if match:
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                center_x = int(sum(x_coords) / 4)
                center_y = int(sum(y_coords) / 4)
                candidates.append((center_x, center_y, confidence))
        if candidates:
            # 返回置信度最高的
            best = max(candidates, key=lambda x: x[2])
            return (best[0], best[1])
        return None

# 示例用法
if __name__ == '__main__':
    ocr = OcrTool(['en', 'ch_sim'], gpu=False)
    pos = ocr.find_text_position('Cui Ji')
    if pos:
        print(f"找到 'Cui Ji' 位置: {pos}")
    else:
        print("未找到 'Cui Ji'")
