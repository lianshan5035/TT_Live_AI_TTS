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
    "Calm": {"rate": "-6%", "pitch": "-2%", "volume": "0dB"},
    "Friendly": {"rate": "+2%", "pitch": "+2%", "volume": "0dB"},
    "Confident": {"rate": "+4%", "pitch": "+1%", "volume": "+1dB"},
    "Playful": {"rate": "+6%", "pitch": "+3%", "volume": "+1dB"},
    "Excited": {"rate": "+10%", "pitch": "+4%", "volume": "+2dB"},
    "Urgent": {"rate": "+12%", "pitch": "+3%", "volume": "+2dB"}
}

# 默认语音模型
DEFAULT_VOICE = "en-US-JennyNeural"

# 最大并发数
MAX_CONCURRENT = 5

def create_directories():
    """创建必要的目录结构"""
    dirs = ['outputs', 'logs', 'input']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)

def get_emotion_params(emotion):
    """获取情绪对应的语音参数"""
    return EMOTION_PARAMS.get(emotion, EMOTION_PARAMS["Friendly"])

def add_random_variation(params):
    """添加 ±2% 随机扰动"""
    import random
    
    # 对 rate 和 pitch 添加随机扰动
    if params["rate"].startswith("+"):
        base_rate = int(params["rate"][1:-1])
        variation = random.randint(-2, 2)
        new_rate = base_rate + variation
        params["rate"] = f"+{new_rate}%" if new_rate >= 0 else f"{new_rate}%"
    
    if params["pitch"].startswith("+"):
        base_pitch = int(params["pitch"][1:-1])
        variation = random.randint(-2, 2)
        new_pitch = base_pitch + variation
        params["pitch"] = f"+{new_pitch}%" if new_pitch >= 0 else f"{new_pitch}%"
    
    return params

async def generate_single_audio(text, voice, emotion, output_path):
    """生成单个音频文件"""
    try:
        # 获取情绪参数
        params = get_emotion_params(emotion)
        params = add_random_variation(params)
        
        # 构建 EdgeTTS 命令参数
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=params["rate"],
            pitch=params["pitch"],
            volume=params["volume"]
        )
        
        # 生成音频文件
        await communicate.save(output_path)
        
        return {
            "success": True,
            "file_path": output_path,
            "params": params
        }
    except Exception as e:
        logger.error(f"生成音频失败: {text[:50]}... - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "file_path": output_path
        }

async def process_scripts_batch(scripts, product_name, discount, emotion="Friendly", voice=DEFAULT_VOICE):
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
            else:
                text = script.get("english_script", str(script))
                emotion = script.get("emotion", emotion)
                voice = script.get("voice", voice)
            
            # 生成音频文件名
            audio_filename = f"tts_{index+1:04d}_{emotion}.mp3"
            audio_path = f"{product_dir}/{audio_filename}"
            
            # 生成音频
            result = await generate_single_audio(text, voice, emotion, audio_path)
            result["index"] = index + 1
            result["emotion"] = emotion
            result["text"] = text
            
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
            audio_filename = f"tts_{i+1:04d}_{emotion}.mp3"
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
