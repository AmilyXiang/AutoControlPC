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

def play_audio(file_path, device_id=None):
    ext = os.path.splitext(file_path)[1].lower()
    # 播放前检测文件可读性
    if not os.path.isfile(file_path):
        print(f"[AUDIO] 文件不存在: {file_path}")
        return False
    if not os.access(file_path, os.R_OK):
        print(f"[AUDIO] 文件不可读: {file_path}")
        return False
    # 优先用 simpleaudio 播放标准 wav/pcm
    if ext in ['.wav', '.pcm'] and sa:
        try:
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            return True
        except Exception as e:
            print(f"[AUDIO] simpleaudio 播放失败: {e}")
    # 其次用 pygame 播放 mp3/wav（支持设备指定）
    if pygame:
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            return True
        except Exception as e:
            print(f"[AUDIO] pygame 播放失败: {e}")
    # 最后兜底用 pydub，静默处理异常
    if AudioSegment and play:
        try:
            audio = AudioSegment.from_file(file_path)
            try:
                play(audio)
            except Exception:
                pass  # 静默处理所有异常
            return True
        except Exception:
            pass  # 静默处理所有异常
    print(f"[AUDIO] 不支持的音频格式或缺少依赖: {file_path}")
    return False

if __name__ == '__main__':
    device_id = None
    file_path = None
    
    if len(sys.argv) < 2:
        print("用法: python audio_player.py <audio文件路径> [设备ID]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if len(sys.argv) >= 3:
        device_id = int(sys.argv[2])
    
    play_audio(file_path, device_id)
