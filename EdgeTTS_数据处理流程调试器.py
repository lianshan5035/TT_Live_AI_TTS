#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS 数据处理流程调试器
详细跟踪数据处理流程，找出为什么每个音频都是"quickstory"开头
"""

import os
import pandas as pd
import asyncio
import edge_tts
import time

class DataProcessingDebugger:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        self.input_dir = "18_批量输入_批量文件输入目录"
        self.output_dir = "20_输出文件_处理完成的音频文件"
        
        # 默认语音
        self.default_voice = "en-US-JennyNeural"
        
        print("🔍 EdgeTTS 数据处理流程调试器")
        print("=" * 60)
        print("🎯 调试目标: 找出为什么每个音频都是'quickstory'开头")
        print("=" * 60)
    
    def debug_data_processing_flow(self):
        """调试数据处理流程"""
        print("\n📊 步骤1: 输入数据处理")
        print("-" * 40)
        
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
        # 获取第一个Excel文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        if not excel_files:
            print("❌ 没有找到Excel文件")
            return False
        
        file_path = os.path.join(self.input_dir, excel_files[0])
        print(f"📁 Excel文件: {excel_files[0]}")
        
        try:
            # 步骤1: pandas读取
            print("\n📖 步骤1.1: pandas读取Excel文件")
            df = pd.read_excel(file_path)
            print(f"✅ 成功读取Excel文件，总行数: {len(df)}")
            print(f"📋 列名: {list(df.columns)}")
            
            # 步骤1.2: 字段识别
            print("\n🔍 步骤1.2: 字段识别")
            if '英文' in df.columns:
                print("✅ 找到'英文'字段")
                english_column_index = df.columns.get_loc('英文')
                print(f"📊 '英文'字段位置: 第{english_column_index + 1}列")
            else:
                print("❌ 没有找到'英文'字段")
                return False
            
            # 步骤1.3: 内容提取
            print("\n📝 步骤1.3: 内容提取")
            print("前5行'英文'字段内容:")
            for i in range(min(5, len(df))):
                row = df.iloc[i]
                english_content = str(row.get('英文', ''))
                print(f"  第{i+1}行: {english_content[:80]}...")
            
            # 步骤1.4: 数据验证
            print("\n✅ 步骤1.4: 数据验证")
            valid_rows = 0
            for i in range(min(10, len(df))):
                row = df.iloc[i]
                english_content = str(row.get('英文', ''))
                if english_content and english_content != '英文' and english_content != 'nan':
                    valid_rows += 1
                    print(f"  ✅ 第{i+1}行: 有效内容")
                else:
                    print(f"  ❌ 第{i+1}行: 无效内容")
            
            print(f"📊 前10行中有效行数: {valid_rows}")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据处理失败: {e}")
            return False
    
    def debug_audio_generation_flow(self):
        """调试音频生成流程"""
        print("\n🎵 步骤2: 音频生成流程")
        print("-" * 40)
        
        # 获取第一个Excel文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        file_path = os.path.join(self.input_dir, excel_files[0])
        
        try:
            df = pd.read_excel(file_path)
            
            # 测试前3行的音频生成
            for i in range(min(3, len(df))):
                row = df.iloc[i]
                english_content = str(row.get('英文', ''))
                
                if not english_content or english_content == '英文' or english_content == 'nan':
                    continue
                
                print(f"\n🎯 测试第{i+1}行音频生成:")
                print(f"📝 英文字段内容: {english_content[:100]}...")
                
                # 步骤2.1: EdgeTTS处理
                print("🔄 步骤2.1: EdgeTTS处理")
                print(f"🎤 使用语音: {self.default_voice}")
                
                # 步骤2.2: 音频生成
                print("🔄 步骤2.2: 音频生成")
                
                # 创建输出目录
                test_output_dir = os.path.join(self.output_dir, "debug_test")
                os.makedirs(test_output_dir, exist_ok=True)
                
                output_file = os.path.join(test_output_dir, f"debug_row_{i+1}.mp3")
                
                # 生成音频
                result = asyncio.run(self.generate_debug_audio(english_content, output_file))
                
                if result:
                    print(f"✅ 音频生成成功: {output_file}")
                    
                    # 步骤2.3: 文件保存
                    print("🔄 步骤2.3: 文件保存")
                    if os.path.exists(output_file):
                        file_size = os.path.getsize(output_file)
                        print(f"📁 文件大小: {file_size} bytes")
                        
                        # 步骤2.4: 质量检查
                        print("🔄 步骤2.4: 质量检查")
                        if file_size > 1000:
                            print("✅ 文件大小正常")
                        else:
                            print("❌ 文件大小异常")
                    else:
                        print("❌ 文件未生成")
                else:
                    print("❌ 音频生成失败")
                
                # 添加延迟
                time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ 音频生成调试失败: {e}")
            return False
    
    async def generate_debug_audio(self, text, output_file):
        """生成调试音频"""
        try:
            # 清理文本
            clean_text = text.strip()
            clean_text = ' '.join(clean_text.split())
            
            print(f"🧹 清理后文本: {clean_text[:80]}...")
            
            # 创建 EdgeTTS 对象
            communicate = edge_tts.Communicate(clean_text, self.default_voice)
            
            # 生成音频
            await communicate.save(output_file)
            
            return True
            
        except Exception as e:
            print(f"❌ 音频生成异常: {e}")
            return False
    
    def debug_current_audio_files(self):
        """调试当前生成的音频文件"""
        print("\n🔍 步骤3: 调试当前生成的音频文件")
        print("-" * 40)
        
        # 检查当前生成的音频文件
        audio_dir = os.path.join(self.output_dir, "全产品_合并版_3200_v9")
        if os.path.exists(audio_dir):
            audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
            print(f"📁 找到 {len(audio_files)} 个音频文件")
            
            # 检查前3个音频文件
            for i, audio_file in enumerate(sorted(audio_files)[:3]):
                file_path = os.path.join(audio_dir, audio_file)
                file_size = os.path.getsize(file_path)
                print(f"📄 音频文件 {i+1}: {audio_file} ({file_size} bytes)")
                
                # 检查文件名对应的行号
                if "english_field_" in audio_file:
                    try:
                        row_number = int(audio_file.split("_")[2])
                        print(f"   📊 对应Excel第{row_number}行")
                        
                        # 读取对应的Excel行内容
                        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
                        file_path_excel = os.path.join(self.input_dir, excel_files[0])
                        df = pd.read_excel(file_path_excel)
                        
                        if row_number <= len(df):
                            row = df.iloc[row_number - 1]
                            english_content = str(row.get('英文', ''))
                            print(f"   📝 Excel第{row_number}行内容: {english_content[:80]}...")
                        else:
                            print(f"   ❌ Excel文件只有{len(df)}行，无法找到第{row_number}行")
                            
                    except Exception as e:
                        print(f"   ❌ 解析文件名失败: {e}")
        else:
            print("❌ 音频目录不存在")

def main():
    """主函数"""
    debugger = DataProcessingDebugger()
    
    # 调试数据处理流程
    if not debugger.debug_data_processing_flow():
        print("❌ 数据处理流程调试失败")
        return False
    
    # 调试音频生成流程
    if not debugger.debug_audio_generation_flow():
        print("❌ 音频生成流程调试失败")
        return False
    
    # 调试当前音频文件
    debugger.debug_current_audio_files()
    
    print("\n🎉 数据处理流程调试完成!")
    return True

if __name__ == "__main__":
    main()
