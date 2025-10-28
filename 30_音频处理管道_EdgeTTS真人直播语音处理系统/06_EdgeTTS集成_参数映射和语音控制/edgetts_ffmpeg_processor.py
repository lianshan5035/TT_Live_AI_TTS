#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS到FFmpeg处理执行器
实现EdgeTTS生成音频后使用FFmpeg进行真人直播语音处理的完整流程
"""

import json
import random
import asyncio
import subprocess
import edge_tts
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import os
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EdgeTTSFFmpegProcessor:
    """EdgeTTS到FFmpeg处理执行器"""
    
    def __init__(self, config_file: str = "edgetts_ffmpeg_config.json"):
        """初始化处理器"""
        self.config_file = config_file
        self.config = self._load_config()
        self.emotion_strategies = self.config.get('emotion_strategies', {})
        self.background_sounds = self.config.get('background_sounds', {})
        self.event_sounds = self.config.get('event_sounds', {})
        
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
            "emotion_strategies": {
                "Urgent": {
                    "rate_range": [0.95, 1.2],
                    "pitch_range": [0.95, 1.1],
                    "volume_range": [0.95, 1.0],
                    "ffmpeg_processing": {
                        "tempo_adjustment": {"base_range": [1.02, 1.08], "method": "rubberband"},
                        "pitch_adjustment": {"base_range": [1.02, 1.05], "method": "rubberband"},
                        "background_sounds": {"probability": 0.85, "volume_range": [0.08, 0.15]},
                        "event_sounds": {"probability": 0.4, "max_events": 2}
                    }
                },
                "Calm": {
                    "rate_range": [0.95, 1.0],
                    "pitch_range": [0.95, 1.0],
                    "volume_range": [0.95, 1.0],
                    "ffmpeg_processing": {
                        "tempo_adjustment": {"base_range": [0.98, 1.02], "method": "rubberband"},
                        "pitch_adjustment": {"base_range": [0.98, 1.02], "method": "rubberband"},
                        "background_sounds": {"probability": 0.7, "volume_range": [0.05, 0.12]},
                        "event_sounds": {"probability": 0.2, "max_events": 1}
                    }
                },
                "Warm": {
                    "rate_range": [0.8, 1.0],
                    "pitch_range": [0.9, 1.1],
                    "volume_range": [0.8, 1.0],
                    "ffmpeg_processing": {
                        "tempo_adjustment": {"base_range": [0.95, 1.05], "method": "rubberband"},
                        "pitch_adjustment": {"base_range": [1.02, 1.08], "method": "rubberband"},
                        "background_sounds": {"probability": 0.8, "volume_range": [0.08, 0.15]},
                        "event_sounds": {"probability": 0.3, "max_events": 2}
                    }
                },
                "Excited": {
                    "rate_range": [1.0, 1.3],
                    "pitch_range": [1.0, 1.2],
                    "volume_range": [0.9, 1.1],
                    "ffmpeg_processing": {
                        "tempo_adjustment": {"base_range": [1.05, 1.15], "method": "rubberband"},
                        "pitch_adjustment": {"base_range": [1.05, 1.12], "method": "rubberband"},
                        "background_sounds": {"probability": 0.9, "volume_range": [0.12, 0.18]},
                        "event_sounds": {"probability": 0.5, "max_events": 3}
                    }
                },
                "Professional": {
                    "rate_range": [0.8, 1.0],
                    "pitch_range": [0.9, 1.0],
                    "volume_range": [0.8, 1.0],
                    "ffmpeg_processing": {
                        "tempo_adjustment": {"base_range": [0.95, 1.05], "method": "rubberband"},
                        "pitch_adjustment": {"base_range": [0.98, 1.02], "method": "rubberband"},
                        "background_sounds": {"probability": 0.5, "volume_range": [0.06, 0.12]},
                        "event_sounds": {"probability": 0.15, "max_events": 1}
                    }
                }
            },
            "background_sounds": {
                "environments": {
                    "cafe": {"file": "cafe_ambient.wav", "volume_range": [0.15, 0.25]},
                    "office": {"file": "office_ambient.wav", "volume_range": [0.12, 0.22]},
                    "living_room": {"file": "living_room.wav", "volume_range": [0.1, 0.2]},
                    "outdoor": {"file": "outdoor_ambient.wav", "volume_range": [0.18, 0.3]},
                    "room_tone": {"file": "room_tone.wav", "volume_range": [0.08, 0.15]}
                }
            },
            "event_sounds": {
                "events": {
                    "keyboard": {"file": "keyboard_typing.wav", "volume_range": [0.15, 0.25]},
                    "water_pour": {"file": "water_pour.wav", "volume_range": [0.12, 0.2]},
                    "footsteps": {"file": "footsteps.wav", "volume_range": [0.1, 0.18]},
                    "chair_creak": {"file": "chair_creak.wav", "volume_range": [0.08, 0.15]},
                    "paper_rustle": {"file": "paper_rustle.wav", "volume_range": [0.06, 0.12]}
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
    
    def generate_emotion_parameters(self, emotion: str) -> Dict:
        """根据情绪类型生成参数"""
        if emotion not in self.emotion_strategies:
            logger.warning(f"未知情绪类型: {emotion}，使用默认参数")
            emotion = "Professional"
        
        strategy = self.emotion_strategies[emotion]
        
        # 生成EdgeTTS参数
        rate = random.uniform(strategy['rate_range'][0], strategy['rate_range'][1])
        pitch = random.uniform(strategy['pitch_range'][0], strategy['pitch_range'][1])
        volume = random.uniform(strategy['volume_range'][0], strategy['volume_range'][1])
        
        # 生成FFmpeg参数
        ffmpeg_params = strategy['ffmpeg_processing']
        tempo = random.uniform(ffmpeg_params['tempo_adjustment']['base_range'][0], 
                              ffmpeg_params['tempo_adjustment']['base_range'][1])
        pitch_adj = random.uniform(ffmpeg_params['pitch_adjustment']['base_range'][0], 
                                 ffmpeg_params['pitch_adjustment']['base_range'][1])
        
        return {
            'emotion': emotion,
            'edge_tts': {
                'rate': rate,
                'pitch': pitch,
                'volume': volume,
                'rate_str': self.python_to_edge_tts_rate(rate),
                'pitch_str': self.python_to_edge_tts_pitch(pitch),
                'volume_str': self.python_to_edge_tts_volume(volume)
            },
            'ffmpeg': {
                'tempo': tempo,
                'pitch': pitch_adj,
                'background_probability': ffmpeg_params['background_sounds']['probability'],
                'background_volume_range': ffmpeg_params['background_sounds']['volume_range'],
                'event_probability': ffmpeg_params['event_sounds']['probability'],
                'max_events': ffmpeg_params['event_sounds']['max_events']
            }
        }
    
    async def generate_edge_tts_audio(self, text: str, voice: str, emotion_params: Dict, 
                                    output_file: str) -> bool:
        """生成EdgeTTS音频"""
        try:
            edge_tts_params = emotion_params['edge_tts']
            
            # 构建SSML
            ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="{voice}">
        <prosody rate="{edge_tts_params['rate_str']}" pitch="{edge_tts_params['pitch_str']}" volume="{edge_tts_params['volume_str']}">
            {text}
        </prosody>
    </voice>
</speak>"""
            
            logger.info(f"🎤 生成EdgeTTS音频: {voice}")
            logger.info(f"📊 EdgeTTS参数: rate={edge_tts_params['rate_str']}, pitch={edge_tts_params['pitch_str']}, volume={edge_tts_params['volume_str']}")
            
            # 调用EdgeTTS
            communicate = edge_tts.Communicate(ssml, voice)
            await communicate.save(output_file)
            
            logger.info(f"✅ EdgeTTS音频生成成功: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ EdgeTTS音频生成失败: {e}")
            return False
    
    def select_background_sound(self, emotion: str) -> Optional[Dict]:
        """选择背景音效"""
        ffmpeg_params = self.emotion_strategies[emotion]['ffmpeg_processing']
        
        if random.random() > ffmpeg_params['background_sounds']['probability']:
            return None
        
        # 根据情绪选择环境
        environment_mapping = {
            "Urgent": ["office", "cafe"],
            "Calm": ["living_room", "room_tone"],
            "Warm": ["cafe", "living_room"],
            "Excited": ["cafe", "outdoor"],
            "Professional": ["office", "room_tone"]
        }
        
        available_envs = environment_mapping.get(emotion, ["room_tone"])
        selected_env = random.choice(available_envs)
        
        if selected_env in self.background_sounds['environments']:
            env_config = self.background_sounds['environments'][selected_env]
            volume = random.uniform(ffmpeg_params['background_sounds']['volume_range'][0],
                                 ffmpeg_params['background_sounds']['volume_range'][1])
            
            return {
                'file': env_config['file'],
                'volume': volume,
                'environment': selected_env
            }
        
        return None
    
    def select_event_sounds(self, emotion: str) -> List[Dict]:
        """选择事件音效"""
        ffmpeg_params = self.emotion_strategies[emotion]['ffmpeg_processing']
        
        if random.random() > ffmpeg_params['event_sounds']['probability']:
            return []
        
        # 根据情绪选择事件
        event_mapping = {
            "Urgent": ["keyboard", "footsteps"],
            "Calm": ["paper_rustle", "chair_creak"],
            "Warm": ["water_pour", "paper_rustle"],
            "Excited": ["keyboard", "footsteps", "water_pour"],
            "Professional": ["keyboard", "paper_rustle"]
        }
        
        available_events = event_mapping.get(emotion, ["keyboard"])
        max_events = ffmpeg_params['event_sounds']['max_events']
        num_events = random.randint(1, max_events)
        
        selected_events = random.sample(available_events, min(num_events, len(available_events)))
        
        event_sounds = []
        for event in selected_events:
            if event in self.event_sounds['events']:
                event_config = self.event_sounds['events'][event]
                volume = random.uniform(event_config['volume_range'][0], event_config['volume_range'][1])
                delay = random.uniform(0.5, 3.0)  # 随机延迟
                
                event_sounds.append({
                    'file': event_config['file'],
                    'volume': volume,
                    'delay': delay,
                    'event': event
                })
        
        return event_sounds
    
    def build_ffmpeg_command(self, input_file: str, emotion_params: Dict, 
                           background_sound: Optional[Dict], event_sounds: List[Dict], 
                           output_file: str) -> List[str]:
        """构建FFmpeg处理命令"""
        ffmpeg_params = emotion_params['ffmpeg']
        
        cmd = ['ffmpeg', '-y']  # -y 覆盖输出文件
        
        # 输入文件
        cmd.extend(['-i', input_file])
        
        # 背景音效输入
        if background_sound:
            cmd.extend(['-i', background_sound['file']])
        
        # 事件音效输入
        for event in event_sounds:
            cmd.extend(['-i', event['file']])
        
        # 构建滤镜链
        filter_parts = []
        
        # 1. 语音处理 (tempo + pitch)
        voice_filters = []
        voice_filters.append(f"rubberband=tempo={ffmpeg_params['tempo']:.3f}:pitch={ffmpeg_params['pitch']:.3f}:formant=preserve")
        voice_filters.append("aresample=resampler=soxr")
        
        filter_parts.append(f"[0]{':'.join(voice_filters)}[voice]")
        
        # 2. 背景音效处理
        if background_sound:
            bg_filters = []
            bg_filters.append(f"volume={background_sound['volume']:.3f}")
            bg_filters.append("aloop=loop=-1:size=2e+09")
            bg_filters.append("afade=t=in:ss=0:d=2")
            bg_filters.append("afade=t=out:st=-2:d=2")
            
            filter_parts.append(f"[1]{':'.join(bg_filters)}[bg]")
        
        # 3. 事件音效处理
        event_inputs = []
        for i, event in enumerate(event_sounds):
            event_idx = 2 + i  # 背景音效后的事件音效索引
            event_filters = []
            event_filters.append(f"volume={event['volume']:.3f}")
            event_filters.append(f"adelay={int(event['delay']*1000)}|{int(event['delay']*1000)}")
            event_filters.append("afade=t=in:ss=0:d=0.5")
            event_filters.append("afade=t=out:st=-0.5:d=0.5")
            
            filter_parts.append(f"[{event_idx}]{':'.join(event_filters)}[event{i}]")
            event_inputs.append(f"[event{i}]")
        
        # 4. 混合所有音效
        mix_inputs = ["[voice]"]
        mix_weights = ["1"]
        
        if background_sound:
            mix_inputs.append("[bg]")
            mix_weights.append(f"{background_sound['volume']:.3f}")
        
        for i in range(len(event_sounds)):
            mix_inputs.append(f"[event{i}]")
            mix_weights.append(f"{event_sounds[i]['volume']:.3f}")
        
        mix_filter = f"{':'.join(mix_inputs)}amix=inputs={len(mix_inputs)}:weights={' '.join(mix_weights)}:dropout_transition=2[mixed]"
        filter_parts.append(mix_filter)
        
        # 5. 音频增强
        enhancement_filters = []
        enhancement_filters.append("acompressor=threshold=-18:ratio=3:attack=15:release=180:makeup=3")
        enhancement_filters.append("equalizer=f=250:width=120:g=2.0")
        enhancement_filters.append("equalizer=f=3500:width=800:g=2.5")
        enhancement_filters.append("highpass=f=80")
        enhancement_filters.append("loudnorm=I=-19:TP=-2:LRA=9")
        
        filter_parts.append(f"[mixed]{':'.join(enhancement_filters)}[output]")
        
        # 添加滤镜链
        cmd.extend(['-filter_complex', ';'.join(filter_parts)])
        
        # 输出设置
        cmd.extend(['-map', '[output]'])
        cmd.extend(['-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2'])
        cmd.append(output_file)
        
        return cmd
    
    def run_ffmpeg_command(self, cmd: List[str]) -> bool:
        """运行FFmpeg命令"""
        try:
            logger.info(f"🔧 运行FFmpeg命令: {' '.join(cmd[:10])}...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ FFmpeg处理成功")
                return True
            else:
                logger.error(f"❌ FFmpeg处理失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ FFmpeg处理超时")
            return False
        except Exception as e:
            logger.error(f"❌ FFmpeg处理异常: {e}")
            return False
    
    async def process_audio(self, text: str, voice: str, emotion: str, 
                          output_file: str) -> bool:
        """完整的音频处理流程"""
        try:
            logger.info(f"🎯 开始处理音频: {emotion} 情绪")
            
            # 1. 生成情绪参数
            emotion_params = self.generate_emotion_parameters(emotion)
            logger.info(f"📊 生成参数: {emotion_params['emotion']}")
            
            # 2. 生成EdgeTTS音频
            temp_edge_tts_file = f"temp_edge_tts_{int(time.time())}.wav"
            edge_tts_success = await self.generate_edge_tts_audio(text, voice, emotion_params, temp_edge_tts_file)
            
            if not edge_tts_success:
                return False
            
            # 3. 选择背景音效
            background_sound = self.select_background_sound(emotion)
            if background_sound:
                logger.info(f"🎵 选择背景音效: {background_sound['environment']} (音量: {background_sound['volume']:.3f})")
            
            # 4. 选择事件音效
            event_sounds = self.select_event_sounds(emotion)
            if event_sounds:
                logger.info(f"🔊 选择事件音效: {len(event_sounds)} 个")
                for event in event_sounds:
                    logger.info(f"   - {event['event']}: 音量 {event['volume']:.3f}, 延迟 {event['delay']:.1f}s")
            
            # 5. 构建FFmpeg命令
            ffmpeg_cmd = self.build_ffmpeg_command(temp_edge_tts_file, emotion_params, 
                                                 background_sound, event_sounds, output_file)
            
            # 6. 运行FFmpeg处理
            ffmpeg_success = self.run_ffmpeg_command(ffmpeg_cmd)
            
            # 7. 清理临时文件
            if os.path.exists(temp_edge_tts_file):
                os.remove(temp_edge_tts_file)
            
            if ffmpeg_success:
                logger.info(f"🎉 音频处理完成: {output_file}")
                return True
            else:
                logger.error("❌ FFmpeg处理失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 音频处理异常: {e}")
            return False
    
    async def batch_process(self, texts: List[str], voices: List[str], emotions: List[str], 
                          output_dir: str = "processed_audio") -> List[str]:
        """批量处理音频"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        successful_files = []
        
        for i, (text, voice, emotion) in enumerate(zip(texts, voices, emotions)):
            try:
                timestamp = int(time.time())
                output_file = output_path / f"batch_{i+1:03d}_{emotion}_{timestamp}.m4a"
                
                success = await self.process_audio(text, voice, emotion, str(output_file))
                
                if success:
                    successful_files.append(str(output_file))
                    logger.info(f"📁 批量处理进度: {i+1}/{len(texts)} ✅")
                else:
                    logger.error(f"📁 批量处理进度: {i+1}/{len(texts)} ❌")
                
                # 添加延迟避免API限制
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ 批量处理失败 {i+1}: {e}")
        
        logger.info(f"🎉 批量处理完成: {len(successful_files)}/{len(texts)} 成功")
        return successful_files

async def main():
    """主函数 - 演示EdgeTTS到FFmpeg处理流程"""
    logger.info("🚀 EdgeTTS到FFmpeg处理执行器启动")
    
    # 创建处理器
    processor = EdgeTTSFFmpegProcessor()
    
    # 测试数据
    test_data = [
        {
            "text": "Hello, this is urgent content! Limited time offer available now!",
            "voice": "en-US-JennyNeural",
            "emotion": "Urgent"
        },
        {
            "text": "This is calm and soothing content. Take a deep breath and relax.",
            "voice": "en-US-AvaNeural",
            "emotion": "Calm"
        },
        {
            "text": "Welcome to our warm and friendly community. We're here to help you.",
            "voice": "en-US-NancyNeural",
            "emotion": "Warm"
        },
        {
            "text": "Exciting news! Our new product is launching today! Don't miss out!",
            "voice": "en-US-AriaNeural",
            "emotion": "Excited"
        },
        {
            "text": "This is professional content. Let me explain the technical details.",
            "voice": "en-US-BrandonNeural",
            "emotion": "Professional"
        }
    ]
    
    # 单个处理测试
    logger.info("🎵 单个音频处理测试...")
    test_item = test_data[0]
    try:
        success = await processor.process_audio(
            text=test_item["text"],
            voice=test_item["voice"],
            emotion=test_item["emotion"],
            output_file=f"single_test_{test_item['emotion']}.m4a"
        )
        if success:
            logger.info("✅ 单个音频处理测试成功")
        else:
            logger.error("❌ 单个音频处理测试失败")
    except Exception as e:
        logger.error(f"❌ 单个音频处理测试异常: {e}")
    
    # 批量处理测试
    logger.info("📦 批量音频处理测试...")
    try:
        texts = [item["text"] for item in test_data]
        voices = [item["voice"] for item in test_data]
        emotions = [item["emotion"] for item in test_data]
        
        batch_files = await processor.batch_process(texts, voices, emotions, "batch_test_output")
        
        logger.info(f"✅ 批量处理完成: {len(batch_files)} 个文件")
        for file in batch_files:
            logger.info(f"   📄 {file}")
            
    except Exception as e:
        logger.error(f"❌ 批量处理测试异常: {e}")
    
    logger.info("🎉 EdgeTTS到FFmpeg处理执行器演示完成")

if __name__ == "__main__":
    asyncio.run(main())
