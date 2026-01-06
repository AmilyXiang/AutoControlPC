"""
network_event.py
网络事件枚举 - 统一定义所有网络事件类型
"""
from enum import Enum


class NetworkEvent(Enum):
    """网络事件类型枚举"""
    
    # 系统事件
    INIT = "init"                          # 初始化网络
    STOP = "stop"                          # 停止网络
    READY = "ready"                        # 就绪信号
    
    # 通话事件
    CALL_START = "call_start"              # 开始呼叫
    CALL_RINGING = "call_ringing"          # 来电铃声
    CALL_ANSWER = "call_answer"            # 接听电话
    CALL_END = "call_end"                  # 结束通话
    CALL_REJECT = "call_reject"            # 拒绝接听
    
    # 音视频事件
    AUDIO_START = "audio_start"            # 开始音频
    AUDIO_STOP = "audio_stop"              # 停止音频
    VIDEO_START = "video_start"            # 开始视频
    VIDEO_STOP = "video_stop"              # 停止视频
    
    # 消息事件
    MESSAGE = "message"                    # 通用消息
    DATA = "data"                          # 通用数据
    
    # 自定义事件
    CUSTOM = "custom"                      # 自定义事件
    
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


# 预定义的常用事件名称
EVENTS = {
    'init': NetworkEvent.INIT,
    'stop': NetworkEvent.STOP,
    'ready': NetworkEvent.READY,
    'call_start': NetworkEvent.CALL_START,
    'call_ringing': NetworkEvent.CALL_RINGING,
    'call_answer': NetworkEvent.CALL_ANSWER,
    'call_end': NetworkEvent.CALL_END,
    'call_reject': NetworkEvent.CALL_REJECT,
    'audio_start': NetworkEvent.AUDIO_START,
    'audio_stop': NetworkEvent.AUDIO_STOP,
    'video_start': NetworkEvent.VIDEO_START,
    'video_stop': NetworkEvent.VIDEO_STOP,
    'message': NetworkEvent.MESSAGE,
    'data': NetworkEvent.DATA,
}


if __name__ == '__main__':
    # 打印所有事件
    print("可用的网络事件类型:")
    for name, event in EVENTS.items():
        print(f"  {name:20} = {event.value}")
