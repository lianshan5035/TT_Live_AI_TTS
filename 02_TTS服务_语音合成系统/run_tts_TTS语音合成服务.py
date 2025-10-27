#!/usr/bin/env python3
"""
TT-Live-AI A3-TK 口播生成系统 - Flask 主服务
支持批量语音生成、多产品并行处理、自动参数映射
"""
import os
import json
import asyncio
import edge_tts
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tts_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 语音参数映射表（TT-Live-AI 标准）
EMOTION_PARAMS = {
    "Excited": {"rate": "+15%", "pitch": "+12Hz", "volume": "+15%"},
    "Confident": {"rate": "+8%", "pitch": "+5Hz", "volume": "+8%"},
    "Empathetic": {"rate": "-12%", "pitch": "-8Hz", "volume": "-10%"},
    "Calm": {"rate": "-10%", "pitch": "-3Hz", "volume": "+0%"},
    "Playful": {"rate": "+18%", "pitch": "+15Hz", "volume": "+5%"},
    "Urgent": {"rate": "+22%", "pitch": "+8Hz", "volume": "+18%"},
    "Authoritative": {"rate": "+5%", "pitch": "+3Hz", "volume": "+10%"},
    "Friendly": {"rate": "+12%", "pitch": "+8Hz", "volume": "+5%"},
    "Inspirational": {"rate": "+10%", "pitch": "+10Hz", "volume": "+12%"},
    "Serious": {"rate": "+0%", "pitch": "+0Hz", "volume": "+5%"},
    "Mysterious": {"rate": "-8%", "pitch": "+5Hz", "volume": "-5%"},
    "Grateful": {"rate": "+5%", "pitch": "+8Hz", "volume": "+8%"}
}

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

# 默认语音模型
DEFAULT_VOICE = "en-US-JennyNeural"

def get_voice_for_emotion(emotion, script_index=0):
    """根据情绪和脚本索引动态选择语音模型"""
    if emotion in EMOTION_VOICE_MAPPING:
        voices = EMOTION_VOICE_MAPPING[emotion]
        # 根据脚本索引选择语音模型，实现语音多样性
        voice_index = script_index % len(voices)
        return voices[voice_index]
    return DEFAULT_VOICE

def get_voice_info(voice_model):
    """获取语音模型信息"""
    if voice_model in VOICE_MODELS:
        return VOICE_MODELS[voice_model]
    return {"gender": "未知", "style": "未知", "name": "未知", "description": "未知"}

def list_available_voices():
    """列出所有可用的语音模型"""
    return list(VOICE_MODELS.keys())

def create_directories():
    dirs = ['outputs', 'logs', 'input']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)

def get_emotion_params(emotion):
    """获取情绪对应的语音参数"""
    return EMOTION_PARAMS.get(emotion, EMOTION_PARAMS["Friendly"])

def add_random_variation(params):
    """添加 ±2% 随机扰动"""
    import random
    
    # 对 rate 添加随机扰动
    if params["rate"].startswith("+"):
        base_rate = int(params["rate"][1:-1])
        variation = random.randint(-2, 2)
        new_rate = base_rate + variation
        params["rate"] = f"+{new_rate}%" if new_rate >= 0 else f"{new_rate}%"
    elif params["rate"].startswith("-"):
        base_rate = int(params["rate"][:-1])
        variation = random.randint(-2, 2)
        new_rate = base_rate + variation
        params["rate"] = f"{new_rate}%" if new_rate <= 0 else f"+{new_rate}%"
    else:
        # 处理没有符号的情况
        base_rate = int(params["rate"][:-1])
        variation = random.randint(-2, 2)
        new_rate = base_rate + variation
        params["rate"] = f"+{new_rate}%" if new_rate >= 0 else f"{new_rate}%"
    
    # 对 pitch 添加随机扰动 (Hz格式)
    if params["pitch"].startswith("+"):
        base_pitch = int(params["pitch"][1:-2])  # 去掉+和Hz
        variation = random.randint(-2, 2)
        new_pitch = base_pitch + variation
        params["pitch"] = f"+{new_pitch}Hz" if new_pitch >= 0 else f"{new_pitch}Hz"
    elif params["pitch"].startswith("-"):
        base_pitch = int(params["pitch"][:-2])  # 去掉-和Hz
        variation = random.randint(-2, 2)
        new_pitch = base_pitch + variation
        params["pitch"] = f"{new_pitch}Hz" if new_pitch >= 0 else f"{new_pitch}Hz"
    
    return params

async def generate_single_audio(text, voice, emotion, output_path):
    """生成单个音频文件"""
    try:
        logger.info(f"开始生成音频: {text[:30]}...")
        logger.info(f"输出路径: {output_path}")
        
        # 获取情绪参数
        params = get_emotion_params(emotion)
        logger.info(f"基础参数: {params}")
        params = add_random_variation(params)
        logger.info(f"最终参数: {params}")
        
        # 构建 EdgeTTS 命令参数
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=params["rate"],
            pitch=params["pitch"],
            volume=params["volume"]
        )
        
        logger.info(f"EdgeTTS对象创建成功，开始保存到: {output_path}")
        
        # 生成音频文件
        await communicate.save(output_path)
        
        # 检查文件是否真的生成了
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"音频文件生成成功: {output_path}, 大小: {file_size} bytes")
        else:
            logger.error(f"音频文件未生成: {output_path}")
            return {
                "success": False,
                "error": "文件未生成",
                "file_path": output_path
            }
        
        return {
            "success": True,
            "file_path": output_path,
            "params": params
        }
    except Exception as e:
        logger.error(f"生成音频失败: {text[:50]}... - {str(e)}")
        logger.error(f"详细错误信息: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "file_path": output_path
        }

async def process_scripts_batch(scripts, product_name, discount, emotion="Friendly", voice=DEFAULT_VOICE, emotions=None, voices=None, rates=None, pitches=None, volumes=None):
    """批量处理脚本"""
    # 创建产品输出目录
    product_dir = f"outputs/{product_name}"
    os.makedirs(product_dir, exist_ok=True)
    
    results = []
    successful = 0
    failed = 0
    start_time = datetime.now()
    
    # 创建信号量控制并发数
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    async def process_single_script(script, index):
        async with semaphore:
            # 如果script是字符串，直接使用；如果是字典，提取text
            if isinstance(script, str):
                text = script
                # 使用GPTs提供的参数（如果存在）
                script_emotion = emotions[index] if emotions and index < len(emotions) and emotions[index] else emotion
                script_voice = voices[index] if voices and index < len(voices) and voices[index] else voice
            else:
                text = script.get("english_script", str(script))
                script_emotion = script.get("emotion", emotions[index] if emotions and index < len(emotions) and emotions[index] else emotion)
                script_voice = script.get("voice", voices[index] if voices and index < len(voices) and voices[index] else voice)
            
            # 如果没有指定语音，使用动态语音选择
            if not script_voice or script_voice == DEFAULT_VOICE:
                script_voice = get_voice_for_emotion(script_emotion, index)
            
            # 生成音频文件名（包含语音模型信息）
            voice_name = get_voice_info(script_voice)["name"]
            audio_filename = f"tts_{index+1:04d}_{script_emotion}_{voice_name}.mp3"
            audio_path = f"{product_dir}/{audio_filename}"
            
            # 生成音频
            result = await generate_single_audio(text, script_voice, script_emotion, audio_path)
            result["index"] = index + 1
            result["emotion"] = script_emotion
            result["voice"] = script_voice
            result["voice_info"] = get_voice_info(script_voice)
            result["text"] = text
            
            # 添加GPTs参数信息
            if rates and index < len(rates) and rates[index]:
                result["rate"] = rates[index]
            if pitches and index < len(pitches) and pitches[index]:
                result["pitch"] = pitches[index]
            if volumes and index < len(volumes) and volumes[index]:
                result["volume"] = volumes[index]
            
            return result
    
    # 并发处理所有脚本
    tasks = [process_single_script(script, i) for i, script in enumerate(scripts)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 统计结果
    for result in results:
        if isinstance(result, dict) and result.get("success"):
            successful += 1
        else:
            failed += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    return {
        "results": results,
        "successful": successful,
        "failed": failed,
        "duration_seconds": duration
    }

def generate_excel_output(scripts, product_name, discount, results):
    """生成 Excel 输出文件"""
    # 创建产品输出目录
    product_dir = f"outputs/{product_name}"
    os.makedirs(product_dir, exist_ok=True)
    
    # 准备 Excel 数据
    excel_data = []
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    for i, (script, result) in enumerate(zip(scripts, results)):
        if isinstance(result, dict) and result.get("success"):
            # 成功生成音频
            emotion = "Friendly"  # 默认情绪
            if isinstance(script, str):
                english_script = script
            else:
                english_script = script.get("english_script", str(script))
                emotion = script.get("emotion", "Friendly")
            
            audio_filename = f"tts_{i+1:04d}_{emotion}.mp3"
            audio_path = f"outputs/{product_name}/{audio_filename}"
            
            excel_data.append({
                "id": i + 1,
                "english_script": english_script,
                "chinese_translation": script.get("chinese_translation", "") if isinstance(script, dict) else "",
                "emotion": emotion,
                "voice": script.get("voice", DEFAULT_VOICE) if isinstance(script, dict) else DEFAULT_VOICE,
                "rate": result.get("params", {}).get("rate", "+2%"),
                "pitch": result.get("params", {}).get("pitch", "+2%"),
                "volume": result.get("params", {}).get("volume", "0dB"),
                "audio_file_path": audio_path
            })
        else:
            # 生成失败
            if isinstance(script, str):
                english_script = script
            else:
                english_script = script.get("english_script", str(script))
            
            excel_data.append({
                "id": i + 1,
                "english_script": english_script,
                "chinese_translation": script.get("chinese_translation", "") if isinstance(script, dict) else "",
                "emotion": script.get("emotion", "Friendly") if isinstance(script, dict) else "Friendly",
                "voice": script.get("voice", DEFAULT_VOICE) if isinstance(script, dict) else DEFAULT_VOICE,
                "rate": "ERROR",
                "pitch": "ERROR",
                "volume": "ERROR",
                "audio_file_path": "ERROR"
            })
    
    # 创建 DataFrame
    df = pd.DataFrame(excel_data)
    
    # 生成 Excel 文件名
    excel_filename = f"Lior_{date_str}_{product_name}_Batch1_Voice.xlsx"
    excel_path = f"{product_dir}/{excel_filename}"
    
    # 保存 Excel 文件
    df.to_excel(excel_path, index=False)
    
    return excel_path

@app.route('/generate', methods=['POST'])
def generate_voice_content():
    """生成语音内容的主接口"""
    try:
        # 获取请求数据
        data = request.get_json()
        product_name = data.get('product_name', 'Unknown_Product')
        discount = data.get('discount', 'Special offer available!')
        scripts = data.get('scripts', [])
        
        if not scripts:
            return jsonify({"error": "No scripts provided"}), 400
        
        logger.info(f"开始处理产品: {product_name}, 脚本数量: {len(scripts)}")
        
        # 异步处理脚本
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            emotion = data.get('emotion', 'Friendly')
            voice = data.get('voice', DEFAULT_VOICE)
            result = loop.run_until_complete(process_scripts_batch(scripts, product_name, discount, emotion, voice))
        finally:
            loop.close()
        
        # 生成 Excel 输出
        excel_path = generate_excel_output(scripts, product_name, discount, result["results"])
        
        # 生成样本音频列表
        sample_audios = []
        emotion = data.get('emotion', 'Friendly')  # 从请求中获取情绪
        for i, script in enumerate(scripts[:3]):  # 取前3个作为样本
            # 如果script是字典，使用其中的emotion，否则使用默认emotion
            script_emotion = emotion
            if isinstance(script, dict) and 'emotion' in script:
                script_emotion = script['emotion']
            audio_filename = f"tts_{i+1:04d}_{script_emotion}.mp3"
            sample_audios.append(f"outputs/{product_name}/{audio_filename}")
        
        # 返回结果
        response = {
            "product_name": product_name,
            "total_scripts": len(scripts),
            "output_excel": excel_path,
            "audio_directory": f"outputs/{product_name}/",
            "sample_audios": sample_audios,
            "summary": {
                "successful": result["successful"],
                "failed": result["failed"],
                "duration_seconds": result["duration_seconds"]
            }
        }
        
        logger.info(f"处理完成: {product_name}, 成功: {result['successful']}, 失败: {result['failed']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"处理请求失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "TT-Live-AI A3-TK Voice Generation System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/voices', methods=['GET'])
def get_voices():
    """获取所有可用的语音模型"""
    try:
        return jsonify({
            "success": True,
            "voices": VOICE_MODELS,
            "emotion_mapping": EMOTION_VOICE_MAPPING,
            "default_voice": DEFAULT_VOICE,
            "total_voices": len(VOICE_MODELS)
        })
    except Exception as e:
        logger.error(f"获取语音模型失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/voices/<emotion>', methods=['GET'])
def get_voices_for_emotion(emotion):
    """获取指定情绪的推荐语音模型"""
    try:
        if emotion in EMOTION_VOICE_MAPPING:
            voices = EMOTION_VOICE_MAPPING[emotion]
            voice_details = []
            for voice in voices:
                voice_info = get_voice_info(voice)
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

@app.route('/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    return jsonify({
        "max_concurrent": MAX_CONCURRENT,
        "supported_emotions": list(EMOTION_PARAMS.keys()),
        "default_voice": DEFAULT_VOICE,
        "output_directory": "outputs/",
        "log_directory": "logs/"
    })

if __name__ == '__main__':
    # 创建必要目录
    create_directories()
    
    # 启动服务
    logger.info("🚀 TT-Live-AI A3-TK 语音生成服务启动...")
    logger.info("📡 服务地址: http://localhost:5000")
    logger.info("🔗 生成接口: POST /generate")
    logger.info("❤️ 健康检查: GET /health")
    logger.info("📊 系统状态: GET /status")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
