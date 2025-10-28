#!/usr/bin/env python3
"""
生成Lior Excel文件的完整800条音频
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
EXCEL_FILE_PATH = "./08_数据文件_输入输出和日志/inputs/Lior2025-10-23淡化美白美容霜腋下和大腿黑斑霜_800合并模板.xlsx"
OUTPUT_DIR = "outputs/Lior2025-10-23淡化美白美容霜腋下和大腿黑斑霜_800合并模板/"

def read_excel_file():
    """读取Excel文件"""
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        logger.info(f"✅ 成功读取Excel文件: {len(df)} 条记录")
        return df
    except Exception as e:
        logger.error(f"❌ 读取Excel文件失败: {e}")
        return None

def prepare_scripts_data(df):
    """准备脚本数据"""
    scripts = []
    for index, row in df.iterrows():
        script = {
            "english_script": row["english_script"],
            "emotion": "Friendly",  # 使用Friendly情绪
            "voice": "en-US-JennyNeural"  # 使用珍妮语音
        }
        scripts.append(script)
    
    logger.info(f"✅ 准备了 {len(scripts)} 条脚本数据")
    return scripts

def generate_audio_batch(scripts, batch_size=50):
    """批量生成音频"""
    total_scripts = len(scripts)
    successful = 0
    failed = 0
    
    logger.info(f"🚀 开始生成 {total_scripts} 条音频，批量大小: {batch_size}")
    
    for i in range(0, total_scripts, batch_size):
        batch_scripts = scripts[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total_scripts + batch_size - 1) // batch_size
        
        logger.info(f"📦 处理第 {batch_num}/{total_batches} 批，包含 {len(batch_scripts)} 条脚本")
        
        # 准备请求数据
        request_data = {
            "product_name": f"Lior2025-10-23淡化美白美容霜腋下和大腿黑斑霜_800合并模板_Batch{batch_num}",
            "scripts": batch_scripts,
            "emotion": "Friendly",
            "voice": "en-US-JennyNeural"
        }
        
        try:
            # 发送请求
            logger.info(f"📡 发送第 {batch_num} 批请求到TTS服务...")
            response = requests.post(f"{TTS_SERVICE_URL}/generate", json=request_data, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                batch_successful = result["summary"]["successful"]
                batch_failed = result["summary"]["failed"]
                
                successful += batch_successful
                failed += batch_failed
                
                logger.info(f"✅ 第 {batch_num} 批完成: 成功 {batch_successful}, 失败 {batch_failed}")
                logger.info(f"📁 音频目录: {result['audio_directory']}")
                
                # 显示进度
                progress = ((i + len(batch_scripts)) / total_scripts) * 100
                logger.info(f"📊 总进度: {progress:.1f}% ({successful + failed}/{total_scripts})")
                
            else:
                logger.error(f"❌ 第 {batch_num} 批请求失败: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                failed += len(batch_scripts)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 第 {batch_num} 批请求异常: {e}")
            failed += len(batch_scripts)
        
        # 批次间暂停，避免过载
        if i + batch_size < total_scripts:
            logger.info("⏳ 批次间暂停 2 秒...")
            time.sleep(2)
    
    return successful, failed

def monitor_progress():
    """监控生成进度"""
    if not os.path.exists(OUTPUT_DIR):
        logger.info("📁 输出目录不存在，等待创建...")
        return
    
    mp3_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.mp3')]
    logger.info(f"📊 当前已生成音频文件: {len(mp3_files)} 个")
    
    if mp3_files:
        latest_file = max(mp3_files, key=lambda x: os.path.getctime(os.path.join(OUTPUT_DIR, x)))
        file_size = os.path.getsize(os.path.join(OUTPUT_DIR, latest_file))
        logger.info(f"📁 最新文件: {latest_file} ({file_size} bytes)")

def main():
    """主函数"""
    logger.info("🎵 开始生成Lior完整800条音频")
    logger.info("=" * 60)
    
    # 检查TTS服务状态
    try:
        response = requests.get(f"{TTS_SERVICE_URL}/health", timeout=10)
        if response.status_code == 200:
            logger.info("✅ TTS服务状态正常")
        else:
            logger.error("❌ TTS服务状态异常")
            return
    except Exception as e:
        logger.error(f"❌ 无法连接到TTS服务: {e}")
        return
    
    # 读取Excel文件
    df = read_excel_file()
    if df is None:
        return
    
    # 准备脚本数据
    scripts = prepare_scripts_data(df)
    if not scripts:
        logger.error("❌ 没有可用的脚本数据")
        return
    
    # 开始生成音频
    start_time = time.time()
    successful, failed = generate_audio_batch(scripts, batch_size=50)
    end_time = time.time()
    
    # 最终统计
    duration = end_time - start_time
    logger.info("=" * 60)
    logger.info("🎉 音频生成完成!")
    logger.info(f"✅ 成功生成: {successful} 个音频文件")
    logger.info(f"❌ 生成失败: {failed} 个")
    logger.info(f"⏱️  总耗时: {duration:.2f} 秒")
    logger.info(f"📁 输出目录: {OUTPUT_DIR}")
    
    # 监控最终进度
    monitor_progress()

if __name__ == "__main__":
    main()
