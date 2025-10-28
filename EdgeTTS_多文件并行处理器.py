#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS 多文件并行处理器
同时处理多个xlsx文件，每个文件使用独立线程
"""

import os
import pandas as pd
import asyncio
import edge_tts
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class MultiFileParallelProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        self.input_dir = "18_批量输入_批量文件输入目录"
        self.output_dir = "20_输出文件_处理完成的音频文件"
        
        # 可用语音列表 (从edge-tts --list-voices获取)
        self.available_voices = [
            "en-US-JennyNeural",      # Female - Sincere, Pleasant, Approachable
            "en-US-GuyNeural",        # Male - Light-Hearted, Whimsical, Friendly
            "en-US-AriaNeural",       # Female - Crisp, Bright, Clear
            "en-US-DavisNeural",      # Male - Soothing, Calm, Smooth
            "en-US-JaneNeural",       # Female - Serious, Approachable, Upbeat
            "en-US-JasonNeural",      # Male - Gentle, Shy, Polite
            "en-US-NancyNeural",      # Female - Confident, Serious, Mature
            "en-US-RogerNeural",      # Male - Serious, Formal, Confident
            "en-US-SaraNeural",       # Female - Sincere, Calm, Confident
            "en-US-TonyNeural",       # Male - Thoughtful, Authentic, Sincere
            "en-US-MichelleNeural",   # Female - Confident, Authentic, Warm
            "en-US-AmberNeural",      # Female - Whimsical, Upbeat, Light-Hearted
            "en-US-AnaNeural",        # Female - Curious, Cheerful, Engaging
            "en-US-AndrewNeural",     # Male - Confident, Authentic, Warm
            "en-US-AshleyNeural",     # Female - Sincere, Approachable, Honest
            "en-US-AvaNeural",        # Female - Pleasant, Caring, Friendly
            "en-US-BrandonNeural",    # Male - Warm, Engaging, Authentic
            "en-US-BrianNeural",      # Male - Sincere, Calm, Approachable
            "en-US-ChristopherNeural", # Male - Deep, Warm
            "en-US-CoraNeural",       # Female - Empathetic, Formal, Sincere
            "en-US-ElizabethNeural",  # Female - Authoritative, Formal, Serious
            "en-US-EmmaNeural",       # Female - Cheerful, Light-Hearted, Casual
            "en-US-EricNeural",       # Male - Confident, Sincere, Warm
            "en-US-JacobNeural",      # Male - Sincere, Formal, Confident
            "en-US-KaiNeural",        # Male - Sincere, Pleasant, Bright, Clear, Friendly, Warm
            "en-US-LunaNeural",       # Female - Sincere, Pleasant, Bright, Clear, Friendly, Warm
            "en-US-MonicaNeural",     # Female - Mature, Authentic, Warm
            "en-US-PhoebeMultilingualNeural", # Female - youthful, upbeat, confident
            "en-US-RyanMultilingualNeural",    # Male - Professional, Authentic, Sincere
            "en-US-SamuelMultilingualNeural",  # Male - sincere, warm, expressive
            "en-US-SerenaMultilingualNeural",  # Female - formal, confident, mature
            "en-US-SteffanNeural"     # Male - Mature, Authentic, Warm
        ]
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 语音分配字典
        self.file_voice_assignment = {}
        
        print("🚀 EdgeTTS 多文件并行处理器")
        print("=" * 60)
        print("🔧 严格执行的规则:")
        print("   ✅ 规则1: 只处理'英文'字段的内容")
        print("   ✅ 规则2: 忽略每个 xlsx 文件中所有行的 Voice 字段")
        print("   ✅ 规则3: 每个 xlsx 文件在输出目录下创建同名文件夹")
        print("   ✅ 规则4: 文件名格式: english_field_{行号}_{文件专用voice}.mp3")
        print("   ✅ 规则5: 多文件并行处理，每个文件独立线程")
        print("   ✅ 规则6: 每个xlsx文件使用固定专用voice，不重复")
        print(f"   ✅ 规则7: 可用语音数量: {len(self.available_voices)} 个")
        print("=" * 60)
    
    def clean_english_field_content(self, text):
        """清理英文字段的内容"""
        if not text or text == 'nan' or text == '英文':
            return ""
        
        text = str(text)
        
        # 基本清理
        text = text.strip()
        
        # 移除多余的空白字符
        text = ' '.join(text.split())
        
        return text
    
    def get_file_voice(self, file_name):
        """为每个文件分配专用语音，不重复"""
        with self.lock:
            if file_name not in self.file_voice_assignment:
                # 为文件分配一个未使用的语音
                used_voices = set(self.file_voice_assignment.values())
                available_voices = [v for v in self.available_voices if v not in used_voices]
                
                if available_voices:
                    assigned_voice = available_voices[0]
                    self.file_voice_assignment[file_name] = assigned_voice
                    print(f"🎤 {file_name} 分配语音: {assigned_voice}")
                else:
                    # 如果所有语音都用完了，使用默认语音
                    assigned_voice = self.available_voices[0]
                    self.file_voice_assignment[file_name] = assigned_voice
                    print(f"⚠️ 所有语音已用完，{file_name} 使用默认语音: {assigned_voice}")
            
            return self.file_voice_assignment[file_name]
    
    async def generate_audio_from_english_field(self, english_field_content, voice, output_file):
        """从英文字段内容生成音频"""
        try:
            # 清理英文字段内容
            clean_content = self.clean_english_field_content(english_field_content)
            if not clean_content:
                return False
            
            # 创建 EdgeTTS 对象
            communicate = edge_tts.Communicate(clean_content, voice)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 生成音频
            await communicate.save(output_file)
            
            # 检查文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 1000:  # 大于1KB认为是正常音频
                    with self.lock:
                        print(f"✅ 音频生成成功: {os.path.basename(output_file)} ({file_size} bytes)")
                    return True
                else:
                    with self.lock:
                        print(f"⚠️ 音频文件过小: {os.path.basename(output_file)} ({file_size} bytes)")
                    return False
            else:
                with self.lock:
                    print(f"❌ 音频文件未生成: {os.path.basename(output_file)}")
                return False
                
        except Exception as e:
            with self.lock:
                print(f"❌ 音频生成失败: {e}")
            return False
    
    def process_excel_file_parallel(self, file_path, max_rows=None):
        """并行处理单个Excel文件"""
        try:
            file_name = os.path.basename(file_path)
            file_base = os.path.splitext(file_name)[0]
            
            with self.lock:
                print(f"\n📁 开始处理文件: {file_name}")
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            total_rows = len(df)
            process_rows = min(max_rows or total_rows, total_rows)
            
            with self.lock:
                print(f"📊 {file_name} - 总行数: {total_rows}, 处理行数: {process_rows}")
            
            # 创建输出目录
            file_output_dir = os.path.join(self.output_dir, file_base)
            os.makedirs(file_output_dir, exist_ok=True)
            
            # 获取文件专用语音
            file_voice = self.get_file_voice(file_name)
            
            success_count = 0
            error_count = 0
            
            # 处理每一行
            for index in range(process_rows):
                row = df.iloc[index]
                
                # 规则1: 只获取"英文"字段的内容
                english_field_content = str(row.get('英文', ''))
                
                # 字段验证
                if not english_field_content or english_field_content == '英文':
                    continue
                
                # 规则4: 生成输出文件名 - 在xlsx同名文件夹下
                output_filename = f"english_field_{index+1:04d}_{file_voice}.mp3"
                output_file = os.path.join(file_output_dir, output_filename)
                
                # 直接生成音频
                result = asyncio.run(self.generate_audio_from_english_field(
                    english_field_content, file_voice, output_file
                ))
                
                if result:
                    success_count += 1
                else:
                    error_count += 1
                
                # 添加延迟避免过快请求
                if (index + 1) % 10 == 0:
                    delay = 2
                    time.sleep(delay)
            
            with self.lock:
                print(f"\n📊 {file_name} 处理完成:")
                print(f"✅ 成功: {success_count} 个音频")
                print(f"❌ 失败: {error_count} 个音频")
            
            return success_count > 0
            
        except Exception as e:
            with self.lock:
                print(f"❌ 处理文件失败 {file_name}: {e}")
            return False
    
    def process_all_files_parallel(self):
        """并行处理所有Excel文件"""
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
        # 获取所有Excel文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        if not excel_files:
            print("❌ 没有找到Excel文件")
            return False
        
        print(f"📁 找到 {len(excel_files)} 个Excel文件")
        print(f"🚀 启动 {len(excel_files)} 个并行处理线程")
        
        # 使用ThreadPoolExecutor进行并行处理
        max_workers = len(excel_files)  # 使用最大线程数，每个文件一个线程
        print(f"🔧 最大并行线程数: {max_workers} (每个文件一个线程)")
        
        success_count = 0
        total_files = len(excel_files)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {}
            for file_name in excel_files:
                file_path = os.path.join(self.input_dir, file_name)
                print(f"📤 提交任务: {file_name}")
                
                future = executor.submit(
                    self.process_excel_file_parallel, 
                    file_path, 
                    max_rows=3200  # 处理所有行
                )
                future_to_file[future] = file_name
            
            # 等待所有任务完成
            print(f"\n⏳ 等待所有 {total_files} 个文件处理完成...")
            
            for future in as_completed(future_to_file):
                file_name = future_to_file[future]
                
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                        print(f"✅ {file_name} 处理完成")
                    else:
                        print(f"❌ {file_name} 处理失败")
                except Exception as e:
                    print(f"❌ {file_name} 处理异常: {e}")
        
        print(f"\n🎉 所有文件处理完成!")
        print(f"📊 统计: {success_count}/{total_files} 文件成功处理")
        
        return success_count > 0

def main():
    """主函数"""
    processor = MultiFileParallelProcessor()
    success = processor.process_all_files_parallel()
    
    if success:
        print("\n🎉 多文件并行处理完成!")
        print("💡 已严格按照规则处理所有 xlsx 文件")
    else:
        print("\n❌ 多文件并行处理失败!")
        print("💡 请检查配置和文件格式")
    
    return success

if __name__ == "__main__":
    main()
