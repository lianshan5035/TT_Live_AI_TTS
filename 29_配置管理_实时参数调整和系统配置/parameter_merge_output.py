#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS与Python语音控制参数合并输出表
展示底层参数调用和高级参数控制的完整映射
"""

import json
import os
from datetime import datetime

def create_parameter_merge_table():
    """创建参数合并输出表"""
    
    # EdgeTTS底层参数
    edge_tts_core_params = {
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
            "available_count": 585
        },
        "rate": {
            "type": "string",
            "description": "语速控制",
            "format": "百分比格式",
            "range": "-50% 到 +200%",
            "example": "+20%",
            "default": "+0%"
        },
        "pitch": {
            "type": "string",
            "description": "音调控制",
            "format": "频率格式", 
            "range": "-50Hz 到 +50Hz",
            "example": "+10Hz",
            "default": "+0Hz"
        },
        "volume": {
            "type": "string",
            "description": "音量控制",
            "format": "百分比格式",
            "range": "-50% 到 +50%",
            "example": "+5%",
            "default": "+0%"
        }
    }
    
    # Python语音控制参数
    python_control_params = {
        "emotion_control": {
            "Urgent": {
                "rate_range": [0.95, 1.2],
                "pitch_range": [0.95, 1.1], 
                "volume_range": [0.95, 1.0],
                "description": "紧迫型 - 语速较快，音调略高"
            },
            "Calm": {
                "rate_range": [0.95, 1.0],
                "pitch_range": [0.95, 1.0],
                "volume_range": [0.95, 1.0], 
                "description": "舒缓型 - 语速正常，音调平稳"
            },
            "Warm": {
                "rate_range": [0.8, 1.0],
                "pitch_range": [0.9, 1.1],
                "volume_range": [0.8, 1.0],
                "description": "温暖型 - 语速适中，音调温暖"
            },
            "Excited": {
                "rate_range": [1.0, 1.3],
                "pitch_range": [1.0, 1.2],
                "volume_range": [0.9, 1.1],
                "description": "兴奋型 - 语速较快，音调较高"
            },
            "Professional": {
                "rate_range": [0.8, 1.0],
                "pitch_range": [0.9, 1.0],
                "volume_range": [0.8, 1.0],
                "description": "专业型 - 语速稳定，音调专业"
            }
        },
        "dynamic_parameters": {
            "rate_base_range": [0.7, 1.3],
            "pitch_base_range": [0.8, 1.2],
            "volume_base_range": [0.7, 1.1],
            "variation_intensity": 0.3,
            "anti_detection_enabled": True,
            "human_features_enabled": True
        },
        "system_parameters": {
            "max_concurrent": 12,
            "batch_size": 80,
            "batch_delay": 2,
            "file_delay": 5,
            "retry_attempts": 3,
            "timeout": 60
        }
    }
    
    # 参数转换映射
    conversion_mapping = {
        "rate_conversion": {
            "formula": "edge_tts_rate = f\"{int((python_rate - 1) * 100):+d}%\"",
            "examples": {
                "0.8": "-20%",
                "0.9": "-10%",
                "1.0": "+0%",
                "1.1": "+10%",
                "1.2": "+20%",
                "1.3": "+30%"
            }
        },
        "pitch_conversion": {
            "formula": "edge_tts_pitch = f\"{int((python_pitch - 1) * 50):+d}Hz\"",
            "examples": {
                "0.8": "-10Hz",
                "0.9": "-5Hz",
                "1.0": "+0Hz",
                "1.1": "+5Hz",
                "1.2": "+10Hz"
            }
        },
        "volume_conversion": {
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
    
    # 语音库统计
    voice_library_stats = {
        "edge_tts_total_voices": 585,
        "configured_file_voices": 9,
        "extended_female_voices": 11,
        "extended_male_voices": 11,
        "multilingual_voices": 12,
        "total_extended_library": 34
    }
    
    # 合并输出表
    merged_output = {
        "analysis_timestamp": datetime.now().isoformat(),
        "summary": {
            "edge_tts_core_parameters": len(edge_tts_core_params),
            "python_emotion_types": len(python_control_params["emotion_control"]),
            "total_voice_options": voice_library_stats["edge_tts_total_voices"],
            "extended_voice_library": voice_library_stats["total_extended_library"]
        },
        "edge_tts_底层参数": edge_tts_core_params,
        "python_语音控制参数": python_control_params,
        "参数转换映射": conversion_mapping,
        "语音库统计": voice_library_stats,
        "实际调用示例": {
            "紧迫型_Urgent": {
                "python_params": {
                    "rate": 1.1,
                    "pitch": 1.05,
                    "volume": 0.95
                },
                "edge_tts_params": {
                    "rate": "+10%",
                    "pitch": "+2Hz", 
                    "volume": "-2%"
                },
                "ssml_example": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="en-US-JennyNeural">
        <prosody rate="+10%" pitch="+2Hz" volume="-2%">
            Hello, this is urgent content!
        </prosody>
    </voice>
</speak>"""
            },
            "舒缓型_Calm": {
                "python_params": {
                    "rate": 0.95,
                    "pitch": 0.95,
                    "volume": 0.95
                },
                "edge_tts_params": {
                    "rate": "-5%",
                    "pitch": "-2Hz",
                    "volume": "-2%"
                },
                "ssml_example": """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="en-US-AvaNeural">
        <prosody rate="-5%" pitch="-2Hz" volume="-2%">
            This is calm and soothing content.
        </prosody>
    </voice>
</speak>"""
            }
        },
        "使用流程": {
            "step_1": "Python系统读取配置文件中的情绪参数",
            "step_2": "根据情绪类型选择对应的rate/pitch/volume范围",
            "step_3": "使用动态参数生成算法计算具体数值",
            "step_4": "将Python浮点数参数转换为EdgeTTS字符串格式",
            "step_5": "构建SSML XML格式的语音合成请求",
            "step_6": "调用EdgeTTS底层API进行音频生成",
            "step_7": "保存生成的音频文件到指定目录"
        },
        "技术优势": {
            "python_control": [
                "高级情绪管理",
                "动态参数生成",
                "批量处理优化",
                "断点续传支持",
                "多API并行策略"
            ],
            "edge_tts_native": [
                "高质量神经网络语音",
                "SSML标准支持",
                "多语言语音库",
                "实时语音合成",
                "云端API调用"
            ],
            "combined_benefits": [
                "Python高级控制 + EdgeTTS高质量输出",
                "情绪化语音 + 技术稳定性",
                "批量处理 + 实时生成",
                "配置化管理 + 底层API调用"
            ]
        }
    }
    
    return merged_output

def main():
    """主函数"""
    print("🔗 EdgeTTS与Python语音控制参数合并输出")
    print("=" * 60)
    
    # 生成合并输出表
    merged_table = create_parameter_merge_table()
    
    # 保存到文件
    output_file = "29_配置管理_实时参数调整和系统配置/edge_tts_python_parameter_merge.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_table, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 参数合并输出表已保存到: {output_file}")
    
    # 显示关键信息
    print("\n📊 参数统计:")
    print(f"   - EdgeTTS核心参数: {merged_table['summary']['edge_tts_core_parameters']}")
    print(f"   - Python情绪类型: {merged_table['summary']['python_emotion_types']}")
    print(f"   - EdgeTTS总语音数: {merged_table['summary']['total_voice_options']}")
    print(f"   - 扩展语音库: {merged_table['summary']['extended_voice_library']}")
    
    print("\n🔄 参数转换示例:")
    rate_examples = merged_table["参数转换映射"]["rate_conversion"]["examples"]
    for python_val, edge_val in list(rate_examples.items())[:3]:
        print(f"   - Python: {python_val} → EdgeTTS: {edge_val}")
    
    print("\n🎭 情绪参数示例:")
    for emotion, params in merged_table["python_语音控制参数"]["emotion_control"].items():
        print(f"   - {emotion}: rate={params['rate_range']}, pitch={params['pitch_range']}, volume={params['volume_range']}")
    
    print("\n🚀 使用流程:")
    for step, description in merged_table["使用流程"].items():
        print(f"   {step}: {description}")
    
    print("\n💡 技术优势:")
    print("   Python控制优势:")
    for advantage in merged_table["技术优势"]["python_control"]:
        print(f"     - {advantage}")
    print("   EdgeTTS原生优势:")
    for advantage in merged_table["技术优势"]["edge_tts_native"]:
        print(f"     - {advantage}")
    print("   合并优势:")
    for advantage in merged_table["技术优势"]["combined_benefits"]:
        print(f"     - {advantage}")

if __name__ == "__main__":
    main()
