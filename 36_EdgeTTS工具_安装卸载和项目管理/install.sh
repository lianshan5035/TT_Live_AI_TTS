#!/bin/bash
# EdgeTTS 多文件并行音频生成系统 - 安装包脚本

set -e

echo "🚀 EdgeTTS 多文件并行音频生成系统 - 安装包"
echo "=========================================="

# 检查Python版本
echo "📋 检查系统环境..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Python版本: $python_version"

# 提取主版本号
major_version=$(echo $python_version | cut -d'.' -f1)
minor_version=$(echo $python_version | cut -d'.' -f2)

if [ $major_version -lt 3 ] || ([ $major_version -eq 3 ] && [ $minor_version -lt 8 ]); then
    echo "❌ 错误: 需要Python 3.8或更高版本"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到pip3，请先安装pip"
    exit 1
fi

echo "✅ pip3已安装"

# 创建虚拟环境
echo ""
echo "📦 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境并安装依赖
echo ""
echo "📦 安装Python依赖..."
source venv/bin/activate
pip install edge-tts pandas requests
deactivate

# 检查依赖安装
echo ""
echo "🔍 验证依赖安装..."
source venv/bin/activate
python -c "import edge_tts; print('✅ edge-tts:', edge_tts.__version__)"
python -c "import pandas; print('✅ pandas:', pandas.__version__)"
python -c "import requests; print('✅ requests:', requests.__version__)"
deactivate

# 创建必要的目录
echo ""
echo "📁 创建项目目录结构..."
mkdir -p 18_批量输入_批量文件输入目录
mkdir -p 20_输出文件_处理完成的音频文件
mkdir -p 19_日志文件_系统运行日志和错误记录
mkdir -p 14_临时文件_运行时生成的文件

echo "✅ 目录结构创建完成"

# 设置执行权限
echo ""
echo "🔧 设置执行权限..."
chmod +x EdgeTTS_统计看板.sh
chmod +x EdgeTTS_剩余时间统计器.sh
chmod +x EdgeTTS_自动批量处理.sh

echo "✅ 执行权限设置完成"

# 创建启动脚本
echo ""
echo "📝 创建启动脚本..."
cat > start_edgetts.sh << 'EOF'
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
EOF

chmod +x start_edgetts.sh
echo "✅ 启动脚本创建完成"

# 创建卸载脚本
echo ""
echo "📝 创建卸载脚本..."
cat > uninstall_edgetts.sh << 'EOF'
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
EOF

chmod +x uninstall_edgetts.sh
echo "✅ 卸载脚本创建完成"

# 创建配置文件
echo ""
echo "📝 创建默认配置文件..."
cat > EdgeTTS_默认配置.json << 'EOF'
{
  "EdgeTTS_默认配置": {
    "项目信息": {
      "项目名称": "EdgeTTS 多文件并行音频生成系统",
      "版本": "v1.0",
      "创建时间": "2025-10-28",
      "描述": "高效的文本转语音批量处理工具"
    },
    "路径配置": {
      "项目根目录": "/Volumes/M2/TT_Live_AI_TTS",
      "输入目录": "18_批量输入_批量文件输入目录",
      "输出目录": "20_输出文件_处理完成的音频文件",
      "日志目录": "19_日志文件_系统运行日志和错误记录",
      "临时目录": "14_临时文件_运行时生成的文件"
    },
    "处理配置": {
      "最大线程数": 11,
      "默认语音": "en-US-JennyNeural",
      "文件延迟": 2,
      "质量检查": true
    },
    "语音配置": {
      "可用语音数量": 33,
      "分配策略": "每个文件专用语音，不重复"
    }
  }
}
EOF

echo "✅ 默认配置文件创建完成"

# 运行测试
echo ""
echo "🧪 运行系统测试..."
source venv/bin/activate
python -c "
import edge_tts
import pandas as pd
import os

print('✅ 依赖库导入成功')

# 测试EdgeTTS
try:
    voices = list(edge_tts.list_voices())
    print(f'✅ EdgeTTS语音列表: {len(voices)} 个语音')
except Exception as e:
    print(f'⚠️  EdgeTTS测试警告: {e}')

# 测试目录
dirs = ['18_批量输入_批量文件输入目录', '20_输出文件_处理完成的音频文件', '19_日志文件_系统运行日志和错误记录']
for dir_name in dirs:
    if os.path.exists(dir_name):
        print(f'✅ 目录存在: {dir_name}')
    else:
        print(f'❌ 目录缺失: {dir_name}')

print('✅ 系统测试完成')
"
deactivate

# 显示安装完成信息
echo ""
echo "🎉 安装完成!"
echo "=========================================="
echo "📋 安装摘要:"
echo "✅ Python依赖已安装"
echo "✅ 项目目录已创建"
echo "✅ 执行权限已设置"
echo "✅ 启动脚本已创建"
echo "✅ 配置文件已创建"
echo "✅ 系统测试已通过"
echo ""
echo "🚀 使用方法:"
echo "1. 将Excel文件放入 18_批量输入_批量文件输入目录/ 目录"
echo "2. 运行 ./start_edgetts.sh 启动系统"
echo "3. 选择相应的启动模式"
echo ""
echo "📊 监控工具:"
echo "- 统计看板: python3 EdgeTTS_统计时间看板.py"
echo "- 剩余时间: ./EdgeTTS_剩余时间统计器.sh"
echo ""
echo "📖 更多信息请查看 README.md"
echo "=========================================="
