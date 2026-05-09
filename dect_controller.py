"""DECT phone controller for AutoControlPC testcase runner.

Wraps dect module's motion control and vision processing into
an interface compatible with the XML testcase step dispatcher.
"""

import sys
import os
import json
import re

# Ensure project root is in Python path so package imports stay stable
_project_root = os.path.normpath(os.path.dirname(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# ---------------------------------------------------------------------------
# OCR fuzzy-match helpers
# ---------------------------------------------------------------------------

# Common OCR substitution pairs  (correct_char → chars that OCR often outputs)
_OCR_CONFUSIONS = {
    '0': 'OoQeD',      # '0' misread as 'e' seen in "60 sec"→"See 0c"
    '1': 'lI|i',
    '2': 'Zz',
    '5': 'Ss$',
    '6': 'GbS',         # '6' misread as 'S' seen in "60 sec"→"See 0c"
    '7': 'T',
    '8': 'B&',
    '9': 'gq',
    'S': '5s$',
    's': '5S$e',
    'O': '0oD',
    'o': '0OQ',
    'l': '1I|i',
    'I': '1l|i',
    'B': '8',
    'G': '6',
    'Z': '2z',
    'g': '9q',
    'e': 'c0s',         # 'e' misread as '0' or 's'
    'c': 'eC(',
    'D': '0O',
    'q': '9g',
    'T': '7',
}


def _normalize_ocr(text: str) -> str:
    """Lowercase, collapse whitespace, strip."""
    return re.sub(r'\s+', '', text).lower()


def _ocr_fuzzy_eq(expected: str, actual: str) -> bool:
    """Check if *expected* and *actual* match under common OCR confusions.

    Rules (applied after normalisation):
    - Characters match literally, OR
    - The actual char is a known confusion substitute of the expected char, OR
    - The expected char is a known confusion substitute of the actual char
      (bidirectional check).
    """
    a = _normalize_ocr(expected)
    b = _normalize_ocr(actual)
    if len(a) != len(b):
        return False
    for ce, ca in zip(a, b):
        if ce == ca:
            continue
        # Forward: actual char in expected char's confusion set
        fwd = _OCR_CONFUSIONS.get(ce, '')
        if ca.lower() in fwd.lower():
            continue
        # Reverse: expected char in actual char's confusion set
        rev = _OCR_CONFUSIONS.get(ca, '')
        if ce.lower() in rev.lower():
            continue
        return False
    return True


def _fuzzy_find(expected: str, texts: list) -> str | None:
    """Try to find *expected* in *texts* using fuzzy OCR matching.

    1. Try each single text element.
    2. Try the joined string with a sliding window of len(expected).
    Returns the matched actual string or None.
    """
    for t in texts:
        if _ocr_fuzzy_eq(expected, t):
            return t
    # sliding window over joined text
    joined = ' '.join(texts)
    norm_exp = _normalize_ocr(expected)
    norm_joined = _normalize_ocr(joined)
    exp_len = len(norm_exp)
    for i in range(len(norm_joined) - exp_len + 1):
        window = norm_joined[i:i + exp_len]
        if _ocr_fuzzy_eq(expected, window):
            return joined
    return None


# Lazy-initialized controllers by device_id
_controllers = {}

# Module-level singletons — survive across controller init/close cycles
# Keyed by device_id for multi-device support
_grabbers = {}
_serials = {}
_movers = {}
_layouts = {}
_cached_models = {}
_cached_com_ports = {}
_cached_camera_indices = {}

# Analyzer (YOLO + PaddleOCR) is shared across all devices
_analyzer = None


def _ensure_vision_loaded(device_id="1", camera_index=0):
    """Load YOLO + PaddleOCR models (shared) and start camera for specified device."""
    global _analyzer
    import time as _t
    t0 = _t.time()

    if _analyzer is None:
        from dect.image.getImage import CameraGrabber
        from dect.image.analyze import Analyze_icon_text
        t1 = _t.time()
        print(f"[DECT][T] vision import: {t1 - t0:.3f}s")

        _analyzer = Analyze_icon_text()
        t2 = _t.time()
        print(f"[DECT][T] vision YOLO+OCR load: {t2 - t1:.3f}s")
    else:
        print("[DECT] Vision models already loaded, reusing")

    if device_id not in _grabbers:
        # 检查是否有其他设备已经打开了相同 camera_index 的摄像头，若有则共用
        existing = None
        for did, idx in _cached_camera_indices.items():
            if idx == camera_index and did in _grabbers:
                existing = did
                break
        if existing:
            _grabbers[device_id] = _grabbers[existing]
            _cached_camera_indices[device_id] = camera_index
            print(f"[DECT] Camera[{device_id}] sharing camera (index={camera_index}) with device {existing}")
        else:
            from dect.image.getImage import CameraGrabber
            t_cam0 = _t.time()
            _grabbers[device_id] = CameraGrabber(camera_index=camera_index)
            _grabbers[device_id].start_grabbing()
            _cached_camera_indices[device_id] = camera_index
            t_cam1 = _t.time()
            print(f"[DECT][T] vision camera[{device_id}] (index={camera_index}): {t_cam1 - t_cam0:.3f}s")
    elif _cached_camera_indices.get(device_id) != camera_index:
        # Camera index changed, recreate
        try:
            _grabbers[device_id].stop_grabbing()
            _grabbers[device_id].close()
        except Exception:
            pass
        from dect.image.getImage import CameraGrabber
        _grabbers[device_id] = CameraGrabber(camera_index=camera_index)
        _grabbers[device_id].start_grabbing()
        _cached_camera_indices[device_id] = camera_index
        print(f"[DECT] Camera[{device_id}] re-initialized with index={camera_index}")
    else:
        print(f"[DECT] Camera[{device_id}] already open, reusing")

    t_end = _t.time()
    print(f"[DECT][T] vision total (device {device_id}): {t_end - t0:.3f}s")
    print(f"[DECT] Vision subsystem initialized for device {device_id}")


def _ensure_motion_loaded(device_id, model, com_port):
    """Open serial port and build motion/layout for a specific device."""
    if (device_id in _serials and
            _cached_models.get(device_id) == model and
            _cached_com_ports.get(device_id) == com_port):
        print(f"[DECT] Motion/serial[{device_id}] already open (model={model}, port={com_port}), reusing")
        return
    # Close previous if params changed
    if device_id in _serials:
        try:
            _serials[device_id].close()
        except Exception:
            pass
    from dect.move.moveserial import SerialInterface
    from dect.move.move import MoveInterface
    from dect.move.layout import KeyLayout
    _layouts[device_id] = KeyLayout(model)
    _serials[device_id] = SerialInterface(port=com_port)
    _movers[device_id] = MoveInterface(_serials[device_id])
    _cached_models[device_id] = model
    _cached_com_ports[device_id] = com_port
    print(f"[DECT] Motion/serial[{device_id}] initialized (model={model}, port={com_port})")


class DectController:
    """High-level controller for DECT phone hardware interaction."""

    def __init__(self, model="8262", com_port=None, device_id="1", camera_index=0):
        self.device_id = device_id
        # Ensure MvCamera SDK path is set up
        _mvcam_env = os.getenv('MVCAM_COMMON_RUNENV')
        if _mvcam_env:
            _mv_path = os.path.join(_mvcam_env, "Samples", "Python", "MvImport")
            if _mv_path not in sys.path:
                sys.path.append(_mv_path)

        _ensure_motion_loaded(device_id, model, com_port)
        self.layout = _layouts[device_id]
        self.ser = _serials[device_id]
        self.mover = _movers[device_id]

        # Eagerly load vision at init time so first capture/verify is fast
        _ensure_vision_loaded(device_id, camera_index)
        self.grabber = _grabbers[device_id]
        self.analyzer = _analyzer
        print(f"[DECT] Init complete: device={device_id}, model={model}")

    def _ensure_vision(self):
        """Ensure vision subsystem is available (uses module-level cache)."""
        if self.grabber is None:
            camera_index = _cached_camera_indices.get(self.device_id, 0)
            _ensure_vision_loaded(self.device_id, camera_index)
            self.grabber = _grabbers[self.device_id]
            self.analyzer = _analyzer

    # ---- Motion actions ----

    def press_key(self, key_name, press_type="short"):
        """Move to key position and press it."""
        if key_name not in self.layout.layout:
            print(f"[DECT] Unknown key: {key_name}")
            return False
        x, y = self.layout.layout[key_name]
        self.mover.move_plain(x, y, self.mover.Z)
        self.ser.receive_response()
        if press_type == "long":
            self.mover.long_press()
        else:
            self.mover.short_press()
        self.ser.receive_response()
        print(f"[DECT] Key '{key_name}' ({press_type}) done")
        return True

    def move_to(self, x, y):
        """Move finger to arbitrary (x, y) coordinate."""
        self.mover.move_plain(x, y, self.mover.Z)
        self.ser.receive_response()

    def origin(self):
        """Return finger to origin position."""
        self.mover.origin()
        self.ser.receive_response()
        print("[DECT] Returned to origin")

    # ---- Vision actions ----

    def capture_and_analyze(self):
        """Capture screen image and run YOLO + OCR analysis.
        
        Returns:
            dict: e.g. {"text": ["10000"], "signal": [...coords...]}
        """
        import cv2, os, time as _time
        t0 = _time.time()
        self._ensure_vision()
        t1 = _time.time()
        print(f"[DECT][T] ensure_vision: {t1 - t0:.3f}s")

        from dect.image.cut_image import straighten_screen_from_np
        img_color = self.grabber.grab_image()
        t2 = _time.time()
        print(f"[DECT][T] grab_image: {t2 - t1:.3f}s")
        if img_color is None:
            print("[DECT] Image capture failed")
            return {}
        # 保存调试图片
        debug_dir = os.path.join(os.path.dirname(__file__), "png", "debug")
        os.makedirs(debug_dir, exist_ok=True)
        debug_path = os.path.join(debug_dir, f"capture_{int(_time.time())}.png")
        cv2.imwrite(debug_path, img_color)
        print(f"[DECT] Debug image saved: {debug_path}")

        img_cut = straighten_screen_from_np(img_color)
        t3 = _time.time()
        print(f"[DECT][T] straighten_screen: {t3 - t2:.3f}s")
        if img_cut is None:
            print("[DECT] Screen straighten failed, using raw image for analysis")
            img_cut = img_color

        self.analyzer.get_results(img_cut)
        t4 = _time.time()
        print(f"[DECT][T] YOLO predict: {t4 - t3:.3f}s")

        result = self.analyzer.get_icon_text()
        t5 = _time.time()
        print(f"[DECT][T] OCR get_icon_text: {t5 - t4:.3f}s")
        print(f"[DECT][T] capture_and_analyze total: {t5 - t0:.3f}s")
        print(f"[DECT] Analysis result: {result}")
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
        import time as _time
        tv0 = _time.time()
        result = self.capture_and_analyze()
        tv1 = _time.time()
        print(f"[DECT][T] verify_screen capture+analyze: {tv1 - tv0:.3f}s")

        all_pass = True
        for key, value in expected.items():
            if key == "text":
                texts = result.get("text", [])
                # 1) exact match on single element
                if value in texts:
                    print(f"[DECT] Text verify PASS: '{value}'")
                else:
                    # 2) joined adjacent elements (YOLO may split one line into multiple boxes)
                    joined = ' '.join(texts)
                    if value in joined:
                        print(f"[DECT] Text verify PASS (joined match): '{value}' found in '{joined}'")
                    else:
                        # 3) fuzzy OCR match (handles common mis-reads like 6→G, 0→O, s→5)
                        fuzzy_hit = _fuzzy_find(value, texts)
                        if fuzzy_hit is not None:
                            print(f"[DECT] Text verify PASS (fuzzy match): '{value}' ~ '{fuzzy_hit}'")
                        else:
                            print(f"[DECT] Text verify FAIL: expected '{value}', actual {texts}")
                            all_pass = False
            else:
                if key in result:
                    print(f"[DECT] Icon verify PASS: '{key}'")
                else:
                    print(f"[DECT] Icon verify FAIL: '{key}' not found")
                    all_pass = False
        tv2 = _time.time()
        print(f"[DECT][T] verify_screen total: {tv2 - tv0:.3f}s ({'PASS' if all_pass else 'FAIL'})")
        return all_pass

    def close(self):
        """Detach from cached resources. Nothing is destroyed — all reused next init."""
        self.grabber = None
        self.analyzer = None
        self.ser = None
        self.mover = None
        self.layout = None
        print("[DECT] Controller detached (all resources cached for reuse)")


def get_dect_controller(device_id="1"):
    """Get the DectController for the specified device (lazy init)."""
    if device_id not in _controllers:
        raise RuntimeError(f"[DECT] Controller for device '{device_id}' not initialized, run 'dect init' step first")
    return _controllers[device_id]


def init_dect_controller(model="8262", device_id="1"):
    """Initialize a DectController for the specified device.
    
    com_port and camera_index are read from devices.json via dect.config.
    """
    from dect.config.settings import get_device_config
    cfg = get_device_config(device_id)
    _controllers[device_id] = DectController(model=model,
                                              com_port=cfg.com_port,
                                              device_id=device_id,
                                              camera_index=cfg.camera_index)
    return _controllers[device_id]


def close_dect_controller(device_id="1"):
    """Close and release the DectController for the specified device."""
    if device_id in _controllers:
        _controllers[device_id].close()
        del _controllers[device_id]


def destroy_all():
    """Fully release ALL hardware (serial, camera, models). Call at process exit only."""
    global _analyzer
    # Close all controllers
    for device_id in list(_controllers.keys()):
        _controllers[device_id].close()
    _controllers.clear()
    # Close all cameras (deduplicate shared grabbers)
    closed_grabbers = set()
    for device_id, grabber in list(_grabbers.items()):
        if id(grabber) not in closed_grabbers:
            closed_grabbers.add(id(grabber))
            try:
                grabber.stop_grabbing()
                grabber.close()
            except Exception:
                pass
    _grabbers.clear()
    _cached_camera_indices.clear()
    _analyzer = None
    # Close all serial ports
    for device_id, serial in list(_serials.items()):
        try:
            serial.close()
        except Exception:
            pass
    _serials.clear()
    _movers.clear()
    _layouts.clear()
    _cached_models.clear()
    _cached_com_ports.clear()
    print("[DECT] All resources fully released")
