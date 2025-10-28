#!/usr/bin/env python3
"""
音频波形可视化工具
使用matplotlib显示音频波形，直观对比白噪音添加效果
"""

import os
import sys
import logging
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import wave
import struct

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioWaveformVisualizer:
    """音频波形可视化器"""
    
    def __init__(self):
        self.processor = FFmpegAudioProcessor()
        
    def extract_audio_data(self, audio_file: str) -> tuple:
        """提取音频数据"""
        try:
            # 使用ffmpeg提取音频数据
            cmd = [
                'ffmpeg', '-i', audio_file, '-f', 'wav', '-acodec', 'pcm_s16le', 
                '-ar', '44100', '-ac', '1', '-y', 'temp_audio.wav'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"音频提取失败: {result.stderr}")
                return None, None
            
            # 读取WAV文件
            with wave.open('temp_audio.wav', 'rb') as wav_file:
                frames = wav_file.readframes(-1)
                sample_rate = wav_file.getframerate()
                
                # 转换为numpy数组
                if wav_file.getsampwidth() == 2:  # 16-bit
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                else:
                    audio_data = np.frombuffer(frames, dtype=np.int8)
                
                # 转换为浮点数并归一化
                audio_data = audio_data.astype(np.float32) / 32768.0
                
                # 清理临时文件
                if os.path.exists('temp_audio.wav'):
                    os.remove('temp_audio.wav')
                
                return audio_data, sample_rate
                
        except Exception as e:
            logger.error(f"音频数据提取异常: {e}")
            return None, None
    
    def plot_waveform_comparison(self, original_file: str, processed_file: str, 
                               output_image: str = "waveform_comparison.png"):
        """绘制波形对比图"""
        logger.info("=" * 60)
        logger.info("生成音频波形对比图")
        logger.info("=" * 60)
        
        # 提取音频数据
        logger.info("提取原始音频数据...")
        original_data, sample_rate = self.extract_audio_data(original_file)
        
        logger.info("提取处理后音频数据...")
        processed_data, sample_rate = self.extract_audio_data(processed_file)
        
        if original_data is None or processed_data is None:
            logger.error("音频数据提取失败")
            return False
        
        # 创建时间轴
        duration_original = len(original_data) / sample_rate
        duration_processed = len(processed_data) / sample_rate
        
        time_original = np.linspace(0, duration_original, len(original_data))
        time_processed = np.linspace(0, duration_processed, len(processed_data))
        
        # 创建图形
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
        
        # 原始音频波形
        ax1.plot(time_original, original_data, 'b-', linewidth=0.5, alpha=0.7)
        ax1.set_title('原始音频波形 (无白噪音)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('振幅', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(-1, 1)
        
        # 处理后音频波形
        ax2.plot(time_processed, processed_data, 'r-', linewidth=0.5, alpha=0.7)
        ax2.set_title('处理后音频波形 (添加18%白噪音)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('振幅', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(-1, 1)
        
        # 叠加对比
        ax3.plot(time_original, original_data, 'b-', linewidth=0.5, alpha=0.5, label='原始音频')
        ax3.plot(time_processed, processed_data, 'r-', linewidth=0.5, alpha=0.5, label='处理后音频')
        ax3.set_title('波形叠加对比', fontsize=14, fontweight='bold')
        ax3.set_xlabel('时间 (秒)', fontsize=12)
        ax3.set_ylabel('振幅', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(-1, 1)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        logger.info(f"波形对比图已保存: {output_image}")
        
        # 显示图片
        plt.show()
        
        return True
    
    def plot_spectrum_comparison(self, original_file: str, processed_file: str,
                               output_image: str = "spectrum_comparison.png"):
        """绘制频谱对比图"""
        logger.info("=" * 60)
        logger.info("生成音频频谱对比图")
        logger.info("=" * 60)
        
        # 提取音频数据
        original_data, sample_rate = self.extract_audio_data(original_file)
        processed_data, sample_rate = self.extract_audio_data(processed_file)
        
        if original_data is None or processed_data is None:
            logger.error("音频数据提取失败")
            return False
        
        # 计算频谱
        fft_original = np.fft.fft(original_data)
        fft_processed = np.fft.fft(processed_data)
        
        # 频率轴
        freqs = np.fft.fftfreq(len(original_data), 1/sample_rate)
        
        # 只取正频率部分
        positive_freqs = freqs[:len(freqs)//2]
        magnitude_original = np.abs(fft_original[:len(fft_original)//2])
        magnitude_processed = np.abs(fft_processed[:len(fft_processed)//2])
        
        # 创建图形
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
        
        # 原始音频频谱
        ax1.semilogy(positive_freqs, magnitude_original, 'b-', linewidth=0.5)
        ax1.set_title('原始音频频谱 (无白噪音)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('幅度', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0, sample_rate//2)
        
        # 处理后音频频谱
        ax2.semilogy(positive_freqs, magnitude_processed, 'r-', linewidth=0.5)
        ax2.set_title('处理后音频频谱 (添加18%白噪音)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('幅度', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, sample_rate//2)
        
        # 频谱差异
        spectrum_diff = magnitude_processed - magnitude_original
        ax3.plot(positive_freqs, spectrum_diff, 'g-', linewidth=0.5)
        ax3.set_title('频谱差异 (处理后 - 原始)', fontsize=14, fontweight='bold')
        ax3.set_xlabel('频率 (Hz)', fontsize=12)
        ax3.set_ylabel('幅度差异', fontsize=12)
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim(0, sample_rate//2)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        logger.info(f"频谱对比图已保存: {output_image}")
        
        # 显示图片
        plt.show()
        
        return True
    
    def plot_multiple_volume_comparison(self, test_files: list, 
                                      output_image: str = "volume_comparison.png"):
        """绘制多音量级别对比图"""
        logger.info("=" * 60)
        logger.info("生成多音量级别对比图")
        logger.info("=" * 60)
        
        # 创建图形
        fig, axes = plt.subplots(len(test_files), 1, figsize=(15, 3*len(test_files)))
        if len(test_files) == 1:
            axes = [axes]
        
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        
        for i, file_info in enumerate(test_files):
            audio_file = file_info['file']
            name = file_info['name']
            noise_vol = file_info['noise_vol']
            
            logger.info(f"处理文件 {i+1}: {name}")
            
            # 提取音频数据
            audio_data, sample_rate = self.extract_audio_data(audio_file)
            
            if audio_data is None:
                logger.error(f"文件 {audio_file} 处理失败")
                continue
            
            # 创建时间轴
            duration = len(audio_data) / sample_rate
            time_axis = np.linspace(0, duration, len(audio_data))
            
            # 绘制波形
            color = colors[i % len(colors)]
            axes[i].plot(time_axis, audio_data, color=color, linewidth=0.5, alpha=0.7)
            axes[i].set_title(f'{name} - 白噪音音量: {noise_vol*100:.0f}%', 
                            fontsize=12, fontweight='bold')
            axes[i].set_ylabel('振幅', fontsize=10)
            axes[i].grid(True, alpha=0.3)
            axes[i].set_ylim(-1, 1)
            
            if i == len(test_files) - 1:
                axes[i].set_xlabel('时间 (秒)', fontsize=12)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        logger.info(f"多音量对比图已保存: {output_image}")
        
        # 显示图片
        plt.show()
        
        return True
    
    def create_audio_analysis_report(self, original_file: str, processed_file: str):
        """创建音频分析报告"""
        logger.info("=" * 60)
        logger.info("音频分析报告")
        logger.info("=" * 60)
        
        # 提取音频数据
        original_data, sample_rate = self.extract_audio_data(original_file)
        processed_data, sample_rate = self.extract_audio_data(processed_file)
        
        if original_data is None or processed_data is None:
            logger.error("音频数据提取失败")
            return
        
        # 计算统计信息
        original_rms = np.sqrt(np.mean(original_data**2))
        processed_rms = np.sqrt(np.mean(processed_data**2))
        
        original_max = np.max(np.abs(original_data))
        processed_max = np.max(np.abs(processed_data))
        
        original_std = np.std(original_data)
        processed_std = np.std(processed_data)
        
        # 计算信噪比
        signal_power = np.mean(original_data**2)
        noise_power = np.mean((processed_data - original_data)**2)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
        
        logger.info("音频统计信息:")
        logger.info(f"  原始音频 RMS: {original_rms:.6f}")
        logger.info(f"  处理后音频 RMS: {processed_rms:.6f}")
        logger.info(f"  RMS 增加: {((processed_rms - original_rms) / original_rms * 100):.2f}%")
        logger.info("")
        logger.info(f"  原始音频 最大振幅: {original_max:.6f}")
        logger.info(f"  处理后音频 最大振幅: {processed_max:.6f}")
        logger.info("")
        logger.info(f"  原始音频 标准差: {original_std:.6f}")
        logger.info(f"  处理后音频 标准差: {processed_std:.6f}")
        logger.info(f"  标准差增加: {((processed_std - original_std) / original_std * 100):.2f}%")
        logger.info("")
        logger.info(f"  信噪比 (SNR): {snr:.2f} dB")
        logger.info("")
        
        # 文件大小对比
        if os.path.exists(original_file) and os.path.exists(processed_file):
            original_size = os.path.getsize(original_file)
            processed_size = os.path.getsize(processed_file)
            
            logger.info("文件大小对比:")
            logger.info(f"  原始文件: {original_size:,} bytes")
            logger.info(f"  处理后文件: {processed_size:,} bytes")
            logger.info(f"  大小增加: {processed_size - original_size:,} bytes")
            logger.info(f"  增加比例: {((processed_size - original_size) / original_size * 100):.1f}%")

def main():
    """主函数"""
    logger.info("音频波形可视化工具")
    
    # 初始化可视化器
    visualizer = AudioWaveformVisualizer()
    
    # 查找测试文件
    test_files = []
    edgetts_dir = Path("../../20_输出文件_处理完成的音频文件")
    if edgetts_dir.exists():
        for folder in edgetts_dir.iterdir():
            if folder.is_dir():
                for audio_file in folder.iterdir():
                    if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                        test_files.append(str(audio_file))
                        break
                if test_files:
                    break
    
    if not test_files:
        logger.error("未找到测试文件")
        return
    
    original_file = test_files[0]
    logger.info(f"使用测试文件: {Path(original_file).name}")
    
    # 查找处理后的文件
    processed_files = []
    current_dir = Path(".")
    
    # 查找各种处理后的文件
    for pattern in ["audible_test_*.m4a", "comparison_*.m4a", "test_white_noise_*.m4a"]:
        processed_files.extend(list(current_dir.glob(pattern)))
    
    if not processed_files:
        logger.error("未找到处理后的文件")
        return
    
    # 选择第一个处理后的文件进行对比
    processed_file = str(processed_files[0])
    logger.info(f"使用处理后文件: {Path(processed_file).name}")
    
    # 生成波形对比图
    visualizer.plot_waveform_comparison(original_file, processed_file)
    
    # 生成频谱对比图
    visualizer.plot_spectrum_comparison(original_file, processed_file)
    
    # 创建音频分析报告
    visualizer.create_audio_analysis_report(original_file, processed_file)
    
    # 如果有多个测试文件，生成多音量对比图
    if len(processed_files) > 1:
        test_file_info = []
        for pf in processed_files[:5]:  # 限制最多5个文件
            # 从文件名提取信息
            filename = pf.name
            if "audible_test" in filename:
                if "轻微可听" in filename:
                    noise_vol = 0.15
                    name = "轻微可听"
                elif "刚好可听" in filename:
                    noise_vol = 0.18
                    name = "刚好可听"
                elif "明显可听" in filename:
                    noise_vol = 0.20
                    name = "明显可听"
                elif "清晰可听" in filename:
                    noise_vol = 0.22
                    name = "清晰可听"
                elif "强烈可听" in filename:
                    noise_vol = 0.25
                    name = "强烈可听"
                else:
                    continue
                
                test_file_info.append({
                    'file': str(pf),
                    'name': name,
                    'noise_vol': noise_vol
                })
        
        if test_file_info:
            visualizer.plot_multiple_volume_comparison(test_file_info)
    
    logger.info("\n" + "=" * 60)
    logger.info("可视化分析完成!")
    logger.info("=" * 60)
    logger.info("生成的图片文件:")
    logger.info("  - waveform_comparison.png: 波形对比图")
    logger.info("  - spectrum_comparison.png: 频谱对比图")
    logger.info("  - volume_comparison.png: 多音量对比图")
    logger.info("")
    logger.info("图片说明:")
    logger.info("  - 波形图: 显示音频的时域特征")
    logger.info("  - 频谱图: 显示音频的频域特征")
    logger.info("  - 对比图: 直观显示白噪音添加效果")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
