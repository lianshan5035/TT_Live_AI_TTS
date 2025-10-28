#!/usr/bin/env python3
"""
白噪音音量对比测试
生成不同音量级别的音频文件，方便您对比选择
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_volume_comparison(input_file: str):
    """创建音量对比文件"""
    logger.info("=" * 60)
    logger.info("创建白噪音音量对比文件")
    logger.info("=" * 60)
    
    # 初始化处理器
    processor = FFmpegAudioProcessor()
    
    # 获取主音频时长
    main_duration = processor.get_audio_duration(input_file)
    logger.info(f"主音频时长: {main_duration:.2f} 秒")
    
    # 白噪音文件
    white_noise_file = processor.background_sounds_dir / "white_noise.wav"
    
    # 创建对比文件
    comparison_files = []
    
    # 测试不同音量级别
    volume_tests = [
        {"noise_vol": 0.0, "mix_weight": "1 0", "name": "无白噪音", "desc": "原始音频，无背景音效"},
        {"noise_vol": 0.05, "mix_weight": "1 0.15", "name": "轻微白噪音", "desc": "5%白噪音，几乎听不出"},
        {"noise_vol": 0.08, "mix_weight": "1 0.25", "name": "标准白噪音", "desc": "8%白噪音，TikTok推荐"},
        {"noise_vol": 0.12, "mix_weight": "1 0.35", "name": "明显白噪音", "desc": "12%白噪音，较明显"},
        {"noise_vol": 0.15, "mix_weight": "1 0.4", "name": "强烈白噪音", "desc": "15%白噪音，很明显"},
        {"noise_vol": 0.20, "mix_weight": "1 0.5", "name": "过度白噪音", "desc": "20%白噪音，可能影响语音"}
    ]
    
    for i, test in enumerate(volume_tests):
        output_file = f"comparison_{i+1:02d}_{test['name'].replace(' ', '_')}.m4a"
        logger.info(f"\n创建文件 {i+1}: {test['name']} - {test['desc']}")
        
        # 构建FFmpeg命令
        cmd = ['ffmpeg', '-y']
        cmd.extend(['-i', input_file])
        
        if test['noise_vol'] > 0:
            cmd.extend(['-i', str(white_noise_file)])
            
            # 构建滤镜链
            filter_parts = [
                f'[0:a]volume=0.88,aresample=44100[main]',
                f'[1:a]volume={test["noise_vol"]},atrim=duration={main_duration}[bg0]',
                f'[main][bg0]amix=inputs=2:duration=first:weights={test["mix_weight"]}[final]'
            ]
        else:
            # 无白噪音版本
            filter_parts = [
                f'[0:a]volume=0.88,aresample=44100[final]'
            ]
        
        cmd.extend(['-filter_complex', ';'.join(filter_parts)])
        cmd.extend(['-map', '[final]'])
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '44100', '-ac', '2'])
        cmd.extend(['-f', 'mp4'])
        cmd.append(output_file)
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ 生成成功: {output_file}")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"文件大小: {file_size:,} bytes")
            
            comparison_files.append({
                'file': output_file,
                'name': test['name'],
                'desc': test['desc'],
                'noise_vol': test['noise_vol']
            })
        else:
            logger.error(f"✗ 生成失败: {result.stderr}")
    
    return comparison_files

def create_audio_analysis(input_file: str, processed_file: str):
    """创建音频分析报告"""
    logger.info("=" * 60)
    logger.info("音频分析报告")
    logger.info("=" * 60)
    
    # 获取原始文件信息
    original_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration,bit_rate,sample_rate,channels', '-of', 'csv=p=0', input_file]
    original_result = subprocess.run(original_cmd, capture_output=True, text=True)
    
    # 获取处理后文件信息
    processed_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration,bit_rate,sample_rate,channels', '-of', 'csv=p=0', processed_file]
    processed_result = subprocess.run(processed_cmd, capture_output=True, text=True)
    
    logger.info("原始音频信息:")
    if original_result.returncode == 0:
        info = original_result.stdout.strip().split(',')
        logger.info(f"  时长: {info[0]} 秒")
        logger.info(f"  比特率: {info[1]} bps")
        logger.info(f"  采样率: {info[2]} Hz")
        logger.info(f"  声道数: {info[3]}")
    
    logger.info("\n处理后音频信息:")
    if processed_result.returncode == 0:
        info = processed_result.stdout.strip().split(',')
        logger.info(f"  时长: {info[0]} 秒")
        logger.info(f"  比特率: {info[1]} bps")
        logger.info(f"  采样率: {info[2]} Hz")
        logger.info(f"  声道数: {info[3]}")
    
    # 文件大小对比
    if os.path.exists(input_file) and os.path.exists(processed_file):
        original_size = os.path.getsize(input_file)
        processed_size = os.path.getsize(processed_file)
        
        logger.info(f"\n文件大小对比:")
        logger.info(f"  原始文件: {original_size:,} bytes")
        logger.info(f"  处理后文件: {processed_size:,} bytes")
        logger.info(f"  增加大小: {processed_size - original_size:,} bytes")
        logger.info(f"  增加比例: {((processed_size - original_size) / original_size * 100):.1f}%")

def main():
    """主函数"""
    logger.info("白噪音音量对比测试")
    
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
    
    test_file = test_files[0]
    logger.info(f"使用测试文件: {Path(test_file).name}")
    
    # 创建音量对比文件
    comparison_files = create_volume_comparison(test_file)
    
    # 显示对比文件列表
    logger.info("\n" + "=" * 60)
    logger.info("对比文件列表")
    logger.info("=" * 60)
    
    for i, file_info in enumerate(comparison_files):
        logger.info(f"{i+1:2d}. {file_info['name']:<15} - {file_info['desc']}")
        logger.info(f"    文件: {file_info['file']}")
        logger.info(f"    白噪音音量: {file_info['noise_vol']*100:.0f}%")
        logger.info("")
    
    # 分析标准版本
    if len(comparison_files) >= 3:
        standard_file = comparison_files[2]['file']  # 标准白噪音版本
        create_audio_analysis(test_file, standard_file)
    
    logger.info("\n" + "=" * 60)
    logger.info("使用建议")
    logger.info("=" * 60)
    logger.info("1. 请依次播放对比文件，选择最适合的音量级别")
    logger.info("2. 推荐使用 '标准白噪音' (8%) 用于TikTok")
    logger.info("3. 如果听不出变化，可以尝试 '明显白噪音' (12%)")
    logger.info("4. 避免使用 '过度白噪音' (20%)，可能影响语音清晰度")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
