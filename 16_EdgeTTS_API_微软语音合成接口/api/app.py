#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS Web API - FastAPI 应用
支持 GPTs 插件调用的语音合成服务
"""

import os
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts
import pandas as pd

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="EdgeTTS API",
    description="基于 EdgeTTS 的语音合成 API，支持 GPTs 插件调用",
    version="1.0.0"
)

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要目录
os.makedirs('outputs', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('temp', exist_ok=True)

# 语音参数映射表（基于你现有的配置）
EMOTION_PARAMS = {
    "Calm": {"rate": "-6%", "pitch": "-2Hz", "volume": "+0%"},
    "Friendly": {"rate": "+2%", "pitch": "+2Hz", "volume": "+0%"},
    "Confident": {"rate": "+4%", "pitch": "+1Hz", "volume": "+1%"},
    "Playful": {"rate": "+6%", "pitch": "+3Hz", "volume": "+1%"},
    "Excited": {"rate": "+10%", "pitch": "+4Hz", "volume": "+2%"},
    "Urgent": {"rate": "+12%", "pitch": "+3Hz", "volume": "+2%"}
}

# 默认语音模型
DEFAULT_VOICE = "en-US-JennyNeural"

# 请求模型
class TTSRequest(BaseModel):
    text: str
    voice: str = DEFAULT_VOICE
    emotion: str = "Friendly"
    format: str = "mp3"

class BatchTTSRequest(BaseModel):
    texts: List[str]
    voice: str = DEFAULT_VOICE
    emotion: str = "Friendly"
    format: str = "mp3"

def get_emotion_params(emotion: str) -> dict:
    """获取情绪对应的语音参数"""
    return EMOTION_PARAMS.get(emotion, EMOTION_PARAMS["Friendly"])

def add_random_variation(params: dict) -> dict:
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
        params["rate"] = f"{new_rate}%" if new_rate >= 0 else f"{new_rate}%"
    
    # 对 pitch 添加随机扰动
    if params["pitch"].startswith("+"):
        base_pitch = int(params["pitch"][1:-2])
        variation = random.randint(-2, 2)
        new_pitch = base_pitch + variation
        params["pitch"] = f"+{new_pitch}Hz" if new_pitch >= 0 else f"{new_pitch}Hz"
    elif params["pitch"].startswith("-"):
        base_pitch = int(params["pitch"][:-2])
        variation = random.randint(-2, 2)
        new_pitch = base_pitch + variation
        params["pitch"] = f"{new_pitch}Hz" if new_pitch >= 0 else f"{new_pitch}Hz"
    
    return params

async def generate_single_audio(text: str, voice: str, emotion: str, output_path: str) -> dict:
    """生成单个音频文件"""
    try:
        logger.info(f"开始生成音频: {text[:30]}...")
        
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
        
        # 检查文件是否生成成功
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"音频文件生成成功: {output_path}, 大小: {file_size} bytes")
            return {
                "success": True,
                "file_path": output_path,
                "params": params,
                "file_size": file_size
            }
        else:
            logger.error(f"音频文件未生成: {output_path}")
            return {
                "success": False,
                "error": "文件未生成",
                "file_path": output_path
            }
        
    except Exception as e:
        logger.error(f"生成音频失败: {text[:50]}... - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "file_path": output_path
        }

@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "EdgeTTS API",
        "version": "1.0.0",
        "description": "基于 EdgeTTS 的语音合成 API，支持 GPTs 插件调用",
        "endpoints": {
            "generate": "POST /generate - 生成单个语音",
            "batch": "POST /batch - 批量生成语音",
            "health": "GET /health - 健康检查",
            "voices": "GET /voices - 获取支持的语音列表"
        }
    }

@app.post("/generate")
async def generate_audio(request: TTSRequest):
    """生成单个语音文件"""
    try:
        # 生成唯一文件名
        file_id = f"{uuid.uuid4()}.{request.format}"
        output_path = f"temp/{file_id}"
        
        # 生成音频
        result = await generate_single_audio(
            request.text, 
            request.voice, 
            request.emotion, 
            output_path
        )
        
        if result["success"]:
            # 返回音频文件
            return FileResponse(
                output_path,
                media_type="audio/mpeg",
                filename=file_id,
                headers={
                    "X-Audio-Params": str(result["params"]),
                    "X-File-Size": str(result["file_size"])
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"生成语音失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch")
async def generate_batch_audio(request: BatchTTSRequest):
    """批量生成语音文件"""
    try:
        results = []
        successful = 0
        failed = 0
        
        # 创建批次目录
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        batch_dir = f"outputs/{batch_id}"
        os.makedirs(batch_dir, exist_ok=True)
        
        # 并发处理所有文本
        semaphore = asyncio.Semaphore(5)  # 限制并发数
        
        async def process_single_text(text: str, index: int):
            async with semaphore:
                file_id = f"tts_{index+1:04d}_{request.emotion}.{request.format}"
                output_path = f"{batch_dir}/{file_id}"
                
                result = await generate_single_audio(
                    text, 
                    request.voice, 
                    request.emotion, 
                    output_path
                )
                result["index"] = index + 1
                result["text"] = text
                return result
        
        # 执行批量处理
        tasks = [process_single_text(text, i) for i, text in enumerate(request.texts)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                successful += 1
            else:
                failed += 1
        
        # 生成 Excel 报告
        excel_data = []
        for i, (text, result) in enumerate(zip(request.texts, results)):
            if isinstance(result, dict) and result.get("success"):
                excel_data.append({
                    "ID": i + 1,
                    "Text": text,
                    "Voice": request.voice,
                    "Emotion": request.emotion,
                    "Rate": result.get("params", {}).get("rate", ""),
                    "Pitch": result.get("params", {}).get("pitch", ""),
                    "Volume": result.get("params", {}).get("volume", ""),
                    "Audio File": result.get("file_path", ""),
                    "Status": "Success"
                })
            else:
                excel_data.append({
                    "ID": i + 1,
                    "Text": text,
                    "Voice": request.voice,
                    "Emotion": request.emotion,
                    "Rate": "ERROR",
                    "Pitch": "ERROR",
                    "Volume": "ERROR",
                    "Audio File": "ERROR",
                    "Status": "Failed"
                })
        
        # 保存 Excel 文件
        df = pd.DataFrame(excel_data)
        excel_path = f"{batch_dir}/batch_report.xlsx"
        df.to_excel(excel_path, index=False)
        
        return {
            "batch_id": batch_id,
            "total_texts": len(request.texts),
            "successful": successful,
            "failed": failed,
            "batch_directory": batch_dir,
            "excel_report": excel_path,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批量生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "EdgeTTS API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "supported_emotions": list(EMOTION_PARAMS.keys()),
        "default_voice": DEFAULT_VOICE
    }

@app.get("/voices")
async def get_voices():
    """获取支持的语音列表"""
    return {
        "voices": [
            "en-US-JennyNeural",
            "en-US-GuyNeural", 
            "en-US-AriaNeural",
            "en-US-DavisNeural",
            "en-US-EmmaNeural",
            "en-US-BrandonNeural",
            "zh-CN-XiaoxiaoNeural",
            "zh-CN-YunyangNeural",
            "zh-CN-YunxiNeural"
        ],
        "emotions": list(EMOTION_PARAMS.keys()),
        "formats": ["mp3", "wav", "ogg"]
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件并解析内容"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="只支持 Excel 和 CSV 文件")
        
        # 保存上传的文件
        file_id = f"{uuid.uuid4()}_{file.filename}"
        file_path = f"temp/{file_id}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 解析文件内容
        try:
            if file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # 查找文本列
            text_column = None
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['text', 'script', 'content', 'english']):
                    text_column = col
                    break
            
            if text_column is None:
                text_column = df.columns[0]  # 使用第一列
            
            texts = df[text_column].dropna().tolist()
            
            return {
                "success": True,
                "file_id": file_id,
                "file_path": file_path,
                "texts": texts,
                "total_texts": len(texts),
                "text_column": text_column
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")
            
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
