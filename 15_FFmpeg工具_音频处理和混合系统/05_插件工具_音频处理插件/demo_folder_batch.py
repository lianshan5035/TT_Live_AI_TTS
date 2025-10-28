#!/usr/bin/env python3
"""
FFmpeg 文件夹识别和批量处理演示脚本
演示如何根据EdgeTTS输出文件夹识别音频并进行批量处理
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

# 导入处理器
from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FFmpegFolderBatchDemo:
    """FFmpeg文件夹批量处理演示"""
    
    def __init__(self):
        """初始化演示"""
        # 初始化FFmpeg处理器（使用默认路径，会在TT_Live_AI_TTS目录下创建20.1_ffpmeg输出文件_处理完成的音频文件）
        self.ffmpeg_processor = FFmpegAudioProcessor()
        
        # EdgeTTS输出目录
        self.edgetts_dir = Path("20_输出文件_处理完成的音频文件")
        
        logger.info("FFmpeg文件夹批量处理演示初始化完成")
        logger.info(f"EdgeTTS目录: {self.edgetts_dir}")
        logger.info(f"FFmpeg输出目录: {self.ffmpeg_processor.output_dir}")
    
    def create_demo_edgetts_folders(self):
        """创建演示用的EdgeTTS文件夹结构"""
        logger.info("创建演示用的EdgeTTS文件夹结构...")
        
        # 确保EdgeTTS目录存在
        self.edgetts_dir.mkdir(exist_ok=True)
        
        # 创建几个演示文件夹
        demo_folders = [
            "batch_001_20241028",
            "batch_002_20241028", 
            "batch_003_20241028"
        ]
        
        for folder_name in demo_folders:
            folder_path = self.edgetts_dir / folder_name
            folder_path.mkdir(exist_ok=True)
            
            # 在每个文件夹中创建几个演示音频文件
            for i in range(3):
                audio_file = folder_path / f"audio_{i+1:03d}.mp3"
                
                # 创建简单的测试音频文件
                import subprocess
                cmd = [
                    'ffmpeg', '-f', 'lavfi',
                    '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                    '-t', '3',  # 3秒测试音频
                    '-y', str(audio_file)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"创建演示音频文件: {audio_file}")
                else:
                    logger.error(f"创建音频文件失败: {audio_file}")
    
    def demo_folder_scanning(self):
        """演示文件夹扫描功能"""
        logger.info("=" * 60)
        logger.info("演示文件夹扫描功能")
        logger.info("=" * 60)
        
        # 扫描EdgeTTS输出文件夹
        folder_audio_map = self.ffmpeg_processor.scan_edgetts_output_folder()
        
        if not folder_audio_map:
            logger.warning("未找到任何EdgeTTS文件夹")
            return
        
        logger.info(f"发现 {len(folder_audio_map)} 个EdgeTTS文件夹:")
        
        for folder_name, audio_files in folder_audio_map.items():
            logger.info(f"  文件夹: {folder_name}")
            logger.info(f"    音频文件数量: {len(audio_files)}")
            for audio_file in audio_files:
                file_path = Path(audio_file)
                file_size = file_path.stat().st_size
                logger.info(f"    - {file_path.name} ({file_size} bytes)")
    
    def demo_single_folder_batch(self):
        """演示单个文件夹批量处理"""
        logger.info("=" * 60)
        logger.info("演示单个文件夹批量处理")
        logger.info("=" * 60)
        
        # 扫描文件夹
        folder_audio_map = self.ffmpeg_processor.scan_edgetts_output_folder()
        
        if not folder_audio_map:
            logger.warning("未找到任何EdgeTTS文件夹")
            return
        
        # 选择第一个文件夹进行演示
        folder_name = list(folder_audio_map.keys())[0]
        logger.info(f"选择文件夹进行演示: {folder_name}")
        
        # 批量处理
        result = self.ffmpeg_processor.process_folder_batch(
            edgetts_folder_name=folder_name,
            background_combination=["white_noise", "room_tone"],
            main_volume=0.85
        )
        
        if result.get("success", True):  # 默认成功，除非明确失败
            logger.info("批量处理完成!")
            logger.info(f"EdgeTTS文件夹: {result['edgetts_folder']}")
            logger.info(f"FFmpeg文件夹: {result['ffmpeg_folder']}")
            logger.info(f"处理文件数: {result['total_files']}")
            logger.info(f"成功数: {result['success_count']}")
            logger.info(f"失败数: {result['failed_count']}")
            logger.info(f"成功率: {result['success_rate']:.1f}%")
        else:
            logger.error(f"批量处理失败: {result.get('error', '未知错误')}")
    
    def demo_multiple_folder_batch(self):
        """演示多个文件夹批量处理"""
        logger.info("=" * 60)
        logger.info("演示多个文件夹批量处理")
        logger.info("=" * 60)
        
        # 扫描文件夹
        folder_audio_map = self.ffmpeg_processor.scan_edgetts_output_folder()
        
        if not folder_audio_map:
            logger.warning("未找到任何EdgeTTS文件夹")
            return
        
        # 不同的背景音效组合
        background_combinations = [
            ["white_noise", "room_tone"],
            ["white_noise", "fireplace", "room_tone"],
            ["white_noise", "keyboard", "room_tone"]
        ]
        
        total_results = []
        
        for i, folder_name in enumerate(folder_audio_map.keys()):
            logger.info(f"\n处理第 {i+1} 个文件夹: {folder_name}")
            
            # 选择背景音效组合
            bg_combo = background_combinations[i % len(background_combinations)]
            
            # 批量处理
            result = self.ffmpeg_processor.process_folder_batch(
                edgetts_folder_name=folder_name,
                background_combination=bg_combo,
                main_volume=0.85
            )
            
            total_results.append(result)
        
        # 显示总体结果
        self.show_total_results(total_results)
    
    def show_total_results(self, results):
        """显示总体处理结果"""
        logger.info("\n" + "=" * 60)
        logger.info("总体处理结果")
        logger.info("=" * 60)
        
        total_files = sum(r.get("total_files", 0) for r in results)
        total_success = sum(r.get("success_count", 0) for r in results)
        total_failed = sum(r.get("failed_count", 0) for r in results)
        
        logger.info(f"总文件夹数: {len(results)}")
        logger.info(f"总文件数: {total_files}")
        logger.info(f"总成功数: {total_success}")
        logger.info(f"总失败数: {total_failed}")
        logger.info(f"总成功率: {total_success/total_files*100:.1f}%" if total_files > 0 else "总成功率: 0%")
        
        logger.info("\n各文件夹处理结果:")
        for result in results:
            logger.info(f"  {result['edgetts_folder']} -> {result['ffmpeg_folder']}")
            logger.info(f"    文件数: {result['total_files']}, 成功: {result['success_count']}, 失败: {result['failed_count']}")
    
    def demo_batch_records(self):
        """演示批量处理记录功能"""
        logger.info("=" * 60)
        logger.info("演示批量处理记录功能")
        logger.info("=" * 60)
        
        # 获取批量处理记录
        batch_records = self.ffmpeg_processor.get_batch_records()
        
        if not batch_records:
            logger.info("暂无批量处理记录")
            return
        
        logger.info(f"批量处理记录数量: {len(batch_records)}")
        
        for folder_name, record in batch_records.items():
            logger.info(f"\n文件夹: {folder_name}")
            logger.info(f"  FFmpeg文件夹: {record['ffmpeg_folder']}")
            logger.info(f"  处理时间: {record['start_time']} - {record['end_time']}")
            logger.info(f"  文件数: {record['total_files']}")
            logger.info(f"  成功率: {record['success_rate']:.1f}%")
            logger.info(f"  背景音效: {record['background_sounds']}")
        
        # 保存记录
        self.ffmpeg_processor.save_batch_records()
    
    def show_folder_mapping(self):
        """显示文件夹映射关系"""
        logger.info("=" * 60)
        logger.info("文件夹映射关系")
        logger.info("=" * 60)
        
        # 扫描EdgeTTS文件夹
        folder_audio_map = self.ffmpeg_processor.scan_edgetts_output_folder()
        
        logger.info("文件夹结构:")
        logger.info(f"  {self.edgetts_dir} (EdgeTTS输出)")
        for folder_name in folder_audio_map.keys():
            logger.info(f"    ├── {folder_name}/")
        
        logger.info(f"  {self.ffmpeg_processor.output_dir} (FFmpeg输出)")
        for folder_name in folder_audio_map.keys():
            ffmpeg_folder_name = f"ffmpeg_{folder_name}"
            logger.info(f"    ├── {ffmpeg_folder_name}/")
        
        logger.info("\n文件对应关系:")
        batch_records = self.ffmpeg_processor.get_batch_records()
        
        for folder_name, record in batch_records.items():
            logger.info(f"\n{folder_name} -> {record['ffmpeg_folder']}:")
            for file_record in record['processed_files']:
                input_name = Path(file_record['input_file']).name
                output_name = Path(file_record['output_file']).name
                status = "✓" if file_record['success'] else "✗"
                logger.info(f"  {status} {input_name} -> {output_name}")

def main():
    """主函数"""
    demo = FFmpegFolderBatchDemo()
    
    print("FFmpeg文件夹识别和批量处理演示")
    print("=" * 50)
    print("1. 创建演示文件夹结构")
    print("2. 演示文件夹扫描功能")
    print("3. 演示单个文件夹批量处理")
    print("4. 演示多个文件夹批量处理")
    print("5. 演示批量处理记录功能")
    print("6. 显示文件夹映射关系")
    print("7. 运行所有演示")
    
    choice = input("\n请输入选择 (1-7): ").strip()
    
    if choice == "1":
        demo.create_demo_edgetts_folders()
    elif choice == "2":
        demo.demo_folder_scanning()
    elif choice == "3":
        demo.demo_single_folder_batch()
    elif choice == "4":
        demo.demo_multiple_folder_batch()
    elif choice == "5":
        demo.demo_batch_records()
    elif choice == "6":
        demo.show_folder_mapping()
    elif choice == "7":
        demo.create_demo_edgetts_folders()
        demo.demo_folder_scanning()
        demo.demo_single_folder_batch()
        demo.demo_multiple_folder_batch()
        demo.demo_batch_records()
        demo.show_folder_mapping()
    else:
        print("无效选择，运行所有演示")
        demo.create_demo_edgetts_folders()
        demo.demo_folder_scanning()
        demo.demo_single_folder_batch()
        demo.demo_multiple_folder_batch()
        demo.demo_batch_records()
        demo.show_folder_mapping()

if __name__ == "__main__":
    main()
