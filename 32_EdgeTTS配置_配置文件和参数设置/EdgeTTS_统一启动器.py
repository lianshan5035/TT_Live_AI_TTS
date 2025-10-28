#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS 统一启动器
=================

解决以下问题：
1. 固定输入和输出路径（都在TT_Live_AI_TTS项目内）
2. 统一多API配置管理
3. 标准化的文件命名规则
4. 统一的配置管理

所有操作都在 TT_Live_AI_TTS 项目文件夹内进行

作者: AI Assistant
版本: 1.0.0
更新日期: 2024-10-28
"""

import os
import sys
import json
import pandas as pd
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any, Optional
import glob

class EdgeTTSUnifiedManager:
    """EdgeTTS 统一管理器 - 仅在TT_Live_AI_TTS项目内操作"""
    
    def __init__(self, config_file: str = "EdgeTTS_统一配置.json"):
        """
        初始化统一管理器
        
        Args:
            config_file (str): 配置文件路径
        """
        # 确保在TT_Live_AI_TTS项目目录内
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        self.config_file = os.path.join(self.project_root, config_file)
        self.config = self.load_config()
        self.setup_directories()
        self.setup_api_services()
        
        # 线程锁
        self.lock = threading.Lock()
        self.url_lock = threading.Lock()
        self.current_url_index = 0
        
    def load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ 配置文件加载成功: {self.config_file}")
            return config["EdgeTTS_统一配置"]
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "路径配置": {
                "输入目录": {
                    "默认路径": "/Volumes/M2/TT_Live_AI_TTS/18_批量输入_批量文件输入目录"
                },
                "输出目录": {
                    "根目录": "/Volumes/M2/TT_Live_AI_TTS",
                    "固定子目录": "20_输出文件_处理完成的音频文件"
                }
            },
            "API配置": {
                "多API服务": {
                    "启用": True,
                    "服务列表": [
                        {"URL": "http://127.0.0.1:5001"},
                        {"URL": "http://127.0.0.1:5002"},
                        {"URL": "http://127.0.0.1:5003"}
                    ]
                }
            },
            "性能配置": {
                "多线程设置": {
                    "最大线程数": 12
                }
            }
        }
    
    def setup_directories(self):
        """设置目录结构 - 都在TT_Live_AI_TTS项目内"""
        # 输入目录
        self.input_dir = self.config["路径配置"]["输入目录"]["默认路径"]
        
        # 输出目录 - 固定路径（TT_Live_AI_TTS项目内）
        output_root = self.config["路径配置"]["输出目录"]["根目录"]
        output_subdir = self.config["路径配置"]["输出目录"]["固定子目录"]
        self.output_dir = os.path.join(output_root, output_subdir)
        
        # 确保目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"📁 项目根目录: {self.project_root}")
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
    
    def setup_api_services(self):
        """设置API服务"""
        api_config = self.config["API配置"]["多API服务"]
        
        if api_config["启用"]:
            self.tts_urls = [service["URL"] for service in api_config["服务列表"]]
            self.max_workers = self.config["性能配置"]["多线程设置"]["最大线程数"]
        else:
            self.tts_urls = [self.config["API配置"]["单API模式"]["URL"]]
            self.max_workers = 8
        
        print(f"🌐 API服务数量: {len(self.tts_urls)}")
        print(f"🧵 最大线程数: {self.max_workers}")
    
    def get_next_tts_url(self) -> str:
        """获取下一个可用的 TTS URL（轮询策略）"""
        with self.url_lock:
            url = self.tts_urls[self.current_url_index]
            self.current_url_index = (self.current_url_index + 1) % len(self.tts_urls)
            return url
    
    def check_tts_services(self) -> bool:
        """检查所有 TTS 服务状态"""
        available_services = []
        
        print("🔍 检查 EdgeTTS 服务状态...")
        for i, url in enumerate(self.tts_urls, 1):
            try:
                response = requests.get(f"{url}/status", timeout=5)
                if response.status_code == 200:
                    available_services.append(url)
                    print(f"✅ TTS 服务 {i} ({url}) 运行正常")
                else:
                    print(f"❌ TTS 服务 {i} ({url}) 响应异常: {response.status_code}")
            except Exception as e:
                print(f"❌ TTS 服务 {i} ({url}) 连接失败: {e}")
        
        if available_services:
            self.tts_urls = available_services
            print(f"🎯 可用服务数量: {len(available_services)}")
            return True
        else:
            print("❌ 没有可用的 TTS 服务")
            return False
    
    def get_emotion_config(self, emotion: str) -> Dict:
        """获取情绪配置"""
        emotion_configs = self.config.get("情绪配置", {}).get("A3标准12种情绪", {})
        
        # 情绪名称映射
        emotion_mapping = {
            "兴奋型": "Excited",
            "专业型": "Confident", 
            "舒缓型": "Calm",
            "活泼型": "Playful",
            "紧迫型": "Urgent",
            "温暖型": "Friendly"
        }
        
        mapped_emotion = emotion_mapping.get(emotion, emotion)
        config = emotion_configs.get(mapped_emotion)
        
        # 如果找不到配置，使用默认配置
        if not config:
            config = emotion_configs.get("Friendly", {
                "rate": 12,
                "pitch": 8,
                "volume": 5,
                "voice": "en-US-JennyNeural"
            })
        
        return {
            "rate": config.get("rate", 12),
            "pitch": config.get("pitch", 8),
            "volume": config.get("volume", 5),
            "voice": config.get("voice", "en-US-JennyNeural")
        }
    
    def generate_audio(self, text: str, emotion: str, output_file: str) -> bool:
        """生成单个音频文件"""
        try:
            config = self.get_emotion_config(emotion)
            
            # 构建请求数据 - 使用正确的scripts格式
            data = {
                "product_name": "统一生成",
                "scripts": [{
                    "text": text,
                    "voice": config["voice"],
                    "rate": f"+{config['rate']}%",
                    "pitch": f"+{config['pitch']}Hz",
                    "volume": f"+{config['volume']}%",
                    "emotion": emotion
                }]
            }
            
            # 使用轮询策略选择 TTS URL
            tts_url = self.get_next_tts_url()
            
            # 发送请求
            response = requests.post(f"{tts_url}/generate", json=data, timeout=60)
            
            if response.status_code == 200:
                content_length = len(response.content)
                
                # 检查文件大小
                if content_length < 1000:
                    print(f"❌ 生成的文件过小: {content_length} bytes")
                    return False
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                # 保存音频文件
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 生成成功: {os.path.basename(output_file)} ({content_length} bytes)")
                return True
            else:
                print(f"❌ 生成失败: {response.status_code} - {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ 生成音频时出错: {e}")
            return False
    
    def process_excel_file(self, filepath: str) -> bool:
        """处理单个 Excel 文件"""
        try:
            filename = os.path.basename(filepath)
            print(f"\n📊 处理文件: {filename}")
            
            # 读取 Excel 文件
            df = pd.read_excel(filepath)
            
            # 检查必要的列
            if '中文' not in df.columns:
                print(f"❌ 缺少 '中文' 列")
                return False
            
            # 准备批量数据
            batch_data = []
            for index, row in df.iterrows():
                text = str(row['中文']).strip()
                if not text or text == 'nan':
                    continue
                
                # 使用文件中的情绪类型
                emotion = str(row.get('情绪类型', 'Friendly')).strip()
                if not emotion or emotion == 'nan':
                    emotion = 'Friendly'
                
                # 生成固定格式的文件名
                audio_filename = f"audio_{index+1:04d}_{emotion}_{filename.split('.')[0]}.mp3"
                output_file = os.path.join(self.output_dir, audio_filename)
                
                batch_data.append({
                    'text': text,
                    'emotion': emotion,
                    'output_file': output_file,
                    'index': index,
                    'total_count': len(df)
                })
            
            print(f"📝 记录数量: {len(batch_data)} 条")
            print(f"🚀 多线程配置: {self.max_workers} 个线程")
            print(f"🌐 多API配置: {len(self.tts_urls)} 个服务")
            
            # 多线程处理
            success_count = 0
            start_time = datetime.now()
            
            print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # 将数据分成批次
            batch_size = max(1, len(batch_data) // (self.max_workers * 2))
            batches = [batch_data[i:i + batch_size] for i in range(0, len(batch_data), batch_size)]
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有批次任务
                future_to_batch = {executor.submit(self.process_batch, batch): batch for batch in batches}
                
                # 处理完成的任务
                completed_count = 0
                for future in as_completed(future_to_batch):
                    try:
                        batch_success = future.result()
                        success_count += batch_success
                        completed_count += len(future_to_batch[future])
                        
                        # 每完成100条显示进度
                        if completed_count % 100 == 0:
                            current_time = datetime.now()
                            elapsed_time = current_time - start_time
                            progress_percent = (completed_count / len(batch_data)) * 100
                            
                            print(f"\n📊 进度报告 [{completed_count:04d}/{len(batch_data)}] ({progress_percent:.1f}%)")
                            print(f"⏱️  已用时间: {str(elapsed_time).split('.')[0]}")
                            print(f"📈 处理速度: {completed_count/elapsed_time.total_seconds():.1f} 条/秒")
                            print("-" * 60)
                        
                    except Exception as e:
                        print(f"❌ 批次处理失败: {e}")
            
            end_time = datetime.now()
            total_time = end_time - start_time
            
            print(f"\n🎉 文件处理完成!")
            print(f"✅ 成功: {success_count}/{len(batch_data)} 个音频文件")
            print(f"⏰ 用时: {str(total_time).split('.')[0]}")
            print(f"📊 平均速度: {len(batch_data)/total_time.total_seconds():.1f} 条/秒")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 处理文件时出错: {e}")
            return False
    
    def process_batch(self, batch_data: List[Dict]) -> int:
        """处理一批音频数据"""
        success_count = 0
        
        for item in batch_data:
            text = item['text']
            emotion = item['emotion']
            output_file = item['output_file']
            index = item['index']
            total_count = item['total_count']
            
            if self.generate_audio(text, emotion, output_file):
                success_count += 1
                with self.lock:
                    print(f"[{index+1:04d}/{total_count}] ✅ {emotion:12s}")
            else:
                with self.lock:
                    print(f"[{index+1:04d}/{total_count}] ❌ {emotion:12s}")
        
        return success_count
    
    def process_all_excel_files(self) -> bool:
        """处理所有 Excel 文件"""
        try:
            # 查找所有 Excel 文件
            excel_files = []
            for file in os.listdir(self.input_dir):
                if file.lower().endswith(('.xlsx', '.xls')):
                    excel_files.append(os.path.join(self.input_dir, file))
            
            if not excel_files:
                print(f"❌ 目录中没有找到 Excel 文件: {self.input_dir}")
                return False
            
            # 按文件名排序
            excel_files.sort()
            
            print(f"🎯 EdgeTTS 统一批量处理")
            print(f"📁 项目根目录: {self.project_root}")
            print(f"📁 输入目录: {self.input_dir}")
            print(f"📁 输出目录: {self.output_dir}")
            print(f"📊 找到 {len(excel_files)} 个 Excel 文件")
            print("=" * 60)
            
            total_success = 0
            total_files = len(excel_files)
            overall_start_time = datetime.now()
            
            for file_index, filepath in enumerate(excel_files, 1):
                filename = os.path.basename(filepath)
                print(f"\n📄 [{file_index}/{total_files}] 处理文件: {filename}")
                print("=" * 60)
                
                # 处理单个文件
                if self.process_excel_file(filepath):
                    total_success += 1
                    print(f"✅ 文件 {filename} 处理成功")
                else:
                    print(f"❌ 文件 {filename} 处理失败")
                
                print("-" * 60)
            
            overall_end_time = datetime.now()
            overall_total_time = overall_end_time - overall_start_time
            
            print(f"\n🎉 所有文件处理完成!")
            print(f"✅ 成功: {total_success}/{total_files} 个文件")
            print(f"⏰ 总用时: {str(overall_total_time).split('.')[0]}")
            print(f"📁 统一输出目录: {self.output_dir}")
            
            return total_success > 0
            
        except Exception as e:
            print(f"❌ 批量处理时出错: {e}")
            return False

def main():
    """主函数 - 默认执行批量处理"""
    print("🚀 EdgeTTS 统一启动器")
    print("=" * 60)
    print("🔧 解决的问题:")
    print("   ✅ 固定输入和输出路径（都在TT_Live_AI_TTS项目内）")
    print("   ✅ 统一多API配置管理")
    print("   ✅ 标准化文件命名规则")
    print("   ✅ 统一配置管理")
    print("   ✅ 默认执行批量处理")
    print("=" * 60)
    
    # 初始化统一管理器
    manager = EdgeTTSUnifiedManager()
    
    # 检查 TTS 服务
    if not manager.check_tts_services():
        print("❌ TTS 服务未运行，请先启动 TTS 服务")
        print("💡 启动命令: cd /Volumes/M2/TT_Live_AI_TTS/02_TTS服务_语音合成系统 && python3 run_tts_TTS语音合成服务.py --port 5001")
        return False
    
    print("✅ 所有 TTS 服务运行正常")
    
    # 默认执行批量处理
    print("\n🎯 开始批量处理 18_批量输入_批量文件输入目录 下的所有 xlsx 文件")
    print("=" * 60)
    
    success = manager.process_all_excel_files()
    
    if success:
        print("\n🎉 所有音频生成完成!")
        print(f"📁 统一输出目录: {manager.output_dir}")
        print("=" * 60)
        print("📊 处理完成统计:")
        print(f"   📁 输出目录: {manager.output_dir}")
        print(f"   📂 输入目录: {manager.input_dir}")
        print(f"   🌐 API服务: {len(manager.tts_urls)} 个")
        print(f"   🧵 线程数: {manager.max_workers}")
    else:
        print("\n❌ 音频生成失败")
        print("💡 请检查:")
        print("   1. Excel 文件是否存在")
        print("   2. TTS 服务是否正常运行")
        print("   3. 网络连接是否正常")
    
    return success

if __name__ == "__main__":
    main()
