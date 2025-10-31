#!/bin/bash
# TT-Live-AI-TTS 简化安装包创建脚本

echo "🚀 开始创建 TT-Live-AI-TTS 安装包..."

# 创建安装包目录
INSTALLER_DIR="/Volumes/M2/TT_Live_AI_TTS_Installer"
mkdir -p "$INSTALLER_DIR"

# 复制安装程序
echo "📁 复制安装程序文件..."
cp -r /Volumes/M2/TT_Live_AI_TTS/installer "$INSTALLER_DIR/"

# 复制项目核心文件（排除音频文件）
echo "📄 复制项目核心文件..."
mkdir -p "$INSTALLER_DIR/project"

# 复制 Python 文件
find /Volumes/M2/TT_Live_AI_TTS -name "*.py" -not -path "*/installer/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" | while read file; do
    rel_path="${file#/Volumes/M2/TT_Live_AI_TTS/}"
    target_dir="$INSTALLER_DIR/project/$(dirname "$rel_path")"
    mkdir -p "$target_dir"
    cp "$file" "$target_dir/"
done

# 复制配置文件
find /Volumes/M2/TT_Live_AI_TTS -name "*.md" -not -path "*/installer/*" | while read file; do
    rel_path="${file#/Volumes/M2/TT_Live_AI_TTS/}"
    target_dir="$INSTALLER_DIR/project/$(dirname "$rel_path")"
    mkdir -p "$target_dir"
    cp "$file" "$target_dir/"
done

# 复制 HTML 模板
find /Volumes/M2/TT_Live_AI_TTS -name "*.html" | while read file; do
    rel_path="${file#/Volumes/M2/TT_Live_AI_TTS/}"
    target_dir="$INSTALLER_DIR/project/$(dirname "$rel_path")"
    mkdir -p "$target_dir"
    cp "$file" "$target_dir/"
done

# 复制 CSS 和 JS 文件
find /Volumes/M2/TT_Live_AI_TTS -name "*.css" -o -name "*.js" | while read file; do
    rel_path="${file#/Volumes/M2/TT_Live_AI_TTS/}"
    target_dir="$INSTALLER_DIR/project/$(dirname "$rel_path")"
    mkdir -p "$target_dir"
    cp "$file" "$target_dir/"
done

# 复制启动脚本
find /Volumes/M2/TT_Live_AI_TTS -name "*.sh" -not -path "*/installer/*" | while read file; do
    rel_path="${file#/Volumes/M2/TT_Live_AI_TTS/}"
    target_dir="$INSTALLER_DIR/project/$(dirname "$rel_path")"
    mkdir -p "$target_dir"
    cp "$file" "$target_dir/"
    chmod +x "$target_dir/$(basename "$file")"
done

# 创建安装包说明文件
echo "📝 创建安装包说明文件..."
cat > "$INSTALLER_DIR/README_安装包说明.md" << 'EOF'
# TT-Live-AI-TTS 跨平台安装包

## 📦 安装包信息
- **项目名称**: TT-Live-AI-TTS
- **版本**: 1.0.0
- **支持平台**: macOS 10.14+ / Windows 10+

## 🚀 快速安装

### 📱 macOS 系统
1. 打开终端 (Terminal)
2. 进入安装包目录: `cd /path/to/installer`
3. 运行安装脚本: `./install_mac.sh`
4. 按提示完成安装

### 💻 Windows 系统
1. 右键点击 `install_windows.bat`
2. 选择"以管理员身份运行"
3. 按提示完成安装

## 📁 安装包结构
```
installer/
├── README_安装程序说明.md      # 详细安装说明
├── install_mac.sh              # macOS 安装脚本
├── install_windows.bat         # Windows 安装脚本
├── requirements.txt            # Python 依赖包
├── config/                     # 配置文件
├── scripts/                    # 辅助脚本
└── exclude_patterns.txt        # 排除文件模式

project/                        # 项目核心文件
├── 01_核心程序_音频生成系统/
├── 02_TTS服务_语音合成系统/
├── 03_Web界面_控制台系统/
├── 04_Web模板_界面模板文件/
├── 05_静态资源_CSS和JS文件/
├── 06_文档资料_使用指南和说明/
├── 07_配置文件_依赖和设置/
├── 08_数据文件_输入输出和日志/
├── 09_报告文件_清理和重命名记录/
├── 10_GPTs文档_指令和知识库/
├── 11_测试文件_测试脚本和临时文件/
├── 12_启动脚本_服务启动和管理/
├── 13_报告文档_状态报告和解决方案/
└── ... (其他项目文件)
```

## ⚠️ 重要说明
- 本安装包已排除所有音频文件以保持轻量化
- 安装后会自动创建虚拟环境
- 首次运行需要网络连接下载依赖包
- 建议在安装前关闭杀毒软件

## 🔧 系统要求
- **macOS**: 10.14+ (Mojave 或更高版本)
- **Windows**: Windows 10+ 或 Windows Server 2016+
- **Python**: 3.8+ (安装程序会自动检查)
- **内存**: 至少 4GB RAM
- **存储**: 至少 2GB 可用空间

## 📞 技术支持
如遇到问题，请查看 `installer/README_安装程序说明.md` 中的故障排除部分。

---
**TT-Live-AI-TTS 项目团队**
EOF

# 创建压缩包
echo "📦 创建压缩包..."
cd /Volumes/M2
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="TT-Live-AI-TTS_Installer_v1.0.0_${TIMESTAMP}.tar.gz"

tar -czf "$ARCHIVE_NAME" TT_Live_AI_TTS_Installer/

if [[ -f "$ARCHIVE_NAME" ]]; then
    echo "✅ 压缩包创建成功: $ARCHIVE_NAME"
    FILE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
    echo "📊 压缩包大小: $FILE_SIZE"
else
    echo "❌ 压缩包创建失败"
fi

echo ""
echo "🎉 安装包创建完成！"
echo "📁 安装包目录: $INSTALLER_DIR"
echo "📦 压缩包文件: $ARCHIVE_NAME"
echo ""
echo "🚀 分发说明:"
echo "  1. 将压缩包文件发送给用户"
echo "  2. 用户解压后运行相应的安装脚本"
echo "  3. macOS 用户运行: ./install_mac.sh"
echo "  4. Windows 用户运行: install_windows.bat"
