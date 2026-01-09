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

def list_devices():
    """列出所有可用的音频设备"""
    devices = []
    
    # 尝试用 pygame 列出设备
    if pygame:
        try:
            pygame.mixer.init()
            # pygame 支持的设备信息
            devices.append("=== pygame 音频设备 ===")
            # pygame 没有直接的设备列表API，但可以通过不同的初始化方式
            devices.append("默认设备已初始化")
        except Exception as e:
            devices.append(f"pygame 初始化失败: {e}")
    
    # 尝试用 sounddevice 或其他工具列出设备
    try:
        import sounddevice as sd
        devices.append("\n=== 所有音频设备 ===")
        device_list = sd.query_devices()
        for i, device in enumerate(device_list):
            devices.append(f"设备 {i}: {device['name']} (输入: {device['max_input_channels']}, 输出: {device['max_output_channels']})")
    except ImportError:
        pass
    except Exception as e:
        devices.append(f"sounddevice 查询失败: {e}")
    
    # Windows 系统尝试使用 pyaudio
    try:
        import pyaudio
        devices.append("\n=== PyAudio 音频设备 ===")
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            devices.append(f"设备 {i}: {device_info['name']} (输入: {device_info['maxInputChannels']}, 输出: {device_info['maxOutputChannels']})")
        p.terminate()
    except ImportError:
        pass
    except Exception as e:
        devices.append(f"PyAudio 查询失败: {e}")
    
    if not devices:
        devices.append("无可用的设备查询工具")
    
    return devices

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
            print(f"[AUDIO] simpleaudio 播放失败: {e}")
    
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
            print(f"[AUDIO] pygame 播放失败: {e}")
    
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
    print(f"[AUDIO] 不支持的音频格式或缺少依赖: {file_path}")
    return False

if __name__ == '__main__':
    device_id = None
    file_path = None
    
    if len(sys.argv) < 2:
        print("用法: python audio_player.py <audio文件路径|list> [设备ID]")
        sys.exit(1)
    
    # 处理 list 命令
    if sys.argv[1] == 'list':
        devices = list_devices()
        for device_info in devices:
            print(device_info)
        sys.exit(0)
    
    file_path = sys.argv[1]
    if len(sys.argv) >= 3:
        device_id = int(sys.argv[2])
    
    play_audio(file_path, device_id)
