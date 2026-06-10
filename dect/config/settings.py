import json
import os
from dataclasses import dataclass, field

_CONFIG_DIR = os.path.dirname(__file__)
_DEVICES_FILE = os.path.join(_CONFIG_DIR, "devices.json")
_MODEL_PROFILES_FILE = os.path.join(_CONFIG_DIR, "model_profiles.json")

# 缓存，避免重复读文件
_device_configs = None
_model_profiles = None


@dataclass
class DeviceConfig:
    com_port: str
    model: str = "8262"
    camera_name: str = ""
    exposure_time: float = 50000
    ext_number: str = ""
    ext_name: str = ""
    emergency_number: str = ""
    IPEI_hex: str = ""
    IPEI_dec: str = ""
    IPEI_oct: str = ""
    lock_pin: str = ""
    new_lock_pin: str = ""
    wrong_pin: str = ""
    reset_pin_code: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "DeviceConfig":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def _load_devices() -> dict[str, DeviceConfig]:
    global _device_configs
    if _device_configs is None:
        with open(_DEVICES_FILE, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        _device_configs = {did: DeviceConfig.from_dict(cfg) for did, cfg in raw.items()}
    return _device_configs


def get_device_config(device_id: str = "1") -> DeviceConfig:
    """获取指定设备的配置"""
    configs = _load_devices()
    if device_id not in configs:
        raise ValueError(f"Unknown device_id '{device_id}', available: {list(configs.keys())}")
    return configs[device_id]


def reload_devices():
    """强制重新加载配置文件"""
    global _device_configs
    _device_configs = None
    _load_devices()


def _load_model_profiles() -> dict:
    global _model_profiles
    if _model_profiles is None:
        with open(_MODEL_PROFILES_FILE, 'r', encoding='utf-8') as f:
            _model_profiles = json.load(f)
    return _model_profiles


def get_model_capabilities(model: str) -> list:
    """获取指定型号的 capabilities 列表"""
    profiles = _load_model_profiles()
    profile = profiles.get(model, {})
    return profile.get("capabilities", [])


def model_has_capability(model: str, cap: str) -> bool:
    """判断指定型号是否具有某 capability"""
    return cap in get_model_capabilities(model)


def get_navigation_path(model: str, path_name: str) -> list:
    """获取指定型号的导航路径（按键序列）。
    
    Args:
        model: 型号名（如 '8262', '8234'）
        path_name: 导航路径名（如 'settings_security', 'test_sw_info'）
    
    Returns:
        按键名列表，如 ['menu', 'down', 'ok', ...]
    
    Raises:
        ValueError: 型号或路径名不存在
    """
    profiles = _load_model_profiles()
    profile = profiles.get(model)
    if not profile:
        raise ValueError(f"Unknown model '{model}', available: {list(profiles.keys())}")
    navigation = profile.get("navigation", {})
    if path_name not in navigation:
        raise ValueError(f"Unknown navigation path '{path_name}' for model '{model}', available: {list(navigation.keys())}")
    return navigation[path_name]


def list_navigation_paths(model: str) -> list:
    """列出指定型号所有可用的导航路径名"""
    profiles = _load_model_profiles()
    profile = profiles.get(model, {})
    return list(profile.get("navigation", {}).keys())
