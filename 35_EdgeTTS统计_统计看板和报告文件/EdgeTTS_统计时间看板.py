#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS 输出数量统计时间看板
实时显示音频生成进度和统计信息
"""

import os
import time
import subprocess
from datetime import datetime, timedelta

class EdgeTTSDashboard:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        self.output_dir = os.path.join(self.project_root, "20_输出文件_处理完成的音频文件")
        self.start_time = datetime.now()
        
        print("📊 EdgeTTS 输出数量统计时间看板")
        print("=" * 80)
        print(f"🕐 启动时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def get_audio_count(self):
        """获取音频文件数量"""
        try:
            result = subprocess.run(
                ['find', self.output_dir, '-name', '*.mp3', '-type', 'f'],
                capture_output=True, text=True
            )
            return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        except:
            return 0
    
    def get_file_stats(self):
        """获取各文件统计信息"""
        stats = {}
        try:
            for item in os.listdir(self.output_dir):
                item_path = os.path.join(self.output_dir, item)
                if os.path.isdir(item_path) and item.startswith('全产品'):
                    mp3_files = [f for f in os.listdir(item_path) if f.endswith('.mp3')]
                    stats[item] = len(mp3_files)
        except:
            pass
        return stats
    
    def get_voice_assignment(self):
        """获取语音分配信息"""
        voice_assignments = {}
        try:
            for item in os.listdir(self.output_dir):
                item_path = os.path.join(self.output_dir, item)
                if os.path.isdir(item_path) and item.startswith('全产品'):
                    mp3_files = [f for f in os.listdir(item_path) if f.endswith('.mp3')]
                    if mp3_files:
                        # 从文件名提取语音
                        first_file = mp3_files[0]
                        voice = first_file.split('_')[-1].replace('.mp3', '')
                        voice_assignments[item] = voice
        except:
            pass
        return voice_assignments
    
    def calculate_progress(self, current_count):
        """计算进度"""
        total_target = 11 * 3200  # 11个文件，每个3200行
        progress_percent = (current_count / total_target) * 100
        return progress_percent, total_target
    
    def estimate_completion_time(self, current_count, elapsed_time):
        """估算完成时间"""
        if current_count > 0:
            rate = current_count / elapsed_time.total_seconds() * 60  # 每分钟生成数量
            remaining_count = (11 * 3200) - current_count
            if rate > 0:
                remaining_minutes = remaining_count / rate
                completion_time = datetime.now() + timedelta(minutes=remaining_minutes)
                return completion_time, rate, remaining_minutes
        return None, 0, 0
    
    def display_dashboard(self):
        """显示看板"""
        # 清屏
        os.system('clear' if os.name == 'posix' else 'cls')
        
        current_time = datetime.now()
        elapsed_time = current_time - self.start_time
        
        # 获取统计数据
        total_count = self.get_audio_count()
        file_stats = self.get_file_stats()
        voice_assignments = self.get_voice_assignment()
        
        # 计算进度
        progress_percent, total_target = self.calculate_progress(total_count)
        
        # 估算完成时间
        completion_time, rate, remaining_minutes = self.estimate_completion_time(total_count, elapsed_time)
        
        print("📊 EdgeTTS 输出数量统计时间看板")
        print("=" * 80)
        print(f"🕐 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  运行时间: {str(elapsed_time).split('.')[0]}")
        print(f"🚀 启动时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 总体统计
        print("📈 总体统计")
        print("-" * 40)
        print(f"🎵 总音频文件: {total_count:,} 个")
        print(f"🎯 目标总数: {total_target:,} 个")
        print(f"📊 完成进度: {progress_percent:.2f}%")
        print(f"⚡ 生成速度: {rate:.1f} 个/分钟")
        if completion_time:
            print(f"⏰ 预计完成: {completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏳ 剩余时间: {int(remaining_minutes//60)}小时{int(remaining_minutes%60)}分钟")
            print(f"📅 剩余文件: {total_target - total_count:,} 个")
        print("")
        
        # 各文件统计
        print("📁 各文件处理进度")
        print("-" * 40)
        sorted_files = sorted(file_stats.items(), key=lambda x: x[1], reverse=True)
        for file_name, count in sorted_files:
            voice = voice_assignments.get(file_name, "未知")
            progress = (count / 3200) * 100
            print(f"{file_name:25} | {count:4d} 个 | {progress:5.1f}% | {voice}")
        print("")
        
        # 语音分配统计
        print("🎤 语音分配统计")
        print("-" * 40)
        voice_count = {}
        for file_name, voice in voice_assignments.items():
            voice_count[voice] = voice_count.get(voice, 0) + 1
        
        for voice, count in sorted(voice_count.items(), key=lambda x: x[1], reverse=True):
            print(f"{voice:35} | {count} 个文件")
        print("")
        
        # 性能指标
        print("⚡ 性能指标")
        print("-" * 40)
        if elapsed_time.total_seconds() > 0:
            avg_rate = total_count / (elapsed_time.total_seconds() / 60)
            print(f"📊 平均速度: {avg_rate:.1f} 个/分钟")
            print(f"🔄 处理效率: {avg_rate/10:.1f}x (基准: 10个/分钟)")
        
        # 时间统计
        print("⏱️  时间统计")
        print("-" * 40)
        print(f"🕐 已运行: {str(elapsed_time).split('.')[0]}")
        if completion_time:
            remaining_time = completion_time - current_time
            print(f"⏳ 预计剩余: {str(remaining_time).split('.')[0]}")
        print("")
        
        print("=" * 80)
        print("🔄 看板每30秒自动刷新 | 按 Ctrl+C 退出")
        print("=" * 80)

def main():
    """主函数"""
    dashboard = EdgeTTSDashboard()
    
    try:
        while True:
            dashboard.display_dashboard()
            time.sleep(30)  # 每30秒刷新一次
    except KeyboardInterrupt:
        print("\n\n👋 看板已退出")
        print("📊 感谢使用 EdgeTTS 输出数量统计时间看板")

if __name__ == "__main__":
    main()
