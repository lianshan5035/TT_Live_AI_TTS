#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拖拽式Excel到音频生成器
支持拖拽Excel文件直接生成音频
"""

import os
import sys
import json
import pandas as pd
import requests
import time
import random
import re
from datetime import datetime
from typing import List, Dict, Any
import argparse

class DragDropAudioGenerator:
    def __init__(self):
        self.tts_url = "http://127.0.0.1:5001"
        self.output_dir = "audio_outputs"
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # A3标准配置
        self.emotion_config = {
            "Excited": {"voice": "en-US-JennyNeural", "rate": [10, 25], "pitch": [5, 15], "volume": [2, 10]},
            "Confident": {"voice": "en-US-GuyNeural", "rate": [5, 20], "pitch": [2, 12], "volume": [0, 8]},
            "Calm": {"voice": "en-US-DavisNeural", "rate": [-5, 10], "pitch": [-2, 8], "volume": [-2, 5]},
            "Playful": {"voice": "en-US-JennyNeural", "rate": [15, 30], "pitch": [8, 18], "volume": [3, 12]},
            "Empathetic": {"voice": "en-US-GuyNeural", "rate": [0, 15], "pitch": [0, 10], "volume": [0, 6]},
            "Motivational": {"voice": "en-US-DavisNeural", "rate": [8, 22], "pitch": [4, 14], "volume": [2, 10]},
            "Soothing": {"voice": "en-US-JennyNeural", "rate": [-2, 8], "pitch": [-1, 6], "volume": [-1, 4]},
            "Gentle": {"voice": "en-US-GuyNeural", "rate": [0, 12], "pitch": [0, 8], "volume": [0, 5]}
        }
        
        # 产品关键词映射
        self.keyword_emotion_map = {
            "美白": "Excited", "淡斑": "Excited", "亮白": "Excited", "brightening": "Excited",
            "抗老": "Confident", "紧致": "Confident", "firming": "Confident", "anti-aging": "Confident",
            "保湿": "Calm", "补水": "Calm", "滋润": "Calm", "moisturizing": "Calm",
            "维生素": "Playful", "vitamin": "Playful", "精华": "Playful", "serum": "Playful",
            "胶原蛋白": "Empathetic", "collagen": "Empathetic", "健康": "Empathetic", "health": "Empathetic",
            "瘦身": "Motivational", "减肥": "Motivational", "fitness": "Motivational", "weight": "Motivational",
            "护发": "Soothing", "hair": "Soothing", "柔顺": "Soothing", "smooth": "Soothing",
            "眼部": "Gentle", "eye": "Gentle", "温和": "Gentle", "gentle": "Gentle"
        }

    def extract_product_name(self, filename: str) -> str:
        """从文件名提取产品名称"""
        name_without_ext = os.path.splitext(filename)[0]
        
        # 清理文件名模式
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
        
        product_name = name_without_ext
        for pattern in patterns:
            match = re.search(pattern, name_without_ext)
            if match:
                product_name = match.group(1).strip()
                break
        
        return product_name

    def auto_select_emotion(self, product_name: str) -> str:
        """根据产品名称自动选择情绪"""
        product_lower = product_name.lower()
        
        for keyword, emotion in self.keyword_emotion_map.items():
            if keyword.lower() in product_lower:
                return emotion
        
        return "Excited"  # 默认情绪

    def parse_excel(self, filepath: str) -> Dict[str, Any]:
        """解析Excel文件"""
        try:
            filename = os.path.basename(filepath)
            product_name = self.extract_product_name(filename)
            
            # 读取文件
            file_ext = os.path.splitext(filepath)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            elif file_ext == '.csv':
                for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            elif file_ext == '.tsv':
                for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']:
                    try:
                        df = pd.read_csv(filepath, sep='\t', encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                return {'success': False, 'error': '不支持的文件格式'}
            
            if df is None or df.empty:
                return {'success': False, 'error': '文件为空'}
            
            # 查找英文文案字段
            english_fields = [
                'english_script', 'English Script', 'english', 'English', 'script', 'Script',
                '文案', '英文文案', 'english_text', 'English Text', 'Content', 'content',
                'English Content', 'english_content', 'Text', 'text', 'English Text',
                'Description', 'description', 'Copy', 'copy', 'Scripts', 'scripts',
                'Prompts', 'prompts', 'Messages', 'messages', 'Posts', 'posts',
                'Ads', 'ads', 'Marketing', 'marketing', 'Sales', 'sales',
                'Copywriting', 'copywriting', 'Headlines', 'headlines', 'Taglines', 'taglines',
                'Slogans', 'slogans', 'Captions', 'captions', 'Titles', 'titles',
                'Subtitles', 'subtitles', 'Body', 'body', 'Main', 'main',
                'Primary', 'primary', 'Core', 'core', 'Key', 'key',
                'Essential', 'essential', 'Important', 'important'
            ]
            
            english_field = None
            for field in english_fields:
                if field in df.columns:
                    english_field = field
                    break
            
            if not english_field:
                return {
                    'success': False,
                    'error': '未找到英文文案字段',
                    'available_fields': list(df.columns)
                }
            
            # 提取文案
            scripts = df[english_field].dropna().tolist()
            
            if not scripts:
                return {'success': False, 'error': '未找到有效文案'}
            
            # 自动选择情绪
            emotion = self.auto_select_emotion(product_name)
            
            return {
                'success': True,
                'product_name': product_name,
                'scripts': scripts,
                'emotion': emotion,
                'voice': self.emotion_config[emotion]['voice'],
                'total_scripts': len(scripts),
                'filename': filename
            }
            
        except Exception as e:
            return {'success': False, 'error': f'解析失败: {str(e)}'}

    def generate_audio(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成音频文件"""
        try:
            product_name = parsed_data['product_name']
            scripts = parsed_data['scripts']
            emotion = parsed_data['emotion']
            voice = parsed_data['voice']
            
            # 创建输出目录
            product_dir = os.path.join(self.output_dir, product_name)
            os.makedirs(product_dir, exist_ok=True)
            
            print(f"🎵 生成音频: {product_name}")
            print(f"   - 情绪: {emotion}")
            print(f"   - 语音: {voice}")
            print(f"   - 文案数: {len(scripts)}")
            
            # 调用TTS服务
            tts_data = {
                "product_name": product_name,
                "scripts": scripts,
                "emotion": emotion,
                "voice": voice,
                "discount": "Special offer available!"
            }
            
            response = requests.post(f"{self.tts_url}/generate", json=tts_data, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'product_name': product_name,
                    'audio_directory': product_dir,
                    'total_scripts': len(scripts),
                    'emotion': emotion,
                    'voice': voice,
                    'tts_result': result
                }
            else:
                return {'success': False, 'error': f'TTS服务错误: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': f'生成失败: {str(e)}'}

    def process_file(self, filepath: str) -> Dict[str, Any]:
        """处理单个文件"""
        print(f"\n📄 处理: {os.path.basename(filepath)}")
        
        # 解析Excel
        parsed = self.parse_excel(filepath)
        if not parsed['success']:
            print(f"❌ 解析失败: {parsed['error']}")
            return parsed
        
        print(f"✅ 解析成功: {parsed['product_name']} ({parsed['total_scripts']}条文案)")
        
        # 生成音频
        result = self.generate_audio(parsed)
        if result['success']:
            print(f"✅ 音频生成完成: {result['audio_directory']}")
        else:
            print(f"❌ 音频生成失败: {result['error']}")
        
        return result

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Excel到音频一键生成器')
    parser.add_argument('files', nargs='*', help='Excel文件路径')
    parser.add_argument('--check-service', action='store_true', help='检查TTS服务状态')
    
    args = parser.parse_args()
    
    generator = DragDropAudioGenerator()
    
    # 检查TTS服务
    try:
        response = requests.get(f"{generator.tts_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ TTS服务未运行")
            if args.check_service:
                return
            print("请先启动TTS服务:")
            print("   python3 run_tts.py")
            return
    except:
        print("❌ TTS服务未运行")
        if args.check_service:
            return
        print("请先启动TTS服务:")
        print("   python3 run_tts.py")
        return
    
    if args.check_service:
        print("✅ TTS服务运行正常")
        return
    
    print("🎯 Excel到音频一键生成器")
    print("=" * 50)
    print("✅ TTS服务运行正常")
    
    # 处理文件
    if args.files:
        # 命令行参数文件
        file_paths = [f for f in args.files if os.path.exists(f)]
        if not file_paths:
            print("❌ 没有找到有效文件")
            return
    else:
        # 交互式输入
        print("\n请选择处理方式:")
        print("1. 处理单个文件")
        print("2. 处理多个文件")
        print("3. 处理目录中的所有Excel文件")
        
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            filepath = input("请输入文件路径: ").strip()
            if os.path.exists(filepath):
                file_paths = [filepath]
            else:
                print("❌ 文件不存在")
                return
        elif choice == "2":
            print("请输入文件路径（每行一个，输入空行结束）:")
            file_paths = []
            while True:
                filepath = input().strip()
                if not filepath:
                    break
                if os.path.exists(filepath):
                    file_paths.append(filepath)
                else:
                    print(f"❌ 文件不存在: {filepath}")
        elif choice == "3":
            directory = input("请输入目录路径: ").strip()
            if os.path.exists(directory):
                file_paths = []
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.lower().endswith(('.xlsx', '.xls', '.csv', '.tsv')):
                            file_paths.append(os.path.join(root, file))
                if not file_paths:
                    print("❌ 目录中没有找到Excel文件")
                    return
            else:
                print("❌ 目录不存在")
                return
        else:
            print("❌ 无效选择")
            return
    
    # 批量处理
    print(f"\n🚀 开始处理 {len(file_paths)} 个文件")
    print("=" * 50)
    
    results = []
    for i, filepath in enumerate(file_paths, 1):
        result = generator.process_file(filepath)
        results.append(result)
    
    # 统计结果
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print("\n" + "=" * 50)
    print("🎉 处理完成!")
    print(f"✅ 成功: {successful}")
    print(f"❌ 失败: {failed}")
    print(f"📁 音频文件保存在: {generator.output_dir}")

if __name__ == "__main__":
    main()
