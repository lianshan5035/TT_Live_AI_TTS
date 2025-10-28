#!/usr/bin/env python3
"""
真人直播语音生成器
基于真人直播特点生成多种风格的测试音频
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

class LiveSpeechGenerator:
    """真人直播语音生成器"""
    
    def __init__(self):
        self.rules = get_rules_loader()
        self.logger = logging.getLogger(__name__)
        
        # 真人直播场景配置
        self.live_scenarios = {
            "gaming": {
                "name": "游戏直播",
                "tempo_range": (1.05, 1.15),
                "pitch_range": (0.1, 0.3),
                "background_prob": 0.9,
                "event_prob": 0.4,
                "compression_ratio": 2.8,
                "description": "游戏直播：语速快、音调高、背景音丰富"
            },
            "chatting": {
                "name": "聊天直播",
                "tempo_range": (0.95, 1.05),
                "pitch_range": (-0.1, 0.1),
                "background_prob": 0.7,
                "event_prob": 0.2,
                "compression_ratio": 2.2,
                "description": "聊天直播：语速正常、音调稳定、环境音适中"
            },
            "teaching": {
                "name": "教学直播",
                "tempo_range": (0.90, 1.00),
                "pitch_range": (-0.2, 0.0),
                "background_prob": 0.5,
                "event_prob": 0.15,
                "compression_ratio": 2.0,
                "description": "教学直播：语速稍慢、音调较低、环境音较少"
            },
            "entertainment": {
                "name": "娱乐直播",
                "tempo_range": (1.00, 1.10),
                "pitch_range": (0.0, 0.2),
                "background_prob": 0.8,
                "event_prob": 0.3,
                "compression_ratio": 2.5,
                "description": "娱乐直播：语速适中、音调略高、环境音丰富"
            },
            "news": {
                "name": "新闻直播",
                "tempo_range": (0.95, 1.05),
                "pitch_range": (-0.1, 0.1),
                "background_prob": 0.3,
                "event_prob": 0.1,
                "compression_ratio": 2.3,
                "description": "新闻直播：语速稳定、音调中性、环境音最少"
            }
        }
    
    def generate_scenario_audio(self, input_file: str, scenario: str) -> Dict[str, Any]:
        """生成特定场景的音频"""
        if scenario not in self.live_scenarios:
            self.logger.error(f"❌ 未知场景: {scenario}")
            return None
        
        config = self.live_scenarios[scenario]
        self.logger.info(f"🎤 生成 {config['name']} 场景音频")
        self.logger.info(f"📝 场景描述: {config['description']}")
        
        # 生成参数
        params = self._generate_scenario_params(config)
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%H%M%S")
        base_name = Path(input_file).stem
        output_file = f"{base_name}_{scenario}_{timestamp}.m4a"
        
        # 构建FFmpeg命令
        cmd = self._build_scenario_command(input_file, output_file, params)
        
        # 执行命令
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"✅ {config['name']} 音频创建成功: {output_file}")
                return {
                    'scenario': scenario,
                    'output_file': output_file,
                    'params': params,
                    'success': True
                }
            else:
                self.logger.error(f"❌ {config['name']} 音频创建失败: {result.stderr}")
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            self.logger.error(f"❌ {config['name']} 音频创建失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_scenario_params(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """生成场景参数"""
        params = {}
        
        # 语速和音高
        params['tempo'] = random.uniform(*config['tempo_range'])
        params['pitch_semitones'] = random.uniform(*config['pitch_range'])
        
        # 背景音效
        if random.random() < config['background_prob']:
            environments = ['room_tone', 'living_room', 'office', 'cafe']
            env = random.choice(environments)
            params['background_sound'] = {
                'file': f"{env}.wav",
                'volume': random.uniform(0.06, 0.18),
                'start_offset': random.uniform(0, 30),
                'looped': True
            }
        else:
            params['background_sound'] = None
        
        # 事件音效
        params['events'] = []
        if random.random() < config['event_prob']:
            event_types = ['keyboard', 'water_pour', 'chair_creak', 'paper_rustle']
            num_events = random.randint(1, 2)
            
            for _ in range(num_events):
                event_type = random.choice(event_types)
                params['events'].append({
                    'file': f"{event_type}.wav",
                    'volume': random.uniform(0.08, 0.20),
                    'trigger_time': random.uniform(3, 27),
                    'duration': random.uniform(1.0, 3.0)
                })
        
        # 音频增强参数
        params['compressor'] = {
            'threshold': -20,
            'ratio': config['compression_ratio'],
            'attack': 15,
            'release': 150,
            'makeup': 2
        }
        
        params['equalizer'] = {
            'bands': [
                {'frequency': 250, 'gain_range': (1.1, 1.6), 'width': 100},
                {'frequency': 3000, 'gain_range': (1.3, 1.9), 'width': 600}
            ]
        }
        
        params['highpass_frequency'] = 60
        params['noise_amplitude'] = random.uniform(0.005, 0.012)
        
        return params
    
    def _build_scenario_command(self, input_file: str, output_file: str, params: Dict[str, Any]) -> List[str]:
        """构建场景FFmpeg命令"""
        cmd = ['ffmpeg', '-y', '-i', input_file]
        
        # 构建滤镜链
        filters = []
        
        # 1. 采样率转换
        filters.append('aresample=48000')
        
        # 2. 语速和音高调整
        if params['tempo'] != 1.0 or params['pitch_semitones'] != 0.0:
            pitch_ratio = 2 ** (params['pitch_semitones'] / 12)
            filters.append(f"rubberband=tempo={params['tempo']}:pitch={pitch_ratio}:formant=preserved")
        
        # 3. 音频增强
        compressor = params['compressor']
        filters.append(f"acompressor=threshold={compressor['threshold']}dB:ratio={compressor['ratio']}:attack={compressor['attack']}:release={compressor['release']}:makeup={compressor['makeup']}")
        
        # EQ调整
        for band in params['equalizer']['bands']:
            gain = random.uniform(*band['gain_range'])
            filters.append(f"equalizer=f={band['frequency']}:width_type=h:width={band['width']}:g={gain}")
        
        # 高通滤波器
        filters.append(f"highpass=f={params['highpass_frequency']}")
        
        # 4. 响度归一化
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        
        # 应用滤镜
        if filters:
            cmd.extend(['-af', ','.join(filters)])
        
        # 5. 输出编码
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '48000', '-ac', '2'])
        cmd.append(output_file)
        
        return cmd
    
    def generate_all_scenarios(self, input_file: str) -> Dict[str, Any]:
        """生成所有场景的音频"""
        self.logger.info("🎤 生成所有真人直播场景音频")
        self.logger.info("=" * 60)
        
        results = {}
        
        for scenario in self.live_scenarios.keys():
            self.logger.info(f"\n🎯 处理场景: {scenario}")
            result = self.generate_scenario_audio(input_file, scenario)
            results[scenario] = result
        
        # 显示结果摘要
        self.logger.info("\n📋 生成结果摘要:")
        for scenario, result in results.items():
            if result and result.get('success'):
                self.logger.info(f"  ✅ {scenario}: {result['output_file']}")
            else:
                self.logger.info(f"  ❌ {scenario}: 生成失败")
        
        return results
    
    def create_comparison_set(self, input_file: str) -> Dict[str, str]:
        """创建完整的对比音频集"""
        self.logger.info("🔄 创建完整对比音频集...")
        
        # 生成所有场景
        scenario_results = self.generate_all_scenarios(input_file)
        
        # 生成原始音频
        timestamp = datetime.now().strftime("%H%M%S")
        base_name = Path(input_file).stem
        original_file = f"{base_name}_original_{timestamp}.m4a"
        
        cmd_original = [
            'ffmpeg', '-y', '-i', input_file,
            '-c:a', 'aac', '-b:a', '192k',
            '-ar', '48000', '-ac', '2',
            original_file
        ]
        
        try:
            result = subprocess.run(cmd_original, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"✅ 原始音频创建成功: {original_file}")
            else:
                self.logger.error(f"❌ 原始音频创建失败: {result.stderr}")
        except Exception as e:
            self.logger.error(f"❌ 原始音频创建失败: {e}")
        
        # 整理结果
        comparison_set = {
            'original': original_file,
            'scenarios': {}
        }
        
        for scenario, result in scenario_results.items():
            if result and result.get('success'):
                comparison_set['scenarios'][scenario] = result['output_file']
        
        return comparison_set

def main():
    """主函数"""
    logger.info("🎤 真人直播语音生成器")
    logger.info("=" * 60)
    
    # 查找测试音频文件
    test_audio = '/Volumes/M2/TT_Live_AI_TTS/audio_pipeline/audio_pipeline/input_raw/test_1.wav'
    
    if not Path(test_audio).exists():
        logger.error(f"❌ 测试音频文件不存在: {test_audio}")
        return
    
    logger.info(f"🎵 使用测试音频: {test_audio}")
    
    # 创建生成器
    generator = LiveSpeechGenerator()
    
    # 显示可用场景
    logger.info("\n🎯 可用直播场景:")
    for scenario, config in generator.live_scenarios.items():
        logger.info(f"  {scenario}: {config['name']} - {config['description']}")
    
    # 创建完整对比音频集
    comparison_set = generator.create_comparison_set(test_audio)
    
    # 显示结果
    logger.info("\n📋 生成的对比音频集:")
    logger.info(f"  原始音频: {comparison_set['original']}")
    logger.info("  场景音频:")
    for scenario, file_path in comparison_set['scenarios'].items():
        logger.info(f"    {scenario}: {file_path}")
    
    # 显示场景特点
    logger.info("\n🎤 各场景特点:")
    for scenario, config in generator.live_scenarios.items():
        logger.info(f"  {config['name']}:")
        logger.info(f"    语速范围: {config['tempo_range']}")
        logger.info(f"    音高范围: {config['pitch_range']}")
        logger.info(f"    背景音概率: {config['background_prob']}")
        logger.info(f"    事件音概率: {config['event_prob']}")

if __name__ == '__main__':
    main()
