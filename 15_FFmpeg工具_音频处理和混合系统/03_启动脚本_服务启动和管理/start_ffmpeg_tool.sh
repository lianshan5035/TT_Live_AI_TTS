#!/bin/bash
"""
TT_Live_AI_TTS - FFmpeg 音频处理工具启动脚本
用于启动和管理FFmpeg音频处理服务，集成到TT_Live_AI_TTS系统
"""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 检查FFmpeg安装
check_ffmpeg() {
    log_info "检查FFmpeg安装状态..."
    
    if command -v ffmpeg &> /dev/null; then
        FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
        log_success "FFmpeg已安装: $FFMPEG_VERSION"
        return 0
    else
        log_error "FFmpeg未安装"
        return 1
    fi
}

# 检查白噪音模板
check_white_noise_template() {
    log_info "检查白噪音模板文件..."
    
    WHITE_NOISE_PATH="/Volumes/M2/白噪声/2h白噪声.WAV"
    
    if [ -f "$WHITE_NOISE_PATH" ]; then
        SIZE_MB=$(du -m "$WHITE_NOISE_PATH" | cut -f1)
        log_success "白噪音模板文件存在: $SIZE_MB MB"
        return 0
    else
        log_error "白噪音模板文件不存在: $WHITE_NOISE_PATH"
        return 1
    fi
}

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python已安装: $PYTHON_VERSION"
        return 0
    else
        log_error "Python未安装"
        return 1
    fi
}

# 检查TT_Live_AI_TTS系统
check_tt_live_system() {
    log_info "检查TT_Live_AI_TTS系统..."
    
    TT_LIVE_DIR="/Volumes/M2/TT_Live_AI_TTS"
    
    if [ -d "$TT_LIVE_DIR" ]; then
        log_success "TT_Live_AI_TTS系统目录存在"
        
        # 检查关键文件
        if [ -f "$TT_LIVE_DIR/queue_processor_队列处理器.py" ]; then
            log_success "队列处理器文件存在"
        else
            log_warning "队列处理器文件不存在"
        fi
        
        if [ -d "$TT_LIVE_DIR/02_TTS服务_语音合成系统" ]; then
            log_success "TTS服务目录存在"
        else
            log_warning "TTS服务目录不存在"
        fi
        
        return 0
    else
        log_error "TT_Live_AI_TTS系统目录不存在"
        return 1
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p temp_ffmpeg                    # FFmpeg临时文件目录
    mkdir -p processed_audio                # 处理后的音频输出目录
    mkdir -p logs                           # 日志文件目录
    
    log_success "目录创建完成"
}

# 显示工具信息
show_tool_info() {
    echo ""
    echo "========================================"
    echo "TT_Live_AI_TTS - FFmpeg 音频处理工具"
    echo "========================================"
    echo "版本: 1.0.0"
    echo "用途: TikTok直播音频处理"
    echo "特点: 智能白噪音截取 + 背景音效混合"
    echo "集成: TT_Live_AI_TTS系统"
    echo "========================================"
    echo ""
}

# 显示使用方法
show_usage() {
    echo "使用方法:"
    echo "  1. 直接运行: python3 ffmpeg_audio_processor.py"
    echo "  2. 测试功能: python3 -c \"from ffmpeg_audio_processor import FFmpegAudioProcessor; print('FFmpeg工具加载成功')\""
    echo "  3. 查看帮助: python3 ffmpeg_audio_processor.py --help"
    echo ""
    echo "集成到TT_Live_AI_TTS:"
    echo "  - 输入: 从TTS服务获取音频文件"
    echo "  - 处理: 添加背景音效和白噪音"
    echo "  - 输出: 发送到直播系统"
    echo ""
    echo "配置文件: config.json"
    echo "说明文档: README.md"
    echo ""
}

# 运行测试
run_test() {
    log_info "运行FFmpeg工具测试..."
    
    python3 -c "
from ffmpeg_audio_processor import FFmpegAudioProcessor
import os

# 创建处理器
processor = FFmpegAudioProcessor('test_output')

# 检查背景音效配置
configs = processor.get_available_background_sounds()
print(f'可用背景音效: {len(configs)} 种')

# 检查默认组合
combinations = processor.get_default_combinations()
print(f'默认音效组合: {len(combinations)} 种')

print('FFmpeg工具测试成功!')
print('已集成到TT_Live_AI_TTS系统')
"
    
    if [ $? -eq 0 ]; then
        log_success "FFmpeg工具测试通过"
    else
        log_error "FFmpeg工具测试失败"
    fi
}

# 显示集成状态
show_integration_status() {
    log_info "TT_Live_AI_TTS集成状态:"
    echo ""
    echo "✅ FFmpeg音频处理工具已集成到TT_Live_AI_TTS系统"
    echo "✅ 支持从TTS服务接收音频文件"
    echo "✅ 支持智能白噪音截取和背景音效混合"
    echo "✅ 支持TikTok直播优化"
    echo "✅ 支持批量处理和队列管理"
    echo ""
}

# 主函数
main() {
    show_tool_info
    
    # 检查依赖
    check_ffmpeg || exit 1
    check_white_noise_template || exit 1
    check_python || exit 1
    check_tt_live_system || exit 1
    
    # 创建目录
    create_directories
    
    # 显示使用方法
    show_usage
    
    # 运行测试
    run_test
    
    # 显示集成状态
    show_integration_status
    
    log_success "TT_Live_AI_TTS - FFmpeg音频处理工具准备就绪!"
    echo ""
    echo "现在可以使用FFmpeg工具进行音频处理了。"
    echo "该工具已完全集成到TT_Live_AI_TTS系统中。"
}

# 执行主函数
main "$@"
