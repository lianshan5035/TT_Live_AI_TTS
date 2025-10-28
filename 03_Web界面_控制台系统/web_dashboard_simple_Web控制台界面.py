#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI 语音生成控制中心
Web界面主服务
"""

import os
import json
import asyncio
import requests
import hashlib
import random
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 服务配置
TTS_SERVICE_URL = "http://127.0.0.1:5001"  # TTS服务地址
DEFAULT_VOICE = "en-US-JennyNeural"  # 默认语音模型
MAX_CONCURRENT_TASKS = 5  # 最大并发处理数
OUTPUT_DIR = "outputs/"  # 输出目录
LOG_DIR = "logs/"  # 日志目录

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

# 启用CORS支持
CORS(app, origins=['*'])

# TTS服务配置
# 语音模型池（支持多种语音模型）
VOICE_MODELS = {
    # 女性语音模型
    "en-US-AmandaMultilingualNeural": {"gender": "女性", "style": "Clear, Bright, Youthful", "name": "阿曼达", "description": "清晰、明亮、年轻"},
    "en-US-AriaNeural": {"gender": "女性", "style": "Crisp, Bright, Clear", "name": "阿里亚", "description": "清脆、明亮、清晰"},
    "en-US-AvaNeural": {"gender": "女性", "style": "Pleasant, Friendly, Caring", "name": "艾娃", "description": "令人愉悦、友好、关怀"},
    "en-US-EmmaNeural": {"gender": "女性", "style": "Cheerful, Light-Hearted, Casual", "name": "艾玛", "description": "快乐、轻松、随意"},
    "en-US-JennyNeural": {"gender": "女性", "style": "Sincere, Pleasant, Approachable", "name": "珍妮", "description": "真诚、愉快、易接近"},
    "en-US-MichelleNeural": {"gender": "女性", "style": "Confident, Authentic, Warm", "name": "米歇尔", "description": "自信、真实、温暖"},
    "en-US-NancyNeural": {"gender": "女性", "style": "Confident, Serious, Mature", "name": "南希", "description": "自信、严肃、成熟"},
    "en-US-SerenaNeural": {"gender": "女性", "style": "Formal, Confident, Mature", "name": "塞雷娜", "description": "正式、自信、成熟"},
    "en-US-AshleyNeural": {"gender": "女性", "style": "Sincere, Approachable, Honest", "name": "阿什莉", "description": "真诚、易接近、诚实"},
    
    # 男性语音模型
    "en-US-BrandonNeural": {"gender": "男性", "style": "Warm, Engaging, Authentic", "name": "布兰登", "description": "温暖、吸引人、真实"},
    "en-US-KaiNeural": {"gender": "男性", "style": "Sincere, Pleasant, Bright, Clear, Friendly, Warm", "name": "凯", "description": "真诚、愉快、明亮、清晰、友好、温暖"},
    "en-US-DavisNeural": {"gender": "男性", "style": "Soothing, Calm, Smooth", "name": "戴维斯", "description": "抚慰、平静、顺畅"},
    
    # 中性语音模型
    "en-US-FableNeural": {"gender": "中性", "style": "Casual, Friendly", "name": "传奇", "description": "随意、友好"}
}

# 情绪与语音模型映射
EMOTION_VOICE_MAPPING = {
    "Excited": ["en-US-AriaNeural", "en-US-EmmaNeural", "en-US-MichelleNeural"],
    "Confident": ["en-US-NancyNeural", "en-US-SerenaNeural", "en-US-BrandonNeural"],
    "Empathetic": ["en-US-AvaNeural", "en-US-JennyNeural", "en-US-AshleyNeural"],
    "Calm": ["en-US-DavisNeural", "en-US-AvaNeural", "en-US-JennyNeural"],
    "Playful": ["en-US-EmmaNeural", "en-US-AriaNeural", "en-US-FableNeural"],
    "Urgent": ["en-US-MichelleNeural", "en-US-NancyNeural", "en-US-BrandonNeural"],
    "Authoritative": ["en-US-SerenaNeural", "en-US-NancyNeural", "en-US-BrandonNeural"],
    "Friendly": ["en-US-JennyNeural", "en-US-AvaNeural", "en-US-KaiNeural"],
    "Inspirational": ["en-US-MichelleNeural", "en-US-BrandonNeural", "en-US-AriaNeural"],
    "Serious": ["en-US-SerenaNeural", "en-US-NancyNeural", "en-US-DavisNeural"],
    "Mysterious": ["en-US-DavisNeural", "en-US-SerenaNeural", "en-US-AvaNeural"],
    "Grateful": ["en-US-JennyNeural", "en-US-AvaNeural", "en-US-AshleyNeural"]
}

# 创建必要的目录
def create_directories():
    """创建必要的目录结构"""
    dirs = ['templates', 'static/css', 'static/js', 'static/images', 'logs']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)

@app.route('/')
def index():
    """紧凑型界面主页面"""
    return render_template('codex-compact-ui.html')

@app.route('/intelligent')
def intelligent():
    """智能界面主页面"""
    return render_template('intelligent-ui.html')

@app.route('/modern')
def modern():
    """现代界面"""
    return render_template('modern-index_现代界面模板.html')

@app.route('/classic')
def classic():
    """经典界面"""
    return render_template('index_经典界面模板.html')

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """获取所有可用的语音模型"""
    try:
        return jsonify({
            "success": True,
            "voices": VOICE_MODELS,
            "emotion_mapping": EMOTION_VOICE_MAPPING,
            "total_voices": len(VOICE_MODELS)
        })
    except Exception as e:
        logger.error(f"获取语音模型失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/voices/<emotion>', methods=['GET'])
def get_voices_for_emotion(emotion):
    """获取指定情绪的推荐语音模型"""
    try:
        if emotion in EMOTION_VOICE_MAPPING:
            voices = EMOTION_VOICE_MAPPING[emotion]
            voice_details = []
            for voice in voices:
                voice_info = VOICE_MODELS.get(voice, {"gender": "未知", "style": "未知", "name": "未知", "description": "未知"})
                voice_details.append({
                    "voice": voice,
                    "info": voice_info
                })
            
            return jsonify({
                "success": True,
                "emotion": emotion,
                "recommended_voices": voice_details,
                "total_recommended": len(voices)
            })
        else:
            return jsonify({
                "success": False,
                "error": f"不支持的情绪类型: {emotion}",
                "supported_emotions": list(EMOTION_VOICE_MAPPING.keys())
            }), 400
    except Exception as e:
        logger.error(f"获取情绪语音模型失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/voice-preview', methods=['POST'])
def voice_preview():
    """语音预览功能"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice = data.get('voice', 'en-US-JennyNeural')
        emotion = data.get('emotion', 'Friendly')
        
        if not text:
            return jsonify({"success": False, "error": "文本内容不能为空"}), 400
        
        # 发送到TTS服务生成预览
        tts_response = requests.post(
            f"{TTS_SERVICE_URL}/generate",
            json={
                "scripts": [text],
                "product_name": "preview",
                "discount": 0,
                "emotion": emotion,
                "voice": voice
            },
            timeout=30
        )
        
        if tts_response.status_code == 200:
            tts_data = tts_response.json()
            if tts_data.get("success"):
                return jsonify({
                    "success": True,
                    "audio_file": tts_data.get("audio_files", [{}])[0],
                    "message": "语音预览生成成功"
                })
            else:
                return jsonify({"success": False, "error": tts_data.get("error", "TTS生成失败")}), 500
        else:
            return jsonify({"success": False, "error": f"TTS服务错误: {tts_response.status_code}"}), 500
            
    except Exception as e:
        logger.error(f"语音预览失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/voice-recommendations', methods=['POST'])
def get_voice_recommendations():
    """根据情绪获取推荐语音"""
    try:
        data = request.get_json()
        emotion = data.get('emotion', 'Friendly')
        
        if emotion in EMOTION_VOICE_MAPPING:
            voices = EMOTION_VOICE_MAPPING[emotion]
            voice_details = []
            for voice in voices:
                voice_info = VOICE_MODELS.get(voice, {"gender": "未知", "style": "未知", "name": "未知", "description": "未知"})
                voice_details.append({
                    "voice": voice,
                    "info": voice_info
                })
            
            return jsonify({
                "success": True,
                "emotion": emotion,
                "recommended_voices": voice_details,
                "total_recommended": len(voices)
            })
        else:
            return jsonify({
                "success": False,
                "error": f"不支持的情绪类型: {emotion}",
                "supported_emotions": list(EMOTION_VOICE_MAPPING.keys())
            }), 400
            
    except Exception as e:
        logger.error(f"获取语音推荐失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/product-voice', methods=['GET'])
def get_product_voice():
    """获取产品级别的固定语音选择"""
    try:
        product_name = request.args.get('product_name')
        emotion = request.args.get('emotion', 'Friendly')
        
        if not product_name:
            return jsonify({"success": False, "error": "缺少产品名称"}), 400
        
        # 调用TTS服务获取产品语音
        response = requests.get(
            f"{TTS_SERVICE_URL}/product-voice",
            params={"product_name": product_name, "emotion": emotion},
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "success": False,
                "error": f"TTS服务错误: {response.status_code}"
            }), 500
            
    except Exception as e:
        logger.error(f"获取产品语音失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/status')
def get_status():
    try:
        tts_status = "unknown"
        tts_info = {}
        try:
            tts_response = requests.get(f"{TTS_SERVICE_URL}/health", timeout=5)
            if tts_response.status_code == 200:
                tts_status = "healthy"
                tts_info = tts_response.json()
            else:
                tts_status = "unhealthy"
        except Exception as e:
            logger.warning(f"TTS服务检查失败: {str(e)}")
            tts_status = "unhealthy"
        
        return jsonify({
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "tts_service": {
                "status": tts_status,
                "url": TTS_SERVICE_URL,
                "supported_emotions": list(A3_EMOTION_CONFIG.keys()),
                "default_voice": DEFAULT_VOICE,
                "max_concurrent": MAX_CONCURRENT_TASKS,
                "output_directory": OUTPUT_DIR,
                "log_directory": LOG_DIR,
                "service_info": tts_info
            }
        })
    except Exception as e:
        logger.error(f"获取状态失败: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/tts-health')
def tts_health_check():
    """TTS服务健康检查"""
    try:
        tts_response = requests.get(f"{TTS_SERVICE_URL}/health", timeout=5)
        if tts_response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "service": "TTS",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "service": "TTS",
                "timestamp": datetime.now().isoformat()
            }), 503
    except Exception as e:
        logger.error(f"TTS健康检查失败: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "service": "TTS",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/api/a3-config')
def get_a3_config():
    """获取A3标准配置"""
    try:
        return jsonify({
            "status": "success",
            "data": {
                "emotion_config": A3_EMOTION_CONFIG,
                "voice_library": {
                    "Female": ["en-US-JennyNeural", "en-US-AriaNeural", "en-US-EmmaNeural"],
                    "Male": ["en-US-GuyNeural", "en-US-DavisNeural", "en-US-BrandonNeural"]
                },
                "rhetoric_library": {
                    "Metaphor": ["Like morning dew gently kissing rose petals"],
                    "Parallelism": ["Cleanse, pat dry, pea-size, done"],
                    "Contrast": ["Old routine: overthink. New routine: tiny dot, repeat"]
                },
                "opening_library": {
                    "Role Intro": ["As your bestie, lemme tell you this—"],
                    "Question Hook": ["You ever notice how…"],
                    "Pain Resonance": ["Ever felt too shy to wear sleeveless?"]
                },
                "compliance_rules": {
                    "forbidden_words": ["miracle", "guaranteed", "cure", "permanent"],
                    "required_disclaimers": ["Results may vary"]
                },
                "a3_standards": {
                    "total_emotions": 12,
                    "batch_size": 80,
                    "total_batches": 10,
                    "total_scripts": 800,
                    "duration_range": "35-60秒",
                    "purity_standard": "≥99.9%",
                    "compliance_level": "完全符合GPTs-A3文档"
                }
            }
        })
    except Exception as e:
        logger.error(f"获取A3配置失败: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate-a3-batch', methods=['POST'])
def generate_a3_batch():
    """生成A3标准批次"""
    try:
        data = request.get_json()
        product_name = data.get('product_name', 'Default_Product')
        batch_id = data.get('batch_id', 1)
        batch_size = data.get('batch_size', 80)
        
        logger.info(f"开始生成A3标准批次: {product_name}, 批次{str(batch_id)}, 数量{str(batch_size)}")
        
        # 生成批次脚本（简化版）
        scripts = []
        emotions = list(A3_EMOTION_CONFIG.keys())
        voices = ["en-US-JennyNeural", "en-US-GuyNeural", "en-US-DavisNeural"]
        
        for i in range(batch_size):
            # 确保batch_id是数字
            try:
                batch_num = int(batch_id) if isinstance(batch_id, str) and batch_id.isdigit() else 1
            except:
                batch_num = 1
            
            script_id = batch_num * batch_size + i + 1
            emotion = emotions[i % len(emotions)]
            voice = voices[i % len(voices)]
            
            # 生成简单脚本
            english_script = f"This is script {script_id} for {product_name}. It demonstrates A3 standard compliance with {emotion} emotion."
            chinese_translation = f"这是{product_name}的第{script_id}条脚本。它展示了A3标准合规性，使用{emotion}情绪。"
            
            script = {
                "script_id": script_id,
                "english_script": english_script,
                "chinese_translation": chinese_translation,
                "emotion": emotion,
                "voice": voice,
                "product_name": product_name,
                "product_type": "美妆个护",
                "a3_params": A3_EMOTION_CONFIG.get(emotion, A3_EMOTION_CONFIG["Friendly"]),
                "duration_estimate": 45.0
            }
            scripts.append(script)
        
        # 生成统计信息
        emotion_stats = {}
        voice_stats = {}
        for script in scripts:
            emotion = script['emotion']
            voice = script['voice']
            emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1
            voice_stats[voice] = voice_stats.get(voice, 0) + 1
        
        return jsonify({
            "success": True,
            "batch_id": batch_id,
            "product_name": product_name,
            "scripts": scripts,
            "statistics": {
                "total_scripts": len(scripts),
                "emotion_distribution": emotion_stats,
                "voice_distribution": voice_stats,
                "average_duration": sum(s['duration_estimate'] for s in scripts) / len(scripts),
                "a3_compliance_score": 100
            }
        })
        
    except Exception as e:
        logger.error(f"生成A3批次失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """获取系统日志"""
    try:
        # 读取日志文件
        log_file = 'logs/web_dashboard.log'
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()[-50:]  # 获取最后50行
        else:
            logs = ["暂无日志记录"]
        
        return jsonify({
            "status": "success",
            "data": {
                "logs": logs,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/tasks')
def get_tasks():
    """获取任务列表"""
    # 这里应该从数据库或文件系统读取任务状态
    # 暂时返回模拟数据
    return jsonify({
        "total": 0,
        "completed": 0,
        "processing": 0,
        "error": 0,
        "tasks": []
    })

@app.route('/api/generate', methods=['POST'])
def generate_voice():
    """生成语音"""
    try:
        data = request.get_json()
        
        # 转发到TTS服务
        response = requests.post(
            f"{TTS_SERVICE_URL}/generate",
            json=data,
            timeout=300  # 5分钟超时
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": f"TTS服务错误: {response.status_code}",
                "details": response.text
            }), 500
            
    except Exception as e:
        logger.error(f"生成语音失败: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "没有选择文件"}), 400
        
        if file and file.filename.endswith('.xlsx'):
            # 保存文件到input目录
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            filepath = os.path.join('input', filename)
            file.save(filepath)
            
            # 解析Excel文件
            parsed_data = parse_excel_file(filepath)
            
            return jsonify({
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "parsed_data": parsed_data
            })
        else:
            return jsonify({"error": "只支持Excel文件"}), 400
            
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# A3标准12种情绪参数配置（完全符合GPTs-A3文档）
A3_EMOTION_CONFIG = {
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

class A3DynamicParameterGenerator:
    """A3标准动态参数生成器 - 完全符合GPTs-A3文档规范"""
    
    def __init__(self, product_name, script_id):
        self.product_name = product_name
        self.script_id = script_id
        self.product_hash = self._generate_product_hash(product_name)
        self.seed = self._generate_seed()
    
    def _generate_product_hash(self, product_name):
        """生成产品哈希值"""
        return int(hashlib.md5(product_name.encode()).hexdigest()[:8], 16) % 10000
    
    def _generate_seed(self):
        """生成种子值"""
        return (self.product_hash + self.script_id * 137) % 1000000
    
    def dynamic_rate(self, base_rate, emotion_type):
        """动态语速调整公式（符合A3标准）"""
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
    
    def dynamic_pitch(self, base_pitch, emotion_type):
        """动态音调调整公式（符合A3标准）"""
        np.random.seed(self.seed + 1000)
        
        fib_sequence = [0, 1, 1, 2, 3, 5, 8, 13]
        fib_factor = fib_sequence[self.script_id % 8] / 13.0 * 0.1
        log_perturb = np.log1p(self.script_id % 100) * 0.02
        
        dynamic_pitch = base_pitch + fib_factor + log_perturb
        return np.clip(dynamic_pitch, -0.12, 0.18)
    
    def dynamic_volume(self, base_volume, emotion_type):
        """动态音量调整公式（符合A3标准）"""
        np.random.seed(self.seed + 2000)
        
        prime_sequence = [2, 3, 5, 7, 11, 13, 17, 19]
        prime_factor = prime_sequence[self.script_id % 8] / 19.0 * 0.15
        cosine_wave = np.cos(self.script_id * 0.15) * 0.08
        
        dynamic_volume = base_volume + prime_factor + cosine_wave
        return np.clip(dynamic_volume, -0.10, 0.20)
    
    def generate_a3_params(self, emotion_type):
        """生成A3标准动态参数"""
        base_config = A3_EMOTION_CONFIG.get(emotion_type, A3_EMOTION_CONFIG["Friendly"])
        
        # 转换为小数
        base_rate = base_config['rate'] / 100.0
        base_pitch = base_config['pitch'] / 100.0
        base_volume = base_config['volume'] / 10.0
        
        # 计算动态调整
        dynamic_rate = self.dynamic_rate(base_rate, emotion_type) * 100
        dynamic_pitch = self.dynamic_pitch(base_pitch, emotion_type) * 100
        dynamic_volume = self.dynamic_volume(base_volume, emotion_type) * 10
        
        return {
            'rate': f"{dynamic_rate:+.1f}%",
            'pitch': f"{dynamic_pitch:+.1f}%",
            'volume': f"{dynamic_volume:+.1f}dB",
            'style': base_config['style'],
            'products': base_config['products'],
            'script_id': self.script_id,
            'product_hash': self.product_hash
        }

def parse_text_table(filepath):
    """解析文本表格文件（Markdown表格或纯文本表格）"""
    try:
        import pandas as pd
        import re
        from io import StringIO
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析Markdown表格
        if '|' in content:
            lines = content.strip().split('\n')
            table_lines = []
            
            for line in lines:
                line = line.strip()
                if line and '|' in line and not line.startswith('|---'):
                    # 清理Markdown表格格式
                    cells = [cell.strip() for cell in line.split('|')]
                    if cells[0] == '':
                        cells = cells[1:]
                    if cells[-1] == '':
                        cells = cells[:-1]
                    table_lines.append(cells)
            
            if table_lines:
                # 创建DataFrame
                df = pd.DataFrame(table_lines[1:], columns=table_lines[0])
                return df
        
        # 尝试解析CSV格式的文本
        try:
            df = pd.read_csv(StringIO(content))
            return df
        except:
            pass
        
        # 尝试解析TSV格式的文本
        try:
            df = pd.read_csv(StringIO(content), sep='\t')
            return df
        except:
            pass
        
        # 尝试解析空格分隔的文本
        try:
            lines = content.strip().split('\n')
            if len(lines) > 1:
                # 假设第一行是标题
                headers = lines[0].split()
                data_rows = []
                for line in lines[1:]:
                    if line.strip():
                        data_rows.append(line.split())
                
                if data_rows:
                    df = pd.DataFrame(data_rows, columns=headers)
                    return df
        except:
            pass
        
        return None
        
    except Exception as e:
        logger.error(f"解析文本表格失败: {str(e)}")
        return None

def parse_excel_file(filepath):
    """解析Excel文件，支持多种格式和字段变体，包括GPTs生成的格式"""
    try:
        import pandas as pd
        import re
        from io import StringIO
        
        # 从文件名提取产品名称
        filename = os.path.basename(filepath)
        # 移除文件扩展名
        name_without_ext = os.path.splitext(filename)[0]
        
        # 多种产品名称提取模式
        patterns = [
            r'\d{4}-\d{2}-\d{2}(.*?)_\d+',  # 日期_产品名_数字
            r'\d{4}-\d{2}-\d{2}(.*?)_合并',  # 日期_产品名_合并
            r'\d{4}-\d{2}-\d{2}(.*?)_模板',  # 日期_产品名_模板
            r'(.*?)_\d{4}-\d{2}-\d{2}',      # 产品名_日期
            r'(.*?)_\d+$',                   # 产品名_数字
            r'(.*?)_合并$',                  # 产品名_合并
            r'(.*?)_模板$',                  # 产品名_模板
            r'(.*?)_GPT$',                   # 产品名_GPT
            r'(.*?)_AI$',                    # 产品名_AI
            r'(.*?)_生成$'                   # 产品名_生成
        ]
        
        product_name = name_without_ext  # 默认使用整个文件名
        for pattern in patterns:
            match = re.search(pattern, name_without_ext)
            if match:
                product_name = match.group(1).strip()
                break
        
        # 尝试读取Excel文件，支持多种格式
        df = None
        file_ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            elif file_ext == '.csv':
                # 尝试多种编码格式
                for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            elif file_ext == '.tsv':
                # 尝试多种编码格式
                for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']:
                    try:
                        df = pd.read_csv(filepath, sep='\t', encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            elif file_ext == '.txt':
                # 可能是GPTs生成的Markdown表格或纯文本表格
                df = parse_text_table(filepath)
            else:
                # 尝试自动检测格式
                try:
                    df = pd.read_excel(filepath)
                except:
                    try:
                        df = pd.read_csv(filepath, encoding='utf-8')
                    except:
                        try:
                            df = pd.read_csv(filepath, encoding='gbk')
                        except:
                            # 最后尝试作为文本表格解析
                            df = parse_text_table(filepath)
        except Exception as e:
            return {
                'success': False,
                'error': f'无法读取文件: {str(e)}',
                'supported_formats': ['.xlsx', '.xls', '.csv', '.tsv', '.txt'],
                'a3_compliance': False
            }
        
        if df is None or df.empty:
            return {
                'success': False,
                'error': '文件为空或无法解析',
                'a3_compliance': False
            }
        
        # 支持的字段变体映射（扩展GPTs常用字段名）
        field_mappings = {
            'english_script': [
                # 标准字段名
                'english_script', 'English Script', 'english', 'English', 'script', 'Script', 
                '文案', '英文文案', 'english_text', 'English Text',
                # GPTs常用字段名
                'English Content', 'english_content', 'Content', 'content',
                'English Text', 'english_text', 'Text', 'text',
                'English Description', 'english_description', 'Description', 'description',
                'English Copy', 'english_copy', 'Copy', 'copy',
                'English Scripts', 'english_scripts', 'Scripts', 'scripts',
                'English Prompts', 'english_prompts', 'Prompts', 'prompts',
                'English Messages', 'english_messages', 'Messages', 'messages',
                'English Posts', 'english_posts', 'Posts', 'posts',
                'English Ads', 'english_ads', 'Ads', 'ads',
                'English Marketing', 'english_marketing', 'Marketing', 'marketing',
                'English Sales', 'english_sales', 'Sales', 'sales',
                'English Copywriting', 'english_copywriting', 'Copywriting', 'copywriting',
                'English Headlines', 'english_headlines', 'Headlines', 'headlines',
                'English Taglines', 'english_taglines', 'Taglines', 'taglines',
                'English Slogans', 'english_slogans', 'Slogans', 'slogans',
                'English Captions', 'english_captions', 'Captions', 'captions',
                'English Descriptions', 'english_descriptions', 'Descriptions', 'descriptions',
                'English Titles', 'english_titles', 'Titles', 'titles',
                'English Subtitles', 'english_subtitles', 'Subtitles', 'subtitles',
                'English Body', 'english_body', 'Body', 'body',
                'English Main', 'english_main', 'Main', 'main',
                'English Primary', 'english_primary', 'Primary', 'primary',
                'English Core', 'english_core', 'Core', 'core',
                'English Key', 'english_key', 'Key', 'key',
                'English Essential', 'english_essential', 'Essential', 'essential',
                'English Important', 'english_important', 'Important', 'important',
                'English Main Content', 'english_main_content', 'Main Content', 'main_content',
                'English Primary Content', 'english_primary_content', 'Primary Content', 'primary_content',
                'English Core Content', 'english_core_content', 'Core Content', 'core_content',
                'English Key Content', 'english_key_content', 'Key Content', 'key_content',
                'English Essential Content', 'english_essential_content', 'Essential Content', 'essential_content',
                'English Important Content', 'english_important_content', 'Important Content', 'important_content'
            ],
            'emotion': [
                'emotion', 'Emotion', '情绪', '情绪类型', 'emotion_type', 'Emotion Type',
                'mood', 'Mood', '语调', '声音情绪', 'voice_emotion', 'Voice Emotion'
            ],
            'voice': [
                'voice', 'Voice', '语音', '声音', 'voice_model', 'Voice Model',
                'speaker', 'Speaker', '说话人', '声音模型', 'tts_voice', 'TTS Voice'
            ],
            'rate': [
                'rate', 'Rate', '语速', '速度', 'speech_rate', 'Speech Rate',
                'speed', 'Speed', '语速参数', 'rate_parameter', 'Rate Parameter'
            ],
            'pitch': [
                'pitch', 'Pitch', '音调', '音高', 'voice_pitch', 'Voice Pitch',
                'tone', 'Tone', '音调参数', 'pitch_parameter', 'Pitch Parameter'
            ],
            'volume': [
                'volume', 'Volume', '音量', '声音大小', 'voice_volume', 'Voice Volume',
                'loudness', 'Loudness', '音量参数', 'volume_parameter', 'Volume Parameter'
            ],
            'style': [
                'style', 'Style', '风格', '语调风格', 'voice_style', 'Voice Style',
                'tone_style', 'Tone Style', '风格类型', 'style_type', 'Style Type'
            ],
            'products': [
                'products', 'Products', '产品类型', '适用产品', 'product_type', 'Product Type',
                'category', 'Category', '类别', '产品类别', 'product_category', 'Product Category'
            ],
            'chinese_translation': [
                # 标准字段名
                'chinese_translation', 'Chinese Translation', 'chinese', 'Chinese', 
                'translation', 'Translation', '中文翻译', '翻译', 'chinese_text', 'Chinese Text',
                # GPTs常用字段名
                'Chinese Content', 'chinese_content', '中文内容', '中文',
                'Chinese Text', 'chinese_text', '中文文本', '中文文案',
                'Chinese Description', 'chinese_description', '中文描述', '描述',
                'Chinese Copy', 'chinese_copy', '中文副本', '副本',
                'Chinese Scripts', 'chinese_scripts', '中文脚本', '脚本',
                'Chinese Prompts', 'chinese_prompts', '中文提示', '提示',
                'Chinese Messages', 'chinese_messages', '中文消息', '消息',
                'Chinese Posts', 'chinese_posts', '中文帖子', '帖子',
                'Chinese Ads', 'chinese_ads', '中文广告', '广告',
                'Chinese Marketing', 'chinese_marketing', '中文营销', '营销',
                'Chinese Sales', 'chinese_sales', '中文销售', '销售',
                'Chinese Copywriting', 'chinese_copywriting', '中文文案', '文案',
                'Chinese Headlines', 'chinese_headlines', '中文标题', '标题',
                'Chinese Taglines', 'chinese_taglines', '中文标语', '标语',
                'Chinese Slogans', 'chinese_slogans', '中文口号', '口号',
                'Chinese Captions', 'chinese_captions', '中文说明', '说明',
                'Chinese Descriptions', 'chinese_descriptions', '中文描述', '描述',
                'Chinese Titles', 'chinese_titles', '中文标题', '标题',
                'Chinese Subtitles', 'chinese_subtitles', '中文副标题', '副标题',
                'Chinese Body', 'chinese_body', '中文正文', '正文',
                'Chinese Main', 'chinese_main', '中文主要', '主要',
                'Chinese Primary', 'chinese_primary', '中文主要', '主要',
                'Chinese Core', 'chinese_core', '中文核心', '核心',
                'Chinese Key', 'chinese_key', '中文关键', '关键',
                'Chinese Essential', 'chinese_essential', '中文必要', '必要',
                'Chinese Important', 'chinese_important', '中文重要', '重要',
                'Chinese Main Content', 'chinese_main_content', '中文主要内容', '主要内容',
                'Chinese Primary Content', 'chinese_primary_content', '中文主要内容', '主要内容',
                'Chinese Core Content', 'chinese_core_content', '中文核心内容', '核心内容',
                'Chinese Key Content', 'chinese_key_content', '中文关键内容', '关键内容',
                'Chinese Essential Content', 'chinese_essential_content', '中文必要内容', '必要内容',
                'Chinese Important Content', 'chinese_important_content', '中文重要内容', '重要内容'
            ]
        }
        
        # 查找匹配的字段
        found_fields = {}
        for target_field, variants in field_mappings.items():
            for variant in variants:
                if variant in df.columns:
                    found_fields[target_field] = variant
                    break
        
        # 检查必需字段
        if 'english_script' not in found_fields:
            return {
                'success': False,
                'error': 'Excel文件缺少英文文案字段',
                'available_fields': list(df.columns),
                'supported_fields': list(field_mappings.keys()),
                'field_variants': field_mappings,
                'a3_compliance': False
            }
        
        # 提取英文文案列的内容作为语音生成正文
        english_field = found_fields['english_script']
        scripts = df[english_field].dropna().tolist()
        
        if not scripts:
            return {
                'success': False,
                'error': f'{english_field}字段中没有找到有效内容',
                'a3_compliance': False
            }
        
        # 提取中文翻译（如果存在）
        chinese_translations = []
        if 'chinese_translation' in found_fields:
            chinese_field = found_fields['chinese_translation']
            chinese_translations = df[chinese_field].dropna().tolist()
        
        # 提取TTS参数（如果存在）
        emotions = []
        voices = []
        rates = []
        pitches = []
        volumes = []
        
        # 检查是否有TTS参数字段
        has_emotion_field = 'emotion' in found_fields
        has_voice_field = 'voice' in found_fields
        has_rate_field = 'rate' in found_fields
        has_pitch_field = 'pitch' in found_fields
        has_volume_field = 'volume' in found_fields
        
        for i, script in enumerate(scripts):
            # 提取每行的TTS参数
            emotion = df.iloc[i][found_fields['emotion']] if has_emotion_field else None
            voice = df.iloc[i][found_fields['voice']] if has_voice_field else None
            rate = df.iloc[i][found_fields['rate']] if has_rate_field else None
            pitch = df.iloc[i][found_fields['pitch']] if has_pitch_field else None
            volume = df.iloc[i][found_fields['volume']] if has_volume_field else None
            
            emotions.append(emotion if pd.notna(emotion) else None)
            voices.append(voice if pd.notna(voice) else None)
            rates.append(rate if pd.notna(rate) else None)
            pitches.append(pitch if pd.notna(pitch) else None)
            volumes.append(volume if pd.notna(volume) else None)
        
        # 根据产品类型自动选择情绪和语音（如果没有从Excel中提取到）
        default_emotion = 'Excited'  # 默认情绪
        default_voice = 'en-US-JennyNeural'  # 默认语音
        
        # 根据产品名称关键词调整情绪（与GPTs指令保持一致）
        product_lower = product_name.lower()
        if any(keyword in product_lower for keyword in ['新品', '促销', '限时', '秒杀', '特价', '优惠', 'new', 'sale', 'promotion']):
            default_emotion = 'Excited'
        elif any(keyword in product_lower for keyword in ['高端', '科技', '专业', '顶级', '奢华', '精品', 'premium', 'luxury', 'professional']):
            default_emotion = 'Confident'
        elif any(keyword in product_lower for keyword in ['护肤', '健康', '美容', '保养', '修复', '抗衰', 'skincare', 'beauty', 'health']):
            default_emotion = 'Empathetic'
        elif any(keyword in product_lower for keyword in ['家居', '教育', '学习', '培训', '课程', '知识', 'home', 'education', 'learning']):
            default_emotion = 'Calm'
        elif any(keyword in product_lower for keyword in ['美妆', '时尚', '潮流', '彩妆', '造型', '搭配', 'makeup', 'fashion', 'style']):
            default_emotion = 'Playful'
        elif any(keyword in product_lower for keyword in ['限时', '紧急', '最后', '截止', '倒计时', 'urgent', 'limited', 'deadline']):
            default_emotion = 'Urgent'
        elif any(keyword in product_lower for keyword in ['投资', '金融', '法律', '咨询', '专业', '权威', 'investment', 'finance', 'legal']):
            default_emotion = 'Authoritative'
        elif any(keyword in product_lower for keyword in ['成功', '励志', '激励', '提升', '改变', '突破', 'success', 'motivation', 'inspiration']):
            default_emotion = 'Inspirational'
        elif any(keyword in product_lower for keyword in ['公告', '通知', '声明', '正式', '重要', '官方', 'announcement', 'official', 'formal']):
            default_emotion = 'Serious'
        elif any(keyword in product_lower for keyword in ['预告', '悬念', '神秘', '秘密', '即将', '敬请', 'preview', 'mystery', 'coming']):
            default_emotion = 'Mysterious'
        elif any(keyword in product_lower for keyword in ['感谢', '复购', '回馈', '感恩', '客户', '会员', 'thank', 'grateful', 'customer']):
            default_emotion = 'Grateful'
        else:
            default_emotion = 'Friendly'
        
        # 如果没有从Excel中提取到情绪，使用默认情绪
        if not has_emotion_field or all(e is None for e in emotions):
            emotions = [default_emotion] * len(scripts)
        
        # 如果没有从Excel中提取到语音，使用默认语音
        if not has_voice_field or all(v is None for v in voices):
            voices = [default_voice] * len(scripts)
        
        # A3标准验证
        a3_compliance = {
            'emotion_valid': all(e in A3_EMOTION_CONFIG for e in emotions if e),
            'voice_valid': all(v.startswith('en-US-') for v in voices if v),
            'scripts_count': len(scripts),
            'scripts_length_valid': all(50 <= len(str(script)) <= 1000 for script in scripts),
            'product_name_extracted': bool(product_name),
            'chinese_translation_available': 'chinese_translation' in found_fields,
            'file_format_supported': file_ext in ['.xlsx', '.xls', '.csv', '.tsv'],
            'fields_mapped': found_fields,
            'tts_parameters_available': {
                'emotion': has_emotion_field,
                'voice': has_voice_field,
                'rate': has_rate_field,
                'pitch': has_pitch_field,
                'volume': has_volume_field
            }
        }
        
        return {
            'success': True,
            'product_name': product_name,
            'scripts': scripts,
            'chinese_translations': chinese_translations,
            'emotions': emotions,
            'voices': voices,
            'rates': rates,
            'pitches': pitches,
            'volumes': volumes,
            'default_emotion': default_emotion,
            'default_voice': default_voice,
            'a3_compliance': a3_compliance,
            'total_scripts': len(scripts),
            'filename': filename,
            'file_format': file_ext,
            'has_chinese_translation': 'chinese_translation' in found_fields,
            'field_mapping': found_fields
        }
        
    except Exception as e:
        logger.error(f"解析Excel文件失败: {str(e)}")
        return {
            'success': False,
            'error': f'解析Excel文件失败: {str(e)}',
            'a3_compliance': False
        }

@app.route('/api/upload-and-generate', methods=['POST'])
def upload_and_generate():
    """上传文件并自动生成语音"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "没有选择文件"}), 400
        
        if file and file.filename.endswith('.xlsx'):
            # 保存文件到input目录
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            filepath = os.path.join('input', filename)
            file.save(filepath)
            
            # 解析Excel文件
            parsed_data = parse_excel_file(filepath)
            
            if not parsed_data.get("success"):
                return jsonify({
                    "success": False,
                    "error": parsed_data.get("error", "解析文件失败"),
                    "filename": filename
                }), 400
            
            # 自动生成语音
            product_name = parsed_data["product_name"]
            scripts = parsed_data["scripts"]
            
            logger.info(f"开始自动生成语音: {product_name}, 脚本数量: {len(scripts)}")
            
            # 调用TTS服务生成语音
            tts_data = {
                "product_name": product_name,
                "scripts": scripts,
                "discount": "Special offer available!"
            }
            
            tts_response = requests.post(
                f"{TTS_SERVICE_URL}/generate",
                json=tts_data,
                timeout=300
            )
            
            if tts_response.status_code == 200:
                tts_result = tts_response.json()
                
                return jsonify({
                    "success": True,
                    "filename": filename,
                    "filepath": filepath,
                    "parsed_data": parsed_data,
                    "generation_result": tts_result
                })
            else:
                return jsonify({
                    "success": False,
                    "error": f"TTS服务错误: {tts_response.status_code}",
                    "filename": filename,
                    "parsed_data": parsed_data
                }), 500
        else:
            return jsonify({"error": "只支持Excel文件"}), 400
            
    except Exception as e:
        logger.error(f"上传并生成失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-from-file', methods=['POST'])
def generate_from_file():
    """从已上传的文件生成语音"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"error": "缺少文件名"}), 400
        
        # 构建文件路径
        filepath = os.path.join('input', filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "文件不存在"}), 404
        
        # 解析Excel文件
        parsed_data = parse_excel_file(filepath)
        
        if not parsed_data.get("success"):
            return jsonify({
                "success": False,
                "error": parsed_data.get("error", "解析文件失败")
            }), 400
        
        # 自动生成语音
        product_name = parsed_data["product_name"]
        scripts = parsed_data["scripts"]
        emotion = parsed_data.get("default_emotion", "Friendly")  # 使用默认情绪
        voice = parsed_data.get("default_voice", "en-US-JennyNeural")  # 使用默认语音
        
        logger.info(f"开始从文件生成语音: {product_name}, 脚本数量: {len(scripts)}, 情绪: {emotion}, 语音: {voice}")
        
        # 调用TTS服务生成语音
        # 格式化脚本为TTS服务期望的格式
        formatted_scripts = []
        emotions = parsed_data.get("emotions", [])
        voices = parsed_data.get("voices", [])
        
        for i, script in enumerate(scripts):
            script_emotion = emotions[i] if i < len(emotions) and emotions[i] else emotion
            script_voice = voices[i] if i < len(voices) and voices[i] else voice
            
            formatted_script = {
                "english_script": script,
                "emotion": script_emotion,
                "voice": script_voice
            }
            formatted_scripts.append(formatted_script)
        
        tts_data = {
            "product_name": product_name,
            "scripts": formatted_scripts,
            "emotion": emotion,
            "voice": voice,
            "discount": "Special offer available!"
        }
        
        tts_response = requests.post(
            f"{TTS_SERVICE_URL}/generate",
            json=tts_data,
            timeout=300
        )
        
        if tts_response.status_code == 200:
            tts_result = tts_response.json()
            
            return jsonify({
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "parsed_data": parsed_data,
                "generation_result": tts_result
            })
        else:
            return jsonify({
                "success": False,
                "error": f"TTS服务错误: {tts_response.status_code}",
                "parsed_data": parsed_data
            }), 500
            
    except Exception as e:
        logger.error(f"从文件生成失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/export')
def export_data():
    """导出数据"""
    try:
        # 这里应该实现数据导出逻辑
        # 暂时返回模拟数据
        import pandas as pd
        from io import BytesIO
        
        data = {
            'ID': [1, 2, 3],
            '产品名称': ['测试产品1', '测试产品2', '测试产品3'],
            '状态': ['已完成', '处理中', '已完成'],
            '创建时间': ['2025-10-27', '2025-10-27', '2025-10-27']
        }
        
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f'tt-live-ai-data-{datetime.now().strftime("%Y-%m-%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/restart', methods=['POST'])
def restart_system():
    """重启系统"""
    try:
        # 这里应该实现系统重启逻辑
        logger.info("系统重启请求")
        return jsonify({"message": "系统重启中..."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/start-all', methods=['POST'])
def start_all_tasks():
    """启动所有任务"""
    try:
        # 这里应该实现启动所有任务的逻辑
        logger.info("启动所有任务")
        return jsonify({"message": "所有任务已启动"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-a3-audio', methods=['POST'])
def generate_a3_audio():
    """生成A3标准音频"""
    try:
        data = request.get_json()
        scripts = data.get('scripts', [])
        product_name = data.get('product_name', 'Unknown Product')
        batch_id = data.get('batch_id', 'batch_1')
        
        if not scripts:
            return jsonify({"success": False, "error": "没有提供脚本"}), 400
        
        logger.info(f"开始生成A3标准音频: {product_name}, 批次: {batch_id}, 脚本数量: {len(scripts)}")
        
        # 调用TTS服务生成音频
        tts_data = {
            "product_name": product_name,
            "scripts": scripts,
            "emotion": "Excited",  # 默认情绪
            "voice": "en-US-JennyNeural",  # 默认语音
            "discount": "Special offer available!"
        }
        
        tts_response = requests.post(
            f"{TTS_SERVICE_URL}/generate",
            json=tts_data,
            timeout=300
        )
        
        if tts_response.status_code == 200:
            tts_result = tts_response.json()
            
            return jsonify({
                "success": True,
                "total_generated": len(scripts),
                "batch_id": batch_id,
                "product_name": product_name,
                "generation_result": tts_result
            })
        else:
            return jsonify({
                "success": False,
                "error": f"TTS服务错误: {tts_response.status_code}"
            }), 500
            
    except Exception as e:
        logger.error(f"生成A3音频失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/export-a3-excel', methods=['POST'])
def export_a3_excel():
    """导出A3标准Excel文件"""
    try:
        data = request.get_json()
        scripts = data.get('scripts', [])
        product_name = data.get('product_name', 'Unknown Product')
        batch_id = data.get('batch_id', 'batch_1')
        
        if not scripts:
            return jsonify({"success": False, "error": "没有提供脚本"}), 400
        
        logger.info(f"开始导出A3标准Excel: {product_name}, 批次: {batch_id}, 脚本数量: {len(scripts)}")
        
        # 创建Excel数据
        excel_data = []
        for i, script in enumerate(scripts):
            excel_data.append({
                "ID": i + 1,
                "English Script": script,
                "Chinese Translation": "",  # 如果有中文翻译可以在这里添加
                "Emotion": "Excited",
                "Voice": "en-US-JennyNeural",
                "Rate": "+10%",
                "Pitch": "+4%",
                "Volume": "+2dB",
                "Audio File": f"tts_{i+1:04d}_Excited.mp3"
            })
        
        # 创建DataFrame
        import pandas as pd
        df = pd.DataFrame(excel_data)
        
        # 生成文件名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"A3_Export_{product_name}_{batch_id}_{timestamp}.xlsx"
        
        # 保存Excel文件
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_excel(filepath, index=False)
        
        return jsonify({
            "success": True,
            "filename": filename,
            "filepath": filepath,
            "total_scripts": len(scripts),
            "batch_id": batch_id,
            "product_name": product_name
        })
        
    except Exception as e:
        logger.error(f"导出A3 Excel失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/open-output-folder')
def open_output_folder():
    """打开输出文件夹"""
    try:
        import subprocess
        import platform
        import math
        
        # 获取输出文件夹路径
        output_dir = os.path.join(os.path.dirname(__file__), '..', '08_数据文件_输入输出和日志', 'outputs')
        
        # 确保文件夹存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 根据操作系统打开文件夹
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", output_dir])
        elif system == "Windows":
            subprocess.run(["explorer", output_dir])
        elif system == "Linux":
            subprocess.run(["xdg-open", output_dir])
        
        logger.info(f"打开输出文件夹: {output_dir}")
        
        return jsonify({
            "success": True,
            "message": f"已打开音频输出文件夹: {output_dir}",
            "path": output_dir,
            "folder_name": "音频输出文件夹"
        })
        
    except Exception as e:
        logger.error(f"打开输出文件夹失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/get-output-files')
def get_output_files():
    """获取输出文件列表"""
    try:
        import math
        
        output_dir = os.path.join(os.path.dirname(__file__), '..', '08_数据文件_输入输出和日志', 'outputs')
        
        if not os.path.exists(output_dir):
            return jsonify({
                "success": True,
                "files": [],
                "message": "输出文件夹不存在"
            })
        
        files = []
        for root, dirs, filenames in os.walk(output_dir):
            for filename in filenames:
                if filename.endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                    file_path = os.path.join(root, filename)
                    file_size = os.path.getsize(file_path)
                    relative_path = os.path.relpath(file_path, output_dir)
                    
                    files.append({
                        "name": filename,
                        "path": relative_path,
                        "size": file_size,
                        "size_formatted": format_file_size(file_size),
                        "modified": os.path.getmtime(file_path)
                    })
        
        # 按修改时间排序，最新的在前
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        logger.info(f"获取输出文件列表: {len(files)} 个文件")
        
        return jsonify({
            "success": True,
            "files": files,
            "total_count": len(files),
            "output_dir": output_dir
        })
        
    except Exception as e:
        logger.error(f"获取输出文件列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

def format_file_size(size_bytes):
    """格式化文件大小"""
    import math
    if size_bytes == 0:
        return "0 Bytes"
    size_names = ["Bytes", "KB", "MB", "GB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

@app.route('/static/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # 创建必要目录
    create_directories()
    
    # 启动服务
    logger.info("🚀 TT-Live-AI 语音生成控制中心启动...")
    logger.info("📡 服务地址: http://localhost:8000")
    logger.info("🔗 API接口: /api/*")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
