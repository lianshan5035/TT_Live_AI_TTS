#!/usr/bin/env python3
"""
EdgeTTS 最终规则处理器
严格按照用户规则执行批量音频生成
"""
import os
import json
import pandas as pd
import asyncio
import edge_tts
import time
from datetime import datetime

class FinalRuleProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        # 加载配置
        with open('EdgeTTS_统一配置.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self.config = config_data['EdgeTTS_统一配置']
        
        self.input_dir = self.config['路径配置']['输入目录']['默认路径']
        self.output_dir = self.config['路径配置']['输出目录']['完整路径']
        
        print(f"🎵 EdgeTTS 最终规则处理器")
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        print("=" * 60)
        print("📋 执行规则:")
        print("   1. ✅ 只处理'英文'字段的内容")
        print("   2. ✅ 每个 xlsx 文件的 3200 条音频使用统一 voice")
        print("   3. ✅ 所有音频文件直接放在总文件夹下，不创建子文件夹")
        print("   4. ✅ 文件名格式: {xlsx文件名}_english_field_{行号}_{voice名}.mp3")
        print("=" * 60)
    
    def clean_english_field_content(self, text):
        """清理英文字段的内容"""
        if not text or text == 'nan':
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
                print(f"⚠️ 英文字段内容为空，跳过: {os.path.basename(output_file)}")
                return False
            
            print(f"📝 英文字段内容: {clean_content}")
            
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
    
    def get_file_voice(self, df):
        """获取文件使用的统一 voice - 规则2"""
        # 统计所有 voice 的使用频率
        voice_counts = {}
        for index in range(len(df)):
            voice = str(df.iloc[index].get('Voice', 'en-US-JennyNeural'))
            voice_counts[voice] = voice_counts.get(voice, 0) + 1
        
        # 选择使用最多的 voice
        most_used_voice = max(voice_counts, key=voice_counts.get)
        print(f"📊 Voice 统计: {voice_counts}")
        print(f"🎤 选择统一 Voice: {most_used_voice}")
        
        return most_used_voice
    
    async def process_excel_file(self, file_path, max_rows=10):
        """处理单个 Excel 文件 - 严格按照规则执行"""
        print(f"\n📊 处理文件: {os.path.basename(file_path)}")
        
        try:
            df = pd.read_excel(file_path)
            total_rows = len(df)
            process_rows = min(max_rows, total_rows)
            
            print(f"📈 总行数: {total_rows}, 处理行数: {process_rows}")
            print(f"📋 列名: {list(df.columns)}")
            
            # 规则2: 获取文件使用的统一 voice
            file_voice = self.get_file_voice(df)
            
            success_count = 0
            error_count = 0
            
            for index in range(process_rows):
                row = df.iloc[index]
                
                # 规则1: 只获取"英文"字段的内容
                english_field_content = str(row.get('英文', ''))
                
                print(f"\n--- 处理第 {index+1} 行 ---")
                print(f"英文字段内容: {english_field_content}")
                print(f"使用统一语音: {file_voice}")
                
                if not english_field_content or english_field_content == 'nan':
                    print("⚠️ 英文字段内容为空，跳过")
                    continue
                
                # 规则3&4: 生成输出文件名 - 直接放在总文件夹下，不创建子文件夹
                file_base = os.path.splitext(os.path.basename(file_path))[0]
                voice_name = file_voice.split('-')[-1] if '-' in file_voice else 'Unknown'
                output_filename = f"{file_base}_english_field_{index+1:04d}_{voice_name}.mp3"
                output_file = os.path.join(self.output_dir, output_filename)
                
                # 生成音频（使用统一的 voice）
                if await self.generate_audio_from_english_field(english_field_content, file_voice, output_file):
                    success_count += 1
                else:
                    error_count += 1
                
                # 延迟避免速率限制
                await asyncio.sleep(3)
            
            print(f"\n✅ 文件处理完成: {success_count} 成功, {error_count} 失败")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 处理文件失败: {e}")
            return False
    
    async def process_all_files(self):
        """处理所有 Excel 文件"""
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
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
            
            # 读取文件获取总行数
            df = pd.read_excel(file_path)
            
            if await self.process_excel_file(file_path, max_rows=len(df)):
                total_success += 1
            
            # 文件间延迟
            if i < total_files:
                delay = 5
                print(f"⏳ 文件间延迟 {delay}秒...")
                await asyncio.sleep(delay)
        
        print(f"\n🎉 所有文件处理完成!")
        print(f"📊 统计: {total_success}/{total_files} 文件成功处理")
        
        return total_success > 0

def main():
    """主函数"""
    print("🎵 EdgeTTS 最终规则处理器")
    print("=" * 60)
    print("🔧 严格执行的规则:")
    print("   ✅ 规则1: 只处理'英文'字段的内容")
    print("   ✅ 规则2: 每个 xlsx 文件的 3200 条音频使用统一 voice")
    print("   ✅ 规则3: 所有音频文件直接放在总文件夹下，不创建子文件夹")
    print("   ✅ 规则4: 文件名格式: {xlsx文件名}_english_field_{行号}_{voice名}.mp3")
    print("=" * 60)
    
    processor = FinalRuleProcessor()
    success = asyncio.run(processor.process_all_files())
    
    if success:
        print("\n🎉 最终规则处理完成!")
        print("💡 已严格按照规则处理所有 xlsx 文件")
    else:
        print("\n❌ 最终规则处理失败!")
        print("💡 请检查配置和文件格式")
    
    return success

if __name__ == "__main__":
    main()
