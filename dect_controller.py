"""DECT phone controller for AutoControlPC testcase runner.

Wraps dect module's motion control and vision processing into
an interface compatible with the XML testcase step dispatcher.
"""

import sys
import os
import json

# Ensure project root is in Python path so package imports stay stable
_project_root = os.path.normpath(os.path.dirname(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# Lazy-initialized singleton
_controller = None


class DectController:
    """High-level controller for DECT phone hardware interaction."""

    def __init__(self, model="8262", com_port=None):
        # Ensure MvCamera SDK path is set up
        _mvcam_env = os.getenv('MVCAM_COMMON_RUNENV')
        if _mvcam_env:
            _mv_path = os.path.join(_mvcam_env, "Samples", "Python", "MvImport")
            if _mv_path not in sys.path:
                sys.path.append(_mv_path)

        from dect.move.moveserial import SerialInterface
        from dect.move.move import MoveInterface
        from dect.move.layout import KeyLayout

        self.layout = KeyLayout(model)
        self.ser = SerialInterface(port=com_port)
        self.mover = MoveInterface(self.ser)
        self.grabber = None
        self.analyzer = None
        print(f"[DECT] 初始化完成: model={model}")

    def _ensure_vision(self):
        """Lazy-init vision subsystem (camera + analyzer) on first use."""
        if self.grabber is None:
            from dect.image.getImage import CameraGrabber
            from dect.image.analyze import Analyze_icon_text
            self.grabber = CameraGrabber()
            self.analyzer = Analyze_icon_text()
            print("[DECT] 视觉子系统初始化完成")

    # ---- Motion actions ----

    def press_key(self, key_name, press_type="short"):
        """Move to key position and press it."""
        if key_name not in self.layout.layout:
            print(f"[DECT] 未知按键: {key_name}")
            return False
        x, y = self.layout.layout[key_name]
        self.mover.move_plain(x, y, self.mover.Z)
        self.ser.receive_response()
        if press_type == "long":
            self.mover.long_press()
        else:
            self.mover.short_press()
        self.ser.receive_response()
        print(f"[DECT] 按键 '{key_name}' ({press_type}) 完成")
        return True

    def move_to(self, x, y):
        """Move finger to arbitrary (x, y) coordinate."""
        self.mover.move_plain(x, y, self.mover.Z)
        self.ser.receive_response()

    def origin(self):
        """Return finger to origin position."""
        self.mover.origin()
        self.ser.receive_response()
        print("[DECT] 已回原点")

    # ---- Vision actions ----

    def capture_and_analyze(self):
        """Capture screen image and run YOLO + OCR analysis.
        
        Returns:
            dict: e.g. {"text": ["10000"], "signal": [...coords...]}
        """
        self._ensure_vision()
        from dect.image.cut_image import straighten_screen_from_np
        self.grabber.start_grabbing()
        img_color = self.grabber.grab_image()
        self.grabber.stop_grabbing()
        if img_color is None:
            print("[DECT] 抓图失败")
            return {}
        img_cut = straighten_screen_from_np(img_color)
        self.analyzer.get_results(img_cut)
        result = self.analyzer.get_icon_text()
        print(f"[DECT] 分析结果: {result}")
        return result

    def verify_screen(self, expected):
        """Capture screen and verify against expected content.
        
        Args:
            expected: dict, e.g. {"text": "10000", "signal": true}
                - key "text": verify text content is present
                - other keys: verify icon/element exists
        
        Returns:
            bool: True if all checks pass.
        """
        result = self.capture_and_analyze()
        all_pass = True
        for key, value in expected.items():
            if key == "text":
                if value in result.get("text", []):
                    print(f"[DECT] 文本验证成功: '{value}'")
                else:
                    print(f"[DECT] 文本验证失败: 期望 '{value}', 实际 {result.get('text', [])}")
                    all_pass = False
            else:
                if key in result:
                    print(f"[DECT] 图标验证成功: '{key}'")
                else:
                    print(f"[DECT] 图标验证失败: '{key}' 未找到")
                    all_pass = False
        return all_pass

    def close(self):
        """Release all hardware resources."""
        if self.grabber:
            self.grabber.close()
        self.ser.close()
        self.mover.origin()
        print("[DECT] 资源已释放")


def get_dect_controller():
    """Get the singleton DectController (lazy init)."""
    global _controller
    if _controller is None:
        raise RuntimeError("[DECT] 控制器未初始化，请先执行 dect init 步骤")
    return _controller


def init_dect_controller(model="8262", com_port=None):
    """Initialize the singleton DectController."""
    global _controller
    if _controller is not None:
        _controller.close()
    _controller = DectController(model=model, com_port=com_port)
    return _controller


def close_dect_controller():
    """Close and release the singleton DectController."""
    global _controller
    if _controller is not None:
        _controller.close()
        _controller = None
