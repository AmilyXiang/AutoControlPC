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

def record_audio(device_idx, duration, out_wav, samplerate=44100, channels=1):
    """同步录音，阻塞直到时长结束或被停止"""
    print(f"[AUDIO] Recording device: {device_idx}, duration: {duration}s, output: {out_wav}")
    try:
        with _recording_state['lock']:
            _recording_state['is_recording'] = True
        
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16', device=device_idx)
        sd.wait()
        
        with _recording_state['lock']:
            _recording_state['is_recording'] = False
        
        sf.write(out_wav, recording, samplerate)
        print(f"[AUDIO] Recording done, saved: {out_wav}")
    except Exception as e:
        print(f"[AUDIO] Recording failed: {e}")
    finally:
        with _recording_state['lock']:
            _recording_state['is_recording'] = False

def stop_record():
    """停止当前录音"""
    with _recording_state['lock']:
        if _recording_state['is_recording']:
            sd.stop()
            _recording_state['is_recording'] = False
            print("[AUDIO] Recording stopped")
        else:
            print("[AUDIO] No recording in progress")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python audio_recorder.py record <device_idx> <duration_sec> <output.wav> | stop")
        print("Tip: run 'python device_manager.py list' to see available devices")
        sys.exit(1)
    if sys.argv[1] == 'record' and len(sys.argv) == 5:
        device_idx = int(sys.argv[2])
        duration = float(sys.argv[3])
        out_wav = sys.argv[4]
        record_audio(device_idx, duration, out_wav)
    elif sys.argv[1] == 'stop':
        stop_record()
    else:
        print("Invalid args. Usage: python audio_recorder.py record <device_idx> <duration_sec> <output.wav> | stop")

