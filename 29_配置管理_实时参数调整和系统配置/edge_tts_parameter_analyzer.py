#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS底层参数调用分析器
展示EdgeTTS原生参数与Python语音控制参数的合并输出
"""

import json
import os
import asyncio
import edge_tts
import logging
from typing import Dict, List, Any
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG_FILE = "29_配置管理_实时参数调整和系统配置/tts_config.json"

class EdgeTTSParameterAnalyzer:
    """EdgeTTS参数分析器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.edge_tts_voices = []
        self.parameter_mapping = {}
        
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.error(f"❌ 配置文件 {CONFIG_FILE} 不存在")
            return {}
    
    async def get_edge_tts_voices(self):
        """获取EdgeTTS所有可用语音"""
        try:
            voices = await edge_tts.list_voices()
            self.edge_tts_voices = voices
            logger.info(f"✅ 成功获取 {len(voices)} 个EdgeTTS语音")
            return voices
        except Exception as e:
            logger.error(f"❌ 获取EdgeTTS语音失败: {e}")
            return []
    
    def analyze_edge_tts_parameters(self):
        """分析EdgeTTS底层参数"""
        edge_tts_params = {
            "core_parameters": {
                "text": {
                    "type": "string",
                    "description": "要转换的文本内容",
                    "required": True,
                    "example": "Hello, this is a test."
                },
                "voice": {
                    "type": "string", 
                    "description": "语音名称",
                    "required": True,
                    "example": "en-US-JennyNeural",
                    "available_values": "所有EdgeTTS支持的语音"
                },
                "rate": {
                    "type": "string",
                    "description": "语速控制",
                    "required": False,
                    "default": "+0%",
                    "format": "百分比格式，如 +20%, -10%",
                    "range": "-50% 到 +200%",
                    "example": "+20%"
                },
                "pitch": {
                    "type": "string",
                    "description": "音调控制", 
                    "required": False,
                    "default": "+0Hz",
                    "format": "频率格式，如 +50Hz, -30Hz",
                    "range": "-50Hz 到 +50Hz",
                    "example": "+10Hz"
                },
                "volume": {
                    "type": "string",
                    "description": "音量控制",
                    "required": False,
                    "default": "+0%",
                    "format": "百分比格式，如 +20%, -10%",
                    "range": "-50% 到 +50%",
                    "example": "+5%"
                }
            },
            "ssml_parameters": {
                "prosody": {
                    "rate": "语速控制，支持相对和绝对值",
                    "pitch": "音调控制，支持相对和绝对值", 
                    "volume": "音量控制，支持相对和绝对值"
                },
                "break": {
                    "time": "停顿时间，如 1s, 500ms",
                    "strength": "停顿强度：none, x-weak, weak, medium, strong, x-strong"
                },
                "emphasis": {
                    "level": "重音级别：strong, moderate, reduced"
                },
                "speak": {
                    "role": "说话角色，如 young adult female, elderly male"
                }
            },
            "audio_format_parameters": {
                "format": {
                    "type": "string",
                    "description": "音频格式",
                    "options": ["mp3", "wav", "ogg", "webm"],
                    "default": "mp3"
                },
                "sample_rate": {
                    "type": "integer",
                    "description": "采样率",
                    "options": [8000, 16000, 22050, 44100, 48000],
                    "default": 22050
                },
                "bit_rate": {
                    "type": "integer", 
                    "description": "比特率",
                    "options": [64, 128, 192, 256, 320],
                    "default": 128
                }
            }
        }
        return edge_tts_params
    
    def analyze_python_control_parameters(self):
        """分析Python语音控制参数"""
        python_params = {
            "emotion_control": {
                "description": "情绪控制参数，基于配置文件",
                "parameters": self.config.get("emotion_settings", {}).get("emotion_parameters", {}),
                "mapping": self.config.get("emotion_settings", {}).get("emotion_mapping", {})
            },
            "dynamic_parameters": {
                "description": "动态参数生成，模拟真人语音",
                "parameters": self.config.get("dynamic_parameters", {}),
                "features": {
                    "variation_intensity": "变化强度控制",
                    "anti_detection_enabled": "反检测功能",
                    "human_features_enabled": "人类特征模拟"
                }
            },
            "system_parameters": {
                "description": "系统性能参数",
                "parameters": self.config.get("system_settings", {}),
                "features": {
                    "max_concurrent": "最大并发数",
                    "batch_size": "批处理大小",
                    "retry_attempts": "重试次数"
                }
            },
            "voice_mapping": {
                "description": "文件语音映射",
                "parameters": self.config.get("voice_settings", {}).get("file_voice_mapping", {}),
                "extended_library": self.config.get("voice_settings", {}).get("extended_voice_library", {})
            }
        }
        return python_params
    
    def create_parameter_conversion_mapping(self):
        """创建参数转换映射"""
        conversion_mapping = {
            "rate_conversion": {
                "python_to_edge_tts": {
                    "description": "Python语速参数转换为EdgeTTS格式",
                    "formula": "edge_tts_rate = f\"{int((python_rate - 1) * 100):+d}%\"",
                    "examples": {
                        "0.8": "-20%",
                        "0.9": "-10%", 
                        "1.0": "+0%",
                        "1.1": "+10%",
                        "1.2": "+20%",
                        "1.3": "+30%"
                    }
                }
            },
            "pitch_conversion": {
                "python_to_edge_tts": {
                    "description": "Python音调参数转换为EdgeTTS格式",
                    "formula": "edge_tts_pitch = f\"{int((python_pitch - 1) * 50):+d}Hz\"",
                    "examples": {
                        "0.8": "-10Hz",
                        "0.9": "-5Hz",
                        "1.0": "+0Hz", 
                        "1.1": "+5Hz",
                        "1.2": "+10Hz"
                    }
                }
            },
            "volume_conversion": {
                "python_to_edge_tts": {
                    "description": "Python音量参数转换为EdgeTTS格式",
                    "formula": "edge_tts_volume = f\"{int((python_volume - 1) * 50):+d}%\"",
                    "examples": {
                        "0.7": "-15%",
                        "0.8": "-10%",
                        "0.9": "-5%",
                        "1.0": "+0%",
                        "1.1": "+5%"
                    }
                }
            }
        }
        return conversion_mapping
    
    def generate_ssml_template(self, text: str, emotion: str = "Friendly", voice: str = "en-US-JennyNeural"):
        """生成SSML模板"""
        emotion_params = self.config.get("emotion_settings", {}).get("emotion_parameters", {}).get(emotion, {})
        
        # 获取情绪参数
        rate_range = emotion_params.get("rate_range", [0.95, 1.0])
        pitch_range = emotion_params.get("pitch_range", [0.95, 1.0]) 
        volume_range = emotion_params.get("volume_range", [0.95, 1.0])
        
        # 转换为EdgeTTS格式
        rate = f"{int((rate_range[0] - 1) * 100):+d}%"
        pitch = f"{int((pitch_range[0] - 1) * 50):+d}Hz"
        volume = f"{int((volume_range[0] - 1) * 50):+d}%"
        
        ssml_template = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="{voice}">
        <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
            {text}
        </prosody>
    </voice>
</speak>"""
        
        return ssml_template
    
    def create_parameter_comparison_table(self):
        """创建参数对比表"""
        comparison_table = {
            "parameter_comparison": {
                "rate": {
                    "edge_tts_format": "字符串百分比格式",
                    "edge_tts_example": "+20%, -10%",
                    "python_format": "浮点数倍数格式", 
                    "python_example": "1.2, 0.9",
                    "conversion": "python_value = 1 + (edge_tts_percentage / 100)"
                },
                "pitch": {
                    "edge_tts_format": "字符串频率格式",
                    "edge_tts_example": "+10Hz, -5Hz",
                    "python_format": "浮点数倍数格式",
                    "python_example": "1.1, 0.95", 
                    "conversion": "python_value = 1 + (edge_tts_hz / 50)"
                },
                "volume": {
                    "edge_tts_format": "字符串百分比格式",
                    "edge_tts_example": "+15%, -10%",
                    "python_format": "浮点数倍数格式",
                    "python_example": "1.15, 0.9",
                    "conversion": "python_value = 1 + (edge_tts_percentage / 100)"
                }
            }
        }
        return comparison_table
    
    async def demonstrate_parameter_usage(self):
        """演示参数使用"""
        demo_text = "Hello, this is a demonstration of EdgeTTS parameters with Python control."
        
        demonstrations = []
        
        # 演示不同情绪的SSML生成
        emotions = ["Urgent", "Calm", "Warm", "Excited", "Professional"]
        voices = ["en-US-JennyNeural", "en-US-AvaNeural", "en-US-KaiNeural"]
        
        for emotion in emotions:
            for voice in voices:
                ssml = self.generate_ssml_template(demo_text, emotion, voice)
                demonstrations.append({
                    "emotion": emotion,
                    "voice": voice,
                    "ssml": ssml,
                    "python_parameters": self.config.get("emotion_settings", {}).get("emotion_parameters", {}).get(emotion, {})
                })
        
        return demonstrations
    
    def generate_complete_analysis_report(self):
        """生成完整分析报告"""
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "edge_tts_parameters": self.analyze_edge_tts_parameters(),
            "python_control_parameters": self.analyze_python_control_parameters(),
            "parameter_conversion": self.create_parameter_conversion_mapping(),
            "parameter_comparison": self.create_parameter_comparison_table(),
            "configuration_summary": {
                "total_voices_configured": len(self.config.get("voice_settings", {}).get("file_voice_mapping", {})),
                "total_emotions_configured": len(self.config.get("emotion_settings", {}).get("emotion_parameters", {})),
                "extended_voice_library_size": {
                    "female_voices": len(self.config.get("voice_settings", {}).get("extended_voice_library", {}).get("female_voices", {})),
                    "male_voices": len(self.config.get("voice_settings", {}).get("extended_voice_library", {}).get("male_voices", {})),
                    "multilingual_voices": len(self.config.get("voice_settings", {}).get("extended_voice_library", {}).get("multilingual_voices", {}))
                }
            }
        }
        return report

async def main():
    """主函数"""
    print("🔍 EdgeTTS参数分析器启动")
    print("=" * 60)
    
    analyzer = EdgeTTSParameterAnalyzer()
    
    # 获取EdgeTTS语音列表
    print("📋 获取EdgeTTS语音列表...")
    voices = await analyzer.get_edge_tts_voices()
    
    # 生成分析报告
    print("📊 生成参数分析报告...")
    report = analyzer.generate_complete_analysis_report()
    
    # 添加EdgeTTS语音信息
    report["edge_tts_voice_list"] = {
        "total_voices": len(voices),
        "sample_voices": voices[:10] if voices else [],  # 显示前10个语音作为示例
        "voice_categories": {
            "female_voices": [v for v in voices if v.get('Gender') == 'Female'][:5],
            "male_voices": [v for v in voices if v.get('Gender') == 'Male'][:5],
            "neutral_voices": [v for v in voices if v.get('Gender') == 'Neutral'][:3]
        } if voices else {}
    }
    
    # 演示参数使用
    print("🎭 生成参数使用演示...")
    demonstrations = await analyzer.demonstrate_parameter_usage()
    report["parameter_demonstrations"] = demonstrations[:5]  # 显示前5个演示
    
    # 保存报告
    report_file = "29_配置管理_实时参数调整和系统配置/edge_tts_parameter_analysis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 分析报告已保存到: {report_file}")
    
    # 显示关键信息
    print("\n📈 关键统计信息:")
    print(f"   - EdgeTTS可用语音总数: {len(voices)}")
    print(f"   - 配置的Excel文件语音映射: {report['configuration_summary']['total_voices_configured']}")
    print(f"   - 配置的情绪类型: {report['configuration_summary']['total_emotions_configured']}")
    print(f"   - 扩展女性语音库: {report['configuration_summary']['extended_voice_library_size']['female_voices']}")
    print(f"   - 扩展男性语音库: {report['configuration_summary']['extended_voice_library_size']['male_voices']}")
    print(f"   - 多语言语音库: {report['configuration_summary']['extended_voice_library_size']['multilingual_voices']}")
    
    print("\n🎯 参数转换示例:")
    conversion = report["parameter_conversion"]["rate_conversion"]["python_to_edge_tts"]["examples"]
    for python_val, edge_val in list(conversion.items())[:3]:
        print(f"   - Python: {python_val} → EdgeTTS: {edge_val}")
    
    print("\n📝 使用建议:")
    print("   1. 使用Python参数进行高级控制和情绪管理")
    print("   2. EdgeTTS原生参数用于底层音频生成")
    print("   3. 通过转换映射实现参数格式统一")
    print("   4. 利用扩展语音库增加语音多样性")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())
