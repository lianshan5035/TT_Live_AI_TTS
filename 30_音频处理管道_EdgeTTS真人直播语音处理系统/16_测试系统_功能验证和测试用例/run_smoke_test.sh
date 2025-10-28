#!/bin/bash
# EdgeTTS 批量语音后处理管线 - 冒烟测试脚本

set -e

echo "=========================================="
echo "EdgeTTS 音频处理管线 - 冒烟测试"
echo "=========================================="

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Python版本: $python_version"

# 检查FFmpeg
echo "检查FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg 未安装，请运行: brew install ffmpeg"
    exit 1
fi

if ! ffmpeg -filters 2>/dev/null | grep -q rubberband; then
    echo "⚠️  FFmpeg 缺少 Rubberband 支持，将使用 atempo 回退"
    echo "   建议安装: brew install ffmpeg rubberband"
else
    echo "✓ FFmpeg 支持 Rubberband"
fi

# 检查FFprobe
if ! command -v ffprobe &> /dev/null; then
    echo "❌ FFprobe 未安装"
    exit 1
fi
echo "✓ FFprobe 已安装"

# 检查Python依赖
echo "检查Python依赖..."
if ! python3 -c "import click, tqdm" 2>/dev/null; then
    echo "❌ 缺少Python依赖，请运行: pip install click tqdm"
    exit 1
fi
echo "✓ Python依赖已安装"

# 创建测试环境
echo "准备测试环境..."

# 清理旧文件
rm -rf audio_pipeline/input_raw/*
rm -rf audio_pipeline/output_processed/*
rm -rf audio_pipeline/logs/failed/*

# 创建测试音频文件（使用FFmpeg生成）
echo "生成测试音频文件..."
mkdir -p audio_pipeline/input_raw

# 生成3个测试音频文件
for i in {1..3}; do
    ffmpeg -f lavfi -i "sine=frequency=440:duration=10" \
           -f lavfi -i "sine=frequency=880:duration=10" \
           -filter_complex "[0:a][1:a]amix=inputs=2:duration=first" \
           -ar 44100 -ac 2 -y "audio_pipeline/input_raw/test_$i.wav" 2>/dev/null
done

echo "✓ 生成了 3 个测试音频文件"

# 创建一些背景音效文件
echo "生成背景音效文件..."
mkdir -p audio_pipeline/assets/ambience

# 生成白噪音
ffmpeg -f lavfi -i "anoisesrc=color=pink:amplitude=0.1:duration=30" \
       -ar 44100 -ac 2 -y "audio_pipeline/assets/ambience/white_noise.wav" 2>/dev/null

# 生成房间音
ffmpeg -f lavfi -i "sine=frequency=60:duration=30" \
       -f lavfi -i "sine=frequency=120:duration=30" \
       -filter_complex "[0:a][1:a]amix=inputs=2:duration=first" \
       -ar 44100 -ac 2 -y "audio_pipeline/assets/ambience/room_tone.wav" 2>/dev/null

echo "✓ 生成了背景音效文件"

# 创建一些事件音效文件
echo "生成事件音效文件..."
mkdir -p audio_pipeline/assets/events

# 生成键盘声
ffmpeg -f lavfi -i "sine=frequency=2000:duration=2" \
       -ar 44100 -ac 2 -y "audio_pipeline/assets/events/keyboard.wav" 2>/dev/null

# 生成倒水声
ffmpeg -f lavfi -i "sine=frequency=1000:duration=1.5" \
       -ar 44100 -ac 2 -y "audio_pipeline/assets/events/water_pour.wav" 2>/dev/null

echo "✓ 生成了事件音效文件"

# 运行测试
echo "运行音频处理测试..."
echo "命令: python3 process_audio.py --preview 2 --threads 1 --seed 123"

python3 process_audio.py --preview 2 --threads 1 --seed 123

# 检查结果
echo "检查处理结果..."

if [ -d "audio_pipeline/output_processed" ] && [ "$(ls -A audio_pipeline/output_processed)" ]; then
    echo "✓ 输出文件已生成"
    ls -la audio_pipeline/output_processed/
else
    echo "❌ 未找到输出文件"
    exit 1
fi

if [ -d "audio_pipeline/logs" ] && [ -f "audio_pipeline/logs/pipeline.log" ]; then
    echo "✓ 日志文件已生成"
else
    echo "❌ 未找到日志文件"
    exit 1
fi

# 检查JSON结果文件
json_files=$(find audio_pipeline/logs -name "results_*.json" | wc -l)
if [ "$json_files" -gt 0 ]; then
    echo "✓ JSON结果文件已生成 ($json_files 个)"
else
    echo "❌ 未找到JSON结果文件"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 冒烟测试通过!"
echo "=========================================="
echo ""
echo "测试结果:"
echo "- 生成了测试音频文件"
echo "- 生成了背景音效和事件音效"
echo "- 成功处理了音频文件"
echo "- 生成了日志和JSON结果文件"
echo ""
echo "可以开始使用音频处理管线了!"
echo ""
echo "使用示例:"
echo "  python3 process_audio.py --preview 5"
echo "  python3 process_audio.py --threads 4 --seed 456"
echo "  python3 process_audio.py --dry-run"
echo ""
