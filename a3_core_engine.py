#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI A3标准核心引擎
完全符合GPTs-A3文档规范的智能口播生成系统
"""

import asyncio
import edge_tts
import json
import os
import hashlib
import random
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A3CoreEngine:
    """A3标准核心引擎 - 完全符合GPTs-A3文档规范"""
    
    def __init__(self):
        self.emotion_config = self._load_emotion_config()
        self.voice_library = self._load_voice_library()
        self.rhetoric_library = self._load_rhetoric_library()
        self.opening_library = self._load_opening_library()
        self.filler_library = self._load_filler_library()
        self.hook_library = self._load_hook_library()
        self.compliance_rules = self._load_compliance_rules()
        
    def _load_emotion_config(self) -> Dict:
        """加载A3标准12种情绪参数配置"""
        return {
            "Excited": {"rate": +15, "pitch": +12, "volume": +15, "style": "cheerful", "products": "新品/促销"},
            "Confident": {"rate": +8, "pitch": +5, "volume": +8, "style": "assertive", "products": "高端/科技"},
            "Empathetic": {"rate": -12, "pitch": -8, "volume": -10, "style": "friendly", "products": "护肤/健康"},
            "Calm": {"rate": -10, "pitch": -3, "volume": 0, "style": "soothing", "products": "家居/教育"},
            "Playful": {"rate": +18, "pitch": +15, "volume": +5, "style": "friendly", "products": "美妆/时尚"},
            "Urgent": {"rate": +22, "pitch": +8, "volume": +18, "style": "serious", "products": "限时/秒杀"},
            "Authoritative": {"rate": +5, "pitch": +3, "volume": +10, "style": "serious", "products": "投资/专业"},
            "Friendly": {"rate": +12, "pitch": +8, "volume": +5, "style": "friendly", "products": "日用/社群"},
            "Inspirational": {"rate": +10, "pitch": +10, "volume": +12, "style": "cheerful", "products": "自提升/健身"},
            "Serious": {"rate": 0, "pitch": 0, "volume": +5, "style": "serious", "products": "金融/公告"},
            "Mysterious": {"rate": -8, "pitch": +5, "volume": -5, "style": "serious", "products": "预告/悬念"},
            "Grateful": {"rate": +5, "pitch": +8, "volume": +8, "style": "friendly", "products": "感谢/复购"}
        }
    
    def _load_voice_library(self) -> Dict:
        """加载en-US声音库"""
        return {
            "Female": [
                "en-US-JennyNeural", "en-US-AriaNeural", "en-US-EmmaNeural",
                "en-US-MichelleNeural", "en-US-SaraNeural", "en-US-NancyNeural"
            ],
            "Male": [
                "en-US-GuyNeural", "en-US-DavisNeural", "en-US-BrandonNeural",
                "en-US-ChristopherNeural", "en-US-EricNeural", "en-US-JacobNeural"
            ]
        }
    
    def _load_rhetoric_library(self) -> Dict:
        """加载修辞增强库"""
        return {
            "Metaphor": ["Like morning dew gently kissing rose petals", "Smooth as silk gliding over polished marble"],
            "Parallelism": ["Cleanse, pat dry, pea-size, done", "Smoother look, softer feel, easier outfits"],
            "Contrast": ["Old routine: overthink. New routine: tiny dot, repeat", "Less cover-up, more show-up"],
            "RQ": ["You ever avoid sleeveless 'just in case'?", "Tell me I'm not the only one who needed this"],
            "Pathos": ["I get it—confidence takes practice", "It's not perfection—it's comfort"],
            "SocialProof": ["My DMs were full after I shared this", "Friends keep asking what changed"],
            "FuturePacing": ["Imagine picking the tank without thinking twice", "Next month, more 'I can wear this' moments"],
            "Sensory": ["Cloud-soft texture; sinks in fast", "Lightweight glide—zero cling"],
            "Humor": ["My bathroom looks like a lab—this one made the cut", "Not me gatekeeping a body cream"],
            "TikTokNative": ["low-key obsessed", "it's giving ___", "no cap", "say less"]
        }
    
    def _load_opening_library(self) -> Dict:
        """加载开场句式库"""
        return {
            "Role Intro": ["As your bestie, lemme tell you this—", "I'm your skincare buddy, okay?"],
            "Question Hook": ["You ever notice how…", "Tell me I'm not the only one who…"],
            "Pain Resonance": ["Ever felt too shy to wear sleeveless?", "You know that shadow thing under your arm?"],
            "Personal Story": ["I used to hide my arms every summer—no more"],
            "Contrast Hook": ["This makes every other cream look basic"],
            "Shock Surprise": ["Girl, this blew my mind—", "Wait, nobody told me this trick existed!"],
            "Trend Viral": ["TikTok made me buy this—worth it"],
            "Direct CTA": ["Hit the cart now—deal's live!"],
            "Soft Value": ["Because self-care shouldn't be complicated"],
            "Social Proof": ["My FYP wouldn't stop showing this—so I tried it"]
        }
    
    def _load_filler_library(self) -> List[str]:
        """加载呼吸填充词库"""
        return [
            "uh", "um", "well", "so", "actually", "basically", "honestly", "you know",
            "right", "okay", "alright", "I mean", "I guess", "trust me", "for real",
            "no joke", "listen up", "hear me out", "mark my words", "take it from me"
        ]
    
    def _load_hook_library(self) -> Dict:
        """加载钩子引用方法库"""
        return {
            "Life Scenes": [
                "Sunday morning pancake vibes", "Your 5 PM work-from-home escape",
                "Netflix and chill perfected", "Saturday garage sale energy"
            ],
            "Work Scenes": [
                "CEO morning routine energy", "Power meeting prep",
                "Remote work upgrade", "Career glow-up moment"
            ],
            "Action Triggers": [
                "Your future self is already thanking you", "This is that 'I'm glad I bought it' feeling",
                "Stop dreaming about better - start living it", "Your 'add to cart' finger is smarter"
            ],
            "Cultural References": [
                "Main character energy", "That 'I woke up like this' feeling",
                "Plot twist your routine", "Season finale level cliffhanger"
            ]
        }
    
    def _load_compliance_rules(self) -> Dict:
        """加载合规规则库"""
        return {
            "forbidden_words": ["miracle", "guaranteed", "cure", "permanent", "overnight results", "medically proven"],
            "replacement_words": {
                "miracle": "amazing transformation",
                "guaranteed": "many users experience",
                "cure": "help improve",
                "permanent": "long-lasting",
                "overnight": "noticeable improvement"
            },
            "required_disclaimers": ["Results may vary", "Individual experience differs"],
            "safe_ranges": {
                "rate": (-25, 35),
                "pitch": (-15, 20),
                "volume": (-50, 50)
            }
        }

class A3DynamicParameterGenerator:
    """A3标准动态参数生成器"""
    
    def __init__(self, product_name: str, script_id: int):
        self.product_name = product_name
        self.script_id = script_id
        self.product_hash = self._generate_product_hash(product_name)
        self.seed = self._generate_seed()
    
    def _generate_product_hash(self, product_name: str) -> int:
        """生成产品哈希值"""
        return int(hashlib.md5(product_name.encode()).hexdigest()[:8], 16) % 10000
    
    def _generate_seed(self) -> int:
        """生成种子值"""
        return (self.product_hash + self.script_id * 137) % 1000000
    
    def dynamic_rate(self, base_rate: float, emotion_type: str) -> float:
        """动态语速调整公式"""
        np.random.seed(self.seed)
        
        emotion_ranges = {
            'Excited': (0.08, 0.15),
            'Calm': (0.03, 0.08),
            'Urgent': (0.10, 0.18),
            'Empathetic': (0.05, 0.10),
            'Playful': (0.12, 0.20),
            'Confident': (0.05, 0.12)
        }
        
        min_range, max_range = emotion_ranges.get(emotion_type, (0.05, 0.12))
        sine_wave = np.sin(self.script_id * 0.1) * 0.05
        random_noise = np.random.uniform(-min_range, max_range)
        
        dynamic_adjustment = base_rate + sine_wave + random_noise
        return np.clip(dynamic_adjustment, -0.20, 0.30)
    
    def dynamic_pitch(self, base_pitch: float, emotion_type: str) -> float:
        """动态音调调整公式"""
        np.random.seed(self.seed + 1000)
        
        fib_sequence = [0, 1, 1, 2, 3, 5, 8, 13]
        fib_factor = fib_sequence[self.script_id % 8] / 13.0 * 0.1
        log_perturb = np.log1p(self.script_id % 100) * 0.02
        
        dynamic_pitch = base_pitch + fib_factor + log_perturb
        return np.clip(dynamic_pitch, -0.12, 0.18)
    
    def dynamic_volume(self, base_volume: float, emotion_type: str) -> float:
        """动态音量调整公式"""
        np.random.seed(self.seed + 2000)
        
        prime_sequence = [2, 3, 5, 7, 11, 13, 17, 19]
        prime_factor = prime_sequence[self.script_id % 8] / 19.0 * 0.15
        cosine_wave = np.cos(self.script_id * 0.15) * 0.08
        
        dynamic_volume = base_volume + prime_factor + cosine_wave
        return np.clip(dynamic_volume, -0.10, 0.20)

class A3ScriptGenerator:
    """A3标准脚本生成器"""
    
    def __init__(self, core_engine: A3CoreEngine):
        self.core_engine = core_engine
        self.param_generator = None
    
    def generate_script(self, product_name: str, script_id: int, emotion: str, 
                       voice: str, product_type: str = "美妆个护") -> Dict:
        """生成单个A3标准脚本"""
        
        # 初始化动态参数生成器
        self.param_generator = A3DynamicParameterGenerator(product_name, script_id)
        
        # 生成脚本结构
        opening = self._generate_opening(emotion, script_id)
        pain_point = self._generate_pain_point(product_type)
        solution = self._generate_solution(product_name)
        hook = self._generate_hook(script_id)
        cta = self._generate_cta()
        
        # 组合完整脚本
        english_script = f"{opening} {pain_point} {solution} {hook} {cta}"
        
        # 生成中文翻译
        chinese_translation = self._translate_to_chinese(english_script)
        
        # 生成A3动态参数
        a3_params = self._generate_a3_params(emotion)
        
        return {
            "script_id": script_id,
            "english_script": english_script,
            "chinese_translation": chinese_translation,
            "emotion": emotion,
            "voice": voice,
            "product_name": product_name,
            "product_type": product_type,
            "a3_params": a3_params,
            "duration_estimate": len(english_script.split()) * 0.5  # 估算时长
        }
    
    def _generate_opening(self, emotion: str, script_id: int) -> str:
        """生成开场句"""
        opening_types = list(self.core_engine.opening_library.keys())
        opening_type = opening_types[script_id % len(opening_types)]
        openings = self.core_engine.opening_library[opening_type]
        return openings[script_id % len(openings)]
    
    def _generate_pain_point(self, product_type: str) -> str:
        """生成痛点描述"""
        pain_points = {
            "美妆个护": "You know that feeling when you're getting ready and something just doesn't look right?",
            "电子产品": "Ever been frustrated with tech that doesn't work the way it should?",
            "家居用品": "Tired of your space not feeling like the sanctuary it should be?",
            "健康运动": "Struggling to find motivation for your wellness journey?"
        }
        return pain_points.get(product_type, pain_points["美妆个护"])
    
    def _generate_solution(self, product_name: str) -> str:
        """生成解决方案"""
        return f"This {product_name} changes everything. It's gentle, effective, and actually works."
    
    def _generate_hook(self, script_id: int) -> str:
        """生成钩子"""
        hook_categories = list(self.core_engine.hook_library.keys())
        category = hook_categories[script_id % len(hook_categories)]
        hooks = self.core_engine.hook_library[category]
        return hooks[script_id % len(hooks)]
    
    def _generate_cta(self) -> str:
        """生成行动号召"""
        ctas = [
            "Tap the cart and see what I mean. Results may vary.",
            "Check it out for yourself. Individual experience differs.",
            "Give it a try and let me know what you think."
        ]
        return random.choice(ctas)
    
    def _translate_to_chinese(self, english_text: str) -> str:
        """生成中文翻译（简化版）"""
        # 这里应该使用专业的翻译API，现在使用简化版本
        translations = {
            "As your bestie, lemme tell you this—": "作为你的好姐妹，让我告诉你这个—",
            "You know that feeling when you're getting ready and something just doesn't look right?": "你知道那种准备出门时总觉得哪里不对的感觉吗？",
            "This changes everything.": "这改变了一切。",
            "Tap the cart and see what I mean.": "点击购物车看看我的意思。",
            "Results may vary.": "效果因人而异。"
        }
        
        chinese_text = english_text
        for eng, chn in translations.items():
            chinese_text = chinese_text.replace(eng, chn)
        
        return chinese_text
    
    def _generate_a3_params(self, emotion: str) -> Dict:
        """生成A3动态参数"""
        base_config = self.core_engine.emotion_config.get(emotion, self.core_engine.emotion_config["Friendly"])
        
        # 转换为小数
        base_rate = base_config['rate'] / 100.0
        base_pitch = base_config['pitch'] / 100.0
        base_volume = base_config['volume'] / 10.0
        
        # 计算动态调整
        dynamic_rate = self.param_generator.dynamic_rate(base_rate, emotion) * 100
        dynamic_pitch = self.param_generator.dynamic_pitch(base_pitch, emotion) * 100
        dynamic_volume = self.param_generator.dynamic_volume(base_volume, emotion) * 10
        
        return {
            'rate': f"{dynamic_rate:+.1f}%",
            'pitch': f"{dynamic_pitch:+.1f}%",
            'volume': f"{dynamic_volume:+.1f}dB",
            'style': base_config['style'],
            'products': base_config['products']
        }

class A3BatchProcessor:
    """A3标准批次处理器"""
    
    def __init__(self, core_engine: A3CoreEngine):
        self.core_engine = core_engine
        self.script_generator = A3ScriptGenerator(core_engine)
    
    def generate_batch(self, product_name: str, batch_id: int, batch_size: int = 80) -> List[Dict]:
        """生成单个批次脚本"""
        scripts = []
        
        # 批次情绪分布策略
        emotion_distribution = self._get_batch_emotion_distribution(batch_id)
        
        for i in range(batch_size):
            script_id = batch_id * batch_size + i + 1
            
            # 选择情绪
            emotion = self._select_emotion_for_script(emotion_distribution, i)
            
            # 选择语音
            voice = self._select_voice_for_script(script_id)
            
            # 生成脚本
            script = self.script_generator.generate_script(
                product_name=product_name,
                script_id=script_id,
                emotion=emotion,
                voice=voice
            )
            
            scripts.append(script)
        
        return scripts
    
    def _get_batch_emotion_distribution(self, batch_id: int) -> Dict[str, float]:
        """获取批次情绪分布"""
        distributions = {
            1: {"Friendly": 0.25, "Empathetic": 0.20, "Calm": 0.20, "Confident": 0.15, "Playful": 0.10, "Excited": 0.10},
            2: {"Confident": 0.25, "Authoritative": 0.20, "Friendly": 0.15, "Serious": 0.15, "Empathetic": 0.10, "Calm": 0.10, "Playful": 0.05},
            3: {"Empathetic": 0.25, "Friendly": 0.20, "Inspirational": 0.15, "Calm": 0.15, "Grateful": 0.10, "Confident": 0.10, "Playful": 0.05},
            4: {"Urgent": 0.20, "Excited": 0.20, "Confident": 0.15, "Playful": 0.15, "Friendly": 0.10, "Authoritative": 0.10, "Mysterious": 0.10}
        }
        
        # 循环使用分布
        return distributions.get((batch_id - 1) % 4 + 1, distributions[1])
    
    def _select_emotion_for_script(self, distribution: Dict[str, float], script_index: int) -> str:
        """根据分布选择情绪"""
        emotions = list(distribution.keys())
        weights = list(distribution.values())
        
        # 添加一些随机性
        adjusted_weights = [w + random.uniform(-0.05, 0.05) for w in weights]
        adjusted_weights = [max(0, w) for w in adjusted_weights]  # 确保非负
        
        return random.choices(emotions, weights=adjusted_weights)[0]
    
    def _select_voice_for_script(self, script_id: int) -> str:
        """选择语音"""
        voices = self.core_engine.voice_library["Female"] + self.core_engine.voice_library["Male"]
        return voices[script_id % len(voices)]

class A3AudioGenerator:
    """A3标准音频生成器"""
    
    def __init__(self, core_engine: A3CoreEngine):
        self.core_engine = core_engine
    
    async def generate_audio(self, script: Dict, output_dir: str) -> str:
        """生成单个音频文件"""
        
        # 创建SSML
        ssml = self._create_ssml(script)
        
        # 生成文件名
        filename = f"tts_{script['script_id']:03d}_{script['emotion']}.mp3"
        output_path = os.path.join(output_dir, filename)
        
        # 生成音频
        communicate = edge_tts.Communicate(ssml, script['voice'])
        await communicate.save(output_path)
        
        logger.info(f"✅ Generated: {filename}")
        return output_path
    
    def _create_ssml(self, script: Dict) -> str:
        """创建SSML文本"""
        params = script['a3_params']
        
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{script['voice']}">
<prosody rate="{params['rate']}" pitch="{params['pitch']}" volume="{params['volume']}">
{script['english_script']}
</prosody>
</voice>
</speak>"""
        
        return ssml.strip()

class A3ComplianceValidator:
    """A3标准合规验证器"""
    
    def __init__(self, core_engine: A3CoreEngine):
        self.core_engine = core_engine
    
    def validate_script(self, script: Dict) -> Tuple[bool, List[str]]:
        """验证脚本合规性"""
        errors = []
        
        # 检查禁用词汇
        forbidden_words = self.core_engine.compliance_rules['forbidden_words']
        for word in forbidden_words:
            if word.lower() in script['english_script'].lower():
                errors.append(f"包含禁用词汇: {word}")
        
        # 检查时长
        if script['duration_estimate'] < 35 or script['duration_estimate'] > 60:
            errors.append(f"时长不符合要求: {script['duration_estimate']}秒")
        
        # 检查免责声明
        has_disclaimer = any(disclaimer in script['english_script'] 
                           for disclaimer in self.core_engine.compliance_rules['required_disclaimers'])
        if not has_disclaimer:
            errors.append("缺少必要的免责声明")
        
        return len(errors) == 0, errors
    
    def clean_script(self, script: Dict) -> Dict:
        """清洗脚本"""
        cleaned_script = script.copy()
        
        # 替换禁用词汇
        replacements = self.core_engine.compliance_rules['replacement_words']
        for forbidden, replacement in replacements.items():
            cleaned_script['english_script'] = cleaned_script['english_script'].replace(
                forbidden, replacement
            )
        
        # 确保有免责声明
        if not any(disclaimer in cleaned_script['english_script'] 
                  for disclaimer in self.core_engine.compliance_rules['required_disclaimers']):
            cleaned_script['english_script'] += " Results may vary."
        
        return cleaned_script

class A3ExportManager:
    """A3标准导出管理器"""
    
    def export_to_excel(self, scripts: List[Dict], product_name: str, batch_id: int) -> str:
        """导出到Excel文件"""
        
        # 准备数据
        data = []
        for script in scripts:
            data.append({
                'english_script': script['english_script'],
                'chinese_translation': script['chinese_translation']
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Lior{timestamp}_{product_name}_Batch{batch_id:02d}_{timestamp}.xlsx"
        filepath = os.path.join('outputs', filename)
        
        # 确保输出目录存在
        os.makedirs('outputs', exist_ok=True)
        
        # 导出Excel
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        logger.info(f"📊 Exported: {filename}")
        return filepath

# 主函数
async def main():
    """主函数 - A3标准完整流程"""
    
    # 初始化A3核心引擎
    core_engine = A3CoreEngine()
    batch_processor = A3BatchProcessor(core_engine)
    audio_generator = A3AudioGenerator(core_engine)
    validator = A3ComplianceValidator(core_engine)
    export_manager = A3ExportManager()
    
    # 产品信息
    product_name = "Dark Spot Patch"
    total_batches = 10
    batch_size = 80
    
    logger.info(f"🚀 Starting A3 Standard Generation for {product_name}")
    logger.info(f"📊 Total: {total_batches} batches × {batch_size} scripts = {total_batches * batch_size} scripts")
    
    all_scripts = []
    
    # 生成所有批次
    for batch_id in range(1, total_batches + 1):
        logger.info(f"🔄 Processing Batch {batch_id}/{total_batches}")
        
        # 生成批次脚本
        batch_scripts = batch_processor.generate_batch(product_name, batch_id, batch_size)
        
        # 验证和清洗
        validated_scripts = []
        for script in batch_scripts:
            is_valid, errors = validator.validate_script(script)
            if not is_valid:
                logger.warning(f"⚠️ Script {script['script_id']} validation failed: {errors}")
                script = validator.clean_script(script)
            
            validated_scripts.append(script)
        
        # 生成音频文件
        output_dir = f"outputs/{product_name}/batch_{batch_id:02d}"
        os.makedirs(output_dir, exist_ok=True)
        
        for script in validated_scripts:
            await audio_generator.generate_audio(script, output_dir)
        
        # 导出Excel
        excel_path = export_manager.export_to_excel(validated_scripts, product_name, batch_id)
        
        all_scripts.extend(validated_scripts)
        
        logger.info(f"✅ Batch {batch_id} completed")
    
    # 生成总报告
    logger.info(f"🎉 A3 Standard Generation Complete!")
    logger.info(f"📊 Total scripts generated: {len(all_scripts)}")
    logger.info(f"📁 Output directory: outputs/{product_name}/")
    
    return all_scripts

if __name__ == "__main__":
    asyncio.run(main())
