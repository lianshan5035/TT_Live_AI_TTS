#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试edge-tts功能
"""

import asyncio
import edge_tts
import os
from datetime import datetime

async def test_edge_tts_direct():
    """直接测试edge-tts"""
    print("🎵 直接测试edge-tts功能...")
    
    # 测试参数
    text = "Hello, this is a test message for voice generation."
    voice = "en-US-JennyNeural"
    emotion = "Friendly"
    
    # 情绪参数映射
    emotion_params = {
        "Calm": {"rate": "-6%", "pitch": "-2Hz", "volume": "+0%"},
        "Friendly": {"rate": "+2%", "pitch": "+2Hz", "volume": "+0%"},
        "Confident": {"rate": "+4%", "pitch": "+1Hz", "volume": "+1%"},
        "Playful": {"rate": "+6%", "pitch": "+3Hz", "volume": "+1%"},
        "Excited": {"rate": "+10%", "pitch": "+4Hz", "volume": "+2%"},
        "Urgent": {"rate": "+12%", "pitch": "+3Hz", "volume": "+2%"}
    }
    
    params = emotion_params.get(emotion, emotion_params["Friendly"])
    
    print(f"📝 文本: {text}")
    print(f"🎤 音色: {voice}")
    print(f"😊 情绪: {emotion}")
    print(f"⚙️ 参数: {params}")
    
    # 创建输出目录
    output_dir = "08_数据文件_输入输出和日志/outputs/test_direct"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_{emotion}_{timestamp}.mp3")
    
    print(f"📁 输出文件: {output_file}")
    
    try:
        # 创建Communicate对象
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=params["rate"],
            pitch=params["pitch"],
            volume=params["volume"]
        )
        
        print("🔄 开始生成音频...")
        
        # 生成音频文件
        await communicate.save(output_file)
        
        # 检查文件是否生成
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ 音频生成成功!")
            print(f"   📁 文件路径: {output_file}")
            print(f"   📊 文件大小: {file_size} bytes")
            print(f"   🎵 文件类型: MP3")
            
            return output_file
        else:
            print(f"❌ 音频文件未生成: {output_file}")
            return None
            
    except Exception as e:
        print(f"❌ 生成音频失败: {str(e)}")
        print(f"   错误类型: {type(e).__name__}")
        import traceback
        print(f"   错误堆栈: {traceback.format_exc()}")
        return None

async def test_multiple_emotions():
    """测试多种情绪"""
    print("\n🎭 测试多种情绪...")
    
    emotions = ["Friendly", "Excited", "Calm", "Confident"]
    text = "Welcome to our amazing product launch event."
    voice = "en-US-JennyNeural"
    
    results = []
    
    for emotion in emotions:
        print(f"\n😊 测试情绪: {emotion}")
        
        # 情绪参数映射
        emotion_params = {
            "Calm": {"rate": "-6%", "pitch": "-2Hz", "volume": "+0%"},
            "Friendly": {"rate": "+2%", "pitch": "+2Hz", "volume": "+0%"},
            "Confident": {"rate": "+4%", "pitch": "+1Hz", "volume": "+1%"},
            "Playful": {"rate": "+6%", "pitch": "+3Hz", "volume": "+1%"},
            "Excited": {"rate": "+10%", "pitch": "+4Hz", "volume": "+2%"},
            "Urgent": {"rate": "+12%", "pitch": "+3Hz", "volume": "+2%"}
        }
        
        params = emotion_params.get(emotion, emotion_params["Friendly"])
        
        # 创建输出目录
        output_dir = "08_数据文件_输入输出和日志/outputs/test_emotions"
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        output_file = os.path.join(output_dir, f"test_{emotion}.mp3")
        
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=params["rate"],
                pitch=params["pitch"],
                volume=params["volume"]
            )
            
            await communicate.save(output_file)
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   ✅ 成功: {output_file} ({file_size} bytes)")
                results.append((emotion, output_file, file_size))
            else:
                print(f"   ❌ 失败: 文件未生成")
                
        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")
    
    return results

if __name__ == "__main__":
    print("🚀 开始edge-tts直接测试...")
    print("=" * 60)
    
    # 运行测试
    result = asyncio.run(test_edge_tts_direct())
    emotion_results = asyncio.run(test_multiple_emotions())
    
    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    
    if result:
        print(f"✅ 单次测试成功: {result}")
    else:
        print("❌ 单次测试失败")
    
    print(f"🎭 情绪测试结果: {len(emotion_results)} 个成功")
    
    if emotion_results:
        print("\n📋 生成的音频文件:")
        for emotion, file_path, size in emotion_results:
            print(f"   🎵 {emotion}: {file_path} ({size} bytes)")
    
    print(f"\n📁 输出目录: {os.path.abspath('08_数据文件_输入输出和日志/outputs')}")
