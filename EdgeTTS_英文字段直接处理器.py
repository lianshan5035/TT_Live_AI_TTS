#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS 英文字段直接处理器
直接使用EdgeTTS库处理"英文"字段，避免API服务问题
"""

import os
import pandas as pd
import asyncio
import edge_tts
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class EnglishFieldDirectProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        self.input_dir = "18_批量输入_批量文件输入目录"
        self.output_dir = "20_输出文件_处理完成的音频文件"
        
        # 默认语音
        self.default_voice = "en-US-JennyNeural"
        
        print("🎵 EdgeTTS 英文字段直接处理器")
        print("=" * 60)
        print("🔧 严格执行的规则:")
        print("   ✅ 规则1: 只处理'英文'字段的内容")
        print("   ✅ 规则2: 忽略每个 xlsx 文件中所有行的 Voice 字段")
        print("   ✅ 规则3: 每个 xlsx 文件在输出目录下创建同名文件夹")
        print("   ✅ 规则4: 文件名格式: english_field_{行号}_{默认voice}.mp3")
        print("   ✅ 规则5: 直接使用EdgeTTS库，避免API服务问题")
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
    
    async def generate_audio_from_english_field(self, english_field_content, voice, output_file):
        """从英文字段内容生成音频"""
        try:
            # 清理英文字段内容
            clean_content = self.clean_english_field_content(english_field_content)
            if not clean_content:
                print(f"⚠️ '英文'字段内容为空，跳过: {os.path.basename(output_file)}")
                return False
            
            print(f"📝 英文字段内容: {clean_content[:100]}...")
            
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
                    print(f"✅ 音频生成成功: {os.path.basename(output_file)} ({file_size} bytes)")
                    return True
                else:
                    print(f"⚠️ 音频文件过小: {os.path.basename(output_file)} ({file_size} bytes)")
                    return False
            else:
                print(f"❌ 音频文件未生成: {os.path.basename(output_file)}")
                return False
                
        except Exception as e:
            print(f"❌ 音频生成失败: {e}")
            return False
    
    def process_excel_file_direct(self, file_path, max_rows=None):
        """直接处理单个Excel文件"""
        try:
            file_name = os.path.basename(file_path)
            file_base = os.path.splitext(file_name)[0]
            
            print(f"\n📁 处理文件: {file_name}")
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            total_rows = len(df)
            process_rows = min(max_rows or total_rows, total_rows)
            
            print(f"📊 总行数: {total_rows}, 处理行数: {process_rows}")
            
            # 创建输出目录
            file_output_dir = os.path.join(self.output_dir, file_base)
            os.makedirs(file_output_dir, exist_ok=True)
            
            # 使用默认语音
            default_voice = self.default_voice
            print(f"🎤 使用默认语音: {default_voice}")
            
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
                output_filename = f"english_field_{index+1:04d}_{default_voice}.mp3"
                output_file = os.path.join(file_output_dir, output_filename)
                
                print(f"\n--- 处理第 {index+1} 行 ---")
                print(f"英文字段内容: {english_field_content[:50]}...")
                
                # 直接生成音频
                result = asyncio.run(self.generate_audio_from_english_field(
                    english_field_content, default_voice, output_file
                ))
                
                if result:
                    success_count += 1
                else:
                    error_count += 1
                
                # 添加延迟避免过快请求
                if (index + 1) % 10 == 0:
                    delay = 2
                    print(f"⏳ 每10个文件延迟 {delay}秒...")
                    time.sleep(delay)
            
            print(f"\n📊 文件处理完成: {file_name}")
            print(f"✅ 成功: {success_count} 个音频")
            print(f"❌ 失败: {error_count} 个音频")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 处理文件失败: {e}")
            return False
    
    def process_all_files_direct(self):
        """直接处理所有Excel文件"""
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
        # 获取所有Excel文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        if not excel_files:
            print("❌ 没有找到Excel文件")
            return False
        
        print(f"📁 找到 {len(excel_files)} 个Excel文件")
        
        total_success = 0
        total_files = len(excel_files)
        
        for i, file_name in enumerate(excel_files, 1):
            file_path = os.path.join(self.input_dir, file_name)
            
            print(f"\n🔄 处理文件 {i}/{total_files}: {file_name}")
            
            # 读取文件获取总行数
            df = pd.read_excel(file_path)
            
            if self.process_excel_file_direct(file_path, max_rows=len(df)):
                total_success += 1
            
            # 文件间延迟
            if i < total_files:
                delay = 5
                print(f"⏳ 文件间延迟 {delay}秒...")
                time.sleep(delay)
        
        print(f"\n🎉 所有文件处理完成!")
        print(f"📊 统计: {total_success}/{total_files} 文件成功处理")
        
        return total_success > 0

def main():
    """主函数"""
    processor = EnglishFieldDirectProcessor()
    success = processor.process_all_files_direct()
    
    if success:
        print("\n🎉 英文字段直接处理完成!")
        print("💡 已严格按照规则处理所有 xlsx 文件")
    else:
        print("\n❌ 英文字段直接处理失败!")
        print("💡 请检查配置和文件格式")
    
    return success

if __name__ == "__main__":
    main()
