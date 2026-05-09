import numpy as np
import librosa
import sys
from pathlib import Path


def detect_silence(audio_path, rms_threshold=0.001, noise_percentile=10, snr_threshold=3.0):
    """
    判断音频文件是否为静音（排除环境噪音）
    
    Args:
        audio_path: 音频文件路径
        rms_threshold: RMS能量绝对阈值
        noise_percentile: 噪音底层百分位数（10表示最低10%）
        snr_threshold: 信噪比阈值
    
    Returns:
        dict:
            - is_silence: 是否为静音
            - rms_mean: 平均RMS能量
            - noise_floor: 环境噪音底层
            - snr: 信噪比
    """
    # 加载音频
    y, sr = librosa.load(audio_path, sr=None, mono=True)
    
    # 分帧计算RMS（帧长512采样点）
    frame_length = 512
    hop_length = 256
    frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
    rms_values = np.sqrt(np.mean(frames ** 2, axis=0))
    
    # 计算噪音底层（环境噪音）
    noise_floor = np.percentile(rms_values, noise_percentile)
    
    # 计算有效信号能量（排除噪音底层）
    signal_frames = rms_values[rms_values > noise_floor * 1.5]
    signal_rms = np.mean(signal_frames) if len(signal_frames) > 0 else np.mean(rms_values)
    
    # 计算信噪比
    snr = signal_rms / (noise_floor + 1e-10)
    
    # 判定：整体RMS很低 且 信噪比小于阈值 = 静音
    rms_mean = np.mean(rms_values)
    is_silence = (rms_mean < rms_threshold) and (snr < snr_threshold)
    
    return {
        "is_silence": is_silence,
        "rms_mean": round(rms_mean, 4),
        "noise_floor": round(noise_floor, 4),
        "snr": round(snr, 2)
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python silence_detect.py <audio_file> [--rms THRESHOLD] [--percentile NUM] [--snr THRESHOLD]")
        print("\nExample:")
        print("  python silence_detect.py test.wav")
        print("  python silence_detect.py test.wav --rms 0.01 --percentile 15 --snr 2.5")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    # 检查文件存在
    if not Path(audio_file).exists():
        print(f"File not found: {audio_file}")
        sys.exit(1)
    
    # 解析参数
    rms_th = float(sys.argv[sys.argv.index("--rms") + 1]) if "--rms" in sys.argv else 0.001
    percentile = float(sys.argv[sys.argv.index("--percentile") + 1]) if "--percentile" in sys.argv else 10
    snr_th = float(sys.argv[sys.argv.index("--snr") + 1]) if "--snr" in sys.argv else 3.0
    
    # 执行检测
    result = detect_silence(audio_file, rms_threshold=rms_th, noise_percentile=percentile, snr_threshold=snr_th)
    
    # 输出结果
    print(f"\nSilence detection result: {Path(audio_file).name}")
    print(f"  Is silence: {'yes' if result['is_silence'] else 'no'}")
    print(f"  Mean RMS: {result['rms_mean']}")
    print(f"  Noise floor: {result['noise_floor']}")
    print(f"  SNR: {result['snr']}")


if __name__ == "__main__":
    main()