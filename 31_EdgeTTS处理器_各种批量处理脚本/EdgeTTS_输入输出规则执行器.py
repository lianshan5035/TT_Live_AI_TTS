#!/usr/bin/env python3
"""
EdgeTTS 输入输出规则执行器 - 多API多线程版本
严格按照用户最新规则执行批量音频生成，使用多API并发处理
"""
import os
import json
import pandas as pd
import asyncio
import edge_tts
import time
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

class EdgeTTSRuleExecutor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        # 加载配置
        with open('EdgeTTS_统一配置.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self.config = config_data['EdgeTTS_统一配置']
        
        self.input_dir = self.config['路径配置']['输入目录']['默认路径']
        self.output_dir = self.config['路径配置']['输出目录']['完整路径']
        
        # 多API配置
        self.api_services = self.config['API配置']['多API服务']['服务列表']
        self.max_workers = len(self.api_services)  # 每个API一个线程
        self.api_queue = queue.Queue()
        
        # 线程锁和状态
        self.lock = threading.Lock()
        self.processed_count = 0
        self.error_count = 0
        
        print(f"🎵 EdgeTTS 输入输出规则执行器 - 多API多线程版本")
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🔧 API服务数量: {len(self.api_services)}")
        print(f"🧵 最大线程数: {self.max_workers}")
        print("=" * 60)
        print("📋 执行规则:")
        print("   1. ✅ 只处理'英文'字段的内容")
        print("   2. ✅ 忽略每个 xlsx 文件中所有行的 Voice 字段")
        print("   3. ✅ 每个 xlsx 文件在输出目录下创建同名文件夹")
        print("   4. ✅ 文件名格式: english_field_{行号}_{默认voice}.mp3")
        print("   5. ✅ 多API多线程并发处理，API环境隔离")
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
    
    def get_default_voice(self):
        """获取默认语音 - 忽略Excel文件中的Voice字段"""
        # 使用固定的默认语音，不读取Excel文件中的Voice字段
        default_voice = "en-US-JennyNeural"
        print(f"🎤 使用默认语音: {default_voice}")
        return default_voice
    
    def check_api_health(self, api_url):
        """检查API服务健康状态"""
        try:
            response = requests.get(f"{api_url.replace('/generate', '/health')}", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_audio_via_api(self, english_field_content, voice, output_file, api_url):
        """通过API生成音频 - 隔离的API环境"""
        try:
            # 清理英文字段内容
            clean_content = self.clean_english_field_content(english_field_content)
            if not clean_content:
                return False
            
            # 准备API请求数据
            data = {
                "product_name": "批量处理",
                "scripts": [{
                    "text": clean_content,
                    "voice": voice,
                    "rate": "+0%",
                    "pitch": "+0Hz", 
                    "volume": "+0%",
                    "emotion": "Friendly"
                }]
            }
            
            # 发送API请求
            response = requests.post(api_url, json=data, timeout=60)
            
            if response.status_code == 200:
                try:
                    # 解析JSON响应
                    result = response.json()
                    
                    # 检查是否有sample_audios
                    if 'sample_audios' in result and result['sample_audios']:
                        # 获取生成的音频文件路径
                        generated_audio_path = result['sample_audios'][0]
                        
                        # 检查生成的音频文件是否存在
                        if os.path.exists(generated_audio_path):
                            file_size = os.path.getsize(generated_audio_path)
                            if file_size > 1000:
                                # 复制到目标位置
                                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                                import shutil
                                shutil.copy2(generated_audio_path, output_file)
                                
                                with self.lock:
                                    self.processed_count += 1
                                return True
                            else:
                                with self.lock:
                                    self.error_count += 1
                                return False
                        else:
                            with self.lock:
                                self.error_count += 1
                            return False
                    else:
                        with self.lock:
                            self.error_count += 1
                        return False
                        
                except json.JSONDecodeError:
                    # 如果不是JSON响应，直接保存为音频文件
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                    
                    # 检查文件
                    if os.path.exists(output_file):
                        file_size = os.path.getsize(output_file)
                        if file_size > 1000:
                            with self.lock:
                                self.processed_count += 1
                            return True
                        else:
                            with self.lock:
                                self.error_count += 1
                            return False
                    else:
                        with self.lock:
                            self.error_count += 1
                        return False
            else:
                with self.lock:
                    self.error_count += 1
                return False
                
        except Exception as e:
            with self.lock:
                self.error_count += 1
            return False
    
    def worker_thread(self, api_url, task_queue):
        """工作线程 - 每个API一个独立线程"""
        thread_id = threading.current_thread().ident
        print(f"🧵 工作线程 {thread_id} 启动，使用API: {api_url}")
        
        while True:
            try:
                # 从队列获取任务
                task = task_queue.get(timeout=1)
                if task is None:  # 结束信号
                    break
                
                english_content, voice, output_file = task
                
                # 使用隔离的API环境处理
                success = self.generate_audio_via_api(english_content, voice, output_file, api_url)
                
                if success:
                    print(f"✅ 线程{thread_id}: {os.path.basename(output_file)} 生成成功")
                else:
                    print(f"❌ 线程{thread_id}: {os.path.basename(output_file)} 生成失败")
                
                # 标记任务完成
                task_queue.task_done()
                
                # 线程间延迟避免API冲突
                time.sleep(2)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 线程{thread_id} 错误: {e}")
                continue
        
        print(f"🏁 工作线程 {thread_id} 结束")
    
    def process_excel_file_with_dedicated_api(self, file_path, max_rows=10, api_index=0):
        """处理单个 Excel 文件 - 使用专用API版本"""
        print(f"\n📊 处理文件: {os.path.basename(file_path)}")
        
        try:
            df = pd.read_excel(file_path)
            total_rows = len(df)
            process_rows = min(max_rows, total_rows)
            
            print(f"📈 总行数: {total_rows}, 处理行数: {process_rows}")
            print(f"📋 列名: {list(df.columns)}")
            
            # 规则2: 忽略Excel文件中的Voice字段，使用默认语音
            default_voice = self.get_default_voice()
            
            # 规则3: 为每个xlsx文件创建同名文件夹
            file_base = os.path.splitext(os.path.basename(file_path))[0]
            file_output_dir = os.path.join(self.output_dir, file_base)
            
            # 分配专用API
            dedicated_api = self.api_services[api_index % len(self.api_services)]
            api_url = dedicated_api['URL']
            if not api_url.endswith('/generate'):
                api_url = f"{api_url}/generate"
            
            print(f"🎯 分配专用API: {dedicated_api['名称']} ({api_url})")
            
            # 检查API健康状态
            if not self.check_api_health(api_url):
                print(f"❌ 专用API不健康: {api_url}")
                return False
            
            success_count = 0
            error_count = 0
            
            # 顺序处理每一行，使用专用API
            for index in range(process_rows):
                row = df.iloc[index]
                
                # 规则1: 只获取"英文"字段的内容
                english_field_content = str(row.get('英文', ''))
                
                # 字段验证
                if not english_field_content or english_field_content == '英文':
                    continue
                
                # 规则4: 生成输出文件名 - 在xlsx同名文件夹下
                voice_name = default_voice.split('-')[-1] if '-' in default_voice else 'Unknown'
                output_filename = f"english_field_{index+1:04d}_{voice_name}.mp3"
                output_file = os.path.join(file_output_dir, output_filename)
                
                print(f"\n--- 处理第 {index+1} 行 (API: {dedicated_api['名称']}) ---")
                print(f"英文字段内容: {english_field_content[:50]}...")
                
                # 使用专用API生成音频
                if self.generate_audio_via_api(english_field_content, default_voice, output_file, api_url):
                    success_count += 1
                    print(f"✅ 第 {index+1} 行处理成功")
                else:
                    error_count += 1
                    print(f"❌ 第 {index+1} 行处理失败")
                
                # 行间延迟避免API过载
                time.sleep(2)
            
            print(f"\n✅ 文件处理完成: {success_count} 成功, {error_count} 失败")
            print(f"📁 输出文件夹: {file_output_dir}")
            print(f"🎯 使用API: {dedicated_api['名称']}")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 处理文件失败: {e}")
            return False
    
    def process_all_files_parallel_apis(self):
        """处理所有 Excel 文件 - 多API并行版本"""
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
        
        # 获取所有 Excel 文件
        excel_files = [f for f in os.listdir(self.input_dir) if f.endswith('.xlsx')]
        if not excel_files:
            print("❌ 没有找到 Excel 文件")
            return False
        
        print(f"📁 找到 {len(excel_files)} 个 Excel 文件")
        print(f"🔧 可用API服务: {len(self.api_services)} 个")
        
        # 显示API分配计划
        print("\n📋 API分配计划:")
        for i, file_name in enumerate(excel_files):
            api_index = i % len(self.api_services)
            api_name = self.api_services[api_index]['名称']
            print(f"  {file_name} → {api_name}")
        
        # 创建文件-API分配
        file_api_assignments = []
        for i, file_name in enumerate(excel_files):
            file_path = os.path.join(self.input_dir, file_name)
            api_index = i % len(self.api_services)
            file_api_assignments.append((file_path, api_index))
        
        # 使用ThreadPoolExecutor进行并行处理
        max_workers = min(len(self.api_services), len(excel_files))
        print(f"\n🚀 启动 {max_workers} 个并行处理线程")
        
        success_count = 0
        total_files = len(excel_files)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {}
            for file_path, api_index in file_api_assignments:
                file_name = os.path.basename(file_path)
                print(f"📤 提交任务: {file_name} → {self.api_services[api_index]['名称']}")
                
                future = executor.submit(
                    self.process_excel_file_with_dedicated_api, 
                    file_path, 
                    max_rows=3200,  # 处理所有行
                    api_index=api_index
                )
                future_to_file[future] = (file_name, api_index)
            
            # 等待所有任务完成
            print(f"\n⏳ 等待所有 {total_files} 个文件处理完成...")
            
            for future in as_completed(future_to_file):
                file_name, api_index = future_to_file[future]
                api_name = self.api_services[api_index]['名称']
                
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                        print(f"✅ {file_name} 处理完成 (API: {api_name})")
                    else:
                        print(f"❌ {file_name} 处理失败 (API: {api_name})")
                except Exception as e:
                    print(f"❌ {file_name} 处理异常 (API: {api_name}): {e}")
        
        print(f"\n🎉 所有文件处理完成!")
        print(f"📊 统计: {success_count}/{total_files} 文件成功处理")
        
        return success_count > 0

def main():
    """主函数"""
    print("🎵 EdgeTTS 输入输出规则执行器 - 多API并行版本")
    print("=" * 60)
    print("🔧 严格执行的规则:")
    print("   ✅ 规则1: 只处理'英文'字段的内容")
    print("   ✅ 规则2: 忽略每个 xlsx 文件中所有行的 Voice 字段")
    print("   ✅ 规则3: 每个 xlsx 文件在输出目录下创建同名文件夹")
    print("   ✅ 规则4: 文件名格式: english_field_{行号}_{默认voice}.mp3")
    print("   ✅ 规则5: 每个 xlsx 文件分配专用API，多API并行处理")
    print("=" * 60)
    
    processor = EdgeTTSRuleExecutor()
    success = processor.process_all_files_parallel_apis()
    
    if success:
        print("\n🎉 输入输出规则执行完成!")
        print("💡 已严格按照规则处理所有 xlsx 文件")
    else:
        print("\n❌ 输入输出规则执行失败!")
        print("💡 请检查配置和文件格式")
    
    return success

if __name__ == "__main__":
    main()
