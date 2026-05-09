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
        """Preprocess a YOLO text-crop before OCR.

        Steps:
        1. Upscale small crops so OCR has enough pixels to work with.
        2. Convert to grayscale → CLAHE for contrast enhancement
           (helps with faded / low-contrast text like '60 sec' on blue bg).
        3. Sharpen to make edges crisper.
        4. Return as 3-channel (PaddleOCR expects BGR).
        """
        import numpy as np

        h, w = crop_img.shape[:2]
        # --- 1. Upscale small crops (target ≥ 64 px height) ---
        scale = max(2.0, 64.0 / h) if h < 64 else 2.0
        scaled = cv2.resize(crop_img, None, fx=scale, fy=scale,
                            interpolation=cv2.INTER_CUBIC)

        # --- 2. Grayscale + CLAHE ---
        gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # --- 3. Sharpen ---
        blurred = cv2.GaussianBlur(enhanced, (0, 0), sigmaX=2)
        sharpened = cv2.addWeighted(enhanced, 1.5, blurred, -0.5, 0)

        # --- 4. Light denoise ---
        denoised = cv2.medianBlur(sharpened, 3)

        # Convert back to 3-channel for PaddleOCR
        return cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
    def process_screen_ocr(self, img_np):
        """
        Run OCR on image, return [(text, score), ...].
        Compatible with PaddleOCR 3.x new return format.
        """
        try:
            result = self.ocr.ocr(img_np)
            if not result:
                print("[OCR] No text found.")
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
            print(f"[OCR] Exception: {e}")
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
                    print(f"[OCR] Crop region: ({x1},{y1})-({x2},{y2}), shape={img_for_ocr.shape}")
                    
                    if img_for_ocr is None:
                        print("[OCR] ERROR: Unable to load image, please check path.")
                        continue

                    # Dual-pass OCR: try preprocessed first, fall back to raw
                    # if raw gives higher confidence (handles cases where
                    # preprocessing hurts good images but helps bad ones).
                    ocr_enhanced = self.ocr.process_screen_ocr(img_for_ocr)
                    ocr_raw = self.ocr.process_screen_ocr(image_text)

                    # Pick the pass with higher average confidence
                    def _avg_conf(results):
                        if not results:
                            return 0.0
                        return sum(s for _, s in results) / len(results)

                    if _avg_conf(ocr_enhanced) >= _avg_conf(ocr_raw):
                        ocr_result = ocr_enhanced
                        ocr_tag = "enhanced"
                    else:
                        ocr_result = ocr_raw
                        ocr_tag = "raw"

                    if ocr_result:
                        if "text" not in res_dect:
                            res_dect["text"] = []
                        for text_str, confidence in ocr_result:
                            print(f"[OCR] Recognized text [{ocr_tag}]: '{text_str}' (confidence: {confidence:.4f})")
                            res_dect["text"].append(text_str)
        return res_dect
