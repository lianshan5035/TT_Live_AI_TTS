#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS参数集成系统
实现Python语音控制参数与EdgeTTS底层参数的完整映射和转换
"""

import json
import random
import asyncio
import edge_tts
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EdgeTTSParameterMapper:
    """EdgeTTS参数映射器"""
    
    def __init__(self, config_file: str = "tts_config.json"):
        """初始化参数映射器"""
        self.config_file = config_file
        self.config = self._load_config()
        self.emotion_params = self.config.get('emotion_settings', {}).get('emotion_parameters', {})
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "emotion_settings": {
                "emotion_parameters": {
                    "Urgent": {
                        "rate_range": [0.95, 1.2],
                        "pitch_range": [0.95, 1.1],
                        "volume_range": [0.95, 1.0],
                        "description": "紧迫型 - 语速较快，音调略高",
                        "usage_scenario": "限时促销、紧急通知、快节奏内容"
                    },
                    "Calm": {
                        "rate_range": [0.95, 1.0],
                        "pitch_range": [0.95, 1.0],
                        "volume_range": [0.95, 1.0],
                        "description": "舒缓型 - 语速正常，音调平稳",
                        "usage_scenario": "冥想引导、睡前故事、放松内容"
                    },
                    "Warm": {
                        "rate_range": [0.8, 1.0],
                        "pitch_range": [0.9, 1.1],
                        "volume_range": [0.8, 1.0],
                        "description": "温暖型 - 语速适中，音调温暖",
                        "usage_scenario": "情感分享、生活感悟、温馨内容"
                    },
                    "Excited": {
                        "rate_range": [1.0, 1.3],
                        "pitch_range": [1.0, 1.2],
                        "volume_range": [0.9, 1.1],
                        "description": "兴奋型 - 语速较快，音调较高",
                        "usage_scenario": "新品发布、活动宣传、激动内容"
                    },
                    "Professional": {
                        "rate_range": [0.8, 1.0],
                        "pitch_range": [0.9, 1.0],
                        "volume_range": [0.8, 1.0],
                        "description": "专业型 - 语速稳定，音调专业",
                        "usage_scenario": "产品介绍、技术讲解、商务内容"
                    }
                }
            },
            "voice_settings": {
                "file_voice_mapping": {
                    "全产品_合并版_3200_v9.xlsx": "en-US-JennyNeural",
                    "全产品_合并版_3200_v5.xlsx": "en-US-AvaNeural",
                    "全产品_合并版_3200_v4.xlsx": "en-US-NancyNeural",
                    "全产品_合并版_3200_v8.xlsx": "en-US-AriaNeural",
                    "全产品_合并版_3200_v3.xlsx": "en-US-KaiNeural",
                    "全产品_合并版_3200_v2.xlsx": "en-US-SerenaNeural",
                    "全产品_合并版_3200.xlsx": "en-US-EmmaNeural",
                    "全产品_合并版_3200_v7.xlsx": "en-US-MichelleNeural",
                    "全产品_合并版_3200_v6.xlsx": "en-US-BrandonNeural"
                }
            }
        }
    
    def python_to_edge_tts_rate(self, python_rate: float) -> str:
        """Python语速值转换为EdgeTTS格式"""
        edge_tts_rate = int((python_rate - 1) * 100)
        return f"{edge_tts_rate:+d}%"
    
    def python_to_edge_tts_pitch(self, python_pitch: float) -> str:
        """Python音调值转换为EdgeTTS格式"""
        edge_tts_pitch = int((python_pitch - 1) * 50)
        return f"{edge_tts_pitch:+d}Hz"
    
    def python_to_edge_tts_volume(self, python_volume: float) -> str:
        """Python音量值转换为EdgeTTS格式"""
        edge_tts_volume = int((python_volume - 1) * 50)
        return f"{edge_tts_volume:+d}%"
    
    def generate_emotion_parameters(self, emotion: str) -> Dict[str, float]:
        """根据情绪类型生成参数"""
        if emotion not in self.emotion_params:
            logger.warning(f"未知情绪类型: {emotion}，使用默认参数")
            emotion = "Professional"
        
        params = self.emotion_params[emotion]
        
        # 生成随机参数
        rate = random.uniform(params['rate_range'][0], params['rate_range'][1])
        pitch = random.uniform(params['pitch_range'][0], params['pitch_range'][1])
        volume = random.uniform(params['volume_range'][0], params['volume_range'][1])
        
        return {
            'rate': rate,
            'pitch': pitch,
            'volume': volume,
            'emotion': emotion,
            'description': params['description']
        }
    
    def build_ssml(self, text: str, voice: str, emotion_params: Dict[str, float]) -> str:
        """构建SSML格式"""
        # 转换为EdgeTTS格式
        edge_tts_rate = self.python_to_edge_tts_rate(emotion_params['rate'])
        edge_tts_pitch = self.python_to_edge_tts_pitch(emotion_params['pitch'])
        edge_tts_volume = self.python_to_edge_tts_volume(emotion_params['volume'])
        
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="{voice}">
        <prosody rate="{edge_tts_rate}" pitch="{edge_tts_pitch}" volume="{edge_tts_volume}">
            {text}
        </prosody>
    </voice>
</speak>"""
        
        return ssml
    
    async def generate_audio(self, text: str, voice: str, emotion: str, output_file: str) -> bool:
        """生成音频文件"""
        try:
            # 生成情绪参数
            emotion_params = self.generate_emotion_parameters(emotion)
            logger.info(f"🎭 使用情绪: {emotion} - {emotion_params['description']}")
            logger.info(f"📊 参数: rate={emotion_params['rate']:.2f}, pitch={emotion_params['pitch']:.2f}, volume={emotion_params['volume']:.2f}")
            
            # 构建SSML
            ssml = self.build_ssml(text, voice, emotion_params)
            
            # 调用EdgeTTS
            communicate = edge_tts.Communicate(ssml, voice)
            await communicate.save(output_file)
            
            logger.info(f"✅ 音频生成成功: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 音频生成失败: {e}")
            return False

class VoiceLibraryManager:
    """语音库管理器"""
    
    def __init__(self):
        """初始化语音库管理器"""
        self.voice_library = self._init_voice_library()
    
    def _init_voice_library(self) -> Dict:
        """初始化语音库"""
        return {
            "base_voices": {
                "en-US-JennyNeural": {"gender": "female", "age": "young", "style": "sweet", "quality": 9.0},
                "en-US-AvaNeural": {"gender": "female", "age": "mature", "style": "warm", "quality": 9.2},
                "en-US-NancyNeural": {"gender": "female", "age": "professional", "style": "professional", "quality": 8.8},
                "en-US-AriaNeural": {"gender": "female", "age": "young", "style": "dynamic", "quality": 8.5},
                "en-US-KaiNeural": {"gender": "male", "age": "young", "style": "energetic", "quality": 8.8},
                "en-US-SerenaNeural": {"gender": "female", "age": "elegant", "style": "elegant", "quality": 8.7},
                "en-US-EmmaNeural": {"gender": "female", "age": "friendly", "style": "friendly", "quality": 8.6},
                "en-US-MichelleNeural": {"gender": "female", "age": "confident", "style": "confident", "quality": 8.4},
                "en-US-BrandonNeural": {"gender": "male", "age": "mature", "style": "professional", "quality": 9.1}
            },
            "content_mapping": {
                "product_intro": ["en-US-JennyNeural", "en-US-AvaNeural", "en-US-NancyNeural"],
                "promotion": ["en-US-AriaNeural", "en-US-KaiNeural", "en-US-MichelleNeural"],
                "education": ["en-US-NancyNeural", "en-US-BrandonNeural", "en-US-AndrewNeural"],
                "entertainment": ["en-US-AriaNeural", "en-US-EmmaNeural", "en-US-GuyNeural"],
                "emotional": ["en-US-AvaNeural", "en-US-LunaNeural", "en-US-ChristopherNeural"]
            }
        }
    
    def select_voice(self, content_type: str, gender_preference: Optional[str] = None) -> str:
        """根据内容类型选择语音"""
        available_voices = self.voice_library["content_mapping"].get(content_type, ["en-US-JennyNeural"])
        
        if gender_preference:
            filtered_voices = [
                v for v in available_voices 
                if self.voice_library["base_voices"].get(v, {}).get("gender") == gender_preference
            ]
            if filtered_voices:
                return random.choice(filtered_voices)
        
        return random.choice(available_voices)
    
    def get_voice_info(self, voice: str) -> Dict:
        """获取语音信息"""
        return self.voice_library["base_voices"].get(voice, {})

class EdgeTTSAudioGenerator:
    """EdgeTTS音频生成器"""
    
    def __init__(self, config_file: str = "tts_config.json"):
        """初始化音频生成器"""
        self.mapper = EdgeTTSParameterMapper(config_file)
        self.voice_manager = VoiceLibraryManager()
    
    async def generate_emotion_audio(self, text: str, emotion: str, content_type: str = "product_intro", 
                                  gender_preference: Optional[str] = None, output_file: Optional[str] = None) -> str:
        """生成情绪化音频"""
        # 选择语音
        voice = self.voice_manager.select_voice(content_type, gender_preference)
        voice_info = self.voice_manager.get_voice_info(voice)
        
        logger.info(f"🎤 选择语音: {voice} ({voice_info.get('style', 'unknown')})")
        
        # 生成输出文件名
        if not output_file:
            timestamp = int(asyncio.get_event_loop().time())
            output_file = f"audio_{emotion}_{voice}_{timestamp}.m4a"
        
        # 生成音频
        success = await self.mapper.generate_audio(text, voice, emotion, output_file)
        
        if success:
            return output_file
        else:
            raise Exception("音频生成失败")
    
    async def generate_batch_audio(self, texts: List[str], emotions: List[str], 
                                 content_types: List[str], output_dir: str = "output") -> List[str]:
        """批量生成音频"""
        output_files = []
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for i, (text, emotion, content_type) in enumerate(zip(texts, emotions, content_types)):
            try:
                output_file = output_path / f"batch_{i+1:03d}_{emotion}.m4a"
                result_file = await self.generate_emotion_audio(text, emotion, content_type, 
                                                              output_file=str(output_file))
                output_files.append(result_file)
                logger.info(f"📁 批量处理进度: {i+1}/{len(texts)}")
                
                # 添加延迟避免API限制
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ 批量处理失败 {i+1}: {e}")
        
        return output_files

async def main():
    """主函数 - 演示EdgeTTS参数集成系统"""
    logger.info("🚀 EdgeTTS参数集成系统启动")
    
    # 创建音频生成器
    generator = EdgeTTSAudioGenerator()
    
    # 测试文本
    test_texts = [
        "Hello, this is urgent content! Limited time offer available now!",
        "This is calm and soothing content. Take a deep breath and relax.",
        "Welcome to our warm and friendly community. We're here to help you.",
        "Exciting news! Our new product is launching today! Don't miss out!",
        "This is professional content. Let me explain the technical details."
    ]
    
    emotions = ["Urgent", "Calm", "Warm", "Excited", "Professional"]
    content_types = ["promotion", "emotional", "emotional", "promotion", "education"]
    
    # 生成单个音频
    logger.info("🎵 生成单个情绪音频...")
    try:
        output_file = await generator.generate_emotion_audio(
            text=test_texts[0],
            emotion=emotions[0],
            content_type=content_types[0],
            gender_preference="female"
        )
        logger.info(f"✅ 单个音频生成成功: {output_file}")
    except Exception as e:
        logger.error(f"❌ 单个音频生成失败: {e}")
    
    # 批量生成音频
    logger.info("📦 批量生成情绪音频...")
    try:
        batch_files = await generator.generate_batch_audio(
            texts=test_texts,
            emotions=emotions,
            content_types=content_types,
            output_dir="emotion_audio_output"
        )
        logger.info(f"✅ 批量音频生成成功: {len(batch_files)} 个文件")
        for file in batch_files:
            logger.info(f"   📄 {file}")
    except Exception as e:
        logger.error(f"❌ 批量音频生成失败: {e}")
    
    logger.info("🎉 EdgeTTS参数集成系统演示完成")

if __name__ == "__main__":
    asyncio.run(main())
