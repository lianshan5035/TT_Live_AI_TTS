#!/bin/bash
# EdgeTTS 项目打包脚本

set -e

echo "📦 EdgeTTS 多文件并行音频生成系统 - 项目打包"
echo "=========================================="

# 获取当前时间戳
timestamp=$(date +"%Y%m%d_%H%M%S")
package_name="EdgeTTS_MultiFile_Parallel_System_${timestamp}"

echo "📋 创建项目包: $package_name"

# 创建临时打包目录
temp_dir="/tmp/$package_name"
mkdir -p "$temp_dir"

echo "📁 复制项目文件..."

# 复制核心文件
cp -r /Volumes/M2/TT_Live_AI_TTS/* "$temp_dir/" 2>/dev/null || true

# 进入临时目录
cd "$temp_dir"

# 清理不需要的文件
echo "🧹 清理临时文件..."
rm -rf .git
rm -rf __pycache__
rm -rf *.pyc
rm -rf .DS_Store
rm -rf venv
rm -rf 20_输出文件_处理完成的音频文件/*
rm -rf 19_日志文件_系统运行日志和错误记录/*
rm -rf 14_临时文件_运行时生成的文件/*

# 创建项目信息文件
echo "📝 创建项目信息文件..."
cat > PROJECT_INFO.txt << EOF
EdgeTTS 多文件并行音频生成系统
================================

项目版本: v1.0
打包时间: $(date)
打包版本: $timestamp

项目描述:
高效的文本转语音(TTS)批量处理工具，支持多文件并行处理、
丰富语音选择、实时进度监控和剩余时间统计。

核心特性:
- 多文件并行处理 (11个线程)
- 33种英语语音选择
- 实时进度监控
- 剩余时间统计
- 虚拟环境支持
- 一键安装部署

安装说明:
1. 解压项目文件
2. 运行 ./install.sh 安装依赖
3. 运行 ./start_edgetts.sh 启动系统

文件结构:
- EdgeTTS_多文件并行处理器.py: 主处理器
- EdgeTTS_统计时间看板.py: 统计看板
- install.sh: 安装脚本
- start_edgetts.sh: 启动脚本
- README.md: 详细说明文档

技术支持:
如有问题请查看 README.md 或提交 Issue

================================
EOF

# 创建压缩包
echo "🗜️  创建压缩包..."
cd /tmp
tar -czf "${package_name}.tar.gz" "$package_name"

# 移动到桌面
mv "${package_name}.tar.gz" ~/Desktop/

echo ""
echo "🎉 项目打包完成!"
echo "=========================================="
echo "📦 打包文件: ~/Desktop/${package_name}.tar.gz"
echo "📁 项目大小: $(du -sh ~/Desktop/${package_name}.tar.gz | cut -f1)"
echo ""
echo "📋 包含内容:"
echo "✅ 完整的项目源代码"
echo "✅ 安装和启动脚本"
echo "✅ 详细的使用文档"
echo "✅ 项目配置文件"
echo "✅ 虚拟环境支持"
echo ""
echo "🚀 使用方法:"
echo "1. 解压: tar -xzf ${package_name}.tar.gz"
echo "2. 安装: cd $package_name && ./install.sh"
echo "3. 启动: ./start_edgetts.sh"
echo ""
echo "📖 更多信息请查看 README.md"
echo "=========================================="

# 清理临时目录
rm -rf "$temp_dir"
