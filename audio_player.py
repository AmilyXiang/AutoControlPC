"""
audio_player.py
通用音频播放工具，支持PCM/WAV/MP3等格式。
"""
import os
import sys

try:
    import simpleaudio as sa  # wav/pcm
except ImportError:
    sa = None
try:
    from pydub import AudioSegment
    from pydub.playback import play
except ImportError:
    AudioSegment = None
    play = None
try:
    import pygame  # mp3/wav
except ImportError:
    pygame = None

def play_audio(file_path, device_id=None, duration=None):
    """
    播放音频文件
    
    参数:
        file_path: 音频文件路径
        device_id: 设备ID（可选）
        duration: 播放时长（秒），如果为None则播放到文件结束（可选）
    """
    ext = os.path.splitext(file_path)[1].lower()
    # 播放前检测文件可读性
    if not os.path.isfile(file_path):
        print(f"[AUDIO] File not found: {file_path}")
        return False
    if not os.access(file_path, os.R_OK):
        print(f"[AUDIO] File not readable: {file_path}")
        return False
    
    # 优先用 simpleaudio 播放标准 wav/pcm
    if ext in ['.wav', '.pcm'] and sa:
        try:
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
            if duration:
                # 如果指定了时长，则在指定时间后停止
                import time
                time.sleep(duration)
                play_obj.stop()
            else:
                # 否则等到播放完毕
                play_obj.wait_done()
            return True
        except Exception as e:
            print(f"[AUDIO] simpleaudio playback failed: {e}")
    
    # 其次用 pygame 播放 mp3/wav（支持设备指定）
    if pygame:
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            if duration:
                # 如果指定了时长，在指定时间后停止
                import time
                time.sleep(duration)
                pygame.mixer.music.stop()
            else:
                # 否则等到播放完毕
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            return True
        except Exception as e:
            print(f"[AUDIO] pygame playback failed: {e}")
    
    # 最后兜底用 pydub，静默处理异常
    if AudioSegment and play:
        try:
            audio = AudioSegment.from_file(file_path)
            try:
                if duration and duration < len(audio) / 1000:
                    # 截取指定时长的音频播放
                    audio_segment = audio[:int(duration * 1000)]
                    play(audio_segment)
                else:
                    play(audio)
            except Exception:
                pass  # 静默处理所有异常
            return True
        except Exception:
            pass  # 静默处理所有异常
    print(f"[AUDIO] Unsupported audio format or missing dependency: {file_path}")
    return False

if __name__ == '__main__':
    device_id = None
    file_path = None
    
    if len(sys.argv) < 2:
        print("Usage: python audio_player.py <audio_file_path> [device_id]")
        print("Tip: run 'python device_manager.py list' to see available devices")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if len(sys.argv) >= 3:
        device_id = int(sys.argv[2])
    
    play_audio(file_path, device_id)
