"""
icon_detector.py
图标检测模块，基于OpenCV模板匹配。
用法：给定模板图片和待检测截图，返回所有匹配位置。
"""
import cv2
import numpy as np
from PIL import ImageGrab, Image

class IconDetector:
    def __init__(self, threshold=0.8):
        self.threshold = threshold  # 匹配阈值，越高越严格

    def find_icons(self, template_path, screenshot=None, max_results=5):
        """
        检测截图中所有与模板相似的图标位置。
        :param template_path: 模板图片路径
        :param screenshot: PIL.Image 或 None（自动截图）
        :param max_results: 返回最多匹配数
        :return: [(center_x, center_y, score), ...]
        """
        if screenshot is None:
            screenshot = ImageGrab.grab()
        img_rgb = np.array(screenshot)
        if img_rgb.shape[2] == 4:
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_RGBA2RGB)
        # 转为灰度图
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        template = cv2.imread(template_path)
        if template is None:
            raise FileNotFoundError(f"模板图片未找到: {template_path}")
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        h, w = template_gray.shape[:2]
        res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= self.threshold)
        matches = []
        for idx, pt in enumerate(zip(*loc[::-1])):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            score = res[pt[1], pt[0]]
            matches.append((center_x, center_y, score))
            # 保存匹配区域截图
            crop = img_rgb[pt[1]:pt[1]+h, pt[0]:pt[0]+w]
            try:
                crop_img = Image.fromarray(crop)
                crop_img.save(f"debug_match_{idx+1}.png")
            except Exception as e:
                print(f"保存匹配区域截图失败: {e}")
        # 去重（防止重叠区域多次计数）
        matches = self._nms(matches, w, h)
        matches = sorted(matches, key=lambda x: -x[2])[:max_results]
        return matches

    def _nms(self, matches, w, h, iou_thresh=0.3):
        # 非极大值抑制，去除重叠框
        boxes = [((x-w//2, y-h//2, x+w//2, y+h//2), score) for x, y, score in matches]
        boxes = sorted(boxes, key=lambda x: -x[1])
        keep = []
        while boxes:
            box, score = boxes.pop(0)
            keep.append((
                (box[0]+box[2])//2,
                (box[1]+box[3])//2,
                score
            ))
            boxes = [b for b in boxes if self._iou(box, b[0]) < iou_thresh]
        return keep

    def _iou(self, boxA, boxB):
        # 计算两个框的交并比
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
        return iou

# 示例用法
if __name__ == '__main__':
    detector = IconDetector(threshold=0.8)
    matches = detector.find_icons('icon_template.png')
    for i, (x, y, score) in enumerate(matches):
        print(f"匹配{i+1}: 位置=({x},{y}), 置信度={score:.2f}")
