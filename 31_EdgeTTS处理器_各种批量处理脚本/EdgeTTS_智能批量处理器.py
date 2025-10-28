#!/usr/bin/env python3
"""
EdgeTTS 智能批量处理器 - 带延迟和错误恢复
解决 EdgeTTS 速率限制和封禁问题
"""
import os
import json
import pandas as pd
import requests
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class SmartBatchProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        # 加载配置
        with open('EdgeTTS_统一配置.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self.config = config_data['EdgeTTS_统一配置']
        
        self.input_dir = self.config['路径配置']['输入目录']['默认路径']
        self.output_dir = self.config['路径配置']['输出目录']['完整路径']
        self.tts_urls = [service['URL'] for service in self.config['API配置']['多API服务']['服务列表']]
        
        # 智能延迟配置
        self.base_delay = 2.0  # 基础延迟（秒）
        self.max_delay = 10.0  # 最大延迟（秒）
        self.delay_increment = 0.5  # 延迟递增
        self.current_delay = self.base_delay
        
        # 错误统计
        self.error_count = 0
        self.success_count = 0
        self.max_errors = 10  # 最大错误次数
        
        print(f"🚀 智能批量处理器启动")
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🌐 API服务: {len(self.tts_urls)} 个")
        print(f"⏱️ 基础延迟: {self.base_delay}秒")
    
    def check_tts_services(self):
        """检查 TTS 服务状态"""
        available_services = []
        for i, url in enumerate(self.tts_urls, 1):
            try:
                response = requests.get(f'{url}/status', timeout=5)
                if response.status_code == 200:
                    available_services.append(url)
                    print(f"✅ TTS 服务 {i} ({url}) 运行正常")
                else:
                    print(f"❌ TTS 服务 {i} ({url}) 响应异常: {response.status_code}")
            except Exception as e:
                print(f"❌ TTS 服务 {i} ({url}) 连接失败: {e}")
        
        return available_services
    
    def get_emotion_config(self, emotion_name):
        """获取情绪配置"""
        emotion_map = {
            '兴奋型': 'Excited',
            '自信型': 'Confident', 
            '共情型': 'Empathetic',
            '舒缓型': 'Calm',
            '活泼型': 'Playful',
            '紧迫型': 'Urgent',
            '权威型': 'Authoritative',
            '友好型': 'Friendly',
            '激励型': 'Inspirational',
            '严肃型': 'Serious',
            '神秘型': 'Mysterious',
            '感恩型': 'Grateful'
        }
        
        english_emotion = emotion_map.get(emotion_name, 'Friendly')
        emotions = self.config['情绪配置']['A3标准12种情绪']
        
        if english_emotion in emotions:
            return emotions[english_emotion]
        else:
            return emotions['Friendly']  # 默认配置
    
    def generate_audio_with_retry(self, text, voice, emotion, output_file, max_retries=3):
        """带重试机制的音频生成"""
        for attempt in range(max_retries):
            try:
                # 智能延迟
                if attempt > 0:
                    delay = self.current_delay + random.uniform(0, 2)
                    print(f"⏳ 重试前等待 {delay:.1f}秒...")
                    time.sleep(delay)
                
                # 随机选择 API 服务
                api_url = random.choice(self.tts_urls)
                
                # 获取情绪配置
                emotion_config = self.get_emotion_config(emotion)
                
                # 构建请求数据
                data = {
                    "product_name": "智能批量处理",
                    "scripts": [{
                        "text": text,
                        "voice": voice,
                        "rate": emotion_config.get('rate', '+0%'),
                        "pitch": emotion_config.get('pitch', '+0Hz'),
                        "volume": emotion_config.get('volume', '+0%'),
                        "emotion": emotion
                    }]
                }
                
                # 发送请求
                response = requests.post(
                    f'{api_url}/generate',
                    json=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    # 检查响应内容长度
                    content_length = len(response.content)
                    if content_length < 1000:
                        print(f"⚠️ 响应内容过小 ({content_length} bytes)，可能生成失败")
                        if attempt < max_retries - 1:
                            self.current_delay = min(self.current_delay + self.delay_increment, self.max_delay)
                            continue
                    
                    # 保存文件
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                    
                    # 重置延迟
                    self.current_delay = self.base_delay
                    self.success_count += 1
                    print(f"✅ 音频生成成功: {os.path.basename(output_file)} ({content_length} bytes)")
                    return True
                    
                else:
                    print(f"❌ API 响应错误: {response.status_code}")
                    if attempt < max_retries - 1:
                        self.current_delay = min(self.current_delay + self.delay_increment, self.max_delay)
                        continue
                        
            except Exception as e:
                print(f"❌ 生成失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    self.current_delay = min(self.current_delay + self.delay_increment, self.max_delay)
                    continue
        
        self.error_count += 1
        print(f"❌ 音频生成最终失败: {os.path.basename(output_file)}")
        return False
    
    def process_excel_file(self, file_path):
        """处理单个 Excel 文件"""
        print(f"\n📊 处理文件: {os.path.basename(file_path)}")
        
        try:
            df = pd.read_excel(file_path)
            total_rows = len(df)
            print(f"📈 总行数: {total_rows}")
            
            success_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                # 检查错误次数
                if self.error_count >= self.max_errors:
                    print(f"❌ 错误次数过多 ({self.error_count})，停止处理")
                    break
                
                # 智能延迟
                if index > 0:
                    delay = self.current_delay + random.uniform(0, 1)
                    time.sleep(delay)
                
                # 获取数据
                text = str(row.get('中文', ''))
                voice = str(row.get('Voice', 'en-US-JennyNeural'))
                emotion = str(row.get('情绪类型', '友好型'))
                
                if not text or text == 'nan':
                    continue
                
                # 生成输出文件名
                file_base = os.path.splitext(os.path.basename(file_path))[0]
                output_filename = f"tts_{index+1:04d}_{emotion}_{voice.split('-')[-1]}_dyn.mp3"
                output_file = os.path.join(self.output_dir, f"{file_base}_{voice.split('-')[-1]}", output_filename)
                
                # 生成音频
                if self.generate_audio_with_retry(text, voice, emotion, output_file):
                    success_count += 1
                else:
                    error_count += 1
                
                # 进度显示
                if (index + 1) % 10 == 0:
                    print(f"📊 进度: {index + 1}/{total_rows} ({success_count} 成功, {error_count} 失败)")
            
            print(f"✅ 文件处理完成: {success_count} 成功, {error_count} 失败")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 处理文件失败: {e}")
            return False
    
    def process_all_files(self):
        """处理所有 Excel 文件"""
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
        # 检查 TTS 服务
        available_services = self.check_tts_services()
        if not available_services:
            print("❌ 没有可用的 TTS 服务")
            return False
        
        self.tts_urls = available_services
        print(f"🎯 使用 {len(self.tts_urls)} 个 TTS 服务")
        
        # 获取所有 Excel 文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        if not excel_files:
            print("❌ 没有找到 Excel 文件")
            return False
        
        print(f"📁 找到 {len(excel_files)} 个 Excel 文件")
        
        # 处理每个文件
        total_success = 0
        total_files = len(excel_files)
        
        for i, file_name in enumerate(excel_files, 1):
            file_path = os.path.join(self.input_dir, file_name)
            print(f"\n🔄 处理文件 {i}/{total_files}: {file_name}")
            
            if self.process_excel_file(file_path):
                total_success += 1
            
            # 文件间延迟
            if i < total_files:
                delay = 5 + random.uniform(0, 3)
                print(f"⏳ 文件间延迟 {delay:.1f}秒...")
                time.sleep(delay)
        
        print(f"\n🎉 批量处理完成!")
        print(f"📊 统计: {total_success}/{total_files} 文件成功处理")
        print(f"✅ 成功: {self.success_count} 个音频")
        print(f"❌ 失败: {self.error_count} 个音频")
        
        return total_success > 0

def main():
    """主函数"""
    print("🚀 EdgeTTS 智能批量处理器")
    print("=" * 60)
    print("🔧 特性:")
    print("   ✅ 智能延迟避免速率限制")
    print("   ✅ 自动重试机制")
    print("   ✅ 错误恢复和统计")
    print("   ✅ 多 API 负载均衡")
    print("=" * 60)
    
    processor = SmartBatchProcessor()
    success = processor.process_all_files()
    
    if success:
        print("\n🎉 智能批量处理完成!")
    else:
        print("\n❌ 批量处理失败")
    
    return success

if __name__ == "__main__":
    main()
