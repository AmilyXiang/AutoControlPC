"""
device_manager.py
设备管理器，支持通过字符串名称查找音频设备ID
"""
import sounddevice as sd

# 设备配置字典，可以在这里手动配置设备昵称
DEVICE_CONFIG = {
    # 格式: "设备昵称": 设备ID
    # 例如:
    # "speakers": 0,
    # "headphones": 1,
    # "microphone": 2,
}

def get_device_list():
    """获取所有可用的音频设备列表"""
    try:
        device_list = sd.query_devices()
        return device_list
    except Exception as e:
        print(f"获取设备列表失败: {e}")
        return []

def _device_score(device_info):
    """
    计算设备的综合评分，用于多设备选择时的排序
    评分标准（从高到低）：
    1. 采样率（越高越好）
    2. 通道数（立体声 > 单声道）
    3. 是否为默认设备
    """
    score = 0
    
    # 1. 采样率评分（0-10000）
    samplerate = device_info.get('default_samplerate', 44100)
    score += int(samplerate / 100)  # 44100Hz = 441分, 48000Hz = 480分
    
    # 2. 通道数评分（0-1000）
    # 输出设备优先考虑输出通道，输入设备优先考虑输入通道
    output_channels = device_info.get('max_output_channels', 0)
    input_channels = device_info.get('max_input_channels', 0)
    max_channels = max(output_channels, input_channels)
    score += max_channels * 500  # 立体声(2通道) = 1000分, 单声道(1通道) = 500分
    
    return score

def find_device_by_name(device_name, selection_strategy='best'):
    """
    根据设备名称查找设备ID
    支持三种查找方式：
    1. 直接使用数字ID（如"0"、"25"）
    2. 使用配置文件中的昵称（如"speakers"、"headphones"）
    3. 模糊匹配设备名称（如"Realtek"、"USB"）
    
    参数:
        device_name: 设备名称或ID
        selection_strategy: 多个匹配时的选择策略
            - 'best': 选择综合评分最高的 (默认)
            - 'first': 选择第一个匹配项
            - 'all': 返回所有匹配项的列表
    
    返回: (device_id, device_info) 或 (None, None) 或 [(device_id, device_info), ...]
    """
    # 如果是纯数字，直接使用作为设备ID
    if device_name.isdigit():
        device_id = int(device_name)
        try:
            device_info = sd.query_devices(device_id)
            return device_id, device_info
        except Exception as e:
            print(f"[DeviceManager] 设备ID {device_id} 不存在: {e}")
            return None, None
    
    # 检查配置字典中的昵称
    if device_name.lower() in DEVICE_CONFIG:
        device_id = DEVICE_CONFIG[device_name.lower()]
        try:
            device_info = sd.query_devices(device_id)
            return device_id, device_info
        except Exception as e:
            print(f"[DeviceManager] 配置中的设备 '{device_name}' (ID={device_id}) 不存在: {e}")
            return None, None
    
    # 模糊匹配设备名称（支持采样率过滤）
    try:
        device_list = sd.query_devices()
        device_name_lower = device_name.lower()
        
        # 解析关键字中的采样率（如 "AH 22 M 44100"）
        target_samplerate = None
        search_name = device_name_lower
        
        # 提取采样率数字（格式: 数字 + 0）
        import re
        samplerate_match = re.search(r'\b(\d{4,6})\b', device_name_lower)
        if samplerate_match:
            potential_rate = int(samplerate_match.group(1))
            # 验证是否是合理的采样率
            valid_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 96000, 192000]
            if potential_rate in valid_rates:
                target_samplerate = potential_rate
                # 从搜索字符串中移除采样率，只保留设备名称部分
                search_name = re.sub(r'\b' + str(potential_rate) + r'\b', '', device_name_lower).strip()
        
        # 找出所有匹配的设备
        matching_devices = []
        for idx, device in enumerate(device_list):
            device_name_str = device['name'].lower()
            
            # 首先检查设备名称是否匹配
            if device_name_str.find(search_name) == -1:
                continue
            
            # 如果指定了采样率，还需要采样率也匹配
            if target_samplerate is not None:
                if int(device['default_samplerate']) != target_samplerate:
                    continue
            
            matching_devices.append((idx, device))
        
        # 根据策略选择
        if not matching_devices:
            # 如果没有找到，打印所有可用设备
            if target_samplerate:
                print(f"[DeviceManager] 未找到包含 '{search_name}' 且采样率为 {target_samplerate} Hz 的设备。")
            else:
                print(f"[DeviceManager] 未找到包含 '{device_name}' 的设备。可用设备列表:")
            list_all_devices()
            return None, None
        
        if selection_strategy == 'all':
            return matching_devices
        
        if selection_strategy == 'first':
            idx, device = matching_devices[0]
            if len(matching_devices) > 1:
                print(f"[DeviceManager] 找到 {len(matching_devices)} 个匹配 '{device_name}' 的设备，已选择第一个 (ID={idx})")
            return idx, device
        
        if selection_strategy == 'best' or selection_strategy is None:
            # 按综合评分选择最佳设备
            best_device = max(matching_devices, key=lambda x: _device_score(x[1]))
            idx, device = best_device
            
            if len(matching_devices) > 1:
                print(f"[DeviceManager] 找到 {len(matching_devices)} 个匹配 '{device_name}' 的设备:")
                # 按评分排序后显示
                sorted_devices = sorted(matching_devices, key=lambda x: _device_score(x[1]), reverse=True)
                for dev_id, dev_info in sorted_devices:
                    marker = "[Selected]" if dev_id == idx else "          "
                    channels = max(dev_info['max_output_channels'], dev_info['max_input_channels'])
                    print(f"  {marker} [ID {dev_id:2d}] 采样率 {int(dev_info['default_samplerate']):5d} Hz, {channels}通道 - {dev_info['name'][:50]}")
            
            return idx, device
        
        # 默认返回第一个
        return matching_devices[0]
        
    except Exception as e:
        print(f"[DeviceManager] 查找设备时出错: {e}")
        return None, None

def get_device_id(device_name):
    """获取设备ID，支持字符串/数字混合输入"""
    device_id, _ = find_device_by_name(str(device_name))
    return device_id

def list_all_devices():
    """列出所有可用的音频设备"""
    try:
        device_list = sd.query_devices()
        print("\n=== 所有音频设备 ===")
        for i, device in enumerate(device_list):
            input_ch = device['max_input_channels']
            output_ch = device['max_output_channels']
            print(f"[{i}] {device['name']}")
            print(f"    输入通道: {input_ch}, 输出通道: {output_ch}")
            if device['default_samplerate']:
                print(f"    默认采样率: {device['default_samplerate']}")
            print()
    except Exception as e:
        print(f"获取设备列表失败: {e}")

def config_device(nickname, device_id):
    """配置设备昵称"""
    try:
        device_info = sd.query_devices(device_id)
        DEVICE_CONFIG[nickname.lower()] = device_id
        print(f"[DeviceManager] 已配置: '{nickname}' -> ID {device_id} ({device_info['name']})")
        return True
    except Exception as e:
        print(f"[DeviceManager] 设备配置失败: {e}")
        return False

def print_device_config():
    """打印当前的设备配置"""
    if not DEVICE_CONFIG:
        print("[DeviceManager] 未配置任何设备昵称")
        return
    
    print("\n=== 设备昵称配置 ===")
    for nickname, device_id in DEVICE_CONFIG.items():
        try:
            device_info = sd.query_devices(device_id)
            print(f"'{nickname}' -> ID {device_id} ({device_info['name']})")
        except:
            print(f"'{nickname}' -> ID {device_id} (设备不可用)")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python device_manager.py list              # 列出所有设备")
        print("  python device_manager.py find <设备名称>   # 查找设备")
        print("  python device_manager.py config <昵称> <ID> # 配置设备昵称")
        print()
        list_all_devices()
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'list':
        list_all_devices()
    elif command == 'find' and len(sys.argv) > 2:
        device_name = sys.argv[2]
        device_id, device_info = find_device_by_name(device_name)
        if device_id is not None:
            print(f"[OK] 找到设备: ID={device_id}, 名称={device_info['name']}")
        else:
            print(f"[FAIL] 未找到设备: {device_name}")
    elif command == 'config' and len(sys.argv) > 3:
        nickname = sys.argv[2]
        device_id = int(sys.argv[3])
        config_device(nickname, device_id)
    else:
        print("无效的命令")
        sys.exit(1)
