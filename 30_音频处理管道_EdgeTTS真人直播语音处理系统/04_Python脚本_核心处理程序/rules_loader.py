#!/usr/bin/env python3
"""
规则加载器 - 集成到主处理程序
从rules_config.json加载规则并应用到音频处理
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class RulesLoader:
    """规则加载器"""
    
    def __init__(self, config_file: str = "rules_config.json"):
        self.config_file = Path(config_file)
        self.rules = None
        self.logger = logging.getLogger(__name__)
        self.load_rules()
    
    def load_rules(self) -> bool:
        """加载规则配置"""
        if not self.config_file.exists():
            self.logger.error(f"规则配置文件不存在: {self.config_file}")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            
            # 验证规则结构
            if 'audio_processing_rules' not in self.rules:
                self.logger.error("规则配置文件格式错误：缺少audio_processing_rules")
                return False
            
            self.logger.info(f"✅ 规则配置已加载: {self.config_file}")
            self.logger.info(f"📅 最后更新: {self.rules['audio_processing_rules'].get('last_updated', '未知')}")
            return True
            
        except Exception as e:
            self.logger.error(f"加载规则配置失败: {e}")
            return False
    
    def get_rule(self, path: str, default: Any = None) -> Any:
        """获取规则值"""
        if not self.rules:
            return default
        
        keys = path.split('.')
        value = self.rules['audio_processing_rules']
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_tempo_range(self) -> tuple:
        """获取语速调整范围"""
        range_value = self.get_rule('tempo_adjustment.base_range', [0.88, 1.12])
        if isinstance(range_value, str):
            # 如果是字符串，尝试解析
            try:
                import ast
                range_list = ast.literal_eval(range_value)
                return tuple(range_list)
            except:
                return (0.88, 1.12)
        elif isinstance(range_value, list):
            return tuple(range_value)
        else:
            return (0.88, 1.12)
    
    def get_pitch_range(self) -> tuple:
        """获取音高调整范围"""
        range_value = self.get_rule('pitch_adjustment.base_range', [-0.4, 0.4])
        if isinstance(range_value, str):
            try:
                import ast
                range_list = ast.literal_eval(range_value)
                return tuple(range_list)
            except:
                return (-0.4, 0.4)
        elif isinstance(range_value, list):
            return tuple(range_value)
        else:
            return (-0.4, 0.4)
    
    def get_background_probability(self) -> float:
        """获取背景音效添加概率"""
        return self.get_rule('background_sounds.probability', 0.8)
    
    def get_background_volume_range(self) -> tuple:
        """获取背景音效音量范围"""
        range_value = self.get_rule('background_sounds.volume_range', [0.15, 0.35])
        if isinstance(range_value, str):
            try:
                import ast
                range_list = ast.literal_eval(range_value)
                return tuple(range_list)
            except:
                return (0.15, 0.35)
        elif isinstance(range_value, list):
            return tuple(range_value)
        else:
            return (0.15, 0.35)
    
    def get_event_probability(self) -> float:
        """获取事件音效添加概率"""
        return self.get_rule('event_sounds.probability', 0.15)
    
    def get_max_events_per_file(self) -> int:
        """获取每个文件最大事件数"""
        return self.get_rule('event_sounds.max_events_per_file', 2)
    
    def get_noise_amplitude_range(self) -> tuple:
        """获取白噪音幅度范围"""
        range_value = self.get_rule('audio_enhancement.noise_amplitude_range', [0.008, 0.015])
        if isinstance(range_value, str):
            try:
                import ast
                range_list = ast.literal_eval(range_value)
                return tuple(range_list)
            except:
                return (0.008, 0.015)
        elif isinstance(range_value, list):
            return tuple(range_value)
        else:
            return (0.008, 0.015)
    
    def get_compressor_settings(self) -> Dict[str, Any]:
        """获取压缩器设置"""
        compressor = self.get_rule('audio_enhancement.compressor', {})
        return {
            'threshold': compressor.get('threshold', -18),
            'ratio': compressor.get('ratio', 3),
            'attack': compressor.get('attack', 15),
            'release': compressor.get('release', 180),
            'makeup': compressor.get('makeup', 3)
        }
    
    def get_equalizer_settings(self) -> Dict[str, Any]:
        """获取EQ设置"""
        eq = self.get_rule('audio_enhancement.equalizer', {})
        bands = eq.get('bands', [
            {'frequency': 250, 'gain_range': [1.5, 2.5], 'width': 120},
            {'frequency': 3500, 'gain_range': [1.8, 2.8], 'width': 800}
        ])
        return {'bands': bands}
    
    def get_highpass_frequency(self) -> int:
        """获取高通滤波器频率"""
        return self.get_rule('audio_enhancement.highpass_filter.frequency', 80)
    
    def get_loudnorm_settings(self) -> Dict[str, Any]:
        """获取响度归一化设置"""
        loudnorm = self.get_rule('audio_enhancement.loudnorm', {})
        return {
            'I': loudnorm.get('I', -19),
            'TP': loudnorm.get('TP', -2),
            'LRA': loudnorm.get('LRA', 9)
        }
    
    def get_output_format(self) -> str:
        """获取输出格式"""
        return self.get_rule('output_settings.format', 'm4a')
    
    def get_output_bitrate(self) -> int:
        """获取输出比特率"""
        return self.get_rule('output_settings.bitrate', 192)
    
    def get_codec_priority(self) -> list:
        """获取编码器优先级"""
        return self.get_rule('output_settings.codec_priority', ['libfdk_aac', 'libmp3lame', 'aac'])
    
    def get_max_workers(self) -> int:
        """获取最大并行处理数"""
        return self.get_rule('processing_settings.max_workers', 4)
    
    def get_timeout(self) -> int:
        """获取处理超时时间"""
        return self.get_rule('processing_settings.timeout', 600)
    
    def get_variation_level(self) -> str:
        """获取变化程度"""
        return self.get_rule('randomization.variation_level', 'medium')
    
    def get_seed_mode(self) -> str:
        """获取种子模式"""
        return self.get_rule('randomization.seed_mode', 'auto')
    
    def get_fixed_seed(self) -> Optional[int]:
        """获取固定种子值"""
        return self.get_rule('randomization.fixed_seed', None)
    
    def is_tempo_adjustment_enabled(self) -> bool:
        """是否启用语速调整"""
        return self.get_rule('tempo_adjustment.enabled', True)
    
    def is_pitch_adjustment_enabled(self) -> bool:
        """是否启用音高调整"""
        return self.get_rule('pitch_adjustment.enabled', True)
    
    def is_background_sounds_enabled(self) -> bool:
        """是否启用背景音效"""
        return self.get_rule('background_sounds.enabled', True)
    
    def is_event_sounds_enabled(self) -> bool:
        """是否启用事件音效"""
        return self.get_rule('event_sounds.enabled', True)
    
    def is_audio_enhancement_enabled(self) -> bool:
        """是否启用音频增强"""
        return self.get_rule('audio_enhancement.enabled', True)
    
    def is_rubberband_priority(self) -> bool:
        """是否优先使用Rubberband"""
        return self.get_rule('advanced_features.rubberband_priority', True)
    
    def is_sox_resampler_enabled(self) -> bool:
        """是否启用SoX重采样器"""
        return self.get_rule('advanced_features.sox_resampler', True)
    
    def get_voice_type_adjustment(self, voice_type: str) -> Dict[str, Any]:
        """获取特定语音类型的调整参数"""
        tempo_adj = self.get_rule(f'tempo_adjustment.voice_type_adjustments.{voice_type}', {})
        pitch_adj = self.get_rule(f'pitch_adjustment.voice_type_adjustments.{voice_type}', {})
        
        return {
            'tempo_range': tempo_adj.get('range', self.get_tempo_range()),
            'pitch_range': pitch_adj.get('range', self.get_pitch_range())
        }
    
    def get_duration_adjustment(self, duration: float) -> tuple:
        """根据音频时长获取语速调整范围"""
        duration_adjustments = self.get_rule('tempo_adjustment.duration_adjustments', {})
        
        if duration <= duration_adjustments.get('short', {}).get('max_duration', 30):
            return tuple(duration_adjustments.get('short', {}).get('range', [0.95, 1.05]))
        elif duration <= duration_adjustments.get('medium', {}).get('max_duration', 60):
            return tuple(duration_adjustments.get('medium', {}).get('range', [0.90, 1.10]))
        else:
            return tuple(duration_adjustments.get('long', {}).get('range', [0.88, 1.12]))
    
    def get_background_environments(self) -> Dict[str, Dict[str, Any]]:
        """获取背景环境音效配置"""
        return self.get_rule('background_sounds.environments', {})
    
    def get_event_sounds(self) -> Dict[str, Dict[str, Any]]:
        """获取事件音效配置"""
        return self.get_rule('event_sounds.events', {})
    
    def get_trigger_timing(self) -> Dict[str, float]:
        """获取事件音效触发时间配置"""
        return self.get_rule('event_sounds.trigger_timing', {
            'start_percentage': 0.2,
            'end_percentage': 0.8
        })
    
    def get_fade_settings(self) -> Dict[str, float]:
        """获取淡入淡出设置"""
        return self.get_rule('background_sounds.fade_settings', {
            'fade_in_duration': 2.0,
            'fade_out_duration': 2.0
        })
    
    def get_quality_control_settings(self) -> Dict[str, Any]:
        """获取质量控制设置"""
        return {
            'min_duration': self.get_rule('quality_control.min_duration', 3.0),
            'max_duration': self.get_rule('quality_control.max_duration', 600.0),
            'sample_rate_target': self.get_rule('quality_control.sample_rate_target', 48000),
            'channels_target': self.get_rule('quality_control.channels_target', 2),
            'max_retries': self.get_rule('quality_control.retry_settings.max_retries', 3),
            'retry_delay': self.get_rule('quality_control.retry_settings.retry_delay', 1.0)
        }
    
    def get_logging_settings(self) -> Dict[str, Any]:
        """获取日志设置"""
        return {
            'level': self.get_rule('logging.level', 'INFO'),
            'file_logging': self.get_rule('logging.file_logging', True),
            'console_logging': self.get_rule('logging.console_logging', True),
            'log_rotation': self.get_rule('logging.log_rotation', True),
            'max_log_size': self.get_rule('logging.max_log_size', '10MB')
        }
    
    def reload_rules(self) -> bool:
        """重新加载规则"""
        self.logger.info("🔄 重新加载规则配置...")
        return self.load_rules()
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """获取规则摘要"""
        if not self.rules:
            return {}
        
        return {
            'version': self.get_rule('version', '1.0.0'),
            'last_updated': self.get_rule('last_updated', '未知'),
            'tempo_range': self.get_tempo_range(),
            'pitch_range': self.get_pitch_range(),
            'background_probability': self.get_background_probability(),
            'event_probability': self.get_event_probability(),
            'output_format': self.get_output_format(),
            'max_workers': self.get_max_workers(),
            'variation_level': self.get_variation_level()
        }

# 全局规则加载器实例
rules_loader = None

def get_rules_loader() -> RulesLoader:
    """获取全局规则加载器实例"""
    global rules_loader
    if rules_loader is None:
        rules_loader = RulesLoader()
    return rules_loader

def reload_rules() -> bool:
    """重新加载规则"""
    global rules_loader
    if rules_loader is None:
        rules_loader = RulesLoader()
    return rules_loader.reload_rules()

if __name__ == '__main__':
    # 测试规则加载器
    loader = RulesLoader()
    
    print("📋 规则加载器测试")
    print("=" * 50)
    
    print(f"语速范围: {loader.get_tempo_range()}")
    print(f"音高范围: {loader.get_pitch_range()}")
    print(f"背景音效概率: {loader.get_background_probability()}")
    print(f"事件音效概率: {loader.get_event_probability()}")
    print(f"输出格式: {loader.get_output_format()}")
    print(f"最大并行数: {loader.get_max_workers()}")
    print(f"变化程度: {loader.get_variation_level()}")
    
    print("\n📊 规则摘要:")
    summary = loader.get_rules_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 规则加载器测试完成")
