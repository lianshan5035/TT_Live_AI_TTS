#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg 音频白噪音混合处理器
为音频文件添加白噪音和房间环境音，使用随机偏移截取
"""

import os
import subprocess
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import datetime

class FFmpegAudioProcessor:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        os.chdir(self.project_root)
        
        # 输入和输出目录
        self.input_dir = "20_输出文件_处理完成的音频文件"
        self.output_dir = "20.2_ffpmeg输出文件_M4A格式音频文件"
        
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
        
        print("🎵 FFmpeg 音频白噪音混合处理器 (M4A格式输出)")
        print("=" * 60)
        print("🔧 处理规则:")
        print("   ✅ 规则1: 识别 20_输出文件_处理完成的音频文件 中的所有音频")
        print("   ✅ 规则2: 添加白噪音，音量设置为 75%")
        print("   ✅ 规则3: 使用随机偏移截取白噪音")
        print("   ✅ 规则4: 保持与源文件夹相同的目录结构")
        print("   ✅ 规则5: 输出到 20.2_ffpmeg输出文件_M4A格式音频文件")
        print("   ✅ 规则6: 输出格式为 M4A (AAC, 128k)")
        print(f"   ✅ 规则7: 白噪音文件: {self.white_noise_file}")
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
    
    def get_audio_duration(self, audio_file):
        """获取音频文件时长"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return duration
            else:
                print(f"⚠️ 无法获取音频时长: {audio_file}")
                return None
        except Exception as e:
            print(f"❌ 获取音频时长失败: {e}")
            return None
    
    def get_white_noise_duration(self):
        """获取白噪音文件时长"""
        if not self.white_noise_file:
            return None
        return self.get_audio_duration(self.white_noise_file)
    
    def generate_random_offset(self, noise_duration, audio_duration):
        """生成随机偏移量"""
        if noise_duration <= audio_duration:
            return 0
        
        max_offset = noise_duration - audio_duration
        return random.uniform(0, max_offset)
    
    def process_single_audio(self, input_file, output_file):
        """处理单个音频文件"""
        try:
            # 获取音频时长
            audio_duration = self.get_audio_duration(input_file)
            if not audio_duration:
                return False
            
            # 获取白噪音时长
            noise_duration = self.get_white_noise_duration()
            if not noise_duration:
                return False
            
            # 生成随机偏移
            offset = self.generate_random_offset(noise_duration, audio_duration)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 构建 ffmpeg 命令
            # 使用 amix 滤镜混合音频和白噪音
            cmd = [
                'ffmpeg', '-y',  # 覆盖输出文件
                '-i', input_file,  # 输入音频
                '-i', self.white_noise_file,  # 白噪音文件
                '-filter_complex', 
                f'[1]atrim=start={offset:.2f}:duration={audio_duration:.2f},volume={self.white_noise_volume}[noise];[0][noise]amix=inputs=2:duration=first:dropout_transition=0',
                '-c:a', 'aac',  # M4A 格式编码
                '-b:a', '128k',  # 比特率
                output_file
            ]
            
            # 执行 ffmpeg 命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # 检查输出文件
                if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                    file_size = os.path.getsize(output_file)
                    file_info = {
                        'filename': os.path.basename(output_file),
                        'size': file_size,
                        'offset': offset,
                        'duration': audio_duration,
                        'format': os.path.splitext(output_file)[1]
                    }
                    
                    with self.lock:
                        self.processed_count += 1
                        self.processed_files_info.append(file_info)
                        self.print_progress()
                    return True
                else:
                    with self.lock:
                        self.error_count += 1
                        print(f"⚠️ 输出文件异常: {os.path.basename(output_file)}")
                    return False
            else:
                with self.lock:
                    self.error_count += 1
                    print(f"❌ FFmpeg 处理失败: {os.path.basename(input_file)}")
                    print(f"   错误信息: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            with self.lock:
                self.error_count += 1
                print(f"⏰ 处理超时: {os.path.basename(input_file)}")
            return False
        except Exception as e:
            with self.lock:
                self.error_count += 1
                print(f"❌ 处理异常: {os.path.basename(input_file)} - {e}")
            return False
    
    def print_progress(self):
        """打印可视化更新看板"""
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
        
        # 格式统计
        format_stats = {}
        for info in self.processed_files_info:
            fmt = info['format']
            format_stats[fmt] = format_stats.get(fmt, 0) + 1
        
        # 创建进度条
        bar_length = 50
        filled_length = int(bar_length * progress_percent / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # 清屏并显示看板
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🎵 FFmpeg 音频白噪音混合处理器 - 实时处理看板")
        print("=" * 80)
        
        # 进度条
        print(f"📊 处理进度: [{bar}] {progress_percent:.1f}%")
        print(f"   📁 文件: {self.processed_count + self.error_count}/{self.total_files}")
        print(f"   ✅ 成功: {self.processed_count} | ❌ 失败: {self.error_count}")
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
            print(f"   🔄 最新处理: {latest_file['filename']}")
        print()
        
        # 格式分布
        if format_stats:
            print(f"📋 格式分布:")
            for fmt, count in sorted(format_stats.items()):
                percentage = count / len(self.processed_files_info) * 100
                print(f"   {fmt}: {count} 个 ({percentage:.1f}%)")
            print()
        
        # 处理速度
        if elapsed_time > 0:
            files_per_second = (self.processed_count + self.error_count) / elapsed_time
            print(f"🚀 处理速度: {files_per_second:.2f} 文件/秒")
        
        print("=" * 80)
        print("💡 提示: 按 Ctrl+C 可安全停止处理")
    
    def print_final_statistics(self):
        """打印最终统计信息"""
        if not self.processed_files_info:
            return
            
        print(f"\n\n🎉 处理完成！最终统计报告")
        print("=" * 80)
        
        # 基本统计
        total_size = sum(info['size'] for info in self.processed_files_info)
        avg_size = total_size / len(self.processed_files_info)
        avg_duration = sum(info['duration'] for info in self.processed_files_info) / len(self.processed_files_info)
        
        print(f"📊 基本统计:")
        print(f"   ✅ 成功处理: {self.processed_count} 个文件")
        print(f"   ❌ 处理失败: {self.error_count} 个文件")
        print(f"   📁 总文件大小: {total_size/1024/1024:.2f} MB")
        print(f"   📈 平均文件大小: {avg_size/1024:.2f} KB")
        print(f"   ⏱️ 平均音频时长: {avg_duration:.2f} 秒")
        
        # 格式统计
        format_stats = {}
        for info in self.processed_files_info:
            fmt = info['format']
            format_stats[fmt] = format_stats.get(fmt, 0) + 1
        
        print(f"\n📋 格式统计:")
        for fmt, count in sorted(format_stats.items()):
            percentage = count / len(self.processed_files_info) * 100
            print(f"   {fmt}: {count} 个文件 ({percentage:.1f}%)")
        
        # 大小分布统计
        size_ranges = {
            "小于1MB": 0,
            "1-5MB": 0,
            "5-10MB": 0,
            "大于10MB": 0
        }
        
        for info in self.processed_files_info:
            size_mb = info['size'] / 1024 / 1024
            if size_mb < 1:
                size_ranges["小于1MB"] += 1
            elif size_mb < 5:
                size_ranges["1-5MB"] += 1
            elif size_mb < 10:
                size_ranges["5-10MB"] += 1
            else:
                size_ranges["大于10MB"] += 1
        
        print(f"\n📏 文件大小分布:")
        for range_name, count in size_ranges.items():
            percentage = count / len(self.processed_files_info) * 100
            print(f"   {range_name}: {count} 个文件 ({percentage:.1f}%)")
        
        # 时长统计
        durations = [info['duration'] for info in self.processed_files_info]
        durations.sort()
        if durations:
            min_duration = durations[0]
            max_duration = durations[-1]
            median_duration = durations[len(durations)//2]
            
            print(f"\n⏱️ 音频时长统计:")
            print(f"   最短时长: {min_duration:.2f} 秒")
            print(f"   最长时长: {max_duration:.2f} 秒")
            print(f"   平均时长: {avg_duration:.2f} 秒")
            print(f"   中位时长: {median_duration:.2f} 秒")
        
        # 偏移统计
        offsets = [info['offset'] for info in self.processed_files_info]
        if offsets:
            avg_offset = sum(offsets) / len(offsets)
            max_offset = max(offsets)
            print(f"\n🎲 白噪音偏移统计:")
            print(f"   平均偏移: {avg_offset:.2f} 秒")
            print(f"   最大偏移: {max_offset:.2f} 秒")
        
        print("=" * 80)
    
    def scan_audio_files(self):
        """扫描输入目录中的所有音频文件，跳过已处理的文件"""
        audio_files = []
        skipped_count = 0
        
        if not os.path.exists(self.input_dir):
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return audio_files
        
        # 支持的音频格式
        audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']
        
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
        
        if skipped_count > 0:
            print(f"⏭️ 跳过已处理文件: {skipped_count} 个")
        
        return audio_files
    
    def process_all_audio_files(self, max_workers=4):
        """处理所有音频文件"""
        if not self.white_noise_file:
            print("❌ 白噪音文件不可用，无法处理")
            return False
        
        # 扫描音频文件
        audio_files = self.scan_audio_files()
        if not audio_files:
            print("❌ 没有找到音频文件")
            return False
        
        print(f"📁 找到 {len(audio_files)} 个音频文件")
        print(f"🚀 启动 {max_workers} 个并行处理线程")
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {}
            for input_file, output_file in audio_files:
                future = executor.submit(self.process_single_audio, input_file, output_file)
                future_to_file[future] = (input_file, output_file)
            
            # 等待所有任务完成
            print(f"\n⏳ 等待所有 {len(audio_files)} 个文件处理完成...")
            
            for future in as_completed(future_to_file):
                input_file, output_file = future_to_file[future]
                
                try:
                    result = future.result()
                    if not result:
                        print(f"❌ 处理失败: {os.path.basename(input_file)}")
                except Exception as e:
                    print(f"❌ 处理异常: {os.path.basename(input_file)} - {e}")
        
        print(f"\n🎉 所有文件处理完成!")
        print(f"📊 统计: 成功 {self.processed_count} 个, 失败 {self.error_count} 个")
        
        return self.processed_count > 0
    
    def test_single_file(self, test_file=None):
        """测试单个文件处理"""
        if not test_file:
            # 找一个测试文件
            audio_files = self.scan_audio_files()
            if audio_files:
                test_file = audio_files[0][0]
            else:
                print("❌ 没有找到测试文件")
                return False
        
        print(f"🧪 测试文件: {os.path.basename(test_file)}")
        
        # 创建测试输出文件
        test_output = os.path.join(self.output_dir, "test_output.m4a")
        
        result = self.process_single_audio(test_file, test_output)
        
        if result:
            print(f"✅ 测试成功: {test_output}")
            return True
        else:
            print(f"❌ 测试失败")
            return False

def main():
    """主函数"""
    processor = FFmpegAudioProcessor()
    
    # 检查 ffmpeg 是否可用
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=10)
        print("✅ FFmpeg 可用")
    except Exception as e:
        print(f"❌ FFmpeg 不可用: {e}")
        print("请安装 FFmpeg: brew install ffmpeg")
        return False
    
    # 先测试单个文件
    print("\n🧪 开始测试单个文件...")
    test_success = processor.test_single_file()
    
    if test_success:
        print("\n🚀 测试成功，开始批量处理...")
        success = processor.process_all_audio_files(max_workers=4)
        
        if success:
            print("\n🎉 批量处理完成!")
            print("💡 所有音频文件已添加白噪音和环境音")
        else:
            print("\n❌ 批量处理失败!")
            print("💡 请检查配置和文件格式")
    else:
        print("\n❌ 测试失败，请检查配置")
    
    return test_success

if __name__ == "__main__":
    main()
