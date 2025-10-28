#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS 测试脚本
===============

测试 EdgeTTS 统一启动器的基本功能

作者: AI Assistant
版本: 1.0.0
更新日期: 2024-10-28
"""

import os
import sys
import json
import requests

def test_config_loading():
    """测试配置文件加载"""
    print("🔍 测试配置文件加载...")
    
    config_file = "/Volumes/M2/TT_Live_AI_TTS/EdgeTTS_统一配置.json"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置文件加载成功")
        
        # 检查关键配置
        edge_config = config["EdgeTTS_统一配置"]
        
        # 检查路径配置
        input_dir = edge_config["路径配置"]["输入目录"]["默认路径"]
        output_dir = edge_config["路径配置"]["输出目录"]["完整路径"]
        
        print(f"📁 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        
        # 检查目录是否存在
        if os.path.exists(input_dir):
            print("✅ 输入目录存在")
        else:
            print("❌ 输入目录不存在")
        
        if os.path.exists(output_dir):
            print("✅ 输出目录存在")
        else:
            print("❌ 输出目录不存在")
        
        # 检查API配置
        api_config = edge_config["API配置"]["多API服务"]
        print(f"🌐 API服务数量: {len(api_config['服务列表'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def test_api_services():
    """测试API服务状态"""
    print("\n🔍 测试API服务状态...")
    
    tts_urls = [
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5002", 
        "http://127.0.0.1:5003"
    ]
    
    available_services = []
    
    for i, url in enumerate(tts_urls, 1):
        try:
            response = requests.get(f"{url}/status", timeout=5)
            if response.status_code == 200:
                available_services.append(url)
                print(f"✅ TTS 服务 {i} ({url}) 运行正常")
            else:
                print(f"❌ TTS 服务 {i} ({url}) 响应异常: {response.status_code}")
        except Exception as e:
            print(f"❌ TTS 服务 {i} ({url}) 连接失败: {e}")
    
    if available_services:
        print(f"🎯 可用服务数量: {len(available_services)}")
        return True
    else:
        print("❌ 没有可用的 TTS 服务")
        return False

def test_audio_generation():
    """测试音频生成"""
    print("\n🔍 测试音频生成...")
    
    # 使用第一个可用的服务
    tts_url = "http://127.0.0.1:5001"
    
    try:
        # 构建测试请求 - 使用正确的scripts格式
        data = {
            "product_name": "测试",
            "scripts": [{
                "text": "Hello, this is a test.",
                "voice": "en-US-JennyNeural",
                "rate": "+10%",
                "pitch": "+2Hz",
                "volume": "+5%",
                "emotion": "Friendly"
            }]
        }
        
        response = requests.post(f"{tts_url}/generate", json=data, timeout=30)
        
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"✅ 音频生成成功: {content_length} bytes")
            
            if content_length < 1000:
                print("⚠️  音频文件过小，可能有问题")
                return False
            else:
                print("✅ 音频文件大小正常")
                return True
        else:
            print(f"❌ 音频生成失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 音频生成测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 EdgeTTS 测试脚本")
    print("=" * 50)
    
    # 切换到项目目录
    project_root = "/Volumes/M2/TT_Live_AI_TTS"
    os.chdir(project_root)
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 运行测试
    tests = [
        ("配置文件加载", test_config_loading),
        ("API服务状态", test_api_services),
        ("音频生成", test_audio_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # 显示测试结果
    print(f"\n{'='*50}")
    print("📊 测试结果汇总:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！EdgeTTS 系统运行正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统状态")
        return False

if __name__ == "__main__":
    main()
