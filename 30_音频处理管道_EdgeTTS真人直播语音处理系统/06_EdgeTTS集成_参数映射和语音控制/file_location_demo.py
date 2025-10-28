#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件位置显示功能
演示每次输出文件时都会明确显示文件位置
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

class FileLocationDemo:
    """文件位置显示演示"""
    
    def __init__(self):
        """初始化演示器"""
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
    
    def create_demo_version(self, profile: str = "demo") -> str:
        """创建演示版本"""
        timestamp = int(time.time())
        output_file = f"tts_0003_舒缓型_珍妮_dyn_{profile}_{timestamp}.m4a"
        
        try:
            logger.info(f"🎯 开始创建演示版本: {profile}")
            
            # 构建简化的FFmpeg命令
            cmd = ['ffmpeg', '-y', '-i', self.input_file]
            
            # 使用简单的滤镜链
            filter_complex = """
            [0]aresample=resampler=soxr:osr=48000[resampled];
            [resampled]atempo=1.05[tempo];
            [tempo]acompressor=threshold=0.1:ratio=3:attack=15:release=180:makeup=3[compressed];
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
                    show_file_location(output_file, f"{profile}演示音频")
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
    
    def create_multiple_demo_versions(self) -> list:
        """创建多个演示版本"""
        profiles = ["warm_demo", "urgent_demo", "excited_demo"]
        output_files = []
        
        logger.info("🎭 开始创建多个演示版本...")
        
        for profile in profiles:
            logger.info(f"📝 处理版本: {profile}")
            output_file = self.create_demo_version(profile)
            if output_file:
                output_files.append(output_file)
                logger.info(f"✅ {profile} 版本完成")
            else:
                logger.error(f"❌ {profile} 版本失败")
            
            # 添加延迟
            time.sleep(1)
        
        return output_files

async def main():
    """主函数"""
    print("🚀 文件位置显示功能演示")
    print("=" * 60)
    
    # 创建演示器
    demo = FileLocationDemo()
    
    # 1. 检查文件是否存在
    if not demo.check_file_exists():
        return
    
    # 2. 创建多个演示版本
    output_files = demo.create_multiple_demo_versions()
    
    if output_files:
        # 3. 显示所有文件位置
        show_multiple_files(output_files, "演示音频")
        
        # 4. 输出总结
        print("\n" + "=" * 60)
        print("🎉 演示完成！")
        print("=" * 60)
        print("📋 功能特点:")
        print("✅ 每次输出文件时都会显示:")
        print("   - 📄 文件名")
        print("   - 📊 文件大小")
        print("   - 📍 完整路径")
        print("   - 📂 所在目录")
        print("   - 🎧 快速播放命令")
        print("=" * 60)
        
    else:
        logger.error("❌ 没有成功创建任何演示版本")

if __name__ == "__main__":
    asyncio.run(main())
