#!/usr/bin/env python3
"""
动态语音处理器 - 混合方案演示
结合EdgeTTS和FFmpeg实现接近真人说话的节奏感
"""

import os
import sys
import logging
import subprocess
import random
import time
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

class DynamicVoiceProcessor:
    """动态语音处理器 - 混合方案"""
    
    def __init__(self):
        self.ffmpeg_processor = FFmpegAudioProcessor()
        
        # 情感参数映射
        self.emotion_params = {
            "excited": {
                "rate": "+15%",
                "pitch": "+12Hz", 
                "volume": "+10%",
                "description": "兴奋 - 快语速、高音调、大声"
            },
            "calm": {
                "rate": "-10%",
                "pitch": "-5Hz",
                "volume": "-5%",
                "description": "平静 - 慢语速、低音调、小声"
            },
            "urgent": {
                "rate": "+20%",
                "pitch": "+8Hz",
                "volume": "+8%",
                "description": "紧急 - 很快语速、稍高音调、大声"
            },
            "friendly": {
                "rate": "+8%",
                "pitch": "+5Hz",
                "volume": "+3%",
                "description": "友好 - 稍快语速、稍高音调、稍大声"
            },
            "serious": {
                "rate": "-5%",
                "pitch": "-3Hz",
                "volume": "+2%",
                "description": "严肃 - 稍慢语速、低音调、稍大声"
            },
            "playful": {
                "rate": "+18%",
                "pitch": "+15Hz",
                "volume": "+5%",
                "description": "活泼 - 很快语速、高音调、稍大声"
            }
        }
        
        # 文本类型参数
        self.text_type_params = {
            "short": {"rate_adjust": "+5%", "description": "短文本 - 稍快语速"},
            "medium": {"rate_adjust": "+0%", "description": "中等文本 - 正常语速"},
            "long": {"rate_adjust": "-8%", "description": "长文本 - 稍慢语速"},
            "question": {"rate_adjust": "+3%", "pitch_adjust": "+2Hz", "description": "疑问句 - 稍快稍高"},
            "exclamation": {"rate_adjust": "+10%", "pitch_adjust": "+5Hz", "description": "感叹句 - 快高"}
        }
    
    def analyze_text(self, text: str) -> dict:
        """分析文本特征"""
        analysis = {
            "length": len(text),
            "type": "medium",
            "has_question": "?" in text,
            "has_exclamation": "!" in text,
            "word_count": len(text.split()),
            "sentence_count": text.count('.') + text.count('!') + text.count('?')
        }
        
        # 判断文本类型
        if analysis["length"] < 30:
            analysis["type"] = "short"
        elif analysis["length"] > 100:
            analysis["type"] = "long"
        
        if analysis["has_question"]:
            analysis["type"] = "question"
        elif analysis["has_exclamation"]:
            analysis["type"] = "exclamation"
        
        return analysis
    
    def create_dynamic_voice_params(self, text: str, emotion: str = "friendly") -> dict:
        """根据文本和情感创建动态语音参数"""
        
        # 分析文本
        analysis = self.analyze_text(text)
        
        # 获取基础情感参数
        base_params = self.emotion_params.get(emotion, self.emotion_params["friendly"])
        
        # 获取文本类型参数
        text_params = self.text_type_params.get(analysis["type"], self.text_type_params["medium"])
        
        # 组合参数
        final_params = {
            "rate": base_params["rate"],
            "pitch": base_params["pitch"],
            "volume": base_params["volume"],
            "emotion": emotion,
            "text_type": analysis["type"],
            "analysis": analysis
        }
        
        # 根据文本类型调整参数
        if "rate_adjust" in text_params:
            # 简单的参数调整逻辑
            base_rate = int(base_params["rate"].replace('%', ''))
            adjust_rate = int(text_params["rate_adjust"].replace('%', ''))
            final_rate = base_rate + adjust_rate
            final_params["rate"] = f"{final_rate:+d}%"
        
        if "pitch_adjust" in text_params:
            base_pitch = int(base_params["pitch"].replace('Hz', ''))
            adjust_pitch = int(text_params["pitch_adjust"].replace('Hz', ''))
            final_pitch = base_pitch + adjust_pitch
            final_params["pitch"] = f"{final_pitch:+d}Hz"
        
        logger.info(f"文本分析: {analysis}")
        logger.info(f"情感参数: {emotion} - {base_params['description']}")
        logger.info(f"文本类型: {analysis['type']} - {text_params['description']}")
        logger.info(f"最终参数: rate={final_params['rate']}, pitch={final_params['pitch']}, volume={final_params['volume']}")
        
        return final_params
    
    def add_rhythm_enhancement(self, input_file: str, enhancement_level: str = "subtle") -> str:
        """添加节奏增强效果"""
        
        logger.info(f"添加节奏增强效果: {enhancement_level}")
        
        # 根据增强级别选择不同的效果
        enhancement_configs = {
            "subtle": {
                "compressor": "acompressor=threshold=0.089:ratio=9:attack=200:release=1000",
                "echo": "aecho=0.8:0.9:100:0.15",
                "volume_variation": "volume=0.98:enable='between(t,0,1)',volume=1.02:enable='between(t,1,2)',volume=0.99:enable='between(t,2,3)'",
                "description": "微妙增强 - 轻微压缩、回声、音量变化"
            },
            "moderate": {
                "compressor": "acompressor=threshold=0.089:ratio=9:attack=150:release=800",
                "echo": "aecho=0.8:0.9:150:0.25",
                "volume_variation": "volume=0.95:enable='between(t,0,1)',volume=1.05:enable='between(t,1,2)',volume=0.98:enable='between(t,2,3)'",
                "description": "中等增强 - 明显压缩、回声、音量变化"
            },
            "strong": {
                "compressor": "acompressor=threshold=0.089:ratio=9:attack=100:release=600",
                "echo": "aecho=0.8:0.9:200:0.35",
                "volume_variation": "volume=0.92:enable='between(t,0,1)',volume=1.08:enable='between(t,1,2)',volume=0.96:enable='between(t,2,3)'",
                "description": "强烈增强 - 强压缩、回声、音量变化"
            }
        }
        
        config = enhancement_configs[enhancement_level]
        output_file = f"rhythm_enhanced_{enhancement_level}.wav"
        
        logger.info(f"增强配置: {config['description']}")
        
        # 构建FFmpeg命令
        cmd = [
            'ffmpeg', '-y', '-i', input_file,
            '-af', config['compressor'],
            '-af', config['echo'],
            '-af', config['volume_variation'],
            output_file
        ]
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ 节奏增强完成: {output_file}")
            return output_file
        else:
            logger.error(f"✗ 节奏增强失败: {result.stderr}")
            return input_file
    
    def process_with_rhythm(self, text: str, emotion: str = "friendly", 
                          enhancement_level: str = "subtle") -> dict:
        """处理带节奏感的语音 - 完整流程"""
        
        logger.info("=" * 60)
        logger.info("开始动态语音处理")
        logger.info("=" * 60)
        
        # 1. 分析文本并创建动态参数
        voice_params = self.create_dynamic_voice_params(text, emotion)
        
        # 2. 生成基础音频文件（模拟EdgeTTS输出）
        base_audio = f"base_audio_{int(time.time())}.wav"
        logger.info(f"生成基础音频: {base_audio}")
        
        # 这里应该调用EdgeTTS，现在用模拟
        # 实际使用时替换为:
        # self.edgetts_processor.synthesize_single(
        #     text=text,
        #     output_file=base_audio,
        #     rate=voice_params["rate"],
        #     pitch=voice_params["pitch"]
        # )
        
        # 3. 添加节奏增强
        enhanced_audio = self.add_rhythm_enhancement(base_audio, enhancement_level)
        
        # 4. 添加白噪音和背景音效
        final_audio = f"final_rhythmic_{int(time.time())}.m4a"
        
        success = self.ffmpeg_processor.process_single_audio(
            input_file=enhanced_audio,
            output_file=final_audio,
            background_combination=["white_noise", "room_tone"],
            main_volume=0.88
        )
        
        # 5. 清理临时文件
        for temp_file in [base_audio, enhanced_audio]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        result = {
            "success": success,
            "final_audio": final_audio,
            "voice_params": voice_params,
            "enhancement_level": enhancement_level,
            "processing_steps": [
                "文本分析",
                "动态参数生成", 
                "基础音频生成",
                "节奏增强",
                "白噪音混合"
            ]
        }
        
        logger.info("=" * 60)
        logger.info("动态语音处理完成")
        logger.info("=" * 60)
        
        return result
    
    def compare_processing_methods(self, text: str) -> dict:
        """对比不同处理方法的效果"""
        
        logger.info("=" * 60)
        logger.info("对比不同处理方法")
        logger.info("=" * 60)
        
        methods = [
            {"name": "基础处理", "emotion": "friendly", "enhancement": "none"},
            {"name": "微妙增强", "emotion": "friendly", "enhancement": "subtle"},
            {"name": "中等增强", "emotion": "friendly", "enhancement": "moderate"},
            {"name": "强烈增强", "emotion": "friendly", "enhancement": "strong"},
            {"name": "情感化处理", "emotion": "excited", "enhancement": "subtle"},
            {"name": "平静处理", "emotion": "calm", "enhancement": "subtle"}
        ]
        
        results = {}
        
        for method in methods:
            logger.info(f"\n处理方法: {method['name']}")
            
            if method["enhancement"] == "none":
                # 基础处理，只添加白噪音
                result = self.ffmpeg_processor.process_single_audio(
                    input_file="temp_input.wav",  # 需要实际输入文件
                    output_file=f"method_{method['name']}.m4a",
                    background_combination=["white_noise", "room_tone"],
                    main_volume=0.88
                )
                results[method["name"]] = {
                    "success": result,
                    "method": method,
                    "description": "仅添加白噪音和背景音效"
                }
            else:
                # 动态处理
                result = self.process_with_rhythm(
                    text=text,
                    emotion=method["emotion"],
                    enhancement_level=method["enhancement"]
                )
                results[method["name"]] = result
        
        return results

def demonstrate_mixed_approach():
    """演示混合方案的效果"""
    
    logger.info("动态语音处理器 - 混合方案演示")
    
    # 初始化处理器
    processor = DynamicVoiceProcessor()
    
    # 测试文本
    test_texts = [
        "欢迎来到我们的直播间！今天为大家带来超值优惠！",
        "这个产品真的太好用了，强烈推荐给大家！",
        "限时特价，错过就没有了，赶紧下单吧！",
        "有什么问题可以随时问我，我会耐心解答。",
        "感谢大家的支持，我们下期再见！"
    ]
    
    # 测试不同情感
    emotions = ["friendly", "excited", "urgent", "calm", "playful"]
    
    logger.info("=" * 60)
    logger.info("混合方案效果演示")
    logger.info("=" * 60)
    
    for i, text in enumerate(test_texts):
        emotion = emotions[i % len(emotions)]
        
        logger.info(f"\n测试 {i+1}: {text[:20]}...")
        logger.info(f"情感: {emotion}")
        
        # 分析文本
        analysis = processor.analyze_text(text)
        logger.info(f"文本分析: 长度={analysis['length']}, 类型={analysis['type']}")
        
        # 创建动态参数
        params = processor.create_dynamic_voice_params(text, emotion)
        logger.info(f"动态参数: rate={params['rate']}, pitch={params['pitch']}")
        
        # 演示不同增强级别
        for enhancement in ["subtle", "moderate", "strong"]:
            logger.info(f"增强级别: {enhancement}")
            # 这里可以实际调用处理函数
            # result = processor.process_with_rhythm(text, emotion, enhancement)
    
    logger.info("\n" + "=" * 60)
    logger.info("混合方案效果总结")
    logger.info("=" * 60)
    logger.info("1. 文本智能分析:")
    logger.info("   - 自动识别文本长度、类型、情感")
    logger.info("   - 根据内容动态调整语音参数")
    logger.info("")
    logger.info("2. 情感化语音合成:")
    logger.info("   - 6种情感模式：兴奋、平静、紧急、友好、严肃、活泼")
    logger.info("   - 每种情感有独特的语速、音调、音量组合")
    logger.info("")
    logger.info("3. 节奏增强处理:")
    logger.info("   - 微妙增强：轻微压缩、回声、音量变化")
    logger.info("   - 中等增强：明显压缩、回声、音量变化")
    logger.info("   - 强烈增强：强压缩、回声、音量变化")
    logger.info("")
    logger.info("4. 环境音效混合:")
    logger.info("   - 白噪音：增加真实感")
    logger.info("   - 房间音效：模拟直播环境")
    logger.info("   - 动态音量平衡：保持语音清晰度")
    logger.info("")
    logger.info("5. 最终效果:")
    logger.info("   - 接近真人说话的节奏感")
    logger.info("   - 情感表达丰富自然")
    logger.info("   - 避免机械化重复")
    logger.info("   - 适合TikTok直播场景")
    logger.info("=" * 60)

def main():
    """主函数"""
    demonstrate_mixed_approach()

if __name__ == "__main__":
    main()
