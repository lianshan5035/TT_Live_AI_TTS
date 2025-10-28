#!/usr/bin/env python3
"""
EdgeTTS 到 FFmpeg 音频处理演示脚本
演示如何让FFmpeg识别EdgeTTS生成的音频并开始工作
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

# 导入处理器
from ffmpeg_audio_processor import FFmpegAudioProcessor

# 模拟EdgeTTS处理器
class MockEdgeTTSProcessor:
    """模拟EdgeTTS处理器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def synthesize_single(self, text: str, output_file: str, voice_name: str = "xiaoxiao") -> bool:
        """模拟TTS音频生成"""
        try:
            # 创建一个简单的测试音频文件
            import subprocess
            cmd = [
                'ffmpeg', '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', '5',  # 5秒测试音频
                '-y', output_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"模拟TTS生成失败: {e}")
            return False

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EdgeTTSToFFmpegDemo:
    """EdgeTTS到FFmpeg处理演示"""
    
    def __init__(self):
        """初始化演示"""
        self.temp_dir = Path("demo_temp")
        self.temp_dir.mkdir(exist_ok=True)
        
        # 初始化处理器
        self.tts_processor = MockEdgeTTSProcessor(str(self.temp_dir / "tts_output"))
        self.ffmpeg_processor = FFmpegAudioProcessor(str(self.temp_dir / "ffmpeg_output"))
        
        logger.info("EdgeTTS到FFmpeg演示初始化完成")
    
    async def demo_complete_flow(self):
        """演示完整流程"""
        logger.info("=" * 60)
        logger.info("EdgeTTS 到 FFmpeg 完整处理流程演示")
        logger.info("=" * 60)
        
        # 测试文本
        test_texts = [
            "欢迎来到TikTok直播，今天我们来聊聊人工智能的发展。",
            "人工智能技术正在改变我们的生活方式，从语音识别到图像处理。",
            "EdgeTTS和FFmpeg的结合为音频处理带来了新的可能性。"
        ]
        
        results = []
        
        for i, text in enumerate(test_texts, 1):
            logger.info(f"\n--- 处理第 {i} 个文本 ---")
            logger.info(f"文本内容: {text}")
            
            # 步骤1: EdgeTTS生成音频
            tts_file = self.temp_dir / f"tts_{i:03d}.mp3"
            logger.info(f"步骤1: EdgeTTS生成音频 -> {tts_file}")
            
            tts_success = await self.tts_processor.synthesize_single(
                text=text,
                output_file=str(tts_file),
                voice_name="xiaoxiao"
            )
            
            if not tts_success:
                logger.error(f"EdgeTTS生成失败: {tts_file}")
                results.append({"text": text, "success": False, "error": "TTS生成失败"})
                continue
            
            # 检查EdgeTTS生成的音频文件
            if tts_file.exists():
                file_size = tts_file.stat().st_size
                logger.info(f"✓ EdgeTTS音频生成成功")
                logger.info(f"  文件路径: {tts_file}")
                logger.info(f"  文件大小: {file_size} bytes")
                
                # 获取音频时长
                duration = self.ffmpeg_processor.get_audio_duration(str(tts_file))
                logger.info(f"  音频时长: {duration:.2f} 秒")
            else:
                logger.error(f"✗ EdgeTTS音频文件不存在: {tts_file}")
                results.append({"text": text, "success": False, "error": "音频文件不存在"})
                continue
            
            # 步骤2: FFmpeg识别音频位置并开始处理
            logger.info(f"步骤2: FFmpeg识别音频位置并开始处理")
            
            # 检查FFmpeg是否能识别音频文件
            if self.ffmpeg_processor._check_ffmpeg():
                logger.info("✓ FFmpeg已就绪，开始处理音频")
                
                # 选择背景音效组合
                background_combinations = [
                    ["white_noise", "room_tone"],
                    ["white_noise", "fireplace", "room_tone"],
                    ["white_noise", "keyboard", "room_tone"]
                ]
                
                bg_combo = background_combinations[(i-1) % len(background_combinations)]
                logger.info(f"  背景音效组合: {bg_combo}")
                
                # FFmpeg处理音频
                output_file = self.temp_dir / f"mixed_{i:03d}.m4a"
                logger.info(f"  输出文件: {output_file}")
                
                ffmpeg_success = self.ffmpeg_processor.process_single_audio(
                    input_file=str(tts_file),  # EdgeTTS生成的音频文件
                    output_file=str(output_file),
                    background_combination=bg_combo,
                    main_volume=0.85
                )
                
                if ffmpeg_success and output_file.exists():
                    output_size = output_file.stat().st_size
                    logger.info(f"✓ FFmpeg处理成功")
                    logger.info(f"  输出文件: {output_file}")
                    logger.info(f"  文件大小: {output_size} bytes")
                    
                    results.append({
                        "text": text,
                        "success": True,
                        "tts_file": str(tts_file),
                        "output_file": str(output_file),
                        "background_sounds": bg_combo,
                        "duration": duration
                    })
                else:
                    logger.error(f"✗ FFmpeg处理失败")
                    results.append({"text": text, "success": False, "error": "FFmpeg处理失败"})
            else:
                logger.error("✗ FFmpeg未就绪")
                results.append({"text": text, "success": False, "error": "FFmpeg未就绪"})
        
        # 显示处理结果
        self.show_results(results)
        
        # 清理临时文件
        self.cleanup_temp_files()
    
    def show_results(self, results):
        """显示处理结果"""
        logger.info("\n" + "=" * 60)
        logger.info("处理结果汇总")
        logger.info("=" * 60)
        
        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)
        
        logger.info(f"总处理数量: {total_count}")
        logger.info(f"成功数量: {success_count}")
        logger.info(f"失败数量: {total_count - success_count}")
        logger.info(f"成功率: {success_count/total_count*100:.1f}%")
        
        logger.info("\n详细结果:")
        for i, result in enumerate(results, 1):
            if result["success"]:
                logger.info(f"  {i}. ✓ 成功")
                logger.info(f"     文本: {result['text'][:30]}...")
                logger.info(f"     时长: {result['duration']:.2f} 秒")
                logger.info(f"     背景音效: {result['background_sounds']}")
                logger.info(f"     输出文件: {result['output_file']}")
            else:
                logger.info(f"  {i}. ✗ 失败")
                logger.info(f"     文本: {result['text'][:30]}...")
                logger.info(f"     错误: {result['error']}")
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        logger.info("\n清理临时文件...")
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("✓ 临时文件清理完成")
        except Exception as e:
            logger.error(f"✗ 临时文件清理失败: {e}")
    
    async def demo_step_by_step(self):
        """分步演示"""
        logger.info("=" * 60)
        logger.info("EdgeTTS 到 FFmpeg 分步演示")
        logger.info("=" * 60)
        
        test_text = "这是一个分步演示，展示EdgeTTS如何生成音频，然后FFmpeg如何识别并处理。"
        
        # 步骤1: EdgeTTS生成音频
        logger.info("\n步骤1: EdgeTTS生成音频")
        logger.info("-" * 30)
        
        tts_file = self.temp_dir / "step_demo.mp3"
        logger.info(f"目标文件: {tts_file}")
        
        tts_success = await self.tts_processor.synthesize_single(
            text=test_text,
            output_file=str(tts_file),
            voice_name="xiaoxiao"
        )
        
        if tts_success:
            logger.info("✓ EdgeTTS音频生成成功")
            
            # 检查文件
            if tts_file.exists():
                file_size = tts_file.stat().st_size
                duration = self.ffmpeg_processor.get_audio_duration(str(tts_file))
                logger.info(f"  文件大小: {file_size} bytes")
                logger.info(f"  音频时长: {duration:.2f} 秒")
                
                # 步骤2: FFmpeg识别和处理
                logger.info("\n步骤2: FFmpeg识别音频位置")
                logger.info("-" * 30)
                
                logger.info(f"检查音频文件: {tts_file}")
                logger.info(f"文件存在: {tts_file.exists()}")
                
                if tts_file.exists():
                    logger.info("✓ FFmpeg检测到音频文件")
                    
                    # 开始FFmpeg处理
                    logger.info("\n步骤3: FFmpeg开始处理")
                    logger.info("-" * 30)
                    
                    output_file = self.temp_dir / "step_output.m4a"
                    logger.info(f"输出文件: {output_file}")
                    
                    ffmpeg_success = self.ffmpeg_processor.process_single_audio(
                        input_file=str(tts_file),
                        output_file=str(output_file),
                        background_combination=["white_noise", "room_tone"],
                        main_volume=0.85
                    )
                    
                    if ffmpeg_success:
                        logger.info("✓ FFmpeg处理成功")
                        if output_file.exists():
                            output_size = output_file.stat().st_size
                            logger.info(f"  输出文件大小: {output_size} bytes")
                    else:
                        logger.error("✗ FFmpeg处理失败")
                else:
                    logger.error("✗ 音频文件不存在")
            else:
                logger.error("✗ EdgeTTS音频文件未生成")
        else:
            logger.error("✗ EdgeTTS音频生成失败")

async def main():
    """主函数"""
    demo = EdgeTTSToFFmpegDemo()
    
    print("选择演示模式:")
    print("1. 完整流程演示")
    print("2. 分步演示")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        await demo.demo_complete_flow()
    elif choice == "2":
        await demo.demo_step_by_step()
    else:
        print("无效选择，运行完整流程演示")
        await demo.demo_complete_flow()

if __name__ == "__main__":
    asyncio.run(main())
