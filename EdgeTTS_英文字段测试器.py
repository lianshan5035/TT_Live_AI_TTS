#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS 英文字段测试器
专门测试"英文"字段内容的提取和处理
"""

import os
import pandas as pd
import asyncio
import edge_tts

class EnglishFieldTester:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        self.input_dir = "18_批量输入_批量文件输入目录"
        self.output_dir = "20_输出文件_处理完成的音频文件"
        
        print("🧪 EdgeTTS 英文字段测试器")
        print("=" * 50)
        print("🎯 测试目标: 验证'英文'字段内容提取和处理")
        print("=" * 50)
    
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
    
    def test_english_field_extraction(self):
        """测试英文字段提取"""
        print("\n📋 测试英文字段提取:")
        
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
        # 获取第一个Excel文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        if not excel_files:
            print("❌ 没有找到Excel文件")
            return False
        
        file_path = os.path.join(self.input_dir, excel_files[0])
        print(f"📁 测试文件: {excel_files[0]}")
        
        try:
            df = pd.read_excel(file_path)
            print(f"📊 总行数: {len(df)}")
            print(f"📋 列名: {list(df.columns)}")
            
            # 检查"英文"列是否存在
            if '英文' not in df.columns:
                print("❌ 没有找到'英文'列")
                return False
            
            print(f"✅ 找到'英文'列")
            
            # 测试前5行的英文字段内容
            print("\n📝 前5行英文字段内容:")
            for i in range(min(5, len(df))):
                english_content = str(df.iloc[i].get('英文', ''))
                clean_content = self.clean_english_field_content(english_content)
                
                print(f"\n第{i+1}行:")
                print(f"  原始内容: {english_content[:100]}...")
                print(f"  清理后内容: {clean_content[:100]}...")
                print(f"  内容长度: {len(clean_content)} 字符")
                
                if not clean_content:
                    print(f"  ⚠️ 内容为空，跳过")
                else:
                    print(f"  ✅ 内容有效")
            
            return True
            
        except Exception as e:
            print(f"❌ 读取Excel文件失败: {e}")
            return False
    
    async def test_single_audio_generation(self):
        """测试单个音频生成"""
        print("\n🎵 测试单个音频生成:")
        
        # 使用测试文本
        test_text = "This is a test audio generation for English field content."
        voice = "en-US-JennyNeural"
        
        # 创建输出目录
        test_output_dir = os.path.join(self.output_dir, "test_english_field")
        os.makedirs(test_output_dir, exist_ok=True)
        
        output_file = os.path.join(test_output_dir, "test_english_field.mp3")
        
        try:
            print(f"📝 测试文本: {test_text}")
            print(f"🎤 使用语音: {voice}")
            print(f"📁 输出文件: {output_file}")
            
            # 创建 EdgeTTS 对象
            communicate = edge_tts.Communicate(test_text, voice)
            
            # 生成音频
            await communicate.save(output_file)
            
            # 检查文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✅ 音频生成成功: {file_size} bytes")
                
                # 检查文件类型
                import subprocess
                result = subprocess.run(['file', output_file], capture_output=True, text=True)
                print(f"📄 文件类型: {result.stdout.strip()}")
                
                return True
            else:
                print(f"❌ 音频文件未生成")
                return False
                
        except Exception as e:
            print(f"❌ 音频生成失败: {e}")
            return False
    
    def test_real_english_content(self):
        """测试真实的英文字段内容"""
        print("\n📖 测试真实英文字段内容:")
        
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
        # 获取第一个Excel文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        if not excel_files:
            print("❌ 没有找到Excel文件")
            return False
        
        file_path = os.path.join(self.input_dir, excel_files[0])
        
        try:
            df = pd.read_excel(file_path)
            
            # 找到第一个有效的英文字段内容
            for i in range(min(10, len(df))):
                english_content = str(df.iloc[i].get('英文', ''))
                clean_content = self.clean_english_field_content(english_content)
                
                if clean_content and len(clean_content) > 50:  # 找到有效内容
                    print(f"📝 第{i+1}行英文字段内容:")
                    print(f"  内容: {clean_content[:200]}...")
                    print(f"  长度: {len(clean_content)} 字符")
                    
                    # 检查是否包含其他字段的内容
                    other_fields = ['ID', '产品', '类目', 'Voice', '情绪子型', '情绪类型', 'rate', 'pitch', 'volume', '中文', 'CTA', '估算时长秒', '语音']
                    contains_other_fields = False
                    
                    for field in other_fields:
                        if field in clean_content:
                            print(f"  ⚠️ 警告: 内容包含'{field}'字段")
                            contains_other_fields = True
                    
                    if not contains_other_fields:
                        print(f"  ✅ 内容纯净，只包含英文字段内容")
                    else:
                        print(f"  ❌ 内容不纯净，包含其他字段")
                    
                    return clean_content
            
            print("❌ 没有找到有效的英文字段内容")
            return None
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return None

def main():
    """主函数"""
    tester = EnglishFieldTester()
    
    # 测试1: 英文字段提取
    print("🧪 测试1: 英文字段提取")
    if not tester.test_english_field_extraction():
        print("❌ 英文字段提取测试失败")
        return False
    
    # 测试2: 单个音频生成
    print("\n🧪 测试2: 单个音频生成")
    audio_result = asyncio.run(tester.test_single_audio_generation())
    if not audio_result:
        print("❌ 单个音频生成测试失败")
        return False
    
    # 测试3: 真实英文字段内容
    print("\n🧪 测试3: 真实英文字段内容")
    real_content = tester.test_real_english_content()
    if not real_content:
        print("❌ 真实英文字段内容测试失败")
        return False
    
    print("\n🎉 所有测试完成!")
    print("✅ 英文字段提取正常")
    print("✅ 音频生成功能正常")
    print("✅ 真实内容处理正常")
    
    return True

if __name__ == "__main__":
    main()
