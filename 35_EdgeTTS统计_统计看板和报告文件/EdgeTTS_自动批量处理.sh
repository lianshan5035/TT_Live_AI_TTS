#!/bin/bash
# EdgeTTS 自动批量处理启动脚本
# ================================
# 每次启动都自动执行 18_批量输入_批量文件输入目录 下的所有 xlsx 文件

echo "🚀 EdgeTTS 自动批量处理启动脚本"
echo "=================================="

# 切换到项目目录
cd /Volumes/M2/TT_Live_AI_TTS

echo "📁 当前目录: $(pwd)"

# 检查 TTS 服务状态
echo "🔍 检查 TTS 服务状态..."
python3 -c "
import requests
import sys

tts_urls = ['http://127.0.0.1:5001', 'http://127.0.0.1:5002', 'http://127.0.0.1:5003']
available_services = []

for i, url in enumerate(tts_urls, 1):
    try:
        response = requests.get(f'{url}/status', timeout=3)
        if response.status_code == 200:
            available_services.append(url)
            print(f'✅ TTS 服务 {i} ({url}) 运行正常')
        else:
            print(f'❌ TTS 服务 {i} ({url}) 响应异常: {response.status_code}')
    except Exception as e:
        print(f'❌ TTS 服务 {i} ({url}) 连接失败')

if not available_services:
    print('❌ 没有可用的 TTS 服务，请先启动服务')
    print('💡 启动命令:')
    print('   cd /Volumes/M2/TT_Live_AI_TTS/02_TTS服务_语音合成系统')
    print('   python3 run_tts_TTS语音合成服务.py --port 5001 &')
    print('   python3 run_tts_TTS语音合成服务.py --port 5002 &')
    print('   python3 run_tts_TTS语音合成服务.py --port 5003 &')
    sys.exit(1)
else:
    print(f'🎯 可用服务数量: {len(available_services)}')
"

if [ $? -ne 0 ]; then
    echo "❌ TTS 服务检查失败，请先启动服务"
    exit 1
fi

echo ""
echo "✅ TTS 服务运行正常，开始批量处理..."
echo "=================================="

# 执行统一启动器
python3 EdgeTTS_统一启动器.py

echo ""
echo "🎉 EdgeTTS 批量处理完成！"
echo "📁 输出目录: /Volumes/M2/TT_Live_AI_TTS/20_输出文件_处理完成的音频文件"
