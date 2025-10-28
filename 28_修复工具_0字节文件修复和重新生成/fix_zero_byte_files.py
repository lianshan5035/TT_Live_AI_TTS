#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
0字节音频文件修复工具
用于重新生成缺失的音频文件
"""

import os
import pandas as pd
import requests
import json
import logging
from pathlib import Path
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('19_日志文件_系统运行日志和错误记录/fix_zero_byte_files.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZeroByteFileFixer:
    """0字节文件修复器"""
    
    def __init__(self):
        self.TTS_SERVICE_URL = "http://127.0.0.1:5001"
        self.INPUTS_DIR = "18_批量输入_批量文件输入目录"
        self.OUTPUTS_DIR = "20_输出文件_处理完成的音频文件"
        
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
        
        # 情绪类型映射
        self.EMOTION_MAPPING = {
            "紧迫型": "Urgent",
            "舒缓型": "Calm", 
            "温暖型": "Warm",
            "兴奋型": "Excited",
            "专业型": "Professional"
        }
    
    def get_voice_name(self, full_file_name):
        """从完整文件名中提取语音名称"""
        voice = self.FILE_VOICE_MAPPING.get(full_file_name, "en-US-JennyNeural")
        return voice.replace("en-US-", "").replace("Neural", "")
    
    def find_missing_files(self):
        """查找缺失的音频文件"""
        missing_files = []
        
        # 检查每个Excel文件
        for excel_file in os.listdir(self.INPUTS_DIR):
            if not excel_file.endswith('.xlsx'):
                continue
                
            logger.info(f"🔍 检查文件: {excel_file}")
            
            # 读取Excel文件
            excel_path = os.path.join(self.INPUTS_DIR, excel_file)
            df = pd.read_excel(excel_path)
            
            # 获取语音
            voice = self.FILE_VOICE_MAPPING.get(excel_file, "en-US-JennyNeural")
            voice_name = self.get_voice_name(excel_file)
            
            # 检查输出目录
            output_dir = os.path.join(self.OUTPUTS_DIR, f"{excel_file.replace('.xlsx', '')}_{voice_name}")
            
            if not os.path.exists(output_dir):
                logger.warning(f"⚠️ 输出目录不存在: {output_dir}")
                continue
            
            # 检查每个脚本的音频文件
            for idx, row in df.iterrows():
                script_id = idx + 1
                
                # 检查所有情绪类型的音频文件
                for emotion_cn, emotion_en in self.EMOTION_MAPPING.items():
                    audio_filename = f"tts_{script_id:04d}_{emotion_cn}_{voice_name}_dyn.mp3"
                    audio_path = os.path.join(output_dir, audio_filename)
                    
                    # 如果文件不存在或大小为0，则标记为缺失
                    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                        missing_files.append({
                            'excel_file': excel_file,
                            'script_id': script_id,
                            'script_text': row.get('英文', ''),
                            'emotion_cn': emotion_cn,
                            'emotion_en': emotion_en,
                            'voice': voice,
                            'voice_name': voice_name,
                            'audio_filename': audio_filename,
                            'audio_path': audio_path
                        })
        
        logger.info(f"📊 发现 {len(missing_files)} 个缺失的音频文件")
        return missing_files
    
    def generate_single_audio(self, script_info):
        """生成单个音频文件"""
        try:
            # 准备请求数据
            request_data = {
                "scripts": [{
                    "script": script_info['script_text'],
                    "emotion": script_info['emotion_en'],
                    "voice": script_info['voice']
                }],
                "product_name": f"{script_info['excel_file'].replace('.xlsx', '')}_Fix",
                "voice": script_info['voice']
            }
            
            # 发送请求到TTS服务
            response = requests.post(
                f"{self.TTS_SERVICE_URL}/generate",
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"✅ 成功生成: {script_info['audio_filename']}")
                    return True
                else:
                    logger.error(f"❌ TTS服务返回失败: {script_info['audio_filename']}")
                    return False
            else:
                logger.error(f"❌ HTTP错误 {response.status_code}: {script_info['audio_filename']}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 生成异常: {script_info['audio_filename']} - {str(e)}")
            return False
    
    def fix_missing_files(self, missing_files):
        """修复缺失的文件"""
        logger.info(f"🔧 开始修复 {len(missing_files)} 个缺失文件")
        
        success_count = 0
        fail_count = 0
        
        for i, script_info in enumerate(missing_files):
            logger.info(f"📝 处理 {i+1}/{len(missing_files)}: {script_info['audio_filename']}")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(script_info['audio_path']), exist_ok=True)
            
            # 生成音频
            if self.generate_single_audio(script_info):
                success_count += 1
            else:
                fail_count += 1
            
            # 添加延迟避免过载
            time.sleep(0.5)
        
        logger.info(f"🎯 修复完成: 成功 {success_count} 个, 失败 {fail_count} 个")
        return success_count, fail_count
    
    def check_tts_service(self):
        """检查TTS服务状态"""
        try:
            response = requests.get(f"{self.TTS_SERVICE_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ TTS服务状态正常")
                return True
            else:
                logger.error(f"❌ TTS服务状态异常: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 无法连接到TTS服务: {str(e)}")
            return False
    
    def run(self):
        """运行修复程序"""
        logger.info("🚀 开始0字节文件修复程序")
        
        # 检查TTS服务
        if not self.check_tts_service():
            logger.error("❌ TTS服务不可用，请先启动TTS服务")
            return
        
        # 查找缺失文件
        missing_files = self.find_missing_files()
        
        if not missing_files:
            logger.info("🎉 没有发现缺失的音频文件")
            return
        
        # 修复缺失文件
        success_count, fail_count = self.fix_missing_files(missing_files)
        
        logger.info(f"🏁 修复程序完成: 成功 {success_count} 个, 失败 {fail_count} 个")

if __name__ == "__main__":
    fixer = ZeroByteFileFixer()
    fixer.run()
