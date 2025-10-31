#!/bin/bash
# TT-Live-AI-TTS 安装包创建脚本
# 将整个项目打包为可分发的安装包

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 配置
PROJECT_NAME="TT-Live-AI-TTS"
VERSION="1.0.0"
SOURCE_DIR="/Volumes/M2/TT_Live_AI_TTS"
PACKAGE_DIR="/Volumes/M2/TT_Live_AI_TTS_Installer"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 显示欢迎信息
show_welcome() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                TT-Live-AI-TTS 安装包创建工具                ║"
    echo "║                        版本: $VERSION                        ║"
    echo "║                    时间戳: $TIMESTAMP                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    log_info "开始创建跨平台安装包..."
    echo ""
}

# 检查源目录
check_source_directory() {
    log_step "检查源目录..."
    
    if [[ ! -d "$SOURCE_DIR" ]]; then
        log_error "源目录不存在: $SOURCE_DIR"
        exit 1
    fi
    
    if [[ ! -d "$SOURCE_DIR/installer" ]]; then
        log_error "安装程序目录不存在: $SOURCE_DIR/installer"
        exit 1
    fi
    
    log_success "源目录检查通过"
}

# 创建打包目录
create_package_directory() {
    log_step "创建打包目录..."
    
    if [[ -d "$PACKAGE_DIR" ]]; then
        log_warning "打包目录已存在，正在清理..."
        rm -rf "$PACKAGE_DIR"
    fi
    
    mkdir -p "$PACKAGE_DIR"
    log_success "打包目录创建完成: $PACKAGE_DIR"
}

# 复制安装程序文件
copy_installer_files() {
    log_step "复制安装程序文件..."
    
    # 复制整个 installer 目录
    cp -r "$SOURCE_DIR/installer" "$PACKAGE_DIR/"
    
    # 复制项目核心文件（排除音频文件）
    log_info "复制项目核心文件..."
    
    # 创建项目目录
    mkdir -p "$PACKAGE_DIR/project"
    
    # 复制 Python 文件
    find "$SOURCE_DIR" -name "*.py" -not -path "*/installer/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$PACKAGE_DIR/project/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
    done
    
    # 复制配置文件
    find "$SOURCE_DIR" -name "*.md" -not -path "*/installer/*" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$PACKAGE_DIR/project/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
    done
    
    # 复制 HTML 模板
    find "$SOURCE_DIR" -name "*.html" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$PACKAGE_DIR/project/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
    done
    
    # 复制 CSS 和 JS 文件
    find "$SOURCE_DIR" -name "*.css" -o -name "*.js" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$PACKAGE_DIR/project/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
    done
    
    # 复制启动脚本
    find "$SOURCE_DIR" -name "*.sh" -not -path "*/installer/*" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$PACKAGE_DIR/project/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
        chmod +x "$target_dir/$(basename "$file")"
    done
    
    log_success "项目文件复制完成"
}

# 创建安装包说明文件
create_package_readme() {
    log_step "创建安装包说明文件..."
    
    cat > "$PACKAGE_DIR/README_安装包说明.md" << EOF
# TT-Live-AI-TTS 跨平台安装包

## 📦 安装包信息
- **项目名称**: TT-Live-AI-TTS
- **版本**: $VERSION
- **创建时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **支持平台**: macOS 10.14+ / Windows 10+

## 🚀 快速安装

### 📱 macOS 系统
1. 打开终端 (Terminal)
2. 进入安装包目录: \`cd /path/to/installer\`
3. 运行安装脚本: \`./install_mac.sh\`
4. 按提示完成安装

### 💻 Windows 系统
1. 右键点击 \`install_windows.bat\`
2. 选择"以管理员身份运行"
3. 按提示完成安装

## 📁 安装包结构
\`\`\`
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
\`\`\`

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
如遇到问题，请查看 \`installer/README_安装程序说明.md\` 中的故障排除部分。

---
**TT-Live-AI-TTS 项目团队**
EOF
    
    log_success "安装包说明文件创建完成"
}

# 创建压缩包
create_archive() {
    log_step "创建压缩包..."
    
    cd "/Volumes/M2"
    
    # 创建 tar.gz 压缩包
    ARCHIVE_NAME="${PROJECT_NAME}_Installer_v${VERSION}_${TIMESTAMP}.tar.gz"
    tar -czf "$ARCHIVE_NAME" -C "$(dirname "$PACKAGE_DIR")" "$(basename "$PACKAGE_DIR")"
    
    if [[ -f "$ARCHIVE_NAME" ]]; then
        log_success "压缩包创建成功: $ARCHIVE_NAME"
        
        # 显示文件大小
        FILE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
        log_info "压缩包大小: $FILE_SIZE"
    else
        log_error "压缩包创建失败"
        exit 1
    fi
}

# 创建 ZIP 压缩包（Windows 兼容）
create_zip_archive() {
    log_step "创建 ZIP 压缩包（Windows 兼容）..."
    
    cd "/Volumes/M2"
    
    # 创建 ZIP 压缩包
    ZIP_NAME="${PROJECT_NAME}_Installer_v${VERSION}_${TIMESTAMP}.zip"
    
    # 使用 zip 命令创建压缩包
    if command -v zip &> /dev/null; then
        zip -r "$ZIP_NAME" "$(basename "$PACKAGE_DIR")"
        
        if [[ -f "$ZIP_NAME" ]]; then
            log_success "ZIP 压缩包创建成功: $ZIP_NAME"
            
            # 显示文件大小
            FILE_SIZE=$(du -h "$ZIP_NAME" | cut -f1)
            log_info "ZIP 压缩包大小: $FILE_SIZE"
        else
            log_error "ZIP 压缩包创建失败"
        fi
    else
        log_warning "zip 命令不可用，跳过 ZIP 压缩包创建"
    fi
}

# 显示完成信息
show_completion_info() {
    log_step "安装包创建完成！"
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    安装包创建成功！                         ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_success "安装包已创建完成"
    echo ""
    echo "📁 安装包目录: $PACKAGE_DIR"
    echo ""
    echo "📦 压缩包文件:"
    
    cd "/Volumes/M2"
    for file in ${PROJECT_NAME}_Installer_v${VERSION}_${TIMESTAMP}.*; do
        if [[ -f "$file" ]]; then
            FILE_SIZE=$(du -h "$file" | cut -f1)
            echo "  ✅ $file ($FILE_SIZE)"
        fi
    done
    
    echo ""
    echo "🚀 分发说明:"
    echo "  1. 将压缩包文件发送给用户"
    echo "  2. 用户解压后运行相应的安装脚本"
    echo "  3. macOS 用户运行: ./install_mac.sh"
    echo "  4. Windows 用户运行: install_windows.bat"
    echo ""
    echo "📚 用户指南:"
    echo "  安装包中包含详细的 README_安装程序说明.md 文件"
    echo "  用户可以参考该文件进行安装和使用"
    echo ""
}

# 主函数
main() {
    show_welcome
    
    # 确认创建
    read -p "是否开始创建安装包？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "安装包创建已取消"
        exit 0
    fi
    
    check_source_directory
    create_package_directory
    copy_installer_files
    create_package_readme
    create_archive
    create_zip_archive
    show_completion_info
    
    log_success "安装包创建工具执行完成！"
}

# 错误处理
trap 'log_error "创建过程中发生错误，请检查日志"; exit 1' ERR

# 执行主程序
main "$@"
