#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI TTS 实时参数配置系统
支持实时修改各种生成参数，无需重启服务
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

class TTSConfigManager:
    """TTS参数配置管理器"""
    
    def __init__(self, config_file: str = "29_配置管理_实时参数调整和系统配置/tts_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 配置文件加载失败: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "system_settings": {
                "max_concurrent": 12,
                "batch_size": 80,
                "batch_delay": 2,
                "file_delay": 5,
                "retry_attempts": 3,
                "timeout": 60
            },
            "voice_settings": {
                "file_voice_mapping": {
                    "全产品_合并版_3200_v9.xlsx": "en-US-JennyNeural",
                    "全产品_合并版_3200_v5.xlsx": "en-US-AvaNeural", 
                    "全产品_合并版_3200_v4.xlsx": "en-US-NancyNeural",
                    "全产品_合并版_3200_v8.xlsx": "en-US-AriaNeural",
                    "全产品_合并版_3200_v3.xlsx": "en-US-KaiNeural",
                    "全产品_合并版_3200_v2.xlsx": "en-US-SerenaNeural",
                    "全产品_合并版_3200.xlsx": "en-US-EmmaNeural",
                    "全产品_合并版_3200_v7.xlsx": "en-US-MichelleNeural",
                    "全产品_合并版_3200_v6.xlsx": "en-US-BrandonNeural"
                }
            },
            "emotion_settings": {
                "emotion_mapping": {
                    "紧迫型": "Urgent",
                    "舒缓型": "Calm",
                    "温暖型": "Warm", 
                    "兴奋型": "Excited",
                    "专业型": "Professional"
                },
                "emotion_parameters": {
                    "Urgent": {
                        "rate_range": [0.8, 1.2],
                        "pitch_range": [0.9, 1.1],
                        "volume_range": [0.8, 1.0],
                        "description": "紧迫型 - 语速较快，音调略高"
                    },
                    "Calm": {
                        "rate_range": [0.7, 0.9],  # 调整：从 [0.5, 0.7] 改为 [0.7, 0.9] 提高语速
                        "pitch_range": [0.8, 1.0],
                        "volume_range": [0.7, 0.9],
                        "description": "舒缓型 - 语速正常，音调平稳"
                    },
                    "Warm": {
                        "rate_range": [0.8, 1.0],
                        "pitch_range": [0.9, 1.1],
                        "volume_range": [0.8, 1.0],
                        "description": "温暖型 - 语速适中，音调温暖"
                    },
                    "Excited": {
                        "rate_range": [1.0, 1.3],
                        "pitch_range": [1.0, 1.2],
                        "volume_range": [0.9, 1.1],
                        "description": "兴奋型 - 语速较快，音调较高"
                    },
                    "Professional": {
                        "rate_range": [0.8, 1.0],
                        "pitch_range": [0.9, 1.0],
                        "volume_range": [0.8, 1.0],
                        "description": "专业型 - 语速稳定，音调专业"
                    }
                }
            },
            "dynamic_parameters": {
                "rate_base_range": [0.7, 1.3],
                "pitch_base_range": [0.8, 1.2],
                "volume_base_range": [0.7, 1.1],
                "variation_intensity": 0.3,
                "anti_detection_enabled": True,
                "human_features_enabled": True
            },
            "ssml_effects": {
                "break_time_range": [0.1, 0.3],
                "emphasis_enabled": True,
                "tone_change_enabled": True,
                "breath_sounds_enabled": True,
                "natural_pauses_enabled": True
            },
            "quality_settings": {
                "target_clarity": 0.9,
                "target_naturalness": 0.85,
                "target_expressiveness": 0.8,
                "anti_detection_score_target": 70
            },
            "output_settings": {
                "audio_format": "mp3",
                "sample_rate": 22050,
                "bit_rate": 128,
                "file_naming_pattern": "tts_{script_id:04d}_{emotion}_{voice_name}_dyn.mp3"
            }
        }
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # 更新最后修改时间
            self.config["last_updated"] = datetime.now().isoformat()
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ 配置已保存到: {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"❌ 配置保存失败: {e}")
            return False
    
    def update_emotion_parameter(self, emotion: str, parameter: str, value: Any) -> bool:
        """更新情绪参数"""
        try:
            if emotion in self.config["emotion_settings"]["emotion_parameters"]:
                self.config["emotion_settings"]["emotion_parameters"][emotion][parameter] = value
                self.save_config()
                self.logger.info(f"✅ 已更新 {emotion} 的 {parameter} 为 {value}")
                return True
            else:
                self.logger.error(f"❌ 未找到情绪类型: {emotion}")
                return False
        except Exception as e:
            self.logger.error(f"❌ 参数更新失败: {e}")
            return False
    
    def update_system_parameter(self, parameter: str, value: Any) -> bool:
        """更新系统参数"""
        try:
            self.config["system_settings"][parameter] = value
            self.save_config()
            self.logger.info(f"✅ 已更新系统参数 {parameter} 为 {value}")
            return True
        except Exception as e:
            self.logger.error(f"❌ 系统参数更新失败: {e}")
            return False
    
    def get_emotion_parameter(self, emotion: str, parameter: str) -> Optional[Any]:
        """获取情绪参数"""
        try:
            return self.config["emotion_settings"]["emotion_parameters"].get(emotion, {}).get(parameter)
        except Exception as e:
            self.logger.error(f"❌ 获取参数失败: {e}")
            return None
    
    def get_system_parameter(self, parameter: str) -> Optional[Any]:
        """获取系统参数"""
        try:
            return self.config["system_settings"].get(parameter)
        except Exception as e:
            self.logger.error(f"❌ 获取系统参数失败: {e}")
            return None
    
    def print_current_config(self):
        """打印当前配置"""
        print("🔧 当前TTS配置:")
        print("=" * 50)
        
        # 系统设置
        print("📊 系统设置:")
        for key, value in self.config["system_settings"].items():
            print(f"  {key}: {value}")
        
        print("\n🎭 情绪参数设置:")
        for emotion, params in self.config["emotion_settings"]["emotion_parameters"].items():
            print(f"  {emotion}:")
            for param, value in params.items():
                if param != "description":
                    print(f"    {param}: {value}")
            print(f"    说明: {params.get('description', '')}")
        
        print("\n🎵 动态参数:")
        for key, value in self.config["dynamic_parameters"].items():
            print(f"  {key}: {value}")
    
    def create_config_editor(self):
        """创建配置编辑器"""
        print("🔧 TTS参数配置编辑器")
        print("=" * 50)
        
        while True:
            print("\n📋 可用的操作:")
            print("1. 查看当前配置")
            print("2. 修改情绪参数")
            print("3. 修改系统参数")
            print("4. 修改动态参数")
            print("5. 重置为默认配置")
            print("6. 保存并退出")
            print("0. 退出不保存")
            
            choice = input("\n请选择操作 (0-6): ").strip()
            
            if choice == "1":
                self.print_current_config()
            
            elif choice == "2":
                self.edit_emotion_parameters()
            
            elif choice == "3":
                self.edit_system_parameters()
            
            elif choice == "4":
                self.edit_dynamic_parameters()
            
            elif choice == "5":
                if input("确认重置为默认配置? (y/N): ").lower() == 'y':
                    self.config = self.get_default_config()
                    print("✅ 已重置为默认配置")
            
            elif choice == "6":
                if self.save_config():
                    print("✅ 配置已保存")
                break
            
            elif choice == "0":
                print("❌ 退出未保存")
                break
            
            else:
                print("❌ 无效选择，请重试")

    def edit_emotion_parameters(self):
        """编辑情绪参数"""
        print("\n🎭 情绪参数编辑:")
        
        emotions = list(self.config["emotion_settings"]["emotion_parameters"].keys())
        for i, emotion in enumerate(emotions, 1):
            print(f"{i}. {emotion}")
        
        try:
            choice = int(input("选择情绪类型 (1-{}): ".format(len(emotions))))
            if 1 <= choice <= len(emotions):
                emotion = emotions[choice - 1]
                self.edit_single_emotion(emotion)
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入数字")

    def edit_single_emotion(self, emotion: str):
        """编辑单个情绪的参数"""
        params = self.config["emotion_settings"]["emotion_parameters"][emotion]
        
        print(f"\n🎯 编辑 {emotion} 参数:")
        print(f"当前设置: {params}")
        
        while True:
            print("\n可修改的参数:")
            print("1. rate_range (语速范围)")
            print("2. pitch_range (音调范围)")
            print("3. volume_range (音量范围)")
            print("4. description (描述)")
            print("0. 返回")
            
            choice = input("选择参数 (0-4): ").strip()
            
            if choice == "1":
                new_range = self.get_range_input("语速范围")
                if new_range:
                    self.update_emotion_parameter(emotion, "rate_range", new_range)
            
            elif choice == "2":
                new_range = self.get_range_input("音调范围")
                if new_range:
                    self.update_emotion_parameter(emotion, "pitch_range", new_range)
            
            elif choice == "3":
                new_range = self.get_range_input("音量范围")
                if new_range:
                    self.update_emotion_parameter(emotion, "volume_range", new_range)
            
            elif choice == "4":
                new_desc = input("输入新描述: ").strip()
                if new_desc:
                    self.update_emotion_parameter(emotion, "description", new_desc)
            
            elif choice == "0":
                break
            
            else:
                print("❌ 无效选择")

    def get_range_input(self, param_name: str) -> Optional[list]:
        """获取范围输入"""
        try:
            min_val = float(input(f"输入{param_name}最小值: "))
            max_val = float(input(f"输入{param_name}最大值: "))
            if min_val <= max_val:
                return [min_val, max_val]
            else:
                print("❌ 最小值不能大于最大值")
                return None
        except ValueError:
            print("❌ 请输入有效数字")
            return None

    def edit_system_parameters(self):
        """编辑系统参数"""
        print("\n📊 系统参数编辑:")
        
        params = self.config["system_settings"]
        for i, (key, value) in enumerate(params.items(), 1):
            print(f"{i}. {key}: {value}")
        
        try:
            choice = int(input("选择要修改的参数 (1-{}): ".format(len(params))))
            param_keys = list(params.keys())
            if 1 <= choice <= len(param_keys):
                param_name = param_keys[choice - 1]
                new_value = self.get_value_input(param_name, params[param_name])
                if new_value is not None:
                    self.update_system_parameter(param_name, new_value)
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入数字")

    def get_value_input(self, param_name: str, current_value: Any) -> Any:
        """获取值输入"""
        if isinstance(current_value, int):
            try:
                return int(input(f"输入新的{param_name}值 (当前: {current_value}): "))
            except ValueError:
                print("❌ 请输入有效整数")
                return None
        elif isinstance(current_value, float):
            try:
                return float(input(f"输入新的{param_name}值 (当前: {current_value}): "))
            except ValueError:
                print("❌ 请输入有效数字")
                return None
        else:
            return input(f"输入新的{param_name}值 (当前: {current_value}): ").strip()

    def edit_dynamic_parameters(self):
        """编辑动态参数"""
        print("\n🎵 动态参数编辑:")
        
        params = self.config["dynamic_parameters"]
        for i, (key, value) in enumerate(params.items(), 1):
            print(f"{i}. {key}: {value}")
        
        try:
            choice = int(input("选择要修改的参数 (1-{}): ".format(len(params))))
            param_keys = list(params.keys())
            if 1 <= choice <= len(param_keys):
                param_name = param_keys[choice - 1]
                new_value = self.get_value_input(param_name, params[param_name])
                if new_value is not None:
                    self.config["dynamic_parameters"][param_name] = new_value
                    self.save_config()
                    print(f"✅ 已更新动态参数 {param_name} 为 {new_value}")
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入数字")

def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('19_日志文件_系统运行日志和错误记录/config_manager.log'),
            logging.StreamHandler()
        ]
    )
    
    # 创建配置管理器
    config_manager = TTSConfigManager()
    
    # 启动配置编辑器
    config_manager.create_config_editor()

if __name__ == "__main__":
    main()
