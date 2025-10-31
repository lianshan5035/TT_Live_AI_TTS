#!/bin/bash
# TT-Live-AI-TTS macOS 安装程序
# 版本: 1.0.0
# 支持: macOS 10.14+

set -e  # 遇到错误立即退出

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

# 安装程序信息
INSTALLER_VERSION="1.0.0"
PROJECT_NAME="TT-Live-AI-TTS"
INSTALL_DIR="$HOME/TT_Live_AI_TTS"
INSTALLER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(dirname "$INSTALLER_DIR")"

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    TT-Live-AI-TTS 安装程序                    ║"
    echo "║                         macOS 版本                           ║"
    echo "║                        版本: $INSTALLER_VERSION                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    log_info "欢迎使用 TT-Live-AI-TTS 安装程序！"
    echo ""
    echo "本安装程序将为您安装："
    echo "  • TTS 语音合成服务"
    echo "  • Web 控制台界面"
    echo "  • 批量处理功能"
    echo "  • API 接口服务"
    echo ""
    echo "安装目录: $INSTALL_DIR"
    echo ""
}

# 检查系统要求
check_system_requirements() {
    log_step "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "此安装程序仅支持 macOS 系统"
        exit 1
    fi
    
    # 检查 macOS 版本
    MACOS_VERSION=$(sw_vers -productVersion)
    MACOS_MAJOR=$(echo $MACOS_VERSION | cut -d. -f1)
    MACOS_MINOR=$(echo $MACOS_VERSION | cut -d. -f2)
    
    if [[ $MACOS_MAJOR -lt 10 ]] || [[ $MACOS_MAJOR -eq 10 && $MACOS_MINOR -lt 14 ]]; then
        log_error "需要 macOS 10.14 (Mojave) 或更高版本，当前版本: $MACOS_VERSION"
        exit 1
    fi
    
    log_success "macOS 版本检查通过: $MACOS_VERSION"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 Python 3，请先安装 Python 3.8+"
        log_info "建议使用 Homebrew 安装: brew install python3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
        log_error "需要 Python 3.8+，当前版本: $PYTHON_VERSION"
        exit 1
    fi
    
    log_success "Python 版本检查通过: $PYTHON_VERSION"
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        log_error "未找到 pip3，请先安装 pip"
        exit 1
    fi
    
    log_success "pip3 检查通过"
    
    # 检查磁盘空间
    AVAILABLE_SPACE=$(df -h "$HOME" | awk 'NR==2 {print $4}' | sed 's/[^0-9.]//g')
    if (( $(echo "$AVAILABLE_SPACE < 2" | bc -l) )); then
        log_warning "可用磁盘空间不足 2GB，当前可用: ${AVAILABLE_SPACE}GB"
        read -p "是否继续安装？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "安装已取消"
            exit 0
        fi
    fi
    
    log_success "系统要求检查完成"
}

# 创建安装目录
create_install_directory() {
    log_step "创建安装目录..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        log_warning "安装目录已存在: $INSTALL_DIR"
        read -p "是否覆盖现有安装？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "备份现有安装..."
            BACKUP_DIR="${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
            mv "$INSTALL_DIR" "$BACKUP_DIR"
            log_success "现有安装已备份到: $BACKUP_DIR"
        else
            log_info "安装已取消"
            exit 0
        fi
    fi
    
    mkdir -p "$INSTALL_DIR"
    log_success "安装目录创建完成: $INSTALL_DIR"
}

# 复制项目文件（排除音频文件）
copy_project_files() {
    log_step "复制项目文件..."
    
    # 创建必要的目录结构
    mkdir -p "$INSTALL_DIR"/{logs,input,outputs,templates,static}
    
    # 复制主要文件，排除音频文件
    log_info "复制核心文件..."
    
    # 复制 Python 文件
    find "$SOURCE_DIR" -name "*.py" -not -path "*/installer/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$INSTALL_DIR/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
    done
    
    # 复制配置文件
    find "$SOURCE_DIR" -name "*.md" -not -path "*/installer/*" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$INSTALL_DIR/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
    done
    
    # 复制 HTML 模板
    find "$SOURCE_DIR" -name "*.html" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$INSTALL_DIR/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
    done
    
    # 复制 CSS 和 JS 文件
    find "$SOURCE_DIR" -name "*.css" -o -name "*.js" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$INSTALL_DIR/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
    done
    
    # 复制启动脚本
    find "$SOURCE_DIR" -name "*.sh" -not -path "*/installer/*" | while read file; do
        rel_path="${file#$SOURCE_DIR/}"
        target_dir="$INSTALL_DIR/$(dirname "$rel_path")"
        mkdir -p "$target_dir"
        cp "$file" "$target_dir/"
        chmod +x "$target_dir/$(basename "$file")"
    done
    
    # 复制配置文件
    cp "$INSTALLER_DIR/config/config.json" "$INSTALL_DIR/"
    cp "$INSTALLER_DIR/config/.env_template" "$INSTALL_DIR/.env"
    
    log_success "项目文件复制完成"
}

# 创建虚拟环境
create_virtual_environment() {
    log_step "创建 Python 虚拟环境..."
    
    cd "$INSTALL_DIR"
    
    # 创建虚拟环境
    python3 -m venv venv
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    log_success "虚拟环境创建完成"
}

# 安装依赖包
install_dependencies() {
    log_step "安装 Python 依赖包..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # 安装依赖
    pip install -r "$INSTALLER_DIR/requirements.txt"
    
    log_success "依赖包安装完成"
}

# 设置权限
set_permissions() {
    log_step "设置文件权限..."
    
    cd "$INSTALL_DIR"
    
    # 设置脚本执行权限
    find . -name "*.sh" -exec chmod +x {} \;
    find . -name "*.py" -exec chmod +x {} \;
    
    # 设置目录权限
    chmod 755 logs input outputs templates static
    
    log_success "文件权限设置完成"
}

# 验证安装
verify_installation() {
    log_step "验证安装..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # 检查关键文件
    REQUIRED_FILES=(
        "02_TTS服务_语音合成系统/run_tts_TTS语音合成服务.py"
        "03_Web界面_控制台系统/web_dashboard_simple_Web控制台界面.py"
        "12_启动脚本_服务启动和管理/start_services_一键启动所有服务.sh"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "关键文件缺失: $file"
            exit 1
        fi
    done
    
    # 检查 Python 包
    REQUIRED_PACKAGES=("flask" "edge-tts" "pandas" "openpyxl")
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! python -c "import $package" 2>/dev/null; then
            log_error "Python 包缺失: $package"
            exit 1
        fi
    done
    
    log_success "安装验证通过"
}

# 创建启动脚本
create_startup_script() {
    log_step "创建启动脚本..."
    
    cat > "$INSTALL_DIR/start_tts_system.sh" << 'EOF'
#!/bin/bash
# TT-Live-AI-TTS 系统启动脚本

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$INSTALL_DIR"

echo "🚀 启动 TT-Live-AI-TTS 系统..."
echo "安装目录: $INSTALL_DIR"

# 激活虚拟环境
source venv/bin/activate

# 启动服务
./12_启动脚本_服务启动和管理/start_services_一键启动所有服务.sh
EOF
    
    chmod +x "$INSTALL_DIR/start_tts_system.sh"
    
    log_success "启动脚本创建完成"
}

# 显示安装完成信息
show_completion_info() {
    log_step "安装完成！"
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    安装成功完成！                           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_success "TT-Live-AI-TTS 已成功安装到: $INSTALL_DIR"
    echo ""
    echo "🚀 快速启动:"
    echo "  cd $INSTALL_DIR"
    echo "  ./start_tts_system.sh"
    echo ""
    echo "🌐 访问地址:"
    echo "  Web 控制台: http://127.0.0.1:8000"
    echo "  TTS 服务: http://127.0.0.1:5001"
    echo ""
    echo "📚 使用说明:"
    echo "  1. 运行启动脚本启动所有服务"
    echo "  2. 打开浏览器访问 Web 控制台"
    echo "  3. 上传 Excel 文件进行语音生成"
    echo "  4. 使用 API 接口进行集成"
    echo ""
    echo "📁 重要目录:"
    echo "  输入文件: $INSTALL_DIR/input"
    echo "  输出文件: $INSTALL_DIR/outputs"
    echo "  日志文件: $INSTALL_DIR/logs"
    echo "  配置文件: $INSTALL_DIR/.env"
    echo ""
    echo "🔧 配置修改:"
    echo "  编辑 $INSTALL_DIR/.env 文件修改配置"
    echo ""
    echo "📖 更多信息请查看: $INSTALL_DIR/README_项目说明.md"
    echo ""
}

# 主安装流程
main() {
    show_welcome
    
    # 确认安装
    read -p "是否继续安装？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "安装已取消"
        exit 0
    fi
    
    check_system_requirements
    create_install_directory
    copy_project_files
    create_virtual_environment
    install_dependencies
    set_permissions
    verify_installation
    create_startup_script
    show_completion_info
    
    log_success "安装程序执行完成！"
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 执行主程序
main "$@"
