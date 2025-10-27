#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试TTS服务功能
"""

import requests
import json
import os

def test_tts_direct():
    """直接测试TTS服务"""
    print("🔍 直接测试TTS服务...")
    
    tts_url = "http://127.0.0.1:5001"
    
    # 测试数据
    test_data = {
        "scripts": ["Hello, this is a test message."],
        "emotion": "Friendly",
        "voice": "en-US-JennyNeural"
    }
    
    print(f"📤 发送请求到: {tts_url}/generate")
    print(f"📝 测试数据: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(f"{tts_url}/generate", json=test_data, timeout=30)
        
        print(f"📥 响应状态码: {response.status_code}")
        print(f"📥 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应成功:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 检查生成的文件
            if "sample_audios" in result:
                for audio_file in result["sample_audios"]:
                    if os.path.exists(audio_file):
                        size = os.path.getsize(audio_file)
                        print(f"🎵 音频文件存在: {audio_file} ({size} bytes)")
                    else:
                        print(f"❌ 音频文件不存在: {audio_file}")
        else:
            print(f"❌ 响应失败: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_tts_direct()
