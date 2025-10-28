#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速调整舒缓型语速脚本
专门用于调整舒缓型音频的语速参数
"""

import json
import os
from datetime import datetime

def quick_fix_calm_speed():
    """快速修复舒缓型语速"""
    
    config_file = "29_配置管理_实时参数调整和系统配置/tts_config.json"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    # 检查配置文件是否存在
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        print("❌ 配置文件不存在，请先运行 config_manager.py")
        return False
    
    # 调整舒缓型参数
    print("🔧 正在调整舒缓型语速参数...")
    
    # 修改舒缓型的语速范围：从 [0.5, 0.7] 改为 [0.7, 0.9]
    config["emotion_settings"]["emotion_parameters"]["Calm"]["rate_range"] = [0.7, 0.9]
    config["emotion_settings"]["emotion_parameters"]["Calm"]["description"] = "舒缓型 - 语速正常，音调平稳"
    
    # 更新最后修改时间
    config["last_updated"] = datetime.now().isoformat()
    
    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ 舒缓型语速已调整为正常范围 [0.7, 0.9]")
    print("📝 说明: 舒缓型音频现在将使用正常语速，不再过慢")
    
    # 显示当前舒缓型参数
    calm_params = config["emotion_settings"]["emotion_parameters"]["Calm"]
    print(f"\n🎭 当前舒缓型参数:")
    print(f"  语速范围: {calm_params['rate_range']}")
    print(f"  音调范围: {calm_params['pitch_range']}")
    print(f"  音量范围: {calm_params['volume_range']}")
    print(f"  说明: {calm_params['description']}")
    
    return True

def show_all_emotion_speeds():
    """显示所有情绪类型的语速设置"""
    
    config_file = "29_配置管理_实时参数调整和系统配置/tts_config.json"
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("🎭 所有情绪类型的语速设置:")
    print("=" * 50)
    
    for emotion, params in config["emotion_settings"]["emotion_parameters"].items():
        rate_range = params["rate_range"]
        description = params["description"]
        
        # 根据语速范围判断语速等级
        avg_speed = sum(rate_range) / 2
        if avg_speed < 0.7:
            speed_level = "🐌 很慢"
        elif avg_speed < 0.9:
            speed_level = "🚶 较慢"
        elif avg_speed < 1.1:
            speed_level = "🚶‍♂️ 正常"
        elif avg_speed < 1.3:
            speed_level = "🏃 较快"
        else:
            speed_level = "🏃‍♂️ 很快"
        
        print(f"{emotion:12} | 语速: {rate_range[0]:.1f}-{rate_range[1]:.1f} | {speed_level}")
        print(f"{'':12} | {description}")
        print()

if __name__ == "__main__":
    print("🔧 舒缓型语速快速调整工具")
    print("=" * 40)
    
    # 显示当前所有情绪类型的语速
    show_all_emotion_speeds()
    
    # 执行调整
    if quick_fix_calm_speed():
        print("\n🎉 调整完成！")
        print("💡 提示: 重新启动TTS服务以应用新配置")
    else:
        print("\n❌ 调整失败")
