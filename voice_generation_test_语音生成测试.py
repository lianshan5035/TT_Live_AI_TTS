#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI 语音生成测试脚本
专门测试语音生成功能
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

def test_voice_generation():
    """测试语音生成功能"""
    print("🎵 测试语音生成功能...")
    
    base_url = "http://127.0.0.1:8000"
    tts_url = "http://127.0.0.1:5001"
    output_dir = "08_数据文件_输入输出和日志/outputs"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试数据
    test_scripts = [
        "Welcome to our amazing product launch event.",
        "This innovative solution will revolutionize your workflow.",
        "Join us for an exclusive demonstration today.",
        "Don't miss this incredible opportunity to transform your business."
    ]
    
    print(f"📝 测试脚本数量: {len(test_scripts)}")
    
    # 测试1: 直接调用TTS服务
    print("\n🔍 测试1: 直接调用TTS服务...")
    try:
        tts_data = {
            "scripts": test_scripts,
            "emotion": "enthusiastic",
            "voice": "en-US-JennyNeural"
        }
        
        response = requests.post(f"{tts_url}/generate", json=tts_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ TTS服务响应成功")
            print(f"   生成文件数: {len(result.get('generated_files', []))}")
            
            # 检查生成的文件
            for file_path in result.get('generated_files', []):
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   ✅ 文件存在: {os.path.basename(file_path)} ({file_size} bytes)")
                else:
                    print(f"   ❌ 文件不存在: {file_path}")
        else:
            print(f"❌ TTS服务响应失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"❌ TTS服务调用异常: {str(e)}")
    
    # 测试2: 通过Web控制台API
    print("\n🔍 测试2: 通过Web控制台API...")
    try:
        web_data = {
            "scripts": test_scripts,
            "emotion": "enthusiastic", 
            "voice": "en-US-JennyNeural"
        }
        
        response = requests.post(f"{base_url}/api/generate-a3-audio", json=web_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Web控制台API响应成功")
            print(f"   生成文件数: {len(result.get('generated_files', []))}")
            
            # 检查生成的文件
            for file_path in result.get('generated_files', []):
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   ✅ 文件存在: {os.path.basename(file_path)} ({file_size} bytes)")
                else:
                    print(f"   ❌ 文件不存在: {file_path}")
        else:
            print(f"❌ Web控制台API响应失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Web控制台API调用异常: {str(e)}")
    
    # 测试3: 单个脚本生成
    print("\n🔍 测试3: 单个脚本生成...")
    try:
        single_data = {
            "scripts": ["Hello, this is a test of the voice generation system."],
            "emotion": "neutral",
            "voice": "en-US-JennyNeural"
        }
        
        response = requests.post(f"{tts_url}/generate", json=single_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 单个脚本生成成功")
            print(f"   生成文件数: {len(result.get('generated_files', []))}")
            
            # 检查生成的文件
            for file_path in result.get('generated_files', []):
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   ✅ 文件存在: {os.path.basename(file_path)} ({file_size} bytes)")
                else:
                    print(f"   ❌ 文件不存在: {file_path}")
        else:
            print(f"❌ 单个脚本生成失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 单个脚本生成异常: {str(e)}")
    
    # 列出所有生成的音频文件
    print(f"\n📁 输出目录中的所有音频文件:")
    audio_files = []
    for file in os.listdir(output_dir):
        if file.endswith(('.mp3', '.wav', '.m4a')):
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            audio_files.append((file, file_path, file_size))
            print(f"   🎵 {file} ({file_size} bytes)")
    
    if not audio_files:
        print("   ❌ 没有找到音频文件")
    
    return audio_files

if __name__ == "__main__":
    print("🚀 开始语音生成功能测试...")
    print("=" * 60)
    
    audio_files = test_voice_generation()
    
    print("\n" + "=" * 60)
    print("🎉 语音生成测试完成！")
    print(f"📁 输出目录: {os.path.abspath('08_数据文件_输入输出和日志/outputs')}")
    print(f"🎵 生成音频文件数: {len(audio_files)}")
    
    if audio_files:
        print("\n📋 生成的音频文件列表:")
        for file, path, size in audio_files:
            print(f"   🎵 {file} - {size} bytes")
            print(f"      路径: {path}")
