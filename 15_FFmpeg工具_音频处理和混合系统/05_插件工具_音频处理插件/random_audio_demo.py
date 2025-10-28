#!/usr/bin/env python3
"""
高级随机化音频处理测试脚本
演示同人不同场次的直播效果
"""

import os
import sys
import logging
import subprocess
import random
import json
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

class RandomAudioDemo:
    """随机化音频处理演示"""
    
    def __init__(self):
        self.processor = FFmpegAudioProcessor()
        
        # 简化的随机参数
        self.demo_config = {
            "tempo_range": (0.88, 1.12),  # ±12% 语速调整
            "pitch_range": (0.8, 1.2),   # ±20% 音高调整（Rubberband格式）
            "background_sounds": [
                {"file": "white_noise.wav", "volume_range": (0.05, 0.12), "description": "白噪音"},
                {"file": "room_tone.wav", "volume_range": (0.06, 0.10), "description": "房间音"},
            ],
            "event_sounds": [
                {"file": "keyboard_typing.wav", "volume_range": (0.10, 0.18), "description": "键盘声"},
                {"file": "water_pour.wav", "volume_range": (0.08, 0.15), "description": "倒水声"},
            ]
        }
    
    def find_test_audio(self) -> str:
        """查找测试音频文件"""
        logger.info("查找EdgeTTS生成的测试音频文件...")
        
        # 查找EdgeTTS输出目录
        edgetts_dir = Path("../../20_输出文件_处理完成的音频文件")
        if not edgetts_dir.exists():
            logger.error("EdgeTTS输出目录不存在")
            return None
        
        # 查找音频文件
        for folder in edgetts_dir.iterdir():
            if folder.is_dir():
                for audio_file in folder.iterdir():
                    if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                        logger.info(f"找到测试音频: {audio_file.name}")
                        return str(audio_file)
        
        logger.error("未找到EdgeTTS音频文件")
        return None
    
    def generate_demo_parameters(self) -> Dict:
        """生成演示参数"""
        logger.info("生成演示随机参数...")
        
        # 随机语速和音高
        tempo = random.uniform(*self.demo_config["tempo_range"])
        pitch = random.uniform(*self.demo_config["pitch_range"])
        
        # 随机选择背景音效
        background_sound = None
        if random.random() < 0.7:  # 70% 概率添加背景音效
            background_sound = random.choice(self.demo_config["background_sounds"]).copy()
            background_sound["volume"] = random.uniform(*background_sound["volume_range"])
            background_sound["start_time"] = random.uniform(0, 10)  # 随机起点
        
        # 随机选择事件音效
        event_sound = None
        if random.random() < 0.2:  # 20% 概率添加事件音效
            event_sound = random.choice(self.demo_config["event_sounds"]).copy()
            event_sound["volume"] = random.uniform(*event_sound["volume_range"])
            event_sound["trigger_time"] = random.uniform(0.3, 0.7)  # 在音频的30%-70%处触发
        
        params = {
            "tempo": tempo,
            "pitch": pitch,
            "background_sound": background_sound,
            "event_sound": event_sound
        }
        
        logger.info(f"演示参数: 语速={tempo:.3f}x, 音高={pitch:.3f}半音")
        logger.info(f"背景音效: {background_sound['description'] if background_sound else '无'}")
        logger.info(f"事件音效: {event_sound['description'] if event_sound else '无'}")
        
        return params
    
    def create_demo_audio(self, input_file: str, params: Dict) -> Optional[str]:
        """创建演示音频"""
        logger.info(f"创建演示音频: {Path(input_file).name}")
        
        # 获取音频时长
        duration = self.processor.get_audio_duration(input_file)
        logger.info(f"音频时长: {duration:.2f} 秒")
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%H%M%S")
        output_file = f"demo_random_{timestamp}.mp4"
        
        # 构建FFmpeg命令
        cmd = ['ffmpeg', '-y']
        cmd.extend(['-i', input_file])
        
        # 添加背景音效输入
        input_count = 1
        if params['background_sound']:
            bg_sound_file = self.processor.background_sounds_dir / params['background_sound']['file']
            if bg_sound_file.exists():
                cmd.extend(['-i', str(bg_sound_file)])
                input_count += 1
        
        # 添加事件音效输入
        if params['event_sound']:
            event_sound_file = self.processor.background_sounds_dir / params['event_sound']['file']
            if event_sound_file.exists():
                cmd.extend(['-i', str(event_sound_file)])
                input_count += 1
        
        # 构建滤镜链
        filter_complex = self._build_demo_filter_complex(input_file, params, input_count)
        cmd.extend(['-filter_complex', filter_complex])
        
        cmd.extend(['-map', '[final]'])
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '44100', '-ac', '2'])
        cmd.extend(['-f', 'mp4'])
        cmd.append(output_file)
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ 演示音频创建成功: {output_file}")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"文件大小: {file_size:,} bytes")
            return output_file
        else:
            logger.error(f"✗ 演示音频创建失败: {result.stderr}")
            return None
    
    def _build_demo_filter_complex(self, input_file: str, params: Dict, input_count: int) -> str:
        """构建演示滤镜链"""
        filter_parts = []
        
        # 获取音频时长
        duration = self.processor.get_audio_duration(input_file)
        
        # 1. 主音频处理
        main_filters = []
        
        # EQ调整（250Hz和3kHz）
        main_filters.append("equalizer=f=250:width_type=h:width=100:g=1.1")
        main_filters.append("equalizer=f=3000:width_type=h:width=500:g=1.2")
        
        # 压缩器
        main_filters.append("acompressor=threshold=0.089:ratio=9:attack=200:release=1000")
        
        # 响度归一化
        main_filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        
        filter_parts.append(f'[0:a]{",".join(main_filters)}[main_pre]')
        
        # 2. Rubberband时间拉伸和音高变换
        if params['tempo'] != 1.0 or params['pitch'] != 0.0:
            rubberband_params = f"tempo={params['tempo']}:pitch={params['pitch']}:formant=preserved"
            filter_parts.append(f'[main_pre]rubberband={rubberband_params}[main_processed]')
        else:
            filter_parts.append(f'[main_pre]volume=1.0[main_processed]')
        
        # 3. 背景音效处理
        if params['background_sound']:
            bg_sound = params['background_sound']
            bg_filters = [
                f"volume={bg_sound['volume']}",
                f"atrim=start={bg_sound['start_time']}",
                f"afade=t=in:ss=0:d=1.0",
                f"afade=t=out:st={duration - 1.0}:d=1.0"
            ]
            filter_parts.append(f'[1:a]{",".join(bg_filters)}[bg_processed]')
        
        # 4. 事件音效处理
        if params['event_sound']:
            event_sound = params['event_sound']
            trigger_time = event_sound['trigger_time'] * duration
            event_filters = [
                f"volume={event_sound['volume']}",
                f"atrim=duration=2.0",
                f"adelay={trigger_time * 1000}|{trigger_time * 1000}"
            ]
            input_idx = 2 if params['background_sound'] else 1
            filter_parts.append(f'[{input_idx}:a]{",".join(event_filters)}[event_processed]')
        
        # 5. 混合所有音效
        mix_inputs = ['[main_processed]']
        mix_weights = ['1']
        
        if params['background_sound']:
            mix_inputs.append('[bg_processed]')
            mix_weights.append('0.3')
        
        if params['event_sound']:
            mix_inputs.append('[event_processed]')
            mix_weights.append('0.2')
        
        mix_filter = f"amix=inputs={len(mix_inputs)}:duration=first:weights={' '.join(mix_weights)}[final]"
        filter_parts.append(mix_filter)
        
        return ';'.join(filter_parts)
    
    def create_multiple_demos(self, input_file: str, count: int = 5) -> List[str]:
        """创建多个演示音频"""
        logger.info("=" * 60)
        logger.info(f"创建 {count} 个演示音频")
        logger.info("=" * 60)
        
        demo_files = []
        
        for i in range(count):
            logger.info(f"\n创建演示 {i+1}/{count}")
            
            # 生成不同的随机参数
            params = self.generate_demo_parameters()
            
            # 创建演示音频
            demo_file = self.create_demo_audio(input_file, params)
            
            if demo_file:
                demo_files.append(demo_file)
        
        return demo_files
    
    def create_demo_guide(self, demo_files: List[str]):
        """创建演示指南"""
        guide_file = "random_audio_demo_guide.txt"
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write("高级随机化音频处理演示指南\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("演示说明:\n")
            f.write("使用同一个EdgeTTS音频，生成多个不同效果的版本\n")
            f.write("每个版本都有不同的语速、音高和背景音效\n")
            f.write("模拟同人不同场次的直播效果\n\n")
            
            f.write("生成的文件:\n")
            for i, demo_file in enumerate(demo_files):
                f.write(f"{i+1}. {demo_file}\n")
            f.write("\n")
            
            f.write("技术特点:\n")
            f.write("- 随机语速调整: ±12% (使用Rubberband)\n")
            f.write("- 随机音高调整: ±0.4半音 (保持formant)\n")
            f.write("- 随机背景音效: 70%概率添加\n")
            f.write("- 随机事件音效: 20%概率添加\n")
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
    logger.info("高级随机化音频处理演示")
    
    # 初始化演示器
    demo = RandomAudioDemo()
    
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
        logger.info("高级随机化音频处理演示完成!")
        logger.info("=" * 60)
        logger.info("生成的演示文件:")
        for demo_file in demo_files:
            logger.info(f"  - {demo_file}")
        logger.info("")
        logger.info("演示特点:")
        logger.info("- 每条音频都有不同的语速和音高")
        logger.info("- 随机添加背景音效和事件音效")
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
