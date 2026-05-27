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
    'o': '0OQa',
    'a': 'oue',
    'l': '1I|i',
    'I': '1l|i',
    'B': '8',
    'G': '6',
    'Z': '2z',
    'g': '9q',
    'y': 'u',
    'e': 'c0s',         # 'e' misread as '0' or 's'
    'C': 'c',
    'c': 'eC(o',
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
    # edit-distance match: tolerate up to 25% character errors/length diff
    for t in texts:
        if _edit_distance_match(expected, t):
            return t
    # edit-distance on joined
    if _edit_distance_match(expected, joined):
        return joined
    return None


def _edit_distance_match(expected: str, actual: str, threshold: float = 0.25) -> bool:
    """Check if normalized edit distance ratio is within threshold."""
    a = _normalize_ocr(expected)
    b = _normalize_ocr(actual)
    if not a or not b:
        return False
    # Quick reject: length difference alone exceeds threshold
    max_len = max(len(a), len(b))
    if abs(len(a) - len(b)) > max_len * threshold:
        return False
    dist = _levenshtein(a, b)
    return dist <= max_len * threshold


def _levenshtein(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            curr_row.append(min(curr_row[j] + 1, prev_row[j + 1] + 1, prev_row[j] + cost))
        prev_row = curr_row
    return prev_row[-1]


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
_cached_camera_names = {}

# Debug switch: controls only whether cropped images are saved.
# Raw images are always saved.
_SAVE_CUT_DEBUG_IMAGE = False

# Analyzer (YOLO + PaddleOCR) is shared across all devices
_analyzer = None


def _ensure_vision_loaded(device_id="1", camera_name=""):
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
        # 检查是否有其他设备已经打开了相同 camera_name 的摄像头，若有则共用
        existing = None
        for did, name in _cached_camera_names.items():
            if name == camera_name and did in _grabbers:
                existing = did
                break
        if existing:
            _grabbers[device_id] = _grabbers[existing]
            _cached_camera_names[device_id] = camera_name
            print(f"[DECT] Camera[{device_id}] sharing camera (name={camera_name}) with device {existing}")
        else:
            from dect.image.getImage import CameraGrabber
            t_cam0 = _t.time()
            _grabbers[device_id] = CameraGrabber(camera_name=camera_name)
            _grabbers[device_id].start_grabbing()
            _cached_camera_names[device_id] = camera_name
            t_cam1 = _t.time()
            print(f"[DECT][T] vision camera[{device_id}] (name={camera_name}): {t_cam1 - t_cam0:.3f}s")
    elif _cached_camera_names.get(device_id) != camera_name:
        # Camera name changed, recreate
        try:
            _grabbers[device_id].stop_grabbing()
            _grabbers[device_id].close()
        except Exception:
            pass
        from dect.image.getImage import CameraGrabber
        _grabbers[device_id] = CameraGrabber(camera_name=camera_name)
        _grabbers[device_id].start_grabbing()
        _cached_camera_names[device_id] = camera_name
        print(f"[DECT] Camera[{device_id}] re-initialized with name={camera_name}")
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

    def __init__(self, model="8262", com_port=None, device_id="1", camera_name=""):
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
        _ensure_vision_loaded(device_id, camera_name)
        self.grabber = _grabbers[device_id]
        self.analyzer = _analyzer
        print(f"[DECT] Init complete: device={device_id}, model={model}")

    def _ensure_vision(self):
        """Ensure vision subsystem is available (uses module-level cache)."""
        if self.grabber is None:
            camera_name = _cached_camera_names.get(self.device_id, "")
            _ensure_vision_loaded(self.device_id, camera_name)
            self.grabber = _grabbers[self.device_id]
            self.analyzer = _analyzer

    # ---- Motion actions ----

    def press_key(self, key_name, press_type="short"):
        """Move to key position and press it."""
        if key_name not in self.layout.layout:
            raise AssertionError(f"[DECT] Unknown key: '{key_name}', available: {list(self.layout.layout.keys())}")
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

    def press_and_verify(self, key_name, expected, press_type="short"):
        """Press key and immediately verify screen (no inter-step delay)."""
        self.press_key(key_name, press_type=press_type)
        return self.verify_screen(expected)

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
            raise AssertionError(f"[DECT] Image capture failed for device {self.device_id}")
        # 保存调试图片
        debug_dir = os.path.join(os.path.dirname(__file__), "png", "debug")
        os.makedirs(debug_dir, exist_ok=True)
        cam_name = _cached_camera_names.get(self.device_id, "unknown")
        timestamp = _time.strftime("%Y%m%d_%H%M%S")
        debug_path = os.path.join(debug_dir, f"{cam_name}_{timestamp}.png")
        cv2.imwrite(debug_path, img_color)
        print(f"[DECT] Debug image saved: {debug_path}")

        img_cut = straighten_screen_from_np(img_color)
        t3 = _time.time()
        print(f"[DECT][T] straighten_screen: {t3 - t2:.3f}s")
        if _SAVE_CUT_DEBUG_IMAGE:
            cut_debug_dir = os.path.join(debug_dir, "cut")
            os.makedirs(cut_debug_dir, exist_ok=True)
            cut_debug_path = os.path.join(cut_debug_dir, f"{cam_name}_{timestamp}_cut.png")
            if img_cut is not None:
                cv2.imwrite(cut_debug_path, img_cut)
                print(f"[DECT] Cut debug image saved: {cut_debug_path}")
            else:
                print("[DECT] Cut debug image skipped: screen straighten returned None")
        if img_cut is None:
            print("[DECT] Screen straighten failed, using raw image for analysis")
            img_cut = img_color

        self._last_cut_img = img_cut  # save for retry without re-capture
        self.analyzer.get_results(img_cut)
        t4 = _time.time()
        print(f"[DECT][T] YOLO predict: {t4 - t3:.3f}s")

        result = self.analyzer.get_icon_text()
        t5 = _time.time()
        print(f"[DECT][T] OCR get_icon_text: {t5 - t4:.3f}s")
        print(f"[DECT][T] capture_and_analyze total: {t5 - t0:.3f}s")
        print(f"[DECT] Analysis result: {result}")
        return result

    def verify_screen(self, expected, _retry=1):
        """Capture screen and verify against expected content.
        
        Args:
            expected: dict, e.g. {"text": "10000", "signal": true}
                - key "text": verify text content is present
                - other keys: verify icon/element exists
            _retry: number of retries on failure (re-analyze same image)
        
        Returns:
            bool: True if all checks pass.
        """
        import time as _time
        tv0 = _time.time()
        result = self.capture_and_analyze()
        tv1 = _time.time()
        print(f"[DECT][T] verify_screen capture+analyze: {tv1 - tv0:.3f}s")

        all_pass = self._check_expected(expected, result)

        tv2 = _time.time()
        print(f"[DECT][T] verify_screen total: {tv2 - tv0:.3f}s ({'PASS' if all_pass else 'FAIL'})")
        if not all_pass:
            if _retry > 0:
                print(f"[DECT] Verify failed, re-running YOLO+OCR on same image... (retries left: {_retry})")
                # Re-analyze the same cut image (already stored in self.analyzer from last capture)
                self.analyzer.get_results(self._last_cut_img)
                result = self.analyzer.get_icon_text()
                print(f"[DECT] Re-analysis result: {result}")
                all_pass = self._check_expected(expected, result)
                if all_pass:
                    print(f"[DECT] Verify PASS on retry")
                    return True
                return self.verify_screen.__wrapped__(self, expected, _retry - 1) if False else self._verify_fail(expected, result, _retry - 1)
            raise AssertionError(f"[DECT] Screen verify FAIL on device {self.device_id}: expected={expected}, actual={result}")
        return True

    def _verify_fail(self, expected, result, _retry):
        """Handle remaining retries after re-analysis still fails."""
        if _retry > 0:
            print(f"[DECT] Still failed, re-running YOLO+OCR... (retries left: {_retry})")
            self.analyzer.get_results(self._last_cut_img)
            result = self.analyzer.get_icon_text()
            print(f"[DECT] Re-analysis result: {result}")
            all_pass = self._check_expected(expected, result)
            if all_pass:
                print(f"[DECT] Verify PASS on retry")
                return True
            return self._verify_fail(expected, result, _retry - 1)
        raise AssertionError(f"[DECT] Screen verify FAIL on device {self.device_id}: expected={expected}, actual={result}")

    def _check_expected(self, expected, result):
        """Check result against expected, return True if all pass."""
        all_pass = True
        for key, value in expected.items():
            if key == "text":
                texts = result.get("text", [])
                if isinstance(value, str):
                    expected_texts = [value]
                elif isinstance(value, (list, tuple)):
                    expected_texts = list(value)
                else:
                    print(f"[DECT] Text verify FAIL: 'text' must be string or list, got {type(value).__name__}")
                    all_pass = False
                    continue

                for exp_text in expected_texts:
                    if not isinstance(exp_text, str):
                        print(f"[DECT] Text verify FAIL: text item must be string, got {type(exp_text).__name__}")
                        all_pass = False
                        continue
                    # 0) regex pattern match (prefix "re:")
                    if exp_text.startswith('re:'):
                        import re as _re
                        pattern = exp_text[3:]
                        joined = ' '.join(texts)
                        if any(_re.search(pattern, t) for t in texts) or _re.search(pattern, joined):
                            print(f"[DECT] Text verify PASS (regex): pattern '{pattern}' matched")
                        else:
                            print(f"[DECT] Text verify FAIL (regex): pattern '{pattern}' not matched in {texts}")
                            all_pass = False
                        continue
                    # 1) exact match on single element
                    if exp_text in texts:
                        print(f"[DECT] Text verify PASS: '{exp_text}'")
                    else:
                        # 2) joined adjacent elements (YOLO may split one line into multiple boxes)
                        joined = ' '.join(texts)
                        if exp_text in joined:
                            print(f"[DECT] Text verify PASS (joined match): '{exp_text}' found in '{joined}'")
                        else:
                            # 3) fuzzy OCR match (handles common mis-reads like 6→G, 0→O, s→5)
                            fuzzy_hit = _fuzzy_find(exp_text, texts)
                            if fuzzy_hit is not None:
                                print(f"[DECT] Text verify PASS (fuzzy match): '{exp_text}' ~ '{fuzzy_hit}'")
                            else:
                                print(f"[DECT] Text verify FAIL: expected '{exp_text}', actual {texts}")
                                all_pass = False
            else:
                if key in result:
                    print(f"[DECT] Icon verify PASS: '{key}'")
                else:
                    print(f"[DECT] Icon verify FAIL: '{key}' not found")
                    all_pass = False
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
    
    com_port and camera_name are read from devices.json via dect.config.
    """
    from dect.config.settings import get_device_config
    cfg = get_device_config(device_id)
    _controllers[device_id] = DectController(model=model,
                                              com_port=cfg.com_port,
                                              device_id=device_id,
                                              camera_name=cfg.camera_name)
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
    _cached_camera_names.clear()
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
