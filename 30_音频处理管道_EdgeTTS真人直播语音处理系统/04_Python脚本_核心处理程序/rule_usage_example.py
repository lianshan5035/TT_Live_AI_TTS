#!/usr/bin/env python3
"""
EdgeTTS音频处理规则使用示例
展示如何在实际处理中使用规则配置
"""

import random
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json

# 导入规则加载器
from rules_loader import get_rules_loader, reload_rules

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RuleBasedAudioProcessor:
    """基于规则的音频处理器"""
    
    def __init__(self):
        self.rules = get_rules_loader()
        self.logger = logging.getLogger(__name__)
        
        # 设置随机种子
        self._setup_random_seed()
    
    def _setup_random_seed(self):
        """设置随机种子"""
        seed_mode = self.rules.get_seed_mode()
        fixed_seed = self.rules.get_fixed_seed()
        
        if seed_mode == '固定' and fixed_seed is not None:
            random.seed(fixed_seed)
            self.logger.info(f"🎲 使用固定随机种子: {fixed_seed}")
        elif seed_mode == 'auto':
            # 使用当前时间作为种子
            import time
            seed = int(time.time())
            random.seed(seed)
            self.logger.info(f"🎲 使用自动随机种子: {seed}")
        else:
            # 完全随机
            self.logger.info("🎲 使用完全随机模式")
    
    def generate_processing_params(self, audio_duration: float, voice_type: str = 'calm') -> Dict[str, Any]:
        """根据规则生成处理参数"""
        params = {}
        
        # 1. 语速调整
        if self.rules.is_tempo_adjustment_enabled():
            # 根据语音类型和时长获取范围
            voice_adj = self.rules.get_voice_type_adjustment(voice_type)
            duration_adj = self.rules.get_duration_adjustment(audio_duration)
            
            # 选择更合适的范围
            tempo_range = voice_adj['tempo_range'] if voice_adj['tempo_range'] != self.rules.get_tempo_range() else duration_adj
            
            params['tempo'] = random.uniform(*tempo_range)
            self.logger.info(f"📊 语速调整: {params['tempo']:.3f}x (范围: {tempo_range})")
        else:
            params['tempo'] = 1.0
            self.logger.info("📊 语速调整: 禁用")
        
        # 2. 音高调整
        if self.rules.is_pitch_adjustment_enabled():
            voice_adj = self.rules.get_voice_type_adjustment(voice_type)
            pitch_range = voice_adj['pitch_range'] if voice_adj['pitch_range'] != self.rules.get_pitch_range() else self.rules.get_pitch_range()
            
            params['pitch_semitones'] = random.uniform(*pitch_range)
            self.logger.info(f"🎵 音高调整: {params['pitch_semitones']:.3f}半音 (范围: {pitch_range})")
        else:
            params['pitch_semitones'] = 0.0
            self.logger.info("🎵 音高调整: 禁用")
        
        # 3. 背景音效
        if self.rules.is_background_sounds_enabled():
            bg_prob = self.rules.get_background_probability()
            if random.random() < bg_prob:
                environments = self.rules.get_background_environments()
                if environments:
                    # 随机选择环境
                    env_name = random.choice(list(environments.keys()))
                    env_config = environments[env_name]
                    
                    params['background_sound'] = {
                        'file': env_config['file'],
                        'volume': random.uniform(*env_config['volume_range']),
                        'start_offset': random.uniform(0, max(0, 120 - audio_duration - 2)),  # 假设背景音效2分钟
                        'looped': audio_duration > 60  # 长音频需要循环
                    }
                    self.logger.info(f"🌍 背景音效: {env_name} (音量: {params['background_sound']['volume']:.3f})")
                else:
                    params['background_sound'] = None
                    self.logger.info("🌍 背景音效: 无可用环境音效")
            else:
                params['background_sound'] = None
                self.logger.info("🌍 背景音效: 未触发")
        else:
            params['background_sound'] = None
            self.logger.info("🌍 背景音效: 禁用")
        
        # 4. 事件音效
        if self.rules.is_event_sounds_enabled():
            event_prob = self.rules.get_event_probability()
            max_events = self.rules.get_max_events_per_file()
            
            params['events'] = []
            if random.random() < event_prob:
                events_config = self.rules.get_event_sounds()
                trigger_timing = self.rules.get_trigger_timing()
                
                num_events = random.randint(1, max_events)
                for _ in range(num_events):
                    if events_config:
                        event_name = random.choice(list(events_config.keys()))
                        event_config = events_config[event_name]
                        
                        # 计算触发时间
                        start_time = audio_duration * trigger_timing['start_percentage']
                        end_time = audio_duration * trigger_timing['end_percentage']
                        trigger_time = random.uniform(start_time, end_time)
                        
                        params['events'].append({
                            'file': event_config['file'],
                            'volume': random.uniform(*event_config['volume_range']),
                            'trigger_time': trigger_time,
                            'duration': random.uniform(*event_config['duration_range'])
                        })
                
                self.logger.info(f"🔊 事件音效: {len(params['events'])}个事件")
            else:
                self.logger.info("🔊 事件音效: 未触发")
        else:
            params['events'] = []
            self.logger.info("🔊 事件音效: 禁用")
        
        # 5. 音频增强参数
        if self.rules.is_audio_enhancement_enabled():
            # 压缩器设置
            compressor = self.rules.get_compressor_settings()
            params['compressor'] = compressor
            
            # EQ设置
            eq = self.rules.get_equalizer_settings()
            params['equalizer'] = eq
            
            # 高通滤波器
            params['highpass_frequency'] = self.rules.get_highpass_frequency()
            
            # 响度归一化
            params['loudnorm'] = self.rules.get_loudnorm_settings()
            
            self.logger.info(f"⚡ 音频增强: 启用 (高通: {params['highpass_frequency']}Hz)")
        else:
            self.logger.info("⚡ 音频增强: 禁用")
        
        # 6. 白噪音
        noise_range = self.rules.get_noise_amplitude_range()
        params['noise_amplitude'] = random.uniform(*noise_range)
        self.logger.info(f"🔇 白噪音幅度: {params['noise_amplitude']:.4f}")
        
        # 7. 输出设置
        params['output_format'] = self.rules.get_output_format()
        params['output_bitrate'] = self.rules.get_output_bitrate()
        params['codec_priority'] = self.rules.get_codec_priority()
        
        self.logger.info(f"📁 输出设置: {params['output_format']} @ {params['output_bitrate']}kbps")
        
        return params
    
    def build_ffmpeg_command(self, input_file: str, output_file: str, params: Dict[str, Any]) -> List[str]:
        """根据参数构建FFmpeg命令"""
        cmd = ['ffmpeg', '-y', '-i', input_file]
        
        # 构建滤镜链
        filters = []
        
        # 1. 采样率转换
        filters.append('aresample=48000')
        
        # 2. 语速和音高调整
        if params['tempo'] != 1.0 or params['pitch_semitones'] != 0.0:
            if self.rules.is_rubberband_priority():
                # 使用Rubberband
                pitch_ratio = 2 ** (params['pitch_semitones'] / 12)
                filters.append(f"rubberband=tempo={params['tempo']}:pitch={pitch_ratio}:formant=preserved")
            else:
                # 使用atempo回退
                tempo = params['tempo']
                while tempo > 2.0:
                    filters.append('atempo=2.0')
                    tempo /= 2.0
                while tempo < 0.5:
                    filters.append('atempo=0.5')
                    tempo /= 0.5
                filters.append(f'atempo={tempo}')
        
        # 3. 音频增强
        if self.rules.is_audio_enhancement_enabled():
            compressor = params['compressor']
            filters.append(f"acompressor=threshold={compressor['threshold']}dB:ratio={compressor['ratio']}:attack={compressor['attack']}:release={compressor['release']}:makeup={compressor['makeup']}")
            
            # EQ
            for band in params['equalizer']['bands']:
                filters.append(f"equalizer=f={band['frequency']}:width_type=h:width={band['width']}:g={random.uniform(*band['gain_range'])}")
            
            # 高通滤波器
            filters.append(f"highpass=f={params['highpass_frequency']}")
        
        # 4. 响度归一化
        loudnorm = params['loudnorm']
        filters.append(f"loudnorm=I={loudnorm['I']}:TP={loudnorm['TP']}:LRA={loudnorm['LRA']}")
        
        # 应用滤镜
        if filters:
            cmd.extend(['-af', ','.join(filters)])
        
        # 5. 输出编码
        codec_priority = params['codec_priority']
        if 'libfdk_aac' in codec_priority:
            cmd.extend(['-c:a', 'libfdk_aac', '-b:a', f"{params['output_bitrate']}k"])
        elif 'libmp3lame' in codec_priority:
            cmd.extend(['-c:a', 'libmp3lame', '-b:a', f"{params['output_bitrate']}k"])
        else:
            cmd.extend(['-c:a', 'aac', '-b:a', f"{params['output_bitrate']}k"])
        
        cmd.extend(['-ar', '48000', '-ac', '2'])
        cmd.append(output_file)
        
        return cmd
    
    def process_audio_file(self, input_file: str, output_file: str, voice_type: str = 'calm') -> bool:
        """处理单个音频文件"""
        try:
            # 获取音频时长（这里简化处理）
            audio_duration = 30.0  # 假设30秒
            
            # 生成处理参数
            params = self.generate_processing_params(audio_duration, voice_type)
            
            # 构建FFmpeg命令
            cmd = self.build_ffmpeg_command(input_file, output_file, params)
            
            # 记录命令
            self.logger.info(f"🔧 FFmpeg命令: {' '.join(cmd)}")
            
            # 这里应该执行FFmpeg命令
            # subprocess.run(cmd, check=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 处理失败: {e}")
            return False
    
    def reload_rules(self):
        """重新加载规则"""
        if reload_rules():
            self.rules = get_rules_loader()
            self._setup_random_seed()
            self.logger.info("🔄 规则已重新加载")
        else:
            self.logger.error("❌ 规则重新加载失败")

def demo_rule_usage():
    """演示规则使用"""
    print("🎛️  EdgeTTS音频处理规则使用演示")
    print("=" * 60)
    
    # 创建处理器
    processor = RuleBasedAudioProcessor()
    
    # 显示当前规则摘要
    rules_summary = processor.rules.get_rules_summary()
    print("\n📋 当前规则摘要:")
    for key, value in rules_summary.items():
        print(f"  {key}: {value}")
    
    # 模拟处理不同语音类型
    voice_types = ['calm', 'excited', 'serious', 'friendly']
    
    for voice_type in voice_types:
        print(f"\n🎤 处理 {voice_type} 类型语音:")
        print("-" * 40)
        
        # 生成参数
        params = processor.generate_processing_params(45.0, voice_type)
        
        # 显示关键参数
        print(f"  语速: {params['tempo']:.3f}x")
        print(f"  音高: {params['pitch_semitones']:.3f}半音")
        print(f"  背景音效: {'是' if params['background_sound'] else '否'}")
        print(f"  事件音效: {len(params['events'])}个")
        print(f"  白噪音: {params['noise_amplitude']:.4f}")
    
    # 演示规则修改
    print(f"\n🔄 演示规则修改:")
    print("-" * 40)
    
    # 修改语速范围（使用规则管理器）
    from rules_manager import RulesManager
    rules_manager = RulesManager()
    rules_manager.set_rule('tempo_adjustment.base_range', [0.90, 1.10])
    print("✅ 已修改语速范围为 [0.90, 1.10]")
    
    # 重新加载规则
    processor.reload_rules()
    
    # 重新生成参数
    new_params = processor.generate_processing_params(30.0, 'calm')
    print(f"  新语速: {new_params['tempo']:.3f}x")
    
    # 恢复原设置
    rules_manager.set_rule('tempo_adjustment.base_range', [0.95, 1.05])
    processor.reload_rules()
    print("✅ 已恢复原语速范围")

if __name__ == '__main__':
    demo_rule_usage()
