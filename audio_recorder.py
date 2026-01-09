"""
audio_recorder.py
支持选择声卡进行录音，保存为wav文件。
依赖：sounddevice、soundfile
"""
import sounddevice as sd
import soundfile as sf
import sys
import threading
import time

# 全局录音控制
_recording_state = {
    'is_recording': False,
    'stream': None,
    'data': None,
    'lock': threading.Lock()
}

def list_input_devices():
    print("可用输入设备（声卡）：")
    for idx, dev in enumerate(sd.query_devices()):
        if dev['max_input_channels'] > 0:
            print(f"[{idx}] {dev['name']}")

def record_audio(device_idx, duration, out_wav, samplerate=44100, channels=1):
    """同步录音，阻塞直到时长结束或被停止"""
    print(f"录音设备: {device_idx}, 时长: {duration}s, 输出: {out_wav}")
    try:
        with _recording_state['lock']:
            _recording_state['is_recording'] = True
        
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16', device=device_idx)
        sd.wait()
        
        with _recording_state['lock']:
            _recording_state['is_recording'] = False
        
        sf.write(out_wav, recording, samplerate)
        print(f"录音完成，已保存: {out_wav}")
    except Exception as e:
        print(f"录音失败: {e}")
    finally:
        with _recording_state['lock']:
            _recording_state['is_recording'] = False

def stop_record():
    """停止当前录音"""
    with _recording_state['lock']:
        if _recording_state['is_recording']:
            sd.stop()
            _recording_state['is_recording'] = False
            print("[AUDIO] 录音已停止")
        else:
            print("[AUDIO] 当前没有正在进行的录音")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python audio_recorder.py list | record <device_idx> <duration秒> <输出wav文件> | stop")
        sys.exit(1)
    if sys.argv[1] == 'list':
        list_input_devices()
    elif sys.argv[1] == 'record' and len(sys.argv) == 5:
        device_idx = int(sys.argv[2])
        duration = float(sys.argv[3])
        out_wav = sys.argv[4]
        record_audio(device_idx, duration, out_wav)
    elif sys.argv[1] == 'stop':
        stop_record()
    else:
        print("参数错误。用法: python audio_recorder.py list | record <device_idx> <duration秒> <输出wav文件> | stop")

