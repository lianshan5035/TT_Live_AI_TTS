# 端口独占管理方案

## 📋 概述

本项目提供了一套完整的端口独占管理方案，确保 8000 端口只能被我们的服务使用。

## 🎯 方案特点

✅ **自动检测端口占用**
✅ **自动清理冲突进程**
✅ **优雅关闭机制**
✅ **PID 文件管理**
✅ **详细的日志记录**

## 🚀 使用方法

### 1. 启动服务

```bash
cd /Volumes/M2/TT_Live_AI_TTS
./start_server.sh
```

脚本会自动：
- 检查 Python 环境
- 检测 8000 端口状态
- 清理占用端口的进程
- 启动 Web 服务
- 保存进程 PID

### 2. 停止服务

```bash
./stop_server.sh
```

脚本会：
- 从 PID 文件读取进程 ID
- 尝试优雅关闭
- 强制关闭占用端口的所有进程

### 3. 查看日志

```bash
tail -f logs/server.log
```

## 🔧 工作原理

### 端口检测

```bash
# 检测端口是否被占用
PID=$(lsof -ti:8000)

if [ -n "$PID" ]; then
    # 端口被占用，清理进程
    kill -9 $PID
fi
```

### PID 管理

```bash
# 保存 PID
echo $SERVER_PID > logs/server.pid

# 读取 PID
PID=$(cat logs/server.pid)

# 停止进程
kill $PID
```

## ⚙️ 配置说明

### 端口配置

编辑 `start_server.sh` 和 `stop_server.sh`:

```bash
PORT=8000  # 修改为您需要的端口
```

### 日志目录

```bash
LOG_DIR="$(pwd)/logs"  # 日志文件目录
```

## 🔍 故障排查

### 端口仍被占用

```bash
# 查看占用端口的进程
lsof -i:8000

# 手动清理
kill -9 $(lsof -ti:8000)
```

### 服务启动失败

1. 检查 Python 是否安装
2. 检查依赖包是否完整
3. 查看日志文件

```bash
tail -f logs/server.log
```

### 权限问题

```bash
# 确保脚本有执行权限
chmod +x start_server.sh stop_server.sh
```

## 📊 端口独占策略

### 级别1: 应用层
- 启动前检查端口
- 自动清理占用进程

### 级别2: 系统层（可选）
- 使用防火墙规则
- 限制特定进程使用端口

### 级别3: 守护进程（可选）
- 使用 supervisord
- 使用 systemd service

## 💡 最佳实践

1. **始终使用脚本启动/停止服务**
   ```bash
   # ❌ 不推荐
   python web_dashboard_simple.py
   
   # ✅ 推荐
   ./start_server.sh
   ```

2. **定期清理日志**
   ```bash
   # 保留最近7天的日志
   find logs/ -name "*.log" -mtime +7 -delete
   ```

3. **监控服务状态**
   ```bash
   # 检查服务是否运行
   lsof -i:8000
   
   # 查看进程资源使用
   ps aux | grep web_dashboard
   ```

## 📝 注意事项

⚠️ **权限警告**: 强制关闭进程需要足够权限

⚠️ **数据安全**: 强制关闭可能影响正在处理的任务

⚠️ **端口冲突**: 如果其他重要服务使用 8000 端口，请修改配置

## 🎯 当前服务状态

```bash
# 查看当前运行状态
ps aux | grep web_dashboard

# 查看端口占用
lsof -i:8000
```

---

**最后更新**: 2025-10-27
**维护者**: TT-Live-AI Team
