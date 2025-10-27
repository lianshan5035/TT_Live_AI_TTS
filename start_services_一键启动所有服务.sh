#!/bin/bash
# TT-Live-AI 语音生成系统
# 一键启动所有服务脚本

echo "🚀 TT-Live-AI 语音生成系统启动中..."
echo "=================================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "📦 检查Python依赖..."
pip list | grep -E "(edge-tts|flask|pandas)" > /dev/null
if [ $? -ne 0 ]; then
    echo "📥 安装必要依赖..."
    pip install edge-tts pandas flask requests numpy
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p logs templates static/css static/js static/images

# 复制模板和静态文件
echo "📋 复制模板和静态文件..."
cp "04_Web模板_界面模板文件/"*.html templates/ 2>/dev/null || echo "⚠️  模板文件已存在"
cp -r "05_静态资源_CSS和JS文件/"* static/ 2>/dev/null || echo "⚠️  静态文件已存在"

# 停止现有服务
echo "🛑 停止现有服务..."
pkill -f "run_tts" 2>/dev/null || true
pkill -f "web_dashboard_simple" 2>/dev/null || true
sleep 2

# 启动TTS服务
echo "🎵 启动TTS语音合成服务 (端口5001)..."
python3 "02_TTS服务_语音合成系统/run_tts_TTS语音合成服务.py" &
TTS_PID=$!

# 等待TTS服务启动
sleep 3

# 检查TTS服务
echo "🔍 检查TTS服务状态..."
curl -s http://127.0.0.1:5001/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ TTS服务启动成功"
else
    echo "❌ TTS服务启动失败"
    exit 1
fi

# 启动Web控制台
echo "🌐 启动Web控制台 (端口8000)..."
python3 "03_Web界面_控制台系统/web_dashboard_simple_Web控制台界面.py" &
WEB_PID=$!

# 等待Web控制台启动
sleep 3

# 检查Web控制台
echo "🔍 检查Web控制台状态..."
curl -s http://127.0.0.1:8000/api/status > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Web控制台启动成功"
else
    echo "❌ Web控制台启动失败"
    exit 1
fi

echo ""
echo "🎉 所有服务启动完成！"
echo "=================================="
echo "📱 Web控制台: http://127.0.0.1:8000"
echo "🎵 TTS服务: http://127.0.0.1:5001"
echo "📊 服务状态:"
echo "   - TTS服务 PID: $TTS_PID"
echo "   - Web控制台 PID: $WEB_PID"
echo ""
echo "💡 使用说明:"
echo "   1. 打开浏览器访问 http://127.0.0.1:8000 (智能界面)"
echo "   2. 或访问 http://127.0.0.1:8000/modern (现代界面)"
echo "   3. 或访问 http://127.0.0.1:8000/classic (经典界面)"
echo "   4. 上传Excel文件进行语音生成"
echo "   5. 按 Ctrl+C 停止所有服务"
echo ""

# 保存PID到文件
echo $TTS_PID > .tts_pid
echo $WEB_PID > .web_pid

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止服务..."; kill $TTS_PID $WEB_PID 2>/dev/null; rm -f .tts_pid .web_pid; echo "✅ 服务已停止"; exit 0' INT

echo "⏳ 服务运行中，按 Ctrl+C 停止..."
wait
