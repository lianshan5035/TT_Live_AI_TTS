#!/usr/bin/env python3
"""
音频试听助手
快速播放和对比生成的测试音频
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioListeningHelper:
    """音频试听助手"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audio_files = self._scan_audio_files()
    
    def _scan_audio_files(self) -> Dict[str, str]:
        """扫描音频文件"""
        audio_files = {}
        current_dir = Path.cwd()
        
        # 查找所有test_1_*.m4a文件
        for file_path in current_dir.glob("test_1_*.m4a"):
            file_name = file_path.name
            if "original" in file_name:
                audio_files["original"] = str(file_path)
            elif "gaming" in file_name:
                audio_files["gaming"] = str(file_path)
            elif "chatting" in file_name:
                audio_files["chatting"] = str(file_path)
            elif "teaching" in file_name:
                audio_files["teaching"] = str(file_path)
            elif "entertainment" in file_name:
                audio_files["entertainment"] = str(file_path)
            elif "news" in file_name:
                audio_files["news"] = str(file_path)
            elif "live_speech" in file_name:
                audio_files["live_speech"] = str(file_path)
            elif "enhanced" in file_name:
                audio_files["enhanced"] = str(file_path)
        
        return audio_files
    
    def list_audio_files(self):
        """列出所有音频文件"""
        self.logger.info("🎵 可用的测试音频文件:")
        self.logger.info("=" * 50)
        
        if not self.audio_files:
            self.logger.warning("❌ 未找到测试音频文件")
            return
        
        # 按类型分组显示
        categories = {
            "对比音频": ["original", "live_speech", "enhanced"],
            "场景音频": ["gaming", "chatting", "teaching", "entertainment", "news"]
        }
        
        for category, types in categories.items():
            self.logger.info(f"\n📁 {category}:")
            for audio_type in types:
                if audio_type in self.audio_files:
                    file_path = self.audio_files[audio_type]
                    file_size = Path(file_path).stat().st_size / 1024  # KB
                    self.logger.info(f"  {audio_type}: {Path(file_path).name} ({file_size:.0f}KB)")
    
    def play_audio(self, audio_type: str):
        """播放指定类型的音频"""
        if audio_type not in self.audio_files:
            self.logger.error(f"❌ 未找到音频类型: {audio_type}")
            return
        
        file_path = self.audio_files[audio_type]
        self.logger.info(f"🎵 播放音频: {audio_type} - {Path(file_path).name}")
        
        try:
            # 使用系统默认播放器播放
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.run(['open', file_path], check=True)
            else:
                self.logger.error("❌ 不支持的操作系统")
        except Exception as e:
            self.logger.error(f"❌ 播放失败: {e}")
    
    def play_comparison(self, audio_types: List[str]):
        """播放对比音频"""
        self.logger.info(f"🔄 播放对比音频: {', '.join(audio_types)}")
        
        for audio_type in audio_types:
            if audio_type in self.audio_files:
                self.play_audio(audio_type)
                input(f"按回车键播放下一个音频 ({audio_type})...")
            else:
                self.logger.warning(f"⚠️ 跳过不存在的音频: {audio_type}")
    
    def play_scenario_comparison(self):
        """播放场景对比"""
        scenarios = ["original", "news", "teaching", "chatting", "entertainment", "gaming"]
        self.play_comparison(scenarios)
    
    def play_processing_comparison(self):
        """播放处理对比"""
        processing_types = ["original", "enhanced", "live_speech"]
        self.play_comparison(processing_types)
    
    def interactive_mode(self):
        """交互式模式"""
        self.logger.info("🎧 音频试听交互模式")
        self.logger.info("=" * 50)
        
        while True:
            print("\n可用命令:")
            print("1. list - 列出所有音频文件")
            print("2. play <type> - 播放指定类型音频")
            print("3. scenarios - 播放场景对比")
            print("4. processing - 播放处理对比")
            print("5. quit - 退出")
            
            try:
                command = input("\n请输入命令: ").strip().split()
                
                if not command:
                    continue
                
                if command[0] == 'quit':
                    break
                elif command[0] == 'list':
                    self.list_audio_files()
                elif command[0] == 'play' and len(command) > 1:
                    self.play_audio(command[1])
                elif command[0] == 'scenarios':
                    self.play_scenario_comparison()
                elif command[0] == 'processing':
                    self.play_processing_comparison()
                else:
                    print("❌ 无效命令")
                    
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

def main():
    """主函数"""
    logger.info("🎧 音频试听助手")
    logger.info("=" * 50)
    
    # 创建助手
    helper = AudioListeningHelper()
    
    # 列出可用音频
    helper.list_audio_files()
    
    # 进入交互模式
    helper.interactive_mode()

if __name__ == '__main__':
    main()
