#!/usr/bin/env python3
"""
简化版随机化音频处理演示
专注于语速和音高的随机化
"""

import os
import sys
import logging
import subprocess
import random
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleRandomDemo:
    """简化版随机化音频处理演示"""
    
    def __init__(self):
        self.processor = FFmpegAudioProcessor()
        
        # 随机参数配置
        self.config = {
            "tempo_range": (0.88, 1.12),  # ±12% 语速调整
            "pitch_range": (0.8, 1.2),    # ±20% 音高调整
        }
    
    def find_test_audio(self) -> str:
        """查找测试音频文件"""
        logger.info("查找EdgeTTS生成的测试音频文件...")
        
        edgetts_dir = Path("../../20_输出文件_处理完成的音频文件")
        if not edgetts_dir.exists():
            logger.error("EdgeTTS输出目录不存在")
            return None
        
        for folder in edgetts_dir.iterdir():
            if folder.is_dir():
                for audio_file in folder.iterdir():
                    if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                        logger.info(f"找到测试音频: {audio_file.name}")
                        return str(audio_file)
        
        logger.error("未找到EdgeTTS音频文件")
        return None
    
    def generate_random_params(self) -> Dict:
        """生成随机参数"""
        tempo = random.uniform(*self.config["tempo_range"])
        pitch = random.uniform(*self.config["pitch_range"])
        
        params = {
            "tempo": tempo,
            "pitch": pitch
        }
        
        logger.info(f"随机参数: 语速={tempo:.3f}x, 音高={pitch:.3f}")
        return params
    
    def process_audio(self, input_file: str, params: Dict) -> Optional[str]:
        """处理音频"""
        logger.info(f"处理音频: {Path(input_file).name}")
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%H%M%S")
        output_file = f"random_demo_{timestamp}.mp4"
        
        # 构建FFmpeg命令
        cmd = ['ffmpeg', '-y', '-i', input_file]
        
        # 构建滤镜链
        filters = []
        
        # EQ调整
        filters.append("equalizer=f=250:width_type=h:width=100:g=1.1")
        filters.append("equalizer=f=3000:width_type=h:width=500:g=1.2")
        
        # 压缩器
        filters.append("acompressor=threshold=0.089:ratio=9:attack=200:release=1000")
        
        # 响度归一化
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        
        # Rubberband时间拉伸和音高变换
        if params['tempo'] != 1.0 or params['pitch'] != 1.0:
            rubberband_params = f"tempo={params['tempo']}:pitch={params['pitch']}:formant=preserved"
            filters.append(f"rubberband={rubberband_params}")
        
        # 应用滤镜
        filter_chain = ",".join(filters)
        cmd.extend(['-af', filter_chain])
        
        # 输出设置
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '44100', '-ac', '2'])
        cmd.extend(['-f', 'mp4'])
        cmd.append(output_file)
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ 处理完成: {output_file}")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"文件大小: {file_size:,} bytes")
            return output_file
        else:
            logger.error(f"✗ 处理失败: {result.stderr}")
            return None
    
    def create_multiple_demos(self, input_file: str, count: int = 5) -> List[str]:
        """创建多个演示音频"""
        logger.info("=" * 60)
        logger.info(f"创建 {count} 个随机化演示音频")
        logger.info("=" * 60)
        
        demo_files = []
        
        for i in range(count):
            logger.info(f"\n创建演示 {i+1}/{count}")
            
            # 生成不同的随机参数
            params = self.generate_random_params()
            
            # 处理音频
            demo_file = self.process_audio(input_file, params)
            
            if demo_file:
                demo_files.append(demo_file)
        
        return demo_files
    
    def create_demo_guide(self, demo_files: List[str]):
        """创建演示指南"""
        guide_file = "simple_random_demo_guide.txt"
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write("简化版随机化音频处理演示指南\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("演示说明:\n")
            f.write("使用同一个EdgeTTS音频，生成多个不同效果的版本\n")
            f.write("每个版本都有不同的语速和音高\n")
            f.write("模拟同人不同场次的直播效果\n\n")
            
            f.write("生成的文件:\n")
            for i, demo_file in enumerate(demo_files):
                f.write(f"{i+1}. {demo_file}\n")
            f.write("\n")
            
            f.write("技术特点:\n")
            f.write("- 随机语速调整: ±12% (使用Rubberband)\n")
            f.write("- 随机音高调整: ±20% (保持formant)\n")
            f.write("- EQ优化: 250Hz和3kHz频段调整\n")
            f.write("- 动态压缩: 平衡音量动态\n")
            f.write("- 响度归一化: 统一响度标准\n\n")
            
            f.write("预期效果:\n")
            f.write("- 听感上像同个人不同场次的对话\n")
            f.write("- 重复率极低，真实感强\n")
            f.write("- 适合TikTok直播场景\n")
            f.write("- 避免AI检测为录播\n\n")
            
            f.write("播放建议:\n")
            f.write("1. 依次播放所有演示文件\n")
            f.write("2. 对比不同版本的差异\n")
            f.write("3. 感受随机化效果\n")
            f.write("4. 选择满意的参数设置\n")
        
        logger.info(f"演示指南已保存: {guide_file}")

def main():
    """主函数"""
    logger.info("简化版随机化音频处理演示")
    
    # 初始化演示器
    demo = SimpleRandomDemo()
    
    # 查找测试音频
    test_audio = demo.find_test_audio()
    if not test_audio:
        logger.error("未找到测试音频文件")
        return
    
    # 创建多个演示音频
    demo_files = demo.create_multiple_demos(test_audio, 5)
    
    if demo_files:
        # 创建演示指南
        demo.create_demo_guide(demo_files)
        
        logger.info("\n" + "=" * 60)
        logger.info("简化版随机化音频处理演示完成!")
        logger.info("=" * 60)
        logger.info("生成的演示文件:")
        for demo_file in demo_files:
            logger.info(f"  - {demo_file}")
        logger.info("")
        logger.info("演示特点:")
        logger.info("- 每条音频都有不同的语速和音高")
        logger.info("- 听感上像同个人不同场次的对话")
        logger.info("- 重复率极低，真实感强")
        logger.info("")
        logger.info("使用说明:")
        logger.info("1. 播放所有演示文件，对比效果")
        logger.info("2. 感受随机化带来的真实感")
        logger.info("3. 确认效果后应用到批量处理")
        logger.info("=" * 60)
    else:
        logger.error("演示音频创建失败")

if __name__ == "__main__":
    main()
