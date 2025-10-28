#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多API并行处理器 - 数量级性能提升方案
支持同时使用多个TTS API服务，实现真正的并行处理
"""

import asyncio
import aiohttp
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import pandas as pd
import os
import glob

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('19_日志文件_系统运行日志和错误记录/multi_api_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiAPITTSProcessor:
    """多API并行TTS处理器"""
    
    def __init__(self):
        # 多个TTS API端点
        self.api_endpoints = [
            "http://127.0.0.1:5001",  # 本地EdgeTTS
            "http://127.0.0.1:5002",  # 第二个EdgeTTS实例
            "http://127.0.0.1:5003",  # 第三个EdgeTTS实例
        ]
        
        # 每个API的并发限制 (最大性能配置)
        self.api_concurrency = {
            "http://127.0.0.1:5001": 20,
            "http://127.0.0.1:5002": 20, 
            "http://127.0.0.1:5003": 20,
        }
        
        # 总并发数
        self.total_concurrency = sum(self.api_concurrency.values())
        
        # 文件语音映射
        self.FILE_VOICE_MAPPING = {
            "全产品_合并版_3200_v9.xlsx": "en-US-JennyNeural",
            "全产品_合并版_3200_v5.xlsx": "en-US-AvaNeural",
            "全产品_合并版_3200_v4.xlsx": "en-US-NancyNeural",
            "全产品_合并版_3200_v8.xlsx": "en-US-AriaNeural",
            "全产品_合并版_3200_v3.xlsx": "en-US-KaiNeural",
            "全产品_合并版_3200_v2.xlsx": "en-US-SerenaNeural",
            "全产品_合并版_3200.xlsx": "en-US-EmmaNeural",
            "全产品_合并版_3200_v7.xlsx": "en-US-MichelleNeural",
            "全产品_合并版_3200_v6.xlsx": "en-US-BrandonNeural",
        }
        
        # API负载均衡
        self.api_load_balancer = {}
        for endpoint in self.api_endpoints:
            self.api_load_balancer[endpoint] = 0
    
    async def get_available_api(self) -> str:
        """获取负载最低的API端点"""
        min_load = min(self.api_load_balancer.values())
        for endpoint, load in self.api_load_balancer.items():
            if load == min_load:
                return endpoint
        return self.api_endpoints[0]
    
    async def send_to_api(self, session: aiohttp.ClientSession, api_url: str, 
                         scripts: List[Dict], voice: str) -> Dict:
        """发送脚本到指定API"""
        try:
            # 更新负载
            self.api_load_balancer[api_url] += len(scripts)
            
            payload = {
                "scripts": scripts,
                "product_name": f"batch_{int(time.time())}",
                "voice": voice,
                "emotion": "Friendly"
            }
            
            async with session.post(f"{api_url}/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ API {api_url} 成功处理 {len(scripts)} 个脚本")
                    return result
                else:
                    logger.error(f"❌ API {api_url} 返回错误: {response.status}")
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ API {api_url} 请求异常: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            # 减少负载
            self.api_load_balancer[api_url] -= len(scripts)
    
    async def process_scripts_parallel(self, all_scripts: List[Dict], voice: str) -> List[Dict]:
        """并行处理所有脚本"""
        logger.info(f"🚀 开始并行处理 {len(all_scripts)} 个脚本")
        
        # 将脚本分组，每组发送到不同API (最大性能配置)
        batch_size = 100  # 每批100个脚本
        batches = [all_scripts[i:i + batch_size] for i in range(0, len(all_scripts), batch_size)]
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # 创建任务列表
            tasks = []
            
            for batch in batches:
                api_url = await self.get_available_api()
                task = self.send_to_api(session, api_url, batch, voice)
                tasks.append(task)
            
            # 并行执行所有任务
            logger.info(f"📡 并行发送 {len(tasks)} 个批次到多个API")
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"❌ 批次 {i} 处理异常: {str(result)}")
                elif result.get("success"):
                    results.append(result)
                else:
                    logger.error(f"❌ 批次 {i} 处理失败: {result.get('error', 'Unknown error')}")
        
        logger.info(f"✅ 并行处理完成，成功: {len(results)} 个批次")
        return results
    
    def process_excel_file(self, file_path: str) -> Dict:
        """处理单个Excel文件"""
        logger.info(f"📁 开始处理文件: {file_path}")
        
        # 读取Excel文件
        df = pd.read_excel(file_path)
        logger.info(f"✅ 读取到 {len(df)} 条记录")
        
        # 获取语音
        file_name = os.path.basename(file_path)
        voice = self.FILE_VOICE_MAPPING.get(file_name, "en-US-JennyNeural")
        logger.info(f"🎤 使用语音: {voice}")
        
        # 准备脚本数据
        scripts = []
        for _, row in df.iterrows():
            script_data = {
                "script": str(row.get("英文", "")),
                "emotion": str(row.get("情绪类型", "Friendly")),
                "voice": voice,
                "rate": row.get("rate", 1.0),
                "pitch": row.get("pitch", 1.0),
                "volume": row.get("volume", 1.0)
            }
            scripts.append(script_data)
        
        # 并行处理
        start_time = time.time()
        results = asyncio.run(self.process_scripts_parallel(scripts, voice))
        end_time = time.time()
        
        # 统计结果
        total_processed = sum(len(result.get("sample_audios", [])) for result in results)
        
        logger.info(f"✅ 文件处理完成: {file_name}")
        logger.info(f"   - 总脚本: {len(scripts)}")
        logger.info(f"   - 成功生成: {total_processed}")
        logger.info(f"   - 耗时: {(end_time - start_time)/60:.1f} 分钟")
        
        return {
            "file_name": file_name,
            "total_scripts": len(scripts),
            "successful": total_processed,
            "duration": end_time - start_time,
            "results": results
        }
    
    def process_all_files(self, input_dir: str = "18_批量输入_批量文件输入目录"):
        """处理所有Excel文件"""
        logger.info("🎵 开始多API并行处理")
        logger.info("=" * 80)
        
        # 查找所有Excel文件
        excel_files = glob.glob(os.path.join(input_dir, "*.xlsx"))
        logger.info(f"📁 发现 {len(excel_files)} 个Excel文件")
        
        total_start_time = time.time()
        all_results = []
        
        for i, file_path in enumerate(excel_files, 1):
            logger.info(f"📁 处理文件 {i}/{len(excel_files)}: {os.path.basename(file_path)}")
            
            try:
                result = self.process_excel_file(file_path)
                all_results.append(result)
                
                # 文件间延迟
                if i < len(excel_files):
                    logger.info("⏳ 文件间暂停 2 秒...")
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ 文件处理失败: {str(e)}")
        
        total_end_time = time.time()
        
        # 最终统计
        total_scripts = sum(r["total_scripts"] for r in all_results)
        total_successful = sum(r["successful"] for r in all_results)
        total_duration = total_end_time - total_start_time
        
        logger.info("=" * 80)
        logger.info("🎉 多API并行处理完成!")
        logger.info(f"📊 总统计:")
        logger.info(f"   - 处理文件: {len(excel_files)}")
        logger.info(f"   - 总脚本: {total_scripts}")
        logger.info(f"   - 成功生成: {total_successful}")
        logger.info(f"   - 成功率: {total_successful/total_scripts*100:.1f}%")
        logger.info(f"   - 总耗时: {total_duration/60:.1f} 分钟")
        logger.info(f"   - 平均速度: {total_successful/(total_duration/60):.1f} 个/分钟")

if __name__ == "__main__":
    processor = MultiAPITTSProcessor()
    processor.process_all_files()
