#!/bin/bash
# EdgeTTS 卸载脚本

echo "🗑️  EdgeTTS 多文件并行音频生成系统 - 卸载"
echo "=========================================="

read -p "确定要卸载EdgeTTS系统吗? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ 取消卸载"
    exit 0
fi

echo "🔄 停止所有EdgeTTS进程..."
pkill -f "EdgeTTS" 2>/dev/null || true

echo "📦 卸载Python依赖..."
pip3 uninstall -y edge-tts pandas requests 2>/dev/null || true

echo "🗑️  清理项目文件..."
rm -f start_edgetts.sh
rm -f uninstall_edgetts.sh

echo "✅ 卸载完成"
echo "注意: 输出文件和日志文件已保留，如需完全清理请手动删除"
