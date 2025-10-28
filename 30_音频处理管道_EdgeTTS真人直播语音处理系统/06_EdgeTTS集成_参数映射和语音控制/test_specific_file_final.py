#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
针对特定文件的直播带货音频优化测试 - 最终修复版
处理 tts_0003_舒缓型_珍妮_dyn.mp3 文件
"""

import asyncio
import subprocess
import logging
import os
import time
from pathlib import Path
from file_location_helper import show_file_location, show_multiple_files

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalFileOptimizer:
    """最终修复版文件优化器"""
    
    def __init__(self):
        """初始化优化器"""
        self.input_file = "/Volumes/M2/TT_Live_AI_TTS/20_输出文件_处理完成的音频文件/batch_1761611986_Jenny/tts_0003_舒缓型_珍妮_dyn.mp3"
        
    def check_file_exists(self) -> bool:
        """检查输入文件是否存在"""
        if os.path.exists(self.input_file):
            file_size = os.path.getsize(self.input_file)
            logger.info(f"✅ 找到输入文件: {self.input_file}")
            logger.info(f"📊 文件大小: {file_size} bytes")
            return True
        else:
            logger.error(f"❌ 输入文件不存在: {self.input_file}")
            return False
    
    def get_audio_info(self) -> dict:
        """获取音频文件信息"""
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', self.input_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                # 提取音频信息
                audio_info = {
                    'duration': float(info['format']['duration']),
                    'bitrate': int(info['format']['bit_rate']),
                    'sample_rate': int(info['streams'][0]['sample_rate']),
                    'channels': int(info['streams'][0]['channels']),
                    'codec': info['streams'][0]['codec_name']
                }
                
                logger.info(f"🎵 音频信息:")
                logger.info(f"   时长: {audio_info['duration']:.2f} 秒")
                logger.info(f"   比特率: {audio_info['bitrate']} bps")
                logger.info(f"   采样率: {audio_info['sample_rate']} Hz")
                logger.info(f"   声道数: {audio_info['channels']}")
                logger.info(f"   编码格式: {audio_info['codec']}")
                
                return audio_info
            else:
                logger.error(f"❌ 获取音频信息失败: {result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ 获取音频信息异常: {e}")
            return {}
    
    def create_final_optimized_version(self, profile: str = "warm_recommendation") -> str:
        """创建最终优化版本"""
        timestamp = int(time.time())
        output_file = f"tts_0003_舒缓型_珍妮_dyn_{profile}_{timestamp}.m4a"
        
        try:
            logger.info(f"🎯 开始优化处理: {profile}")
            
            # 构建简化的FFmpeg命令 - 使用正确的参数格式
            cmd = ['ffmpeg', '-y', '-i', self.input_file]
            
            # 根据profile选择不同的处理参数 - 修复所有参数格式
            if profile == "warm_recommendation":
                # 温暖推荐型 - 适合舒缓型音频
                filter_complex = """
                [0]aresample=resampler=soxr:osr=48000[resampled];
                [resampled]atempo=1.02[tempo];
                [tempo]asetrate=48000*1.01,aresample=48000[pitch];
                [pitch]acompressor=threshold=0.1:ratio=3:attack=15:release=180:makeup=3[compressed];
                [compressed]equalizer=f=250:width=120:g=2.0[eq1];
                [eq1]equalizer=f=3500:width=800:g=2.5[eq2];
                [eq2]highpass=f=80[filtered];
                [filtered]aecho=0.8:0.2:0.7:0.15[reverb];
                [reverb]loudnorm=I=-19:TP=-2:LRA=9[output]
                """
            elif profile == "urgent_promotion":
                # 紧急促销型 - 加快语速
                filter_complex = """
                [0]aresample=resampler=soxr:osr=48000[resampled];
                [resampled]atempo=1.08[tempo];
                [tempo]asetrate=48000*1.03,aresample=48000[pitch];
                [pitch]acompressor=threshold=0.15:ratio=4:attack=10:release=150:makeup=3[compressed];
                [compressed]equalizer=f=250:width=120:g=2.5[eq1];
                [eq1]equalizer=f=3500:width=800:g=3.0[eq2];
                [eq2]highpass=f=80[filtered];
                [filtered]aecho=0.8:0.3:0.5:0.2[reverb];
                [reverb]loudnorm=I=-19:TP=-2:LRA=9[output]
                """
            elif profile == "excited_showcase":
                # 兴奋展示型 - 增强活力
                filter_complex = """
                [0]aresample=resampler=soxr:osr=48000[resampled];
                [resampled]atempo=1.05[tempo];
                [tempo]asetrate=48000*1.05,aresample=48000[pitch];
                [pitch]acompressor=threshold=0.2:ratio=4.5:attack=8:release=140:makeup=3.5[compressed];
                [compressed]equalizer=f=250:width=120:g=2.8[eq1];
                [eq1]equalizer=f=3500:width=800:g=3.2[eq2];
                [eq2]highpass=f=80[filtered];
                [filtered]aecho=0.8:0.25:0.6:0.18[reverb];
                [reverb]loudnorm=I=-19:TP=-2:LRA=9[output]
                """
            elif profile == "professional_explanation":
                # 专业讲解型 - 保持稳定
                filter_complex = """
                [0]aresample=resampler=soxr:osr=48000[resampled];
                [resampled]atempo=1.0[tempo];
                [tempo]asetrate=48000*1.0,aresample=48000[pitch];
                [pitch]acompressor=threshold=0.05:ratio=2.5:attack=20:release=200:makeup=2.5[compressed];
                [compressed]equalizer=f=250:width=120:g=1.8[eq1];
                [eq1]equalizer=f=3500:width=800:g=2.2[eq2];
                [eq2]highpass=f=80[filtered];
                [filtered]aecho=0.8:0.15:0.8:0.1[reverb];
                [reverb]loudnorm=I=-19:TP=-2:LRA=9[output]
                """
            else:
                # 默认处理
                filter_complex = """
                [0]aresample=resampler=soxr:osr=48000[resampled];
                [resampled]acompressor=threshold=0.1:ratio=3:attack=15:release=180:makeup=3[compressed];
                [compressed]equalizer=f=250:width=120:g=2.0[eq1];
                [eq1]equalizer=f=3500:width=800:g=2.5[eq2];
                [eq2]highpass=f=80[filtered];
                [filtered]loudnorm=I=-19:TP=-2:LRA=9[output]
                """
            
            cmd.extend(['-filter_complex', filter_complex])
            cmd.extend(['-map', '[output]'])
            cmd.extend(['-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2'])
            cmd.append(output_file)
            
            logger.info(f"🔧 运行FFmpeg命令...")
            logger.info(f"📤 输出文件: {output_file}")
            
            # 运行FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                if os.path.exists(output_file):
                    # 使用新的文件位置显示功能
                    show_file_location(output_file, f"{profile}优化音频")
                    return output_file
                else:
                    logger.error("❌ 输出文件未生成")
                    return None
            else:
                logger.error(f"❌ FFmpeg处理失败: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 处理异常: {e}")
            return None
    
    def create_multiple_versions(self) -> list:
        """创建多个版本的优化音频"""
        profiles = ["warm_recommendation", "urgent_promotion", "excited_showcase", "professional_explanation"]
        output_files = []
        
        logger.info("🎭 开始创建多个优化版本...")
        
        for profile in profiles:
            logger.info(f"📝 处理版本: {profile}")
            output_file = self.create_final_optimized_version(profile)
            if output_file:
                output_files.append(output_file)
                logger.info(f"✅ {profile} 版本完成")
            else:
                logger.error(f"❌ {profile} 版本失败")
            
            # 添加延迟
            time.sleep(1)
        
        return output_files
    
    def create_comparison_audio(self, output_files: list) -> str:
        """创建对比音频"""
        if not output_files:
            logger.error("❌ 没有输出文件可以对比")
            return None
        
        try:
            timestamp = int(time.time())
            comparison_file = f"tts_0003_舒缓型_珍妮_dyn_comparison_{timestamp}.m4a"
            
            # 构建对比音频命令
            cmd = ['ffmpeg', '-y']
            
            # 添加输入文件
            cmd.extend(['-i', self.input_file])  # 原始文件
            for output_file in output_files:
                cmd.extend(['-i', output_file])  # 优化版本
            
            # 构建滤镜链 - 将多个音频连接在一起
            filter_parts = []
            for i in range(len(output_files) + 1):
                filter_parts.append(f"[{i}]")
            
            filter_complex = f"{''.join(filter_parts)}concat=n={len(output_files) + 1}:v=0:a=1[out]"
            
            cmd.extend(['-filter_complex', filter_complex])
            cmd.extend(['-map', '[out]'])
            cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
            cmd.append(comparison_file)
            
            logger.info(f"🔧 创建对比音频...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                if os.path.exists(comparison_file):
                    # 使用新的文件位置显示功能
                    show_file_location(comparison_file, "对比音频")
                    return comparison_file
                else:
                    logger.error("❌ 对比音频文件未生成")
                    return None
            else:
                logger.error(f"❌ 对比音频创建失败: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 对比音频创建异常: {e}")
            return None

async def main():
    """主函数"""
    logger.info("🚀 开始处理 tts_0003_舒缓型_珍妮_dyn.mp3 文件 (最终修复版)")
    
    # 创建优化器
    optimizer = FinalFileOptimizer()
    
    # 1. 检查文件是否存在
    if not optimizer.check_file_exists():
        return
    
    # 2. 获取音频信息
    audio_info = optimizer.get_audio_info()
    if not audio_info:
        logger.warning("⚠️ 无法获取音频信息，继续处理...")
    
    # 3. 创建多个优化版本
    output_files = optimizer.create_multiple_versions()
    
    if output_files:
        # 4. 创建对比音频
        comparison_file = optimizer.create_comparison_audio(output_files)
        if comparison_file:
            output_files.append(comparison_file)
        
        # 5. 显示所有文件位置
        show_multiple_files(output_files, "优化音频")
        
        # 6. 输出试听建议
        print("\n" + "=" * 60)
        print("🎧 试听建议:")
        print("1. 原始文件: tts_0003_舒缓型_珍妮_dyn.mp3")
        print("2. 温暖推荐型: 适合产品介绍，语速适中，音调温暖")
        print("3. 紧急促销型: 适合限时促销，语速较快，音调略高")
        print("4. 兴奋展示型: 适合新品发布，语速较快，音调较高")
        print("5. 专业讲解型: 适合技术说明，语速稳定，音调专业")
        print("6. 对比音频: 包含所有版本的连续播放")
        print("=" * 60)
        
    else:
        logger.error("❌ 没有成功创建任何优化版本")

if __name__ == "__main__":
    asyncio.run(main())
