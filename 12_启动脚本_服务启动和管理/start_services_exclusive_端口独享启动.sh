#!/bin/bash
# TT-Live-AI 端口独享启动脚本
# 确保TTS服务端口独享，不允许被占用

echo "🚀 TT-Live-AI 端口独享启动脚本"
echo "=================================="

# 设置端口
TTS_PORT=5001
WEB_PORT=8000

# 检查并清理端口
echo "🔍 检查端口占用情况..."
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  端口 $port ($service_name) 被占用，正在清理..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
        
        # 再次检查
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "❌ 端口 $port 清理失败，请手动处理"
            return 1
        else
            echo "✅ 端口 $port 已清理"
        fi
    else
        echo "✅ 端口 $port ($service_name) 可用"
    fi
    return 0
}

# 检查TTS端口
if ! check_port $TTS_PORT "TTS服务"; then
    echo "❌ TTS端口检查失败，退出"
    exit 1
fi

# 检查Web端口
if ! check_port $WEB_PORT "Web服务"; then
    echo "❌ Web端口检查失败，退出"
    exit 1
fi

# 进入项目目录
cd /Volumes/M2/TT_Live_AI_TTS

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p logs outputs inputs

# 启动TTS服务（端口独享）
echo "🎵 启动TTS语音合成服务 (端口$TTS_PORT)..."
nohup python3 02_TTS服务_语音合成系统/run_tts_TTS语音合成服务.py > logs/tts_service_startup.log 2>&1 &
TTS_PID=$!

# 等待TTS服务启动
echo "⏳ 等待TTS服务启动..."
sleep 5

# 检查TTS服务状态
echo "🔍 检查TTS服务状态..."
if curl -s http://127.0.0.1:$TTS_PORT/health > /dev/null 2>&1; then
    echo "✅ TTS服务启动成功 (PID: $TTS_PID)"
else
    echo "❌ TTS服务启动失败"
    echo "📋 TTS服务日志:"
    tail -20 logs/tts_service_startup.log
    exit 1
fi

# 启动Web服务（端口独享）
echo "🌐 启动Web控制台服务 (端口$WEB_PORT)..."
nohup python3 03_Web界面_控制台系统/web_dashboard_simple_Web控制台界面.py > logs/web_service_startup.log 2>&1 &
WEB_PID=$!

# 等待Web服务启动
echo "⏳ 等待Web服务启动..."
sleep 5

# 检查Web服务状态
echo "🔍 检查Web服务状态..."
if curl -s http://127.0.0.1:$WEB_PORT > /dev/null 2>&1; then
    echo "✅ Web服务启动成功 (PID: $WEB_PID)"
else
    echo "❌ Web服务启动失败"
    echo "📋 Web服务日志:"
    tail -20 logs/web_service_startup.log
    exit 1
fi

# 最终状态检查
echo ""
echo "🎉 所有服务启动完成！"
echo "=================================="
echo "📊 服务状态:"
echo "  TTS服务: http://127.0.0.1:$TTS_PORT (PID: $TTS_PID)"
echo "  Web控制台: http://127.0.0.1:$WEB_PORT (PID: $WEB_PID)"
echo ""
echo "🔗 访问地址:"
echo "  Web界面: http://127.0.0.1:$WEB_PORT"
echo "  TTS API: http://127.0.0.1:$TTS_PORT/generate"
echo "  健康检查: http://127.0.0.1:$TTS_PORT/health"
echo ""
echo "📋 进程管理:"
echo "  停止所有服务: pkill -f 'run_tts_TTS语音合成服务.py' && pkill -f 'web_dashboard_simple_Web控制台界面.py'"
echo "  查看TTS日志: tail -f logs/tts_service.log"
echo "  查看Web日志: tail -f logs/web_service.log"
echo ""
echo "⚠️  端口独享设置:"
echo "  TTS端口 $TTS_PORT: 独享，不允许其他进程占用"
echo "  Web端口 $WEB_PORT: 独享，不允许其他进程占用"
echo ""

# 保存PID到文件
echo "$TTS_PID" > logs/tts_service.pid
echo "$WEB_PID" > logs/web_service.pid

echo "✅ 服务启动完成，端口独享设置生效！"
