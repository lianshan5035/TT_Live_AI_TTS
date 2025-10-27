#!/bin/bash
# TT-Live-AI 音频生成系统快速启动脚本

echo "🎯 TT-Live-AI 音频生成系统"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查必要文件
if [ ! -f "01_核心程序_音频生成系统/excel_to_audio_generator_Excel到音频一键生成器.py" ]; then
    echo "❌ excel_to_audio_generator_Excel到音频一键生成器.py 文件不存在"
    exit 1
fi

if [ ! -f "01_核心程序_音频生成系统/drag_drop_generator_拖拽式音频生成器.py" ]; then
    echo "❌ drag_drop_generator_拖拽式音频生成器.py 文件不存在"
    exit 1
fi

# 检查TTS服务
echo "🔍 检查TTS服务状态..."
python3 "01_核心程序_音频生成系统/drag_drop_generator_拖拽式音频生成器.py" --check-service

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  TTS服务未运行，正在启动..."
    echo "请在新终端中运行: python3 02_TTS服务_语音合成系统/run_tts_TTS语音合成服务.py"
    echo "然后重新运行此脚本"
    exit 1
fi

echo ""
echo "✅ TTS服务运行正常"
echo ""

# 显示使用选项
echo "请选择使用方式："
echo "1. 交互式处理（推荐新手）"
echo "2. 命令行处理（推荐高级用户）"
echo "3. 查看使用指南"
echo "4. 运行测试"
echo "5. 退出"
echo ""

read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        echo "🚀 启动交互式处理..."
        python3 "01_核心程序_音频生成系统/excel_to_audio_generator_Excel到音频一键生成器.py"
        ;;
    2)
        echo "🚀 启动命令行处理..."
        echo "使用方法："
        echo "  python3 01_核心程序_音频生成系统/drag_drop_generator_拖拽式音频生成器.py file1.xlsx file2.xlsx"
        echo "  python3 01_核心程序_音频生成系统/drag_drop_generator_拖拽式音频生成器.py --directory /path/to/files"
        echo ""
        read -p "按回车键继续..."
        ;;
    3)
        echo "📖 打开使用指南..."
        if command -v open &> /dev/null; then
            open "06_文档资料_使用指南和说明/USAGE_GUIDE_使用指南.md"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "06_文档资料_使用指南和说明/USAGE_GUIDE_使用指南.md"
        else
            echo "请手动打开 06_文档资料_使用指南和说明/USAGE_GUIDE_使用指南.md 文件"
        fi
        ;;
    4)
        echo "🧪 运行测试..."
        python3 "01_核心程序_音频生成系统/simple_test_parsing_Excel解析功能测试.py"
        ;;
    5)
        echo "👋 再见！"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 操作完成！"
echo "📁 音频文件保存在: 08_数据文件_输入输出和日志/outputs/"
echo "📊 生成报告保存在: 08_数据文件_输入输出和日志/outputs/generation_report_*.json"
