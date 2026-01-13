"""
network_event.py
网络事件枚举 - 统一定义所有网络事件类型
"""
from enum import Enum


class NetworkEvent(Enum):
    """网络事件类型枚举
    
    说明：
    - 下列为常用的预定义事件
    - 如需自定义事件，直接在XML中使用任意字符串即可，无需预定义
    - 例如：<step type="network" action="send" content="my_custom_event" data="{...}" />
    """
    
    # 系统事件
    INIT = "init"                          # 初始化网络
    STOP = "stop"                          # 停止网络
    READY = "ready"                        # 就绪信号
    
    # 通话事件
    CALL_START = "call_start"              # 开始呼叫
    CALL_ANSWER = "call_answer"            # 接听电话
    
    # 音视频事件
    AUDIO_PLAY_START = "audio_play_start"  # 音频播放开始
    AUDIO_PLAY_END = "audio_play_end"      # 音频播放结束
    RECORD_STOPPED = "record_stopped"      # 录音已停止
    
    # 自定义事件标记
    CUSTOM = "custom"                      # 用于标记自定义事件
    
    @staticmethod
    def from_string(event_str):
        """从字符串获取枚举值"""
        try:
            return NetworkEvent[event_str.upper()]
        except KeyError:
            return NetworkEvent.CUSTOM
    
    def to_string(self):
        """转换为字符串"""
        return self.value


# 预定义的常用事件名称映射
# 自定义事件可直接在XML中使用，无需在此定义
EVENTS = {
    # 系统事件
    'init': NetworkEvent.INIT,
    'stop': NetworkEvent.STOP,
    'ready': NetworkEvent.READY,
    
    # 通话事件
    'call_start': NetworkEvent.CALL_START,
    'call_answer': NetworkEvent.CALL_ANSWER,
    
    # 音视频事件
    'audio_play_start': NetworkEvent.AUDIO_PLAY_START,
    'audio_play_end': NetworkEvent.AUDIO_PLAY_END,
    'record_stopped': NetworkEvent.RECORD_STOPPED,
}


if __name__ == '__main__':
    # 打印所有事件
    print("可用的网络事件类型:")
    for name, event in EVENTS.items():
        print(f"  {name:20} = {event.value}")
