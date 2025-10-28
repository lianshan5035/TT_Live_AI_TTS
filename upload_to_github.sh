#!/bin/bash
# EdgeTTS 项目上传到GitHub脚本

set -e

echo "🚀 EdgeTTS 项目上传到GitHub"
echo "=========================================="

# 检查Git状态
echo "📋 检查Git状态..."
if [ ! -d ".git" ]; then
    echo "❌ 错误: 当前目录不是Git仓库"
    echo "请先运行: git init"
    exit 1
fi

# 检查GitHub远程仓库
echo "🔍 检查GitHub远程仓库..."
if ! git remote get-url origin &> /dev/null; then
    echo "⚠️  未找到GitHub远程仓库"
    echo "请先添加GitHub远程仓库:"
    echo "git remote add origin https://github.com/yourusername/EdgeTTS-MultiFile-Parallel.git"
    echo ""
    read -p "是否继续? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "❌ 取消上传"
        exit 0
    fi
fi

# 创建.gitignore文件
echo "📝 更新.gitignore文件..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db

# 日志文件
*.log
logs/

# 临时文件
temp/
tmp/
*.tmp

# 输出文件 (可选，根据需要调整)
# 20_输出文件_处理完成的音频文件/
# 19_日志文件_系统运行日志和错误记录/

# 输入文件 (可选，根据需要调整)
# 18_批量输入_批量文件输入目录/

# 配置文件 (包含敏感信息)
# EdgeTTS_统一配置.json
# EdgeTTS_最终配置_固定版.json
EOF

echo "✅ .gitignore文件已更新"

# 添加文件到Git
echo "📦 添加文件到Git..."
git add .

# 检查文件状态
echo "📋 检查文件状态..."
git status

# 提交更改
echo "💾 提交更改..."
read -p "请输入提交信息 (默认: Update EdgeTTS MultiFile Parallel System): " commit_msg
commit_msg=${commit_msg:-"Update EdgeTTS MultiFile Parallel System"}

git commit -m "$commit_msg"

# 推送到GitHub
echo "🚀 推送到GitHub..."
git push origin main

echo ""
echo "🎉 上传完成!"
echo "=========================================="
echo "📋 上传摘要:"
echo "✅ 文件已添加到Git"
echo "✅ 更改已提交"
echo "✅ 已推送到GitHub"
echo ""
echo "🔗 GitHub仓库地址:"
git remote get-url origin
echo ""
echo "📖 项目文档:"
echo "- README.md: 项目说明和使用指南"
echo "- install.sh: 安装脚本"
echo "- EdgeTTS_多文件并行处理器.py: 主处理器"
echo "- EdgeTTS_统计时间看板.py: 统计看板"
echo "=========================================="
