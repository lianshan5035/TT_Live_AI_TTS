#!/usr/bin/env python3
"""
EdgeTTS 直接测试器
直接使用 EdgeTTS 库测试音频生成
"""
import asyncio
import edge_tts
import os

async def test_edge_tts_direct():
    """直接测试 EdgeTTS"""
    print("🎵 EdgeTTS 直接测试器")
    print("=" * 50)
    
    # 测试参数
    text = "这是一个测试音频，用于验证 EdgeTTS 是否正常工作。"
    voice = "en-US-JennyNeural"
    
    print(f"📝 测试文本: {text}")
    print(f"🎤 测试语音: {voice}")
    print("=" * 50)
    
    try:
        print("🎵 开始生成音频...")
        
        # 创建 EdgeTTS 对象
        communicate = edge_tts.Communicate(text, voice)
        
        # 生成音频
        output_file = "/Volumes/M2/TT_Live_AI_TTS/20_输出文件_处理完成的音频文件/EdgeTTS直接测试.mp3"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        await communicate.save(output_file)
        
        # 检查文件
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ 音频生成成功!")
            print(f"📁 保存位置: {output_file}")
            print(f"📏 文件大小: {file_size} bytes")
            
            if file_size > 10000:  # 大于10KB认为是正常音频
                print("🎉 音频文件正常，可以播放!")
                return True
            else:
                print("⚠️ 音频文件可能有问题，大小异常")
                return False
        else:
            print("❌ 音频文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ EdgeTTS 生成失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 EdgeTTS 直接测试器启动")
    print("=" * 60)
    
    # 运行异步测试
    success = asyncio.run(test_edge_tts_direct())
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 EdgeTTS 直接测试成功!")
        print("💡 说明: EdgeTTS 库本身工作正常")
    else:
        print("❌ EdgeTTS 直接测试失败!")
        print("💡 说明: EdgeTTS 库可能有问题")
    
    return success

if __name__ == "__main__":
    main()
