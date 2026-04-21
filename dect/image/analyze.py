import cv2
from ultralytics import YOLO
import time
import os
import ssl

from . import cut_image
from . import getImage

# 核心：关闭 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

# 告诉 requests 库不要检查证书
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# 禁用模型源检查，加速启动
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
# 顺便禁用掉一些不必要的日志输出
os.environ['PADDLE_SDK_LOG_LEVEL'] = '3'

from paddleocr import PaddleOCR

# 默认模型路径：相对于本文件所在目录
_DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "best_openvino_model")

class Yolo_icon_text:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = _DEFAULT_MODEL_DIR
        self.model = YOLO(model_path)
    def predict(self, img):
        print("prepare to predict...")
        results = self.model.predict(img, conf=0.5)
        return results

class Paddle_ocr:
    def __init__(self):
        self.ocr = PaddleOCR(
            lang='en',
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=True,
        )
    def preprocess_crop(self, crop_img):
        denoised = cv2.medianBlur(crop_img, 5)
        return denoised
    def process_screen_ocr(self, img_np):
        """
        对图片进行OCR识别，返回 [(text, score), ...] 格式的结果。
        适配 PaddleOCR 3.x 新返回格式。
        """
        try:
            result = self.ocr.ocr(img_np)
            if not result:
                print("未发现任何文字")
                return []
            # PaddleOCR 3.x 返回 list of dict，每个 dict 含 rec_texts, rec_scores
            texts = []
            for page in result:
                if page is None:
                    continue
                if isinstance(page, dict):
                    rec_texts = page.get('rec_texts', [])
                    rec_scores = page.get('rec_scores', [])
                    for t, s in zip(rec_texts, rec_scores):
                        texts.append((t, s))
                else:
                    # 兼容旧格式 [[box, (text, score)], ...]
                    if isinstance(page, list):
                        for line in page:
                            if line and len(line) >= 2:
                                texts.append((str(line[1][0]), float(line[1][1])))
            return texts
        except Exception as e:
            print(f"解析出错: {e}")
            return []

class Analyze_icon_text:
    def __init__(self):
        self.yolo = Yolo_icon_text()
        self.model = self.yolo.model 
        self.ocr = Paddle_ocr()
    def get_results(self, img):
        self.img = img
        self.results = self.yolo.predict(img)
        return self.results
    def get_icon_text(self, results=None):
        if results is None:
            results = self.results
        res_dect = {}
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_name = self.model.names[int(box.cls)]
                if cls_name != "text":
                    if cls_name not in res_dect:
                        res_dect[cls_name] = []
                    res_dect[cls_name].append(box.xyxy[0].cpu().numpy().astype(int))
                else:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    image_text = self.img[y1:y2, x1:x2]
                    img_for_ocr = self.ocr.preprocess_crop(image_text)
                    print(f"[OCR] 裁剪区域: ({x1},{y1})-({x2},{y2}), shape={img_for_ocr.shape}")
                    
                    if img_for_ocr is None:
                        print("错误：无法加载图片，请检查路径是否正确。")
                        continue
                    ocr_result = self.ocr.process_screen_ocr(img_for_ocr)
                    if ocr_result:
                        if "text" not in res_dect:
                            res_dect["text"] = []
                        for text_str, confidence in ocr_result:
                            print(f"[OCR] 识别文字: '{text_str}' (置信度: {confidence:.4f})")
                            res_dect["text"].append(text_str)
        return res_dect
