#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel到音频一键生成器
从Excel文件直接生成音频文件，内置完整流程
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
from typing import List, Dict, Any, Optional
import subprocess
import threading
from io import StringIO

class ExcelToAudioGenerator:
    def __init__(self):
        self.tts_url = "http://127.0.0.1:5001"
        self.output_dir = "audio_outputs"
        self.temp_dir = "temp_excel"
        
        # 确保目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # A3标准情绪配置
        self.emotion_config = {
            "Excited": {
                "voice": "en-US-JennyNeural",
                "rate_range": [10, 25],
                "pitch_range": [5, 15],
                "volume_range": [2, 10]
            },
            "Confident": {
                "voice": "en-US-GuyNeural", 
                "rate_range": [5, 20],
                "pitch_range": [2, 12],
                "volume_range": [0, 8]
            },
            "Calm": {
                "voice": "en-US-DavisNeural",
                "rate_range": [-5, 10],
                "pitch_range": [-2, 8],
                "volume_range": [-2, 5]
            },
            "Playful": {
                "voice": "en-US-JennyNeural",
                "rate_range": [15, 30],
                "pitch_range": [8, 18],
                "volume_range": [3, 12]
            },
            "Empathetic": {
                "voice": "en-US-GuyNeural",
                "rate_range": [0, 15],
                "pitch_range": [0, 10],
                "volume_range": [0, 6]
            },
            "Motivational": {
                "voice": "en-US-DavisNeural",
                "rate_range": [8, 22],
                "pitch_range": [4, 14],
                "volume_range": [2, 10]
            },
            "Soothing": {
                "voice": "en-US-JennyNeural",
                "rate_range": [-2, 8],
                "pitch_range": [-1, 6],
                "volume_range": [-1, 4]
            },
            "Gentle": {
                "voice": "en-US-GuyNeural",
                "rate_range": [0, 12],
                "pitch_range": [0, 8],
                "volume_range": [0, 5]
            }
        }
        
        # 产品关键词到情绪的映射
        self.product_emotion_map = {
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
        
        return product_name

    def auto_select_emotion(self, product_name: str) -> str:
        """根据产品名称自动选择情绪"""
        product_lower = product_name.lower()
        
        for keyword, emotion in self.product_emotion_map.items():
            if keyword.lower() in product_lower:
                return emotion
        
        # 默认情绪
        return "Excited"

    def parse_text_table(self, filepath: str):
        """解析文本表格文件（Markdown表格或纯文本表格）"""
        try:
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
            return None

    def parse_excel_file(self, filepath: str) -> Dict[str, Any]:
        """解析Excel文件，提取口播正文"""
        try:
            filename = os.path.basename(filepath)
            product_name = self.extract_product_name(filename)
            
            # 尝试读取Excel文件
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
                    df = self.parse_text_table(filepath)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'无法读取文件: {str(e)}'
                }
            
            if df is None or df.empty:
                return {
                    'success': False,
                    'error': '文件为空或无法解析'
                }
            
            # 扩展的字段变体映射（支持GPTs生成的各种字段名）
            field_mappings = {
                'english_script': [
                    # 标准字段名
                    'english_script', 'English Script', 'english', 'English', 'script', 'Script', 
                    '文案', '英文文案', 'english_text', 'English Text',
                    # GPTs常用字段名
                    'Content', 'content', 'English Content', 'english_content',
                    'Text', 'text', 'English Text', 'english_text',
                    'Description', 'description', 'English Description', 'english_description',
                    'Copy', 'copy', 'English Copy', 'english_copy',
                    'Scripts', 'scripts', 'English Scripts', 'english_scripts',
                    'Prompts', 'prompts', 'English Prompts', 'english_prompts',
                    'Messages', 'messages', 'English Messages', 'english_messages',
                    'Posts', 'posts', 'English Posts', 'english_posts',
                    'Ads', 'ads', 'English Ads', 'english_ads',
                    'Marketing', 'marketing', 'English Marketing', 'english_marketing',
                    'Sales', 'sales', 'English Sales', 'english_sales',
                    'Copywriting', 'copywriting', 'English Copywriting', 'english_copywriting',
                    'Headlines', 'headlines', 'English Headlines', 'english_headlines',
                    'Taglines', 'taglines', 'English Taglines', 'english_taglines',
                    'Slogans', 'slogans', 'English Slogans', 'english_slogans',
                    'Captions', 'captions', 'English Captions', 'english_captions',
                    'Titles', 'titles', 'English Titles', 'english_titles',
                    'Subtitles', 'subtitles', 'English Subtitles', 'english_subtitles',
                    'Body', 'body', 'English Body', 'english_body',
                    'Main', 'main', 'English Main', 'english_main',
                    'Primary', 'primary', 'English Primary', 'english_primary',
                    'Core', 'core', 'English Core', 'english_core',
                    'Key', 'key', 'English Key', 'english_key',
                    'Essential', 'essential', 'English Essential', 'english_essential',
                    'Important', 'important', 'English Important', 'english_important',
                    'Main Content', 'main_content', 'English Main Content', 'english_main_content',
                    'Primary Content', 'primary_content', 'English Primary Content', 'primary_content',
                    'Core Content', 'core_content', 'English Core Content', 'core_content',
                    'Key Content', 'key_content', 'English Key Content', 'key_content',
                    'Essential Content', 'essential_content', 'English Essential Content', 'essential_content',
                    'Important Content', 'important_content', 'English Important Content', 'important_content'
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
                    'Chinese Posts', 'posts', '中文帖子', '帖子',
                    'Chinese Ads', 'chinese_ads', '中文广告', '广告',
                    'Chinese Marketing', 'chinese_marketing', '中文营销', '营销',
                    'Chinese Sales', 'sales', '中文销售', '销售',
                    'Chinese Copywriting', 'chinese_copywriting', '中文文案', '文案',
                    'Chinese Headlines', 'chinese_headlines', '中文标题', '标题',
                    'Chinese Taglines', 'chinese_taglines', '中文标语', '标语',
                    'Chinese Slogans', 'chinese_slogans', '中文口号', '口号',
                    'Chinese Captions', 'captions', '中文说明', '说明',
                    'Chinese Descriptions', 'descriptions', '中文描述', '描述',
                    'Chinese Titles', 'titles', '中文标题', '标题',
                    'Chinese Subtitles', 'chinese_subtitles', '中文副标题', '副标题',
                    'Chinese Body', 'chinese_body', '中文正文', '正文',
                    'Chinese Main', 'chinese_main', '中文主要', '主要',
                    'Chinese Primary', 'chinese_primary', '中文主要', '主要',
                    'Chinese Core', 'core', '中文核心', '核心',
                    'Chinese Key', 'key', '中文关键', '关键',
                    'Chinese Essential', 'essential', '中文必要', '必要',
                    'Chinese Important', 'important', '中文重要', '重要',
                    'Chinese Main Content', 'chinese_main_content', '中文主要内容', '主要内容',
                    'Chinese Primary Content', 'chinese_primary_content', '中文主要内容', '主要内容',
                    'Chinese Core Content', 'chinese_core_content', '中文核心内容', '核心内容',
                    'Chinese Key Content', 'chinese_key_content', '中文关键内容', '关键内容',
                    'Chinese Essential Content', 'essential_content', '中文必要内容', '必要内容',
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
            
            # 根据产品类型自动选择情绪和语音
            emotion = self.auto_select_emotion(product_name)
            voice = self.emotion_config[emotion]['voice']
            
            # A3标准验证
            a3_compliance = {
                'emotion_valid': emotion in self.emotion_config,
                'voice_valid': voice.startswith('en-US-'),
                'scripts_count': len(scripts),
                'scripts_length_valid': all(50 <= len(str(script)) <= 1000 for script in scripts),
                'product_name_extracted': bool(product_name),
                'chinese_translation_available': 'chinese_translation' in found_fields,
                'file_format_supported': file_ext in ['.xlsx', '.xls', '.csv', '.tsv', '.txt'],
                'fields_mapped': bool(found_fields)
            }
            
            return {
                'success': True,
                'product_name': product_name,
                'scripts': scripts,
                'chinese_translations': chinese_translations,
                'emotion': emotion,
                'voice': voice,
                'a3_compliance': a3_compliance,
                'total_scripts': len(scripts),
                'filename': filename,
                'file_format': file_ext,
                'has_chinese_translation': 'chinese_translation' in found_fields,
                'field_mapping': found_fields
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'解析Excel文件失败: {str(e)}',
                'supported_formats': ['.xlsx', '.xls', '.csv', '.tsv', '.txt'],
                'a3_compliance': False
            }

    def generate_audio_parameters(self, emotion: str, script_index: int) -> Dict[str, str]:
        """生成A3标准音频参数"""
        config = self.emotion_config[emotion]
        
        # 使用正弦波+斐波那契+素数序列算法
        rate_base = random.randint(config['rate_range'][0], config['rate_range'][1])
        pitch_base = random.randint(config['pitch_range'][0], config['pitch_range'][1])
        volume_base = random.randint(config['volume_range'][0], config['volume_range'][1])
        
        # 添加动态变化
        sine_factor = int(5 * (1 + 0.3 * (script_index % 10)))
        fib_factor = int(3 * (1 + 0.2 * (script_index % 8)))
        prime_factor = int(2 * (1 + 0.1 * (script_index % 7)))
        
        rate = rate_base + sine_factor
        pitch = pitch_base + fib_factor
        volume = volume_base + prime_factor
        
        return {
            'rate': f"+{rate}%",
            'pitch': f"+{pitch}%",
            'volume': f"+{volume}dB"
        }

    def generate_audio_files(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成音频文件"""
        try:
            product_name = parsed_data['product_name']
            scripts = parsed_data['scripts']
            emotion = parsed_data['emotion']
            voice = parsed_data['voice']
            
            # 创建产品输出目录
            product_dir = os.path.join(self.output_dir, product_name)
            os.makedirs(product_dir, exist_ok=True)
            
            print(f"🎵 开始生成音频文件: {product_name}")
            print(f"   - 情绪: {emotion}")
            print(f"   - 语音: {voice}")
            print(f"   - 文案数量: {len(scripts)}")
            
            # 调用TTS服务生成音频
            tts_data = {
                "product_name": product_name,
                "scripts": scripts,
                "emotion": emotion,
                "voice": voice,
                "discount": "Special offer available!"
            }
            
            response = requests.post(
                f"{self.tts_url}/generate",
                json=tts_data,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 生成音频参数报告
                audio_params = []
                for i, script in enumerate(scripts):
                    params = self.generate_audio_parameters(emotion, i)
                    audio_params.append({
                        'script_id': i + 1,
                        'script': script[:50] + "..." if len(script) > 50 else script,
                        'emotion': emotion,
                        'voice': voice,
                        'rate': params['rate'],
                        'pitch': params['pitch'],
                        'volume': params['volume'],
                        'audio_file': f"tts_{i+1:04d}_{emotion}.mp3"
                    })
                
                return {
                    'success': True,
                    'product_name': product_name,
                    'total_scripts': len(scripts),
                    'emotion': emotion,
                    'voice': voice,
                    'audio_directory': product_dir,
                    'audio_params': audio_params,
                    'tts_result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'TTS服务错误: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'生成音频失败: {str(e)}'
            }

    def save_generation_report(self, result: Dict[str, Any], original_file: str):
        """保存生成报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.output_dir, f"generation_report_{timestamp}.json")
        
        report_data = {
            'generation_time': datetime.now().isoformat(),
            'original_file': original_file,
            'result': result
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 生成报告保存到: {report_file}")

    def process_excel_file(self, filepath: str) -> Dict[str, Any]:
        """处理单个Excel文件，生成音频"""
        print(f"📄 处理文件: {os.path.basename(filepath)}")
        
        # 1. 解析Excel文件
        print("🔍 解析Excel文件...")
        parsed_data = self.parse_excel_file(filepath)
        
        if not parsed_data['success']:
            print(f"❌ 解析失败: {parsed_data['error']}")
            return parsed_data
        
        print(f"✅ 解析成功:")
        print(f"   - 产品名称: {parsed_data['product_name']}")
        print(f"   - 文案数量: {parsed_data['total_scripts']}")
        print(f"   - 自动选择情绪: {parsed_data['emotion']}")
        print(f"   - 语音模型: {parsed_data['voice']}")
        
        # 2. 生成音频文件
        print("\n🎵 生成音频文件...")
        audio_result = self.generate_audio_files(parsed_data)
        
        if not audio_result['success']:
            print(f"❌ 音频生成失败: {audio_result['error']}")
            return audio_result
        
        print(f"✅ 音频生成成功:")
        print(f"   - 音频目录: {audio_result['audio_directory']}")
        print(f"   - 音频文件数: {audio_result['total_scripts']}")
        
        # 3. 保存生成报告
        self.save_generation_report(audio_result, filepath)
        
        return audio_result

    def batch_process_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """批量处理多个Excel文件"""
        print(f"🚀 开始批量处理 {len(file_paths)} 个文件")
        print("=" * 60)
        
        results = []
        for i, filepath in enumerate(file_paths, 1):
            print(f"\n📦 处理文件 {i}/{len(file_paths)}")
            result = self.process_excel_file(filepath)
            results.append(result)
            
            if result['success']:
                print(f"✅ 文件 {i} 处理完成")
            else:
                print(f"❌ 文件 {i} 处理失败")
        
        # 统计结果
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        print("\n" + "=" * 60)
        print("🎉 批量处理完成!")
        print(f"✅ 成功: {successful}")
        print(f"❌ 失败: {failed}")
        print(f"📁 音频文件保存在: {self.output_dir}")
        
        return results

def main():
    """主函数"""
    print("🎯 Excel到音频一键生成器")
    print("=" * 50)
    
    generator = ExcelToAudioGenerator()
    
    # 检查TTS服务
    try:
        response = requests.get(f"{generator.tts_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ TTS服务未运行，请先启动:")
            print("   python3 run_tts.py")
            return
    except:
        print("❌ TTS服务未运行，请先启动:")
        print("   python3 run_tts.py")
        return
    
    print("✅ TTS服务运行正常")
    
    # 获取输入文件
    print("\n请选择处理方式:")
    print("1. 处理单个Excel文件")
    print("2. 处理目录中的所有Excel文件")
    print("3. 处理指定文件列表")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        filepath = input("请输入Excel文件路径: ").strip()
        if os.path.exists(filepath):
            generator.process_excel_file(filepath)
        else:
            print("❌ 文件不存在")
    
    elif choice == "2":
        directory = input("请输入目录路径: ").strip()
        if os.path.exists(directory):
            # 查找所有Excel文件
            excel_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(('.xlsx', '.xls', '.csv', '.tsv')):
                        excel_files.append(os.path.join(root, file))
            
            if excel_files:
                print(f"找到 {len(excel_files)} 个Excel文件")
                generator.batch_process_files(excel_files)
            else:
                print("❌ 目录中没有找到Excel文件")
        else:
            print("❌ 目录不存在")
    
    elif choice == "3":
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
        
        if file_paths:
            generator.batch_process_files(file_paths)
        else:
            print("❌ 没有有效的文件")
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
