#!/usr/bin/env python3
"""
EdgeTTS 单个 API 测试器
测试单个 API 的音频生成功能
"""
import os
import json
import requests
import time

def test_single_api():
    """测试单个 API"""
    print("🧪 EdgeTTS 单个 API 测试器")
    print("=" * 50)
    
    # 测试文本
    test_text = "这是一个测试音频，用于验证 EdgeTTS 服务是否正常工作。"
    test_voice = "en-US-JennyNeural"
    test_emotion = "友好型"
    
    # API 地址
    api_url = "http://127.0.0.1:5001"
    
    print(f"📡 测试 API: {api_url}")
    print(f"📝 测试文本: {test_text}")
    print(f"🎤 测试语音: {test_voice}")
    print(f"😊 测试情绪: {test_emotion}")
    print("=" * 50)
    
    # 检查 API 状态
    try:
        print("🔍 检查 API 状态...")
        response = requests.get(f'{api_url}/status', timeout=5)
        if response.status_code == 200:
            print("✅ API 状态正常")
        else:
            print(f"❌ API 状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API 连接失败: {e}")
        return False
    
    # 构建请求数据
    data = {
        "product_name": "单个API测试",
        "scripts": [{
            "text": test_text,
            "voice": test_voice,
            "rate": "+0%",
            "pitch": "+0Hz", 
            "volume": "+0%",
            "emotion": test_emotion
        }]
    }
    
    print("🎵 开始生成音频...")
    
    try:
        # 发送请求
        response = requests.post(
            f'{api_url}/generate',
            json=data,
            timeout=60
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📏 响应内容长度: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content_length = len(response.content)
            
            if content_length > 1000:
                # 保存测试文件
                output_file = "/Volumes/M2/TT_Live_AI_TTS/20_输出文件_处理完成的音频文件/单个API测试.mp3"
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 音频生成成功!")
                print(f"📁 保存位置: {output_file}")
                print(f"📏 文件大小: {content_length} bytes")
                
                # 检查文件是否可播放
                if content_length > 10000:  # 大于10KB认为是正常音频
                    print("🎉 音频文件正常，可以播放!")
                    return True
                else:
                    print("⚠️ 音频文件可能有问题，大小异常")
                    return False
            else:
                print(f"❌ 响应内容过小 ({content_length} bytes)，生成失败")
                print(f"📄 响应内容: {response.text[:200]}...")
                return False
        else:
            print(f"❌ API 响应错误: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_multiple_apis():
    """测试多个 API"""
    apis = [
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5002", 
        "http://127.0.0.1:5003"
    ]
    
    print("\n🔄 测试多个 API...")
    print("=" * 50)
    
    for i, api_url in enumerate(apis, 1):
        print(f"\n📡 测试 API {i}: {api_url}")
        
        try:
            response = requests.get(f'{api_url}/status', timeout=3)
            if response.status_code == 200:
                print(f"✅ API {i} 状态正常")
            else:
                print(f"❌ API {i} 状态异常: {response.status_code}")
        except Exception as e:
            print(f"❌ API {i} 连接失败: {e}")

def main():
    """主函数"""
    print("🚀 EdgeTTS 单个 API 测试器启动")
    print("=" * 60)
    
    # 测试多个 API 状态
    test_multiple_apis()
    
    # 测试单个 API 生成
    success = test_single_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 单个 API 测试成功!")
        print("💡 建议: 可以继续使用单个 API 进行音频生成")
    else:
        print("❌ 单个 API 测试失败!")
        print("💡 建议: 检查 EdgeTTS 服务配置或重新部署")
    
    return success

if __name__ == "__main__":
    main()
