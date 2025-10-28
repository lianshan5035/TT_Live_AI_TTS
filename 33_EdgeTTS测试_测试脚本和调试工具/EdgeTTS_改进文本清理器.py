#!/usr/bin/env python3
"""
EdgeTTS 改进文本清理器
专门解决 HTTP 链接音频问题
"""
import os
import json
import pandas as pd
import asyncio
import edge_tts
import re
import time
from datetime import datetime

class ImprovedTextProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        # 加载配置
        with open('EdgeTTS_统一配置.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self.config = config_data['EdgeTTS_统一配置']
        
        self.input_dir = self.config['路径配置']['输入目录']['默认路径']
        self.output_dir = self.config['路径配置']['输出目录']['完整路径']
        
        print(f"🎵 EdgeTTS 改进文本清理器")
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🎯 解决 HTTP 链接音频问题")
    
    def advanced_text_cleanup(self, text):
        """高级文本清理，防止 HTTP 链接音频问题"""
        if not text or text == 'nan':
            return ""
        
        text = str(text)
        
        # 1. 移除常见的元数据标记
        text = text.replace('(pause)', '')
        text = text.replace('(Pause)', '')
        text = text.replace('(PAUSE)', '')
        text = text.replace('(break)', '')
        text = text.replace('(Break)', '')
        text = text.replace('(BREAK)', '')
        
        # 2. 移除可能被误识别为URL的内容
        # 移除 "Add to cart" 等可能被误识别的内容
        text = re.sub(r'Add to cart', 'Add to shopping cart', text, flags=re.IGNORECASE)
        text = re.sub(r'cart', 'shopping cart', text, flags=re.IGNORECASE)
        
        # 3. 移除任何看起来像URL的内容
        url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}',
            r'[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(?=\s|$|[.!?])'
        ]
        
        for pattern in url_patterns:
            text = re.sub(pattern, '[URL_REMOVED]', text, flags=re.IGNORECASE)
        
        # 4. 移除可能被误识别为URL的缩写
        text = re.sub(r'\b[A-Z]{2,}\b', lambda m: m.group().lower() if len(m.group()) > 3 else m.group(), text)
        
        # 5. 清理多余的空格和标点
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\[URL_REMOVED\]', '', text)
        text = text.strip()
        
        return text
    
    async def generate_clean_audio(self, english_text, voice, output_file):
        """生成清理后的音频"""
        try:
            # 高级文本清理
            clean_text = self.advanced_text_cleanup(english_text)
            if not clean_text:
                print(f"⚠️ 清理后文本为空，跳过: {os.path.basename(output_file)}")
                return False
            
            # 创建 EdgeTTS 对象
            communicate = edge_tts.Communicate(clean_text, voice)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 生成音频
            await communicate.save(output_file)
            
            # 检查文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 1000:  # 大于1KB认为是正常音频
                    print(f"✅ 音频生成成功: {os.path.basename(output_file)} ({file_size} bytes)")
                    print(f"📝 清理后文本: {clean_text[:80]}...")
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
            process_rows = min(max_rows, total_rows)
            
            print(f"📈 总行数: {total_rows}, 处理行数: {process_rows}")
            
            success_count = 0
            error_count = 0
            
            for index in range(process_rows):
                row = df.iloc[index]
                
                # 获取英文字段和语音
                english_text = str(row.get('英文', ''))
                voice = str(row.get('Voice', 'en-US-JennyNeural'))
                
                if not english_text or english_text == 'nan':
                    continue
                
                # 生成输出文件名
                file_base = os.path.splitext(os.path.basename(file_path))[0]
                voice_name = voice.split('-')[-1] if '-' in voice else 'Unknown'
                output_filename = f"clean_{index+1:04d}_{voice_name}.mp3"
                output_file = os.path.join(self.output_dir, f"{file_base}_Clean", output_filename)
                
                # 生成音频
                if await self.generate_clean_audio(english_text, voice, output_file):
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
    
    async def process_first_file(self):
        """处理第一个文件进行测试"""
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
        # 获取第一个 Excel 文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        if not excel_files:
            print("❌ 没有找到 Excel 文件")
            return False
        
        first_file = excel_files[0]
        file_path = os.path.join(self.input_dir, first_file)
        
        print(f"📁 找到 {len(excel_files)} 个 Excel 文件")
        print(f"🎯 测试处理第一个文件: {first_file}")
        
        # 处理文件（限制50行用于测试）
        success = await self.process_excel_file(file_path, max_rows=50)
        
        if success:
            print("\n🎉 改进文本处理测试成功!")
        else:
            print("\n❌ 改进文本处理测试失败!")
        
        return success

def main():
    """主函数"""
    print("🎵 EdgeTTS 改进文本清理器")
    print("=" * 60)
    print("🔧 特性:")
    print("   ✅ 高级文本清理")
    print("   ✅ 防止 HTTP 链接音频问题")
    print("   ✅ 移除可能被误识别的内容")
    print("   ✅ 直接使用 EdgeTTS 库")
    print("   ✅ 异步处理提高效率")
    print("=" * 60)
    
    processor = ImprovedTextProcessor()
    success = asyncio.run(processor.process_first_file())
    
    if success:
        print("\n🎉 改进文本处理完成!")
        print("💡 已解决 HTTP 链接音频问题")
    else:
        print("\n❌ 改进文本处理失败!")
        print("💡 请检查配置和文件格式")
    
    return success

if __name__ == "__main__":
    main()
