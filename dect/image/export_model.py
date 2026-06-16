"""
One-time utility: export best.pt to OpenVINO format.
Run this script when the .pt model is updated and needs re-export.

Usage:
    python -m dect.image.export_model
"""
import os
from ultralytics import YOLO

_MODEL_PT = os.path.join(os.path.dirname(__file__), "best.pt")


def export_to_openvino(model_path=None, dynamic=False):
    if model_path is None:
        model_path = _MODEL_PT
    model = YOLO(model_path)
    model.export(format="openvino", dynamic=dynamic)
    print(f"Export complete: {model_path} -> openvino")


if __name__ == "__main__":
    export_to_openvino()
