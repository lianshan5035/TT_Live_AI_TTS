#!/bin/bash
# TTS服务集群启动脚本
# 启动多个TTS服务实例，实现真正的并行处理

echo "🚀 启动TTS服务集群..."

# 创建日志目录
mkdir -p 19_日志文件_系统运行日志和错误记录

# 启动多个TTS服务实例
echo "📡 启动TTS服务实例 1 (端口5001)..."
python3 02_TTS服务_语音合成系统/run_tts_TTS语音合成服务.py --port 5001 > 19_日志文件_系统运行日志和错误记录/tts_service_5001.log 2>&1 &
echo $! > tts_service_5001.pid

echo "📡 启动TTS服务实例 2 (端口5002)..."
python3 02_TTS服务_语音合成系统/run_tts_TTS语音合成服务.py --port 5002 > 19_日志文件_系统运行日志和错误记录/tts_service_5002.log 2>&1 &
echo $! > tts_service_5002.pid

echo "📡 启动TTS服务实例 3 (端口5003)..."
python3 02_TTS服务_语音合成系统/run_tts_TTS语音合成服务.py --port 5003 > 19_日志文件_系统运行日志和错误记录/tts_service_5003.log 2>&1 &
echo $! > tts_service_5003.pid

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
for port in 5001 5002 5003; do
    if curl -s http://127.0.0.1:$port/health > /dev/null; then
        echo "✅ 服务 $port 运行正常"
    else
        echo "❌ 服务 $port 启动失败"
    fi
done

echo "🎉 TTS服务集群启动完成!"
echo "📊 集群信息:"
echo "   - 实例数量: 3"
echo "   - 总并发数: 45 (15×3)"
echo "   - 预计提升: 3-5倍速度"
echo ""
echo "💡 使用方法:"
echo "   python3 27_高级优化_多API并行策略/multi_api_processor.py"
