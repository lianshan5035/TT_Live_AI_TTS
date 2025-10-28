#!/usr/bin/env python3
"""
EdgeTTS 正确批量处理器
专门处理 18_批量输入_批量文件输入目录 下的 xlsx 文件
只输出口播正文，不输出元数据
"""
import os
import json
import pandas as pd
import asyncio
import edge_tts
import time
from datetime import datetime

class CorrectBatchProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        # 加载配置
        with open('EdgeTTS_统一配置.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self.config = config_data['EdgeTTS_统一配置']
        
        self.input_dir = self.config['路径配置']['输入目录']['默认路径']
        self.output_dir = self.config['路径配置']['输出目录']['完整路径']
        
        print(f"🎵 EdgeTTS 正确批量处理器启动")
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🎯 专门处理 xlsx 文件的口播正文")
    
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
    
    def clean_text(self, text):
        """清理文本，只保留口播正文"""
        if not text or text == 'nan':
            return ""
        
        # 移除常见的元数据标记
        text = str(text)
        
        # 移除 (pause) 等标记
        text = text.replace('(pause)', '')
        text = text.replace('(Pause)', '')
        text = text.replace('(PAUSE)', '')
        
        # 移除其他可能的元数据
        text = text.replace('(break)', '')
        text = text.replace('(Break)', '')
        text = text.replace('(BREAK)', '')
        
        # 清理多余的空格
        text = ' '.join(text.split())
        
        return text.strip()
    
    async def generate_audio_direct(self, text, voice, emotion, output_file):
        """直接使用 EdgeTTS 生成音频"""
        try:
            # 清理文本
            clean_text = self.clean_text(text)
            if not clean_text:
                print(f"⚠️ 文本为空，跳过: {os.path.basename(output_file)}")
                return False
            
            # 获取情绪配置
            emotion_config = self.get_emotion_config(emotion)
            
            # 构建 SSML
            rate = emotion_config.get('rate', '+0%')
            pitch = emotion_config.get('pitch', '+0Hz')
            volume = emotion_config.get('volume', '+0%')
            
            ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US"><voice name="{voice}"><prosody rate="{rate}" pitch="{pitch}" volume="{volume}">{clean_text}</prosody></voice></speak>'
            
            # 创建 EdgeTTS 对象
            communicate = edge_tts.Communicate(ssml, voice)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 生成音频
            await communicate.save(output_file)
            
            # 检查文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 1000:  # 大于1KB认为是正常音频
                    print(f"✅ 音频生成成功: {os.path.basename(output_file)} ({file_size} bytes)")
                    print(f"📝 文本内容: {clean_text[:50]}...")
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
    
    async def process_excel_file(self, file_path, max_rows=50):
        """处理单个 Excel 文件"""
        print(f"\n📊 处理文件: {os.path.basename(file_path)}")
        
        try:
            df = pd.read_excel(file_path)
            total_rows = len(df)
            process_rows = min(max_rows, total_rows)  # 限制处理行数
            
            print(f"📈 总行数: {total_rows}, 处理行数: {process_rows}")
            
            success_count = 0
            error_count = 0
            
            for index in range(process_rows):
                row = df.iloc[index]
                
                # 获取数据 - 使用英文字段作为口播正文
                text = str(row.get('英文', ''))
                voice = str(row.get('Voice', 'en-US-JennyNeural'))
                emotion = str(row.get('情绪类型', '友好型'))
                
                if not text or text == 'nan':
                    continue
                
                # 生成输出文件名
                file_base = os.path.splitext(os.path.basename(file_path))[0]
                output_filename = f"tts_{index+1:04d}_{emotion}_{voice.split('-')[-1]}_clean.mp3"
                output_file = os.path.join(self.output_dir, f"{file_base}_{voice.split('-')[-1]}_clean", output_filename)
                
                # 生成音频
                if await self.generate_audio_direct(text, voice, emotion, output_file):
                    success_count += 1
                else:
                    error_count += 1
                
                # 延迟避免速率限制
                await asyncio.sleep(3)
                
                # 进度显示
                if (index + 1) % 10 == 0:
                    print(f"📊 进度: {index + 1}/{process_rows} ({success_count} 成功, {error_count} 失败)")
            
            print(f"✅ 文件处理完成: {success_count} 成功, {error_count} 失败")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 处理文件失败: {e}")
            return False
    
    async def process_all_excel_files(self):
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
            
            if await self.process_excel_file(file_path, max_rows=50):
                total_success += 1
            
            # 文件间延迟
            if i < total_files:
                delay = 10
                print(f"⏳ 文件间延迟 {delay}秒...")
                await asyncio.sleep(delay)
        
        print(f"\n🎉 批量处理完成!")
        print(f"📊 统计: {total_success}/{total_files} 文件成功处理")
        
        return total_success > 0

def main():
    """主函数"""
    print("🎵 EdgeTTS 正确批量处理器")
    print("=" * 60)
    print("🔧 特性:")
    print("   ✅ 专门处理 xlsx 文件")
    print("   ✅ 只输出口播正文")
    print("   ✅ 清理元数据标记")
    print("   ✅ 直接使用 EdgeTTS 库")
    print("   ✅ 异步处理提高效率")
    print("=" * 60)
    
    processor = CorrectBatchProcessor()
    success = asyncio.run(processor.process_all_excel_files())
    
    if success:
        print("\n🎉 正确批量处理完成!")
        print("💡 所有 xlsx 文件的口播正文已生成")
    else:
        print("\n❌ 批量处理失败!")
        print("💡 请检查配置和文件格式")
    
    return success

if __name__ == "__main__":
    main()
