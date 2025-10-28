#!/usr/bin/env python3
"""
EdgeTTS 纯净英文字段处理器
只提取英文字段内容，完全屏蔽其他所有内容
"""
import os
import json
import pandas as pd
import asyncio
import edge_tts
import re
import time
from datetime import datetime

class PureEnglishProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        # 加载配置
        with open('EdgeTTS_统一配置.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self.config = config_data['EdgeTTS_统一配置']
        
        self.input_dir = self.config['路径配置']['输入目录']['默认路径']
        self.output_dir = self.config['路径配置']['输出目录']['完整路径']
        
        print(f"🎵 EdgeTTS 纯净英文字段处理器")
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🎯 只提取英文字段，屏蔽其他所有内容")
    
    def extract_pure_english(self, text):
        """提取纯净的英文内容"""
        if not text or text == 'nan':
            return ""
        
        text = str(text)
        
        # 1. 移除所有元数据标记
        metadata_patterns = [
            r'\(pause\)', r'\(Pause\)', r'\(PAUSE\)',
            r'\(break\)', r'\(Break\)', r'\(BREAK\)',
            r'\(for real\)', r'\(For Real\)', r'\(FOR REAL\)',
            r'\(right\)', r'\(Right\)', r'\(RIGHT\)',
            r'\(listen\)', r'\(Listen\)', r'\(LISTEN\)',
            r'\(trust me\)', r'\(Trust Me\)', r'\(TRUST ME\)',
            r'\(actually\)', r'\(Actually\)', r'\(ACTUALLY\)',
            r'\(get this\)', r'\(Get This\)', r'\(GET THIS\)'
        ]
        
        for pattern in metadata_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 2. 移除所有可能被误识别的内容
        # 移除购物车相关内容
        text = re.sub(r'Add to cart.*?off', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'Don\'t miss it!', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Cosmetic product.*?sensitive areas\.', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # 3. 移除任何看起来像URL或链接的内容
        text = re.sub(r'http[s]?://[^\s]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'www\.[^\s]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
        
        # 4. 移除数字和百分比
        text = re.sub(r'\d+%', '', text)
        text = re.sub(r'\d+pc[s]?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d+ off', '', text, flags=re.IGNORECASE)
        
        # 5. 只保留基本的英文句子
        # 移除多余的标点符号
        text = re.sub(r'[^\w\s.,!?]', ' ', text)
        
        # 6. 清理空格
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # 7. 确保以句号结尾
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    async def generate_pure_english_audio(self, english_text, voice, output_file):
        """生成纯净英文音频"""
        try:
            # 提取纯净英文内容
            pure_text = self.extract_pure_english(english_text)
            if not pure_text:
                print(f"⚠️ 纯净文本为空，跳过: {os.path.basename(output_file)}")
                return False
            
            print(f"📝 原始文本: {english_text[:100]}...")
            print(f"📝 纯净文本: {pure_text}")
            
            # 创建 EdgeTTS 对象 - 使用纯净文本
            communicate = edge_tts.Communicate(pure_text, voice)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 生成音频
            await communicate.save(output_file)
            
            # 检查文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 1000:  # 大于1KB认为是正常音频
                    print(f"✅ 纯净音频生成成功: {os.path.basename(output_file)} ({file_size} bytes)")
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
    
    async def process_excel_file(self, file_path, max_rows=20):
        """处理单个 Excel 文件 - 只提取英文字段"""
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
                
                # 只获取英文字段，完全忽略其他字段
                english_text = str(row.get('英文', ''))
                voice = str(row.get('Voice', 'en-US-JennyNeural'))
                
                if not english_text or english_text == 'nan':
                    continue
                
                # 生成输出文件名
                file_base = os.path.splitext(os.path.basename(file_path))[0]
                voice_name = voice.split('-')[-1] if '-' in voice else 'Unknown'
                output_filename = f"pure_english_{index+1:04d}_{voice_name}.mp3"
                output_file = os.path.join(self.output_dir, f"{file_base}_PureEnglish", output_filename)
                
                # 生成纯净英文音频
                if await self.generate_pure_english_audio(english_text, voice, output_file):
                    success_count += 1
                else:
                    error_count += 1
                
                # 延迟避免速率限制
                await asyncio.sleep(2)
                
                # 进度显示
                if (index + 1) % 5 == 0:
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
        
        # 处理文件（限制20行用于测试）
        success = await self.process_excel_file(file_path, max_rows=20)
        
        if success:
            print("\n🎉 纯净英文字段处理测试成功!")
        else:
            print("\n❌ 纯净英文字段处理测试失败!")
        
        return success

def main():
    """主函数"""
    print("🎵 EdgeTTS 纯净英文字段处理器")
    print("=" * 60)
    print("🔧 特性:")
    print("   ✅ 只提取英文字段内容")
    print("   ✅ 完全屏蔽其他所有内容")
    print("   ✅ 移除所有元数据和标记")
    print("   ✅ 移除购物车和链接内容")
    print("   ✅ 生成纯净英文音频")
    print("=" * 60)
    
    processor = PureEnglishProcessor()
    success = asyncio.run(processor.process_first_file())
    
    if success:
        print("\n🎉 纯净英文字段处理完成!")
        print("💡 已完全屏蔽其他内容，只保留纯净英文")
    else:
        print("\n❌ 纯净英文字段处理失败!")
        print("💡 请检查配置和文件格式")
    
    return success

if __name__ == "__main__":
    main()
