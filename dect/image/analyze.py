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
        try:
            result = self.ocr.ocr(img_np)
            if not result or result[0] is None:
                print("未发现任何文字")
                return []
            return result
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
                if self.model.names[int(box.cls)] != "text":
                    if self.model.names[int(box.cls)] not in res_dect:
                        res_dect[self.model.names[int(box.cls)]] = []
                    res_dect[self.model.names[int(box.cls)]].append(box.xyxy[0].cpu().numpy().astype(int))
                else:
                    image_text = self.img[box.xyxy[0][1].cpu().numpy().astype(int):box.xyxy[0][3].cpu().numpy().astype(int), box.xyxy[0][0].cpu().numpy().astype(int):box.xyxy[0][2].cpu().numpy().astype(int)]
                    img_for_ocr = self.ocr.preprocess_crop(image_text)
                    print(img_for_ocr.shape, img_for_ocr.dtype)
                    
                    if img_for_ocr is None:
                        print("错误：无法加载图片，请检查路径是否正确。")
                    result = self.ocr.process_screen_ocr(img_for_ocr)
                    if result:
                        for i, res in enumerate(result):
                            if self.model.names[int(box.cls)] not in res_dect:
                                res_dect[self.model.names[int(box.cls)]] = []
                            res_dect[self.model.names[int(box.cls)]].append(res[0][0])
        return res_dect
