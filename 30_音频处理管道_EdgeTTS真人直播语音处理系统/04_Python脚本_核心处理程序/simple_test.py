#!/usr/bin/env python3
"""
简化版EdgeTTS音频处理测试
"""

import os
import sys
import logging
import subprocess
import random
from pathlib import Path
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_processing():
    """测试基本音频处理功能"""
    logger.info("测试基本音频处理功能...")
    
    # 查找测试文件
    input_file = Path("audio_pipeline/input_raw/test_1.wav")
    if not input_file.exists():
        logger.error("测试文件不存在")
        return False
    
    # 生成输出文件
    output_file = Path("audio_pipeline/output_processed/test_basic.mp3")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 构建简单的FFmpeg命令
    cmd = [
        'ffmpeg', '-y',
        '-i', str(input_file),
        '-af', 'rubberband=tempo=1.0:pitch=1.0:formant=preserved,acompressor=threshold=-18dB:ratio=3:attack=15:release=180:makeup=3',
        '-c:a', 'libmp3lame', '-b:a', '192k',
        '-ar', '48000', '-ac', '2',
        str(output_file)
    ]
    
    logger.info(f"执行命令: {' '.join(cmd)}")
    
    # 运行命令
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        logger.info("✓ 基本处理测试成功")
        if output_file.exists():
            file_size = output_file.stat().st_size
            logger.info(f"输出文件大小: {file_size:,} bytes")
        return True
    else:
        logger.error(f"✗ 基本处理测试失败: {result.stderr}")
        return False

def test_with_background():
    """测试带背景音效的处理"""
    logger.info("测试带背景音效的处理...")
    
    # 查找文件
    input_file = Path("audio_pipeline/input_raw/test_1.wav")
    bg_file = Path("audio_pipeline/assets/ambience/white_noise.wav")
    
    if not input_file.exists() or not bg_file.exists():
        logger.error("测试文件不存在")
        return False
    
    # 生成输出文件
    output_file = Path("audio_pipeline/output_processed/test_with_bg.mp3")
    
    # 构建FFmpeg命令
    cmd = [
        'ffmpeg', '-y',
        '-i', str(input_file),
        '-i', str(bg_file),
        '-filter_complex', 
        '[0:a]rubberband=tempo=1.0:pitch=1.0:formant=preserved[voice];'
        '[1:a]volume=0.1[bg];'
        '[voice][bg]amix=inputs=2:duration=first[out]',
        '-map', '[out]',
        '-c:a', 'libmp3lame', '-b:a', '192k',
        '-ar', '48000', '-ac', '2',
        str(output_file)
    ]
    
    logger.info(f"执行命令: {' '.join(cmd)}")
    
    # 运行命令
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        logger.info("✓ 背景音效处理测试成功")
        if output_file.exists():
            file_size = output_file.stat().st_size
            logger.info(f"输出文件大小: {file_size:,} bytes")
        return True
    else:
        logger.error(f"✗ 背景音效处理测试失败: {result.stderr}")
        return False

def test_randomization():
    """测试随机化处理"""
    logger.info("测试随机化处理...")
    
    # 设置随机种子
    random.seed(123)
    
    # 生成随机参数
    tempo = random.uniform(0.95, 1.05)
    pitch = random.uniform(0.9, 1.1)
    
    logger.info(f"随机参数: tempo={tempo:.3f}, pitch={pitch:.3f}")
    
    # 查找文件
    input_file = Path("audio_pipeline/input_raw/test_1.wav")
    if not input_file.exists():
        logger.error("测试文件不存在")
        return False
    
    # 生成输出文件
    output_file = Path("audio_pipeline/output_processed/test_random.mp3")
    
    # 构建FFmpeg命令
    cmd = [
        'ffmpeg', '-y',
        '-i', str(input_file),
        '-af', f'rubberband=tempo={tempo}:pitch={pitch}:formant=preserved,acompressor=threshold=-18dB:ratio=3:attack=15:release=180:makeup=3',
        '-c:a', 'libmp3lame', '-b:a', '192k',
        '-ar', '48000', '-ac', '2',
        str(output_file)
    ]
    
    logger.info(f"执行命令: {' '.join(cmd)}")
    
    # 运行命令
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        logger.info("✓ 随机化处理测试成功")
        if output_file.exists():
            file_size = output_file.stat().st_size
            logger.info(f"输出文件大小: {file_size:,} bytes")
        return True
    else:
        logger.error(f"✗ 随机化处理测试失败: {result.stderr}")
        return False

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("EdgeTTS 音频处理管线 - 简化测试")
    logger.info("=" * 60)
    
    # 检查FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✓ FFmpeg 已安装")
        else:
            logger.error("✗ FFmpeg 未正确安装")
            return
    except Exception as e:
        logger.error(f"✗ FFmpeg 检查失败: {e}")
        return
    
    # 检查Rubberband
    try:
        result = subprocess.run(['ffmpeg', '-filters'], capture_output=True, text=True, timeout=10)
        if 'rubberband' in result.stdout:
            logger.info("✓ Rubberband 支持已启用")
        else:
            logger.error("✗ Rubberband 支持未启用")
            return
    except Exception as e:
        logger.error(f"✗ Rubberband 检查失败: {e}")
        return
    
    # 运行测试
    tests = [
        ("基本处理", test_basic_processing),
        ("背景音效", test_with_background),
        ("随机化处理", test_randomization)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n运行测试: {test_name}")
        success = test_func()
        results.append((test_name, success))
    
    # 输出结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        logger.info(f"{test_name}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    logger.info(f"\n总计: {success_count}/{total_count} 个测试通过")
    
    if success_count == total_count:
        logger.info("🎉 所有测试通过！音频处理管线工作正常")
    else:
        logger.warning("⚠️  部分测试失败，请检查配置")

if __name__ == "__main__":
    main()
