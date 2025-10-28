#!/usr/bin/env python3
"""
真人直播语音参数分析器
分析真人直播语音的特点并生成测试音频
"""

import random
import logging
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 导入规则加载器
import sys
sys.path.append('/Volumes/M2/TT_Live_AI_TTS/audio_pipeline')
from rules_loader import get_rules_loader

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiveSpeechAnalyzer:
    """真人直播语音分析器"""
    
    def __init__(self):
        self.rules = get_rules_loader()
        self.logger = logging.getLogger(__name__)
        
        # 真人直播语音特点分析
        self.live_speech_characteristics = {
            "tempo": {
                "normal_range": (0.95, 1.05),  # 正常语速范围
                "excited_range": (1.05, 1.15),  # 兴奋时语速
                "calm_range": (0.90, 1.00),    # 平静时语速
                "description": "真人直播语速通常比TTS稍快，有自然变化"
            },
            "pitch": {
                "normal_range": (-0.2, 0.2),    # 正常音高变化
                "excited_range": (0.1, 0.4),    # 兴奋时音高
                "calm_range": (-0.3, 0.1),     # 平静时音高
                "description": "真人直播音高有自然波动，不会过于机械"
            },
            "background": {
                "room_tone_level": (0.05, 0.12),  # 房间底噪
                "environment_level": (0.08, 0.18), # 环境音效
                "description": "真人直播有轻微的房间音和环境音"
            },
            "events": {
                "keyboard_probability": 0.25,     # 键盘声概率
                "water_probability": 0.15,        # 喝水声概率
                "movement_probability": 0.20,     # 移动声概率
                "description": "真人直播会有自然的动作声音"
            },
            "audio_quality": {
                "compression_ratio": 2.5,         # 压缩比
                "eq_250hz_gain": (1.2, 1.8),     # 250Hz增益
                "eq_3khz_gain": (1.5, 2.2),      # 3kHz增益
                "highpass_freq": 60,              # 高通滤波频率
                "description": "真人直播音频质量更自然，不会过度处理"
            }
        }
    
    def analyze_live_speech_params(self) -> Dict[str, Any]:
        """分析真人直播语音参数"""
        self.logger.info("🎤 分析真人直播语音参数...")
        
        # 基于真人直播特点生成参数
        params = {}
        
        # 1. 语速参数 - 真人直播通常比TTS稍快
        params['tempo'] = random.uniform(1.02, 1.08)  # 比正常稍快
        self.logger.info(f"📊 语速调整: {params['tempo']:.3f}x (真人直播通常稍快)")
        
        # 2. 音高参数 - 真人直播有自然波动
        params['pitch_semitones'] = random.uniform(-0.15, 0.25)  # 轻微波动
        self.logger.info(f"🎵 音高调整: {params['pitch_semitones']:.3f}半音 (自然波动)")
        
        # 3. 背景音效 - 真人直播有轻微环境音
        if random.random() < 0.85:  # 85%概率有背景音
            environments = ['room_tone', 'living_room', 'office']
            env = random.choice(environments)
            params['background_sound'] = {
                'file': f"{env}.wav",
                'volume': random.uniform(0.08, 0.15),  # 较低音量
                'start_offset': random.uniform(0, 30),
                'looped': True
            }
            self.logger.info(f"🌍 背景音效: {env} (音量: {params['background_sound']['volume']:.3f})")
        else:
            params['background_sound'] = None
            self.logger.info("🌍 背景音效: 无")
        
        # 4. 事件音效 - 真人直播有自然动作
        params['events'] = []
        if random.random() < 0.30:  # 30%概率有事件音
            event_types = ['keyboard', 'water_pour', 'chair_creak']
            num_events = random.randint(1, 2)
            
            for _ in range(num_events):
                event_type = random.choice(event_types)
                params['events'].append({
                    'file': f"{event_type}.wav",
                    'volume': random.uniform(0.10, 0.18),
                    'trigger_time': random.uniform(5, 25),  # 在5-25秒触发
                    'duration': random.uniform(1.0, 2.5)
                })
            
            self.logger.info(f"🔊 事件音效: {len(params['events'])}个事件")
        else:
            self.logger.info("🔊 事件音效: 无")
        
        # 5. 音频增强参数 - 真人直播更自然
        params['compressor'] = {
            'threshold': -20,  # 更温和的压缩
            'ratio': 2.5,      # 更低的压缩比
            'attack': 20,      # 更慢的攻击时间
            'release': 200,    # 更慢的释放时间
            'makeup': 2        # 更少的增益补偿
        }
        
        params['equalizer'] = {
            'bands': [
                {'frequency': 250, 'gain_range': (1.2, 1.8), 'width': 100},
                {'frequency': 3000, 'gain_range': (1.5, 2.2), 'width': 600}
            ]
        }
        
        params['highpass_frequency'] = 60  # 更低的截止频率
        params['noise_amplitude'] = random.uniform(0.006, 0.012)  # 更低的噪音
        
        self.logger.info(f"⚡ 音频增强: 自然模式 (高通: {params['highpass_frequency']}Hz)")
        self.logger.info(f"🔇 白噪音幅度: {params['noise_amplitude']:.4f}")
        
        return params
    
    def create_live_speech_audio(self, input_file: str, output_file: str) -> bool:
        """创建真人直播风格的音频"""
        try:
            self.logger.info(f"🎤 创建真人直播风格音频: {input_file}")
            
            # 分析参数
            params = self.analyze_live_speech_params()
            
            # 构建FFmpeg命令
            cmd = self.build_live_speech_command(input_file, output_file, params)
            
            # 执行命令
            self.logger.info(f"🔧 执行FFmpeg命令...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"✅ 真人直播风格音频创建成功: {output_file}")
                return True
            else:
                self.logger.error(f"❌ 创建失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 处理失败: {e}")
            return False
    
    def build_live_speech_command(self, input_file: str, output_file: str, params: Dict[str, Any]) -> List[str]:
        """构建真人直播风格的FFmpeg命令"""
        cmd = ['ffmpeg', '-y', '-i', input_file]
        
        # 构建滤镜链
        filters = []
        
        # 1. 采样率转换
        filters.append('aresample=48000')
        
        # 2. 语速和音高调整
        if params['tempo'] != 1.0 or params['pitch_semitones'] != 0.0:
            pitch_ratio = 2 ** (params['pitch_semitones'] / 12)
            filters.append(f"rubberband=tempo={params['tempo']}:pitch={pitch_ratio}:formant=preserved")
        
        # 3. 音频增强 - 真人直播风格
        compressor = params['compressor']
        filters.append(f"acompressor=threshold={compressor['threshold']}dB:ratio={compressor['ratio']}:attack={compressor['attack']}:release={compressor['release']}:makeup={compressor['makeup']}")
        
        # EQ调整
        for band in params['equalizer']['bands']:
            gain = random.uniform(*band['gain_range'])
            filters.append(f"equalizer=f={band['frequency']}:width_type=h:width={band['width']}:g={gain}")
        
        # 高通滤波器
        filters.append(f"highpass=f={params['highpass_frequency']}")
        
        # 4. 响度归一化 - 真人直播标准
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        
        # 应用滤镜
        if filters:
            cmd.extend(['-af', ','.join(filters)])
        
        # 5. 输出编码
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '48000', '-ac', '2'])
        cmd.append(output_file)
        
        return cmd
    
    def create_comparison_audio(self, input_file: str) -> Dict[str, str]:
        """创建对比音频"""
        self.logger.info("🔄 创建对比音频...")
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%H%M%S")
        base_name = Path(input_file).stem
        
        outputs = {
            'original': f"{base_name}_original_{timestamp}.m4a",
            'live_speech': f"{base_name}_live_speech_{timestamp}.m4a",
            'enhanced': f"{base_name}_enhanced_{timestamp}.m4a"
        }
        
        # 1. 原始音频（仅转换格式）
        cmd_original = [
            'ffmpeg', '-y', '-i', input_file,
            '-c:a', 'aac', '-b:a', '192k',
            '-ar', '48000', '-ac', '2',
            outputs['original']
        ]
        
        # 2. 真人直播风格
        self.create_live_speech_audio(input_file, outputs['live_speech'])
        
        # 3. 增强版本（使用当前规则）
        cmd_enhanced = [
            'ffmpeg', '-y', '-i', input_file,
            '-af', 'aresample=48000,rubberband=tempo=1.05:pitch=1.1:formant=preserved,acompressor=threshold=-18dB:ratio=3:attack=15:release=180:makeup=3,equalizer=f=250:width_type=h:width=120:g=2,equalizer=f=3500:width_type=h:width=800:g=2,highpass=f=80,loudnorm=I=-19:TP=-2:LRA=9',
            '-c:a', 'aac', '-b:a', '192k',
            '-ar', '48000', '-ac', '2',
            outputs['enhanced']
        ]
        
        # 执行命令
        for name, cmd in [('original', cmd_original), ('enhanced', cmd_enhanced)]:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info(f"✅ {name} 音频创建成功: {outputs[name]}")
                else:
                    self.logger.error(f"❌ {name} 音频创建失败: {result.stderr}")
            except Exception as e:
                self.logger.error(f"❌ {name} 音频创建失败: {e}")
        
        return outputs

def main():
    """主函数"""
    logger.info("🎤 真人直播语音参数分析器")
    logger.info("=" * 60)
    
    # 查找测试音频文件
    test_dirs = [
        "/Volumes/M2/TT_Live_AI_TTS/20_输出文件_处理完成的音频文件",
        "/Volumes/M2/TT_Live_AI_TTS/audio_pipeline/input_raw"
    ]
    
    test_audio = None
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if test_path.exists():
            for f in test_path.iterdir():
                if f.is_file() and f.suffix.lower() in ['.wav', '.mp3', '.m4a', '.aac']:
                    test_audio = f
                    break
            if test_audio:
                break
    
    if not test_audio:
        logger.error("❌ 未找到测试音频文件")
        return
    
    logger.info(f"🎵 找到测试音频: {test_audio.name}")
    
    # 创建分析器
    analyzer = LiveSpeechAnalyzer()
    
    # 创建对比音频
    outputs = analyzer.create_comparison_audio(str(test_audio))
    
    # 显示结果
    logger.info("\n📋 生成的对比音频:")
    for name, file_path in outputs.items():
        if Path(file_path).exists():
            logger.info(f"  {name}: {file_path}")
        else:
            logger.info(f"  {name}: 创建失败")
    
    # 显示真人直播语音特点
    logger.info("\n🎤 真人直播语音特点:")
    characteristics = analyzer.live_speech_characteristics
    for category, params in characteristics.items():
        logger.info(f"  {category}: {params['description']}")

if __name__ == '__main__':
    main()
