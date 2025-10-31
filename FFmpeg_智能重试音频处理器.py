#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg 智能重试音频处理器
支持失败文件标记和重试机制
"""

import os
import subprocess
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import datetime
import multiprocessing
import json

class FFmpegSmartRetryProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        # 输入和输出目录
        self.input_dir = "20_输出文件_处理完成的音频文件"
        self.output_dir = "20.2_ffpmeg输出文件_M4A格式音频文件"
        
        # 失败文件记录
        self.failed_files_log = "ffpmeg_输入输出规则/05_处理日志/failed_files.json"
        self.failed_files = []
        
        # 白噪音文件路径
        self.white_noise_paths = [
            "15_FFmpeg工具_音频处理和混合系统/09_背景音效_音效文件存储/white_noise.wav",
            "15_FFmpeg工具_音频处理和混合系统/07_输出文件_处理完成的音频/09_背景音效_音效文件存储/white_noise.wav",
            "30_音频处理管道_EdgeTTS真人直播语音处理系统/12_原始管道_基础音频处理系统/assets/ambience/white_noise.wav"
        ]
        
        # 找到可用的白噪音文件
        self.white_noise_file = self.find_white_noise_file()
        
        # 白噪音音量设置 (75%)
        self.white_noise_volume = 0.75
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 统计信息
        self.processed_count = 0
        self.error_count = 0
        self.total_files = 0
        self.start_time = None
        self.processed_files_info = []
        
        # 性能优化设置
        self.cached_noise_duration = None
        
        print("🔄 FFmpeg 智能重试音频处理器")
        print("=" * 60)
        print("🔧 智能特性:")
        print("   ✅ 失败文件自动标记")
        print("   ✅ 智能重试机制")
        print("   ✅ 失败原因记录")
        print("   ✅ 处理状态持久化")
        print("   ✅ 高性能并行处理")
        print(f"   ✅ 白噪音文件: {self.white_noise_file}")
        print("=" * 60)
    
    def find_white_noise_file(self):
        """查找可用的白噪音文件"""
        for noise_path in self.white_noise_paths:
            full_path = os.path.join(self.project_root, noise_path)
            if os.path.exists(full_path):
                print(f"✅ 找到白噪音文件: {noise_path}")
                return full_path
        
        print("❌ 未找到白噪音文件")
        return None
    
    def load_failed_files(self):
        """加载失败文件记录"""
        if os.path.exists(self.failed_files_log):
            try:
                with open(self.failed_files_log, 'r', encoding='utf-8') as f:
                    self.failed_files = json.load(f)
                print(f"📋 加载了 {len(self.failed_files)} 个失败文件记录")
            except Exception as e:
                print(f"⚠️ 加载失败文件记录失败: {e}")
                self.failed_files = []
        else:
            self.failed_files = []
    
    def save_failed_files(self):
        """保存失败文件记录"""
        try:
            os.makedirs(os.path.dirname(self.failed_files_log), exist_ok=True)
            with open(self.failed_files_log, 'w', encoding='utf-8') as f:
                json.dump(self.failed_files, f, ensure_ascii=False, indent=2)
            print(f"💾 已保存 {len(self.failed_files)} 个失败文件记录")
        except Exception as e:
            print(f"❌ 保存失败文件记录失败: {e}")
    
    def add_failed_file(self, input_file, output_file, error_reason):
        """添加失败文件记录"""
        failed_info = {
            'input_file': input_file,
            'output_file': output_file,
            'error_reason': error_reason,
            'timestamp': datetime.datetime.now().isoformat(),
            'retry_count': 0
        }
        
        # 检查是否已存在
        existing = False
        for failed in self.failed_files:
            if failed['input_file'] == input_file:
                failed['retry_count'] += 1
                failed['last_error'] = error_reason
                failed['last_timestamp'] = datetime.datetime.now().isoformat()
                existing = True
                break
        
        if not existing:
            self.failed_files.append(failed_info)
    
    def get_optimal_thread_count(self):
        """获取最优线程数"""
        cpu_count = multiprocessing.cpu_count()
        optimal_threads = min(cpu_count * 4, 64)
        
        print(f"💻 检测到 {cpu_count} 个CPU核心")
        print(f"🎯 使用 {optimal_threads} 个线程")
        
        return optimal_threads
    
    def get_audio_duration_fast(self, audio_file):
        """快速获取音频文件时长"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', '-select_streams', 'a:0', audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return duration
            else:
                return None
        except Exception:
            return None
    
    def get_white_noise_duration_cached(self):
        """缓存白噪音文件时长"""
        if self.cached_noise_duration is None:
            self.cached_noise_duration = self.get_audio_duration_fast(self.white_noise_file)
        return self.cached_noise_duration
    
    def generate_random_offset(self, noise_duration, audio_duration):
        """生成随机偏移量"""
        if noise_duration <= audio_duration:
            return 0
        
        max_offset = noise_duration - audio_duration
        return random.uniform(0, max_offset)
    
    def process_single_audio_with_retry(self, input_file, output_file, is_retry=False):
        """带重试机制的单文件处理"""
        try:
            # 快速获取音频时长
            audio_duration = self.get_audio_duration_fast(input_file)
            if not audio_duration:
                error_reason = "无法获取音频时长"
                self.add_failed_file(input_file, output_file, error_reason)
                return False
            
            # 使用缓存的白噪音时长
            noise_duration = self.get_white_noise_duration_cached()
            if not noise_duration:
                error_reason = "无法获取白噪音时长"
                self.add_failed_file(input_file, output_file, error_reason)
                return False
            
            # 生成随机偏移
            offset = self.generate_random_offset(noise_duration, audio_duration)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 优化的FFmpeg命令
            cmd = [
                'ffmpeg', '-y', '-v', 'quiet',
                '-i', input_file,
                '-i', self.white_noise_file,
                '-filter_complex', 
                f'[1]atrim=start={offset:.2f}:duration={audio_duration:.2f},volume={self.white_noise_volume}[noise];[0][noise]amix=inputs=2:duration=first:dropout_transition=0',
                '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart',
                output_file
            ]
            
            # 执行FFmpeg命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            
            if result.returncode == 0:
                # 快速检查输出文件
                if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                    file_size = os.path.getsize(output_file)
                    file_info = {
                        'filename': os.path.basename(output_file),
                        'size': file_size,
                        'offset': offset,
                        'duration': audio_duration,
                        'format': os.path.splitext(output_file)[1],
                        'is_retry': is_retry
                    }
                    
                    with self.lock:
                        self.processed_count += 1
                        self.processed_files_info.append(file_info)
                        
                        # 如果这是重试成功的文件，从失败列表中移除
                        if is_retry:
                            self.failed_files = [f for f in self.failed_files if f['input_file'] != input_file]
                        
                        self.print_progress()
                    return True
                else:
                    error_reason = "输出文件异常"
                    self.add_failed_file(input_file, output_file, error_reason)
                    return False
            else:
                error_reason = f"FFmpeg处理失败: {result.stderr[:100]}"
                self.add_failed_file(input_file, output_file, error_reason)
                return False
                
        except subprocess.TimeoutExpired:
            error_reason = "处理超时"
            self.add_failed_file(input_file, output_file, error_reason)
            return False
        except Exception as e:
            error_reason = f"处理异常: {str(e)[:100]}"
            self.add_failed_file(input_file, output_file, error_reason)
            return False
    
    def print_progress(self):
        """打印进度看板"""
        if self.total_files == 0:
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time if self.start_time else 0
        
        # 计算进度百分比
        progress_percent = (self.processed_count + self.error_count) / self.total_files * 100
        
        # 计算剩余时间
        if self.processed_count > 0 and elapsed_time > 0:
            avg_time_per_file = elapsed_time / (self.processed_count + self.error_count)
            remaining_files = self.total_files - (self.processed_count + self.error_count)
            estimated_remaining_time = remaining_files * avg_time_per_file
            remaining_time_str = str(datetime.timedelta(seconds=int(estimated_remaining_time)))
        else:
            remaining_time_str = "计算中..."
        
        # 计算文件大小统计
        total_size = sum(info['size'] for info in self.processed_files_info)
        avg_size = total_size / len(self.processed_files_info) if self.processed_files_info else 0
        
        # 创建进度条
        bar_length = 50
        filled_length = int(bar_length * progress_percent / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # 清屏并显示看板
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔄 FFmpeg 智能重试音频处理器 - 实时处理看板")
        print("=" * 80)
        
        # 进度条
        print(f"📊 处理进度: [{bar}] {progress_percent:.1f}%")
        print(f"   📁 文件: {self.processed_count + self.error_count}/{self.total_files}")
        print(f"   ✅ 成功: {self.processed_count} | ❌ 失败: {self.error_count}")
        print(f"   🔄 待重试: {len(self.failed_files)} 个")
        print()
        
        # 时间信息
        elapsed_str = str(datetime.timedelta(seconds=int(elapsed_time)))
        print(f"⏱️ 时间统计:")
        print(f"   🕐 已用时间: {elapsed_str}")
        print(f"   ⏳ 剩余时间: {remaining_time_str}")
        if self.processed_count > 0 and elapsed_time > 0:
            avg_time = elapsed_time / (self.processed_count + self.error_count)
            print(f"   📈 平均处理时间: {avg_time:.2f}秒/文件")
        print()
        
        # 文件统计
        print(f"📁 文件统计:")
        print(f"   💾 总大小: {total_size/1024/1024:.2f} MB")
        print(f"   📊 平均大小: {avg_size/1024:.2f} KB")
        if self.processed_files_info:
            latest_file = self.processed_files_info[-1]
            retry_mark = " (重试)" if latest_file.get('is_retry', False) else ""
            print(f"   🔄 最新处理: {latest_file['filename']}{retry_mark}")
        print()
        
        # 性能统计
        if elapsed_time > 0:
            files_per_second = (self.processed_count + self.error_count) / elapsed_time
            print(f"🚀 处理速度: {files_per_second:.2f} 文件/秒")
            
            # 预估完成时间
            if files_per_second > 0:
                remaining_seconds = (self.total_files - self.processed_count - self.error_count) / files_per_second
                eta_str = str(datetime.timedelta(seconds=int(remaining_seconds)))
                print(f"⏰ 预计完成时间: {eta_str}")
        
        print("=" * 80)
        print("💡 提示: 按 Ctrl+C 可安全停止处理")
    
    def scan_audio_files(self, include_failed=False):
        """扫描音频文件"""
        audio_files = []
        skipped_count = 0
        
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return audio_files
        
        # 支持的音频格式
        audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']
        
        print("🔍 扫描音频文件...")
        
        # 递归扫描所有音频文件
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    input_file = os.path.join(root, file)
                    
                    # 计算相对路径
                    rel_path = os.path.relpath(input_file, self.input_dir)
                    # 将扩展名改为 .m4a
                    rel_path = os.path.splitext(rel_path)[0] + '.m4a'
                    output_file = os.path.join(self.output_dir, rel_path)
                    
                    # 检查输出文件是否已存在
                    if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                        skipped_count += 1
                        continue
                    
                    audio_files.append((input_file, output_file))
        
        # 如果需要包含失败文件
        if include_failed:
            for failed in self.failed_files:
                input_file = failed['input_file']
                output_file = failed['output_file']
                if os.path.exists(input_file):
                    audio_files.append((input_file, output_file))
        
        if skipped_count > 0:
            print(f"⏭️ 跳过已处理文件: {skipped_count} 个")
        
        return audio_files
    
    def process_all_audio_files(self, max_workers=None, retry_failed=False):
        """处理所有音频文件"""
        if not self.white_noise_file:
            print("❌ 白噪音文件不可用，无法处理")
            return False
        
        # 加载失败文件记录
        self.load_failed_files()
        
        # 扫描音频文件
        audio_files = self.scan_audio_files(include_failed=retry_failed)
        if not audio_files:
            print("❌ 没有找到需要处理的音频文件")
            return False
        
        # 自动计算最优线程数
        if max_workers is None:
            max_workers = self.get_optimal_thread_count()
        
        self.total_files = len(audio_files)
        self.start_time = time.time()
        
        if retry_failed:
            print(f"🔄 重试模式: 处理 {self.total_files} 个文件 (包含 {len(self.failed_files)} 个失败文件)")
        else:
            print(f"📁 找到 {self.total_files} 个需要处理的音频文件")
        
        print(f"🚀 启动 {max_workers} 个并行处理线程")
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {}
            for input_file, output_file in audio_files:
                # 检查是否是失败文件
                is_retry = any(f['input_file'] == input_file for f in self.failed_files)
                future = executor.submit(self.process_single_audio_with_retry, input_file, output_file, is_retry)
                future_to_file[future] = (input_file, output_file)
            
            # 等待所有任务完成
            print(f"\n⏳ 等待所有 {self.total_files} 个文件处理完成...")
            
            for future in as_completed(future_to_file):
                input_file, output_file = future_to_file[future]
                
                try:
                    result = future.result()
                except Exception as e:
                    print(f"❌ 处理异常: {os.path.basename(input_file)} - {e}")
        
        # 保存失败文件记录
        self.save_failed_files()
        
        print(f"\n🎉 所有文件处理完成!")
        print(f"📊 统计: 成功 {self.processed_count} 个, 失败 {self.error_count} 个")
        print(f"🔄 失败文件: {len(self.failed_files)} 个已记录")
        
        return self.processed_count > 0
    
    def retry_failed_files(self):
        """重试失败的文件"""
        if not self.failed_files:
            print("✅ 没有失败文件需要重试")
            return True
        
        print(f"🔄 开始重试 {len(self.failed_files)} 个失败文件...")
        return self.process_all_audio_files(retry_failed=True)

def main():
    """主函数"""
    processor = FFmpegSmartRetryProcessor()
    
    # 检查 ffmpeg 是否可用
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=10)
        print("✅ FFmpeg 可用")
    except Exception as e:
        print(f"❌ FFmpeg 不可用: {e}")
        print("请安装 FFmpeg: brew install ffmpeg")
        return False
    
    # 开始处理
    print("\n🚀 开始智能处理...")
    success = processor.process_all_audio_files()
    
    if success:
        print("\n🎉 智能处理完成!")
        
        # 如果有失败文件，询问是否重试
        if processor.failed_files:
            print(f"\n🔄 发现 {len(processor.failed_files)} 个失败文件")
            print("💡 失败文件已记录，可以稍后重试")
            
            # 自动重试失败文件
            print("\n🔄 自动开始重试失败文件...")
            retry_success = processor.retry_failed_files()
            
            if retry_success:
                print("✅ 重试完成!")
            else:
                print("⚠️ 重试过程中仍有失败文件")
        else:
            print("✅ 所有文件处理成功!")
    else:
        print("\n❌ 智能处理失败!")
        print("💡 请检查配置和文件格式")
    
    return success

if __name__ == "__main__":
    main()
