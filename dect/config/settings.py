import json
import os
from dataclasses import dataclass, field

_CONFIG_DIR = os.path.dirname(__file__)
_DEVICES_FILE = os.path.join(_CONFIG_DIR, "devices.json")

# 缓存，避免重复读文件
_device_configs = None


@dataclass
class DeviceConfig:
    com_port: str
    camera_index: int = 0
    ext_number: str = ""

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
