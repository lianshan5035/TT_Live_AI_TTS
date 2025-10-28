#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg 音频处理配置检查器
用于验证输入输出配置是否正确
"""

import os
import subprocess
from pathlib import Path

class FFmpegConfigChecker:
    def __init__(self):
        self.project_root = "/Volumes/M2/TT_Live_AI_TTS"
        self.input_dir = "20_输出文件_处理完成的音频文件"
        self.output_dir = "20.2_ffpmeg输出文件_M4A格式音频文件"
        
        # 白噪音文件路径
        self.white_noise_paths = [
            "15_FFmpeg工具_音频处理和混合系统/09_背景音效_音效文件存储/white_noise.wav",
            "15_FFmpeg工具_音频处理和混合系统/07_输出文件_处理完成的音频/09_背景音效_音效文件存储/white_noise.wav",
            "30_音频处理管道_EdgeTTS真人直播语音处理系统/12_原始管道_基础音频处理系统/assets/ambience/white_noise.wav"
        ]
    
    def check_project_root(self):
        """检查项目根目录"""
        print("🔍 检查项目根目录...")
        if os.path.exists(self.project_root):
            print(f"✅ 项目根目录存在: {self.project_root}")
            return True
        else:
            print(f"❌ 项目根目录不存在: {self.project_root}")
            return False
    
    def check_input_directory(self):
        """检查输入目录"""
        print("\n🔍 检查输入目录...")
        input_path = os.path.join(self.project_root, self.input_dir)
        
        if os.path.exists(input_path):
            print(f"✅ 输入目录存在: {self.input_dir}")
            
            # 统计音频文件数量
            audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']
            audio_count = 0
            
            for root, dirs, files in os.walk(input_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in audio_extensions):
                        audio_count += 1
            
            print(f"📁 找到 {audio_count} 个音频文件")
            return True
        else:
            print(f"❌ 输入目录不存在: {self.input_dir}")
            return False
    
    def check_output_directory(self):
        """检查输出目录"""
        print("\n🔍 检查输出目录...")
        output_path = os.path.join(self.project_root, self.output_dir)
        
        if os.path.exists(output_path):
            print(f"✅ 输出目录存在: {self.output_dir}")
            
            # 统计已处理文件数量
            m4a_count = 0
            for root, dirs, files in os.walk(output_path):
                for file in files:
                    if file.lower().endswith('.m4a'):
                        m4a_count += 1
            
            print(f"📁 已处理 {m4a_count} 个M4A文件")
            return True
        else:
            print(f"⚠️ 输出目录不存在，将自动创建: {self.output_dir}")
            return True
    
    def check_white_noise_files(self):
        """检查白噪音文件"""
        print("\n🔍 检查白噪音文件...")
        
        found_noise = False
        for i, noise_path in enumerate(self.white_noise_paths, 1):
            full_path = os.path.join(self.project_root, noise_path)
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                print(f"✅ 白噪音文件 {i}: {noise_path}")
                print(f"   📁 文件大小: {file_size/1024/1024:.2f} MB")
                found_noise = True
            else:
                print(f"❌ 白噪音文件 {i} 不存在: {noise_path}")
        
        if found_noise:
            print("✅ 至少找到一个可用的白噪音文件")
            return True
        else:
            print("❌ 未找到任何可用的白噪音文件")
            return False
    
    def check_ffmpeg(self):
        """检查FFmpeg是否可用"""
        print("\n🔍 检查FFmpeg...")
        
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ FFmpeg 可用: {version_line}")
                return True
            else:
                print("❌ FFmpeg 不可用")
                return False
        except Exception as e:
            print(f"❌ FFmpeg 检查失败: {e}")
            return False
    
    def check_disk_space(self):
        """检查磁盘空间"""
        print("\n🔍 检查磁盘空间...")
        
        try:
            statvfs = os.statvfs(self.project_root)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            total_space = statvfs.f_frsize * statvfs.f_blocks
            
            free_gb = free_space / 1024 / 1024 / 1024
            total_gb = total_space / 1024 / 1024 / 1024
            
            print(f"💾 总空间: {total_gb:.2f} GB")
            print(f"💾 可用空间: {free_gb:.2f} GB")
            
            if free_gb > 10:  # 至少需要10GB空间
                print("✅ 磁盘空间充足")
                return True
            else:
                print("⚠️ 磁盘空间不足，建议清理空间")
                return False
                
        except Exception as e:
            print(f"❌ 磁盘空间检查失败: {e}")
            return False
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🎵 FFmpeg 音频处理配置检查器")
        print("=" * 60)
        
        checks = [
            self.check_project_root,
            self.check_input_directory,
            self.check_output_directory,
            self.check_white_noise_files,
            self.check_ffmpeg,
            self.check_disk_space
        ]
        
        results = []
        for check in checks:
            results.append(check())
        
        print("\n" + "=" * 60)
        print("📊 检查结果汇总:")
        
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print(f"✅ 所有检查通过 ({passed}/{total})")
            print("🚀 配置正确，可以开始处理音频文件")
        else:
            print(f"⚠️ 部分检查失败 ({passed}/{total})")
            print("🔧 请修复问题后重新检查")
        
        return passed == total

def main():
    """主函数"""
    checker = FFmpegConfigChecker()
    success = checker.run_all_checks()
    return success

if __name__ == "__main__":
    main()
