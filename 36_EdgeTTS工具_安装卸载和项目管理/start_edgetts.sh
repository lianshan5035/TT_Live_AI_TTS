#!/bin/bash
# EdgeTTS 启动脚本

echo "🚀 启动 EdgeTTS 多文件并行音频生成系统"
echo "=========================================="

# 检查输入文件
input_count=$(ls 18_批量输入_批量文件输入目录/*.xlsx 2>/dev/null | wc -l)
if [ $input_count -eq 0 ]; then
    echo "⚠️  警告: 输入目录中没有找到Excel文件"
    echo "请将.xlsx文件放入 18_批量输入_批量文件输入目录/ 目录"
    echo ""
    echo "按任意键继续..."
    read -n 1
fi

echo "📁 找到 $input_count 个Excel文件"
echo ""

# 选择启动模式
echo "请选择启动模式:"
echo "1) 启动多文件并行处理器"
echo "2) 启动统计看板"
echo "3) 启动剩余时间统计器"
echo "4) 全部启动"
echo ""
read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "🚀 启动多文件并行处理器..."
        source venv/bin/activate
        python EdgeTTS_多文件并行处理器.py
        deactivate
        ;;
    2)
        echo "📊 启动统计看板..."
        source venv/bin/activate
        python EdgeTTS_统计时间看板.py
        deactivate
        ;;
    3)
        echo "⏰ 启动剩余时间统计器..."
        ./EdgeTTS_剩余时间统计器.sh
        ;;
    4)
        echo "🚀 启动所有服务..."
        echo "启动多文件并行处理器..."
        source venv/bin/activate
        python EdgeTTS_多文件并行处理器.py &
        sleep 2
        echo "启动统计看板..."
        python EdgeTTS_统计时间看板.py &
        deactivate
        echo "✅ 所有服务已启动"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
