#!/bin/bash
# EdgeTTS API 启动脚本

echo "🚀 启动 EdgeTTS API 服务..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖包..."
pip3 install -r requirements.txt

# 创建必要目录
echo "📁 创建目录结构..."
mkdir -p logs outputs temp

# 启动服务
echo "🎵 启动 FastAPI 服务..."
echo "📍 服务地址: http://localhost:8000"
echo "📖 API 文档: http://localhost:8000/docs"
echo "❤️ 健康检查: http://localhost:8000/health"

uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
