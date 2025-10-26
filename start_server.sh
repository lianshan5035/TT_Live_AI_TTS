#!/bin/bash
# TT-Live-AI Web 服务启动脚本
# 自动检查和清理 8000 端口，确保独占使用

PORT=8000
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/server.log"

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 TT-Live-AI Web 服务启动脚本${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查并清理端口
check_and_clean_port() {
    echo -e "${YELLOW}📌 检查端口 $PORT 状态...${NC}"
    
    # 检查端口是否被占用
    PID=$(lsof -ti:$PORT 2>/dev/null)
    
    if [ -n "$PID" ]; then
        echo -e "${RED}⚠️  端口 $PORT 已被进程 $PID 占用${NC}"
        echo -e "${YELLOW}🔄 正在清理占用端口的进程...${NC}"
        
        # 获取进程信息
        PROCESS_INFO=$(ps -p $PID -o comm= 2>/dev/null)
        
        if [ -n "$PROCESS_INFO" ]; then
            echo -e "   进程名称: $PROCESS_INFO"
            echo -e "   进程ID: $PID"
            
            # 尝试优雅关闭
            kill -TERM $PID 2>/dev/null
            sleep 1
            
            # 如果还在运行，强制关闭所有占用端口的进程
            for pid in $(lsof -ti:$PORT 2>/dev/null); do
                echo -e "${YELLOW}   强制关闭进程: $pid${NC}"
                kill -9 $pid 2>/dev/null
            done
            sleep 1
        fi
        
        # 再次检查
        if lsof -ti:$PORT >/dev/null 2>&1; then
            echo -e "${RED}❌ 无法清理端口 $PORT，请手动处理${NC}"
            echo -e "   运行命令查看: ${BLUE}lsof -i:$PORT${NC}"
            exit 1
        else
            echo -e "${GREEN}✅ 端口 $PORT 已释放${NC}"
        fi
    else
        echo -e "${GREEN}✅ 端口 $PORT 可用${NC}"
    fi
}

# 检查 Python 是否安装
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 未安装${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"
}

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}📦 检查依赖包...${NC}"
    
    cd "$SCRIPT_DIR"
    
    # 检查是否需要安装依赖（跳过自动安装，手动处理）
    if [ -f "requirements.txt" ]; then
        if ! python3 -c "import flask" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  缺少依赖包${NC}"
            echo -e "${YELLOW}   请手动安装: ${BLUE}pip3 install -r requirements.txt${NC}"
        fi
    fi
    
    echo -e "${GREEN}✅ 依赖检查完成${NC}"
}

# 设置端口独占（可选，需要管理员权限）
set_port_exclusive() {
    echo -e "${YELLOW}🔒 设置端口 $PORT 为独占模式...${NC}"
    
    # macOS 使用 pfctl
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # 检查是否已有规则
        if sudo pfctl -sr 2>/dev/null | grep -q "$PORT"; then
            echo -e "${GREEN}✅ 端口独占规则已存在${NC}"
        else
            echo -e "${YELLOW}⚠️  需要管理员权限设置端口独占${NC}"
            # 这里可以选择是否设置，因为通常不需要
        fi
    fi
}

# 启动服务
start_server() {
    echo -e "${YELLOW}🚀 启动 Web 服务...${NC}"
    
    cd "$SCRIPT_DIR"
    
    # 将输出重定向到日志文件
    nohup python3 web_dashboard_simple.py > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    
    # 等待服务启动
    sleep 2
    
    # 检查服务是否启动成功
    if ps -p $SERVER_PID > /dev/null; then
        echo -e "${GREEN}✅ 服务启动成功！${NC}"
        echo -e "${GREEN}   PID: $SERVER_PID${NC}"
        echo -e "${GREEN}   访问地址: ${BLUE}http://127.0.0.1:$PORT${NC}"
        echo -e "${GREEN}   日志文件: ${BLUE}$LOG_FILE${NC}"
        echo ""
        echo -e "${GREEN}📋 服务信息：${NC}"
        echo "   - 进程ID: $SERVER_PID"
        echo "   - 日志文件: $LOG_FILE"
        echo "   - 停止服务: kill $SERVER_PID"
        echo ""
        
        # 保存PID到文件
        echo $SERVER_PID > "$SCRIPT_DIR/logs/server.pid"
        
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}🎉 TT-Live-AI 服务已就绪！${NC}"
    else
        echo -e "${RED}❌ 服务启动失败${NC}"
        echo -e "${YELLOW}查看日志: ${BLUE}tail -f $LOG_FILE${NC}"
        exit 1
    fi
}

# 主流程
main() {
    check_python
    check_dependencies
    check_and_clean_port
    start_server
    
    # 显示实时日志
    echo -e "${YELLOW}📋 实时日志（按 Ctrl+C 停止，服务继续运行）:${NC}"
    tail -f "$LOG_FILE"
}

# 运行主流程
main
