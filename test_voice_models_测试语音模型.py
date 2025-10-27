#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音模型测试脚本
测试新增的13种语音模型是否正常工作
"""

import requests
import json
import time

def test_voice_models():
    """测试语音模型"""
    print("🎤 测试语音模型...")
    
    # 测试TTS服务的语音模型API
    try:
        response = requests.get("http://127.0.0.1:5001/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TTS服务语音模型API正常")
            print(f"📊 总语音模型数量: {data['total_voices']}")
            print(f"🎯 默认语音: {data['default_voice']}")
            
            # 显示所有语音模型
            print("\n📋 所有语音模型:")
            for voice, info in data['voices'].items():
                print(f"  {voice}: {info['name']} ({info['gender']}) - {info['description']}")
            
            # 测试情绪映射
            print("\n🎭 情绪语音映射:")
            for emotion, voices in data['emotion_mapping'].items():
                print(f"  {emotion}: {', '.join(voices)}")
                
        else:
            print(f"❌ TTS服务语音模型API失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ TTS服务语音模型API错误: {str(e)}")
    
    # 测试Web服务的语音模型API
    try:
        response = requests.get("http://127.0.0.1:8000/api/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Web服务语音模型API正常")
            print(f"📊 总语音模型数量: {data['total_voices']}")
        else:
            print(f"❌ Web服务语音模型API失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Web服务语音模型API错误: {str(e)}")

def test_emotion_voice_mapping():
    """测试情绪语音映射"""
    print("\n🎭 测试情绪语音映射...")
    
    emotions = ["Excited", "Confident", "Empathetic", "Calm", "Playful", "Urgent"]
    
    for emotion in emotions:
        try:
            response = requests.get(f"http://127.0.0.1:5001/voices/{emotion}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {emotion}: {data['total_recommended']} 个推荐语音")
                for voice_detail in data['recommended_voices']:
                    voice_info = voice_detail['info']
                    print(f"    {voice_detail['voice']}: {voice_info['name']} ({voice_info['gender']})")
            else:
                print(f"❌ {emotion}: API失败 {response.status_code}")
                
        except Exception as e:
            print(f"❌ {emotion}: 错误 {str(e)}")

def test_voice_generation():
    """测试语音生成"""
    print("\n🎵 测试语音生成...")
    
    # 测试不同语音模型的语音生成
    test_voices = [
        "en-US-JennyNeural",
        "en-US-AriaNeural", 
        "en-US-EmmaNeural",
        "en-US-BrandonNeural",
        "en-US-DavisNeural"
    ]
    
    test_text = "Hello, this is a test of the new voice models!"
    
    for voice in test_voices:
        try:
            print(f"🎤 测试语音: {voice}")
            
            # 发送语音生成请求
            response = requests.post(
                "http://127.0.0.1:5001/generate",
                json={
                    "scripts": [test_text],
                    "product_name": "VoiceTest",
                    "discount": 0,
                    "emotion": "Friendly",
                    "voice": voice
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ {voice}: 生成成功")
                    print(f"   音频文件: {data.get('audio_files', [])}")
                else:
                    print(f"❌ {voice}: 生成失败 - {data.get('error')}")
            else:
                print(f"❌ {voice}: HTTP错误 {response.status_code}")
                
        except Exception as e:
            print(f"❌ {voice}: 错误 {str(e)}")
        
        time.sleep(1)  # 避免请求过快

def main():
    """主函数"""
    print("🚀 语音模型测试开始...")
    print("=" * 50)
    
    # 测试语音模型API
    test_voice_models()
    
    # 测试情绪语音映射
    test_emotion_voice_mapping()
    
    # 测试语音生成
    test_voice_generation()
    
    print("\n" + "=" * 50)
    print("🎉 语音模型测试完成!")

if __name__ == "__main__":
    main()
