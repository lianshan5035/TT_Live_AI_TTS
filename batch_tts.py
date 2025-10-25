#!/usr/bin/env python3
"""
TT-Live-AI A3-TK 口播生成系统 - 批量 Excel 处理模块
支持从 Excel 文件批量生成语音，多产品并行处理
"""
import os
import pandas as pd
import asyncio
import edge_tts
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/batch_tts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 语音参数映射表
EMOTION_PARAMS = {
    "Calm": {"rate": "-6%", "pitch": "-2%", "volume": "0dB"},
    "Friendly": {"rate": "+2%", "pitch": "+2%", "volume": "0dB"},
    "Confident": {"rate": "+4%", "pitch": "+1%", "volume": "+1dB"},
    "Playful": {"rate": "+6%", "pitch": "+3%", "volume": "+1dB"},
    "Excited": {"rate": "+10%", "pitch": "+4%", "volume": "+2dB"},
    "Urgent": {"rate": "+12%", "pitch": "+3%", "volume": "+2dB"}
}

DEFAULT_VOICE = "en-US-JennyNeural"
MAX_CONCURRENT = 5

def get_emotion_params(emotion):
    """获取情绪对应的语音参数"""
    return EMOTION_PARAMS.get(emotion, EMOTION_PARAMS["Friendly"])

def add_random_variation(params):
    """添加 ±2% 随机扰动"""
    import random
    
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
        params = get_emotion_params(emotion)
        params = add_random_variation(params)
        
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=params["rate"],
            pitch=params["pitch"],
            volume=params["volume"]
        )
        
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

async def process_excel_file(excel_path, output_dir="outputs"):
    """处理 Excel 文件，生成语音"""
    try:
        # 读取 Excel 文件
        df = pd.read_excel(excel_path)
        logger.info(f"读取 Excel 文件: {excel_path}, 行数: {len(df)}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理每一行
        results = []
        successful = 0
        failed = 0
        start_time = datetime.now()
        
        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def process_row(row):
            async with semaphore:
                text = row.get('english_script', '')
                emotion = row.get('emotion', 'Friendly')
                voice = row.get('voice', DEFAULT_VOICE)
                
                # 生成音频文件名
                index = row.get('id', 0)
                audio_filename = f"tts_{index:04d}_{emotion}.mp3"
                audio_path = os.path.join(output_dir, audio_filename)
                
                # 生成音频
                result = await generate_single_audio(text, voice, emotion, audio_path)
                result["row_id"] = index
                result["emotion"] = emotion
                result["text"] = text
                
                return result
        
        # 并发处理所有行
        tasks = [process_row(row) for _, row in df.iterrows()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                successful += 1
            else:
                failed += 1
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 生成结果报告
        report = {
            "excel_file": excel_path,
            "total_rows": len(df),
            "successful": successful,
            "failed": failed,
            "duration_seconds": duration,
            "output_directory": output_dir
        }
        
        # 保存报告
        report_path = os.path.join(output_dir, "batch_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"批量处理完成: 成功 {successful}, 失败 {failed}, 耗时 {duration:.2f}秒")
        return report
        
    except Exception as e:
        logger.error(f"处理 Excel 文件失败: {str(e)}")
        return {"error": str(e)}

def process_multiple_excel_files(excel_files, output_base_dir="outputs"):
    """处理多个 Excel 文件"""
    results = []
    
    for excel_file in excel_files:
        if not os.path.exists(excel_file):
            logger.error(f"Excel 文件不存在: {excel_file}")
            continue
        
        # 为每个文件创建独立的输出目录
        file_name = os.path.splitext(os.path.basename(excel_file))[0]
        output_dir = os.path.join(output_base_dir, file_name)
        
        # 异步处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(process_excel_file(excel_file, output_dir))
            results.append(result)
        finally:
            loop.close()
    
    return results

def create_sample_excel(output_path="input/sample_scripts.xlsx"):
    """创建示例 Excel 文件"""
    sample_data = [
        {
            "id": 1,
            "english_script": "Hey bestie, this patch really works!",
            "chinese_translation": "闺蜜，这个贴片真的有用！",
            "emotion": "Excited",
            "voice": "en-US-JennyNeural"
        },
        {
            "id": 2,
            "english_script": "Gentle and fast, this patch is amazing.",
            "chinese_translation": "温和快速，这个贴片太棒了。",
            "emotion": "Confident",
            "voice": "en-US-JennyNeural"
        },
        {
            "id": 3,
            "english_script": "Don't miss out on this incredible deal!",
            "chinese_translation": "不要错过这个令人难以置信的优惠！",
            "emotion": "Urgent",
            "voice": "en-US-JennyNeural"
        }
    ]
    
    df = pd.DataFrame(sample_data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    logger.info(f"创建示例 Excel 文件: {output_path}")
    return output_path

if __name__ == '__main__':
    # 创建必要目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('input', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    # 创建示例 Excel 文件
    sample_file = create_sample_excel()
    
    # 处理示例文件
    logger.info("开始处理示例 Excel 文件...")
    result = process_multiple_excel_files([sample_file])
    
    print("\n" + "="*50)
    print("批量处理结果:")
    for i, r in enumerate(result):
        print(f"文件 {i+1}: {r}")
    print("="*50)
