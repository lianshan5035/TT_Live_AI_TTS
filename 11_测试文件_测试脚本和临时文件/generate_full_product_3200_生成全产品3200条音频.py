#!/usr/bin/env python3
"""
生成全产品_合并版_3200.xlsx文件的完整3200条音频
包含增强的元数据参数、节奏变化和真人直播高级感
"""
import requests
import pandas as pd
import time
import logging
import os
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TTS_SERVICE_URL = "http://127.0.0.1:5001"
EXCEL_FILE_PATH = "./inputs/全产品_合并版_3200.xlsx"
OUTPUT_BASE_DIR = "outputs/"

def get_product_name_from_excel(excel_path):
    """从Excel文件名中提取产品名称"""
    base_name = os.path.basename(excel_path)
    return base_name.split('.xlsx')[0]

def generate_full_audio_batch(excel_path):
    """
    上传Excel文件到TTS服务并触发批量音频生成。
    """
    logger.info(f"🎵 开始生成全产品3200条音频")
    logger.info(f"============================================================")

    # 1. 检查TTS服务健康状态
    try:
        health_response = requests.get(f"{TTS_SERVICE_URL}/health")
        if health_response.status_code == 200 and health_response.json().get("status") == "healthy":
            logger.info("✅ TTS服务状态正常")
        else:
            logger.error(f"❌ TTS服务不健康或无法访问: {health_response.status_code} - {health_response.text}")
            return
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 无法连接到TTS服务: {e}")
        return

    # 2. 读取Excel文件
    try:
        df = pd.read_excel(excel_path)
        logger.info(f"✅ 成功读取Excel文件: {len(df)} 条记录")
    except Exception as e:
        logger.error(f"❌ 读取Excel文件失败: {e}")
        return

    # 3. 准备脚本数据
    scripts_data = []
    product_name = get_product_name_from_excel(excel_path)
    
    for index, row in df.iterrows():
        # 使用"英文"字段作为口播正文
        english_script = row["英文"]
        if pd.isna(english_script) or not english_script.strip():
            logger.warning(f"第{index+1}行英文字段为空，跳过")
            continue
            
        # 获取语音和情绪信息
        voice = row.get("Voice", "en-US-JennyNeural")
        emotion = row.get("情绪类型", "Friendly")
        
        # 如果Voice字段为空，使用默认语音
        if pd.isna(voice) or not voice.strip():
            voice = "en-US-JennyNeural"
        
        scripts_data.append({
            "english_script": english_script.strip(),
            "emotion": emotion,
            "voice": voice
        })
    
    logger.info(f"✅ 准备了 {len(scripts_data)} 条脚本数据")

    # 4. 发送请求到TTS服务
    payload = {
        "product_name": product_name,
        "scripts": scripts_data,
        "default_emotion": "Friendly",
        "default_voice": "en-US-JennyNeural"
    }

    logger.info(f"🚀 开始生成 {len(scripts_data)} 条音频")
    
    # 模拟分批发送，实际Flask后端会处理并发
    batch_size = 50  # 每次发送50条，避免单个请求过大
    total_batches = (len(scripts_data) + batch_size - 1) // batch_size

    for i in range(total_batches):
        start_index = i * batch_size
        end_index = min((i + 1) * batch_size, len(scripts_data))
        current_batch_scripts = scripts_data[start_index:end_index]

        batch_payload = {
            "product_name": product_name,
            "scripts": current_batch_scripts,
            "default_emotion": "Friendly",
            "default_voice": "en-US-JennyNeural"
        }

        logger.info(f"📦 处理第 {i+1}/{total_batches} 批，包含 {len(current_batch_scripts)} 条脚本")
        try:
            logger.info(f"📡 发送第 {i+1} 批请求到TTS服务...")
            response = requests.post(f"{TTS_SERVICE_URL}/generate", json=batch_payload, timeout=300)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ 第 {i+1} 批生成成功: 成功 {result.get('summary', {}).get('successful', 0)} 条, 失败 {result.get('summary', {}).get('failed', 0)} 条")
                if result.get("sample_audios"):
                    logger.info(f"  示例音频: {result['sample_audios'][0]}")
            else:
                logger.error(f"❌ 第 {i+1} 批请求失败: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 第 {i+1} 批请求异常: {e}")
        time.sleep(1)  # 每批之间稍作停顿

    logger.info(f"============================================================")
    logger.info(f"🎉 全产品3200条音频生成任务已提交！请监控输出目录: {OUTPUT_BASE_DIR}{product_name}/")

if __name__ == "__main__":
    generate_full_audio_batch(EXCEL_FILE_PATH)
