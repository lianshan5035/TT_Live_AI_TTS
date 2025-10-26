#!/bin/bash
# TT-Live-AI Web 服务停止脚本

PORT=8000
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/server.pid"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛑 停止 TT-Live-AI Web 服务${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 方法1: 从PID文件获取
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}📌 从PID文件找到进程: $PID${NC}"
        kill -TERM $PID 2>/dev/null
        sleep 2
        
        # 如果还在运行，强制关闭
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${YELLOW}强制关闭进程...${NC}"
            kill -9 $PID 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        echo -e "${GREEN}✅ 服务已停止${NC}"
    fi
fi

# 方法2: 通过端口查找并停止
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ -n "$PID" ]; then
    echo -e "${YELLOW}📌 发现端口 $PORT 被进程 $PID 占用${NC}"
    PROCESS_INFO=$(ps -p $PID -o comm= 2>/dev/null)
    if [ -n "$PROCESS_INFO" ]; then
        echo -e "   进程名称: $PROCESS_INFO"
        
        kill -TERM $PID 2>/dev/null
        sleep 2
        
        if lsof -ti:$PORT >/dev/null 2>&1; then
            echo -e "${YELLOW}强制关闭进程...${NC}"
            kill -9 $PID 2>/dev/null
        fi
        
        echo -e "${GREEN}✅ 服务已停止${NC}"
    fi
else
    echo -e "${GREEN}✅ 端口 $PORT 未被占用${NC}"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 清理完成${NC}"
