# TT-Live-AI-TTS 跨平台安装程序

## 📦 安装程序概述

本安装程序为 TT-Live-AI-TTS 项目提供跨平台部署解决方案，支持 macOS 和 Windows 系统。

### 🎯 主要功能
- **智能语音合成**: 基于微软 EdgeTTS 的高质量语音生成
- **批量处理**: 支持 Excel 文件批量转换语音
- **Web 控制台**: 现代化的 Web 界面，操作简单直观
- **API 接口**: 完整的 RESTful API，支持第三方集成
- **跨平台支持**: 同时支持 macOS 和 Windows 系统

## 🎯 功能特性

- ✅ 跨平台支持 (macOS & Windows)
- ✅ 自动依赖安装
- ✅ 虚拟环境管理
- ✅ 服务自动启动
- ✅ 配置文件管理
- ✅ 排除音频文件（保持项目轻量化）
- ✅ 保持原有目录结构
- ✅ 输入输出规则不变

## 📁 安装程序结构

```
installer/
├── README_安装程序说明.md          # 本说明文件
├── install_mac.sh                 # macOS 安装脚本
├── install_windows.bat            # Windows 安装脚本
├── requirements.txt               # Python 依赖包
├── config/                        # 配置文件
│   ├── .env_template              # 环境变量模板
│   └── config.json                # 系统配置
├── scripts/                       # 辅助脚本
│   ├── check_dependencies.py      # 依赖检查
│   ├── setup_environment.py       # 环境设置
│   └── validate_installation.py   # 安装验证
└── exclude_patterns.txt           # 排除文件模式
```

## 🚀 快速安装

### 📱 macOS 系统安装步骤
1. **下载安装程序**: 将整个 `installer` 文件夹下载到本地
2. **打开终端**: 按 `Command + 空格` 搜索 "终端" 并打开
3. **进入安装目录**: 使用 `cd` 命令进入 installer 文件夹
4. **赋予执行权限**: 运行 `chmod +x install_mac.sh`
5. **开始安装**: 运行 `./install_mac.sh`
6. **按提示操作**: 根据屏幕提示完成安装

```bash
# 示例命令
cd ~/Downloads/TT_Live_AI_TTS/installer
chmod +x install_mac.sh
./install_mac.sh
```

### 💻 Windows 系统安装步骤
1. **下载安装程序**: 将整个 `installer` 文件夹下载到本地
2. **以管理员身份运行**: 右键点击 `install_windows.bat`，选择"以管理员身份运行"
3. **按提示操作**: 根据屏幕提示完成安装
4. **等待完成**: 安装过程可能需要几分钟，请耐心等待

```cmd
# 直接双击运行或在命令提示符中执行
install_windows.bat
```

## 📋 安装前准备

### 💻 系统要求
- **macOS**: 10.14+ (Mojave 或更高版本)
  - 支持 Intel 和 Apple Silicon (M1/M2) 芯片
  - 建议使用最新版本的 macOS
- **Windows**: Windows 10+ 或 Windows Server 2016+
  - 支持 64 位系统
  - 建议使用 Windows 11 获得最佳体验
- **Python**: 3.8+ (安装程序会自动检查并提示安装)
- **内存**: 至少 4GB RAM (推荐 8GB+)
- **存储**: 至少 2GB 可用空间 (推荐 5GB+)

### 🌐 网络要求
- **稳定网络**: 需要稳定的互联网连接（用于下载依赖包）
- **访问权限**: 能够访问 PyPI (Python Package Index)
- **防火墙**: 确保防火墙允许 Python 和浏览器访问网络
- **代理设置**: 如果使用代理，请确保 Python 能正常访问外网

## 🔧 详细安装过程

安装程序会自动执行以下步骤，您只需要按照提示操作：

### 1️⃣ 系统环境检查
- ✅ **操作系统验证**: 检查 macOS/Windows 版本是否满足要求
- ✅ **Python 环境**: 自动检测 Python 版本，如不满足会提示安装
- ✅ **磁盘空间**: 检查可用空间是否足够
- ✅ **网络连接**: 测试网络连接是否正常

### 2️⃣ 项目文件部署
- 📁 **目录创建**: 自动创建必要的文件夹结构
- 📄 **文件复制**: 复制所有核心文件（排除音频文件以节省空间）
- 🔐 **权限设置**: 设置正确的文件权限
- ⚙️ **配置初始化**: 创建默认配置文件

### 3️⃣ 虚拟环境配置
- 🐍 **环境创建**: 创建独立的 Python 虚拟环境
- 📦 **依赖安装**: 自动安装所有必需的 Python 包
- 🔄 **版本升级**: 升级 pip 到最新版本
- ✅ **环境验证**: 验证虚拟环境是否正常工作

### 4️⃣ 服务配置
- 🚀 **启动脚本**: 创建系统启动脚本
- ⚙️ **配置文件**: 生成默认配置文件
- 🔗 **端口设置**: 配置服务端口（TTS: 5001, Web: 8000）
- 🧪 **功能测试**: 测试核心功能是否正常

## 📂 智能文件过滤

为了保持安装包轻量化，安装程序会自动排除以下文件：

### 🎵 音频文件（已生成）
- **EdgeTTS 音频**: `*.mp3`, `*.wav`, `*.m4a`, `*.aac`, `*.ogg`, `*.flac`
- **FFmpeg 处理**: `*_processed.*`, `*_mixed.*`, `*_converted.*`
- **输出目录**: `outputs/**/*.mp3` 等所有音频文件

### 🗂️ 临时和缓存文件
- **Python 缓存**: `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`
- **临时文件**: `temp/`, `tmp/`, `cache/`, `*.swp`, `*.swo`
- **系统文件**: `.DS_Store` (macOS), `Thumbs.db` (Windows)

### 📝 日志文件（保留结构）
- **运行日志**: `logs/*.log`, `logs/*.pid`, `logs/*.pkl`
- **安装日志**: 保留目录结构，但不复制现有日志内容

### 🔧 开发环境文件
- **虚拟环境**: `venv/`, `env/`, `.venv/`, `.env/` (会重新创建)
- **IDE 配置**: `.vscode/`, `.idea/`, `*.sublime-*`
- **版本控制**: `.git/`, `.gitignore`

## 🎛️ 系统配置说明

### 📋 环境变量配置 (.env)
安装完成后，您可以编辑 `.env` 文件来自定义系统设置：

```bash
# ===========================================
# 服务配置 - 修改端口和主机地址
# ===========================================
TTS_HOST=127.0.0.1          # TTS 服务主机地址
TTS_PORT=5001               # TTS 服务端口
WEB_PORT=8000               # Web 控制台端口

# ===========================================
# 语音合成配置 - 调整语音参数
# ===========================================
DEFAULT_VOICE=Lior          # 默认语音模型 (Lior, Allison, Aria, Davis, Emma)
MAX_CONCURRENT=5            # 最大并发处理数量
AUDIO_FORMAT=mp3           # 音频格式 (mp3, wav, m4a)
AUDIO_QUALITY=high          # 音频质量 (low, medium, high)

# ===========================================
# 文件路径配置 - 自定义输入输出目录
# ===========================================
INPUT_DIR=input             # 输入文件目录
OUTPUT_DIR=outputs          # 输出文件目录
LOG_DIR=logs               # 日志文件目录
TEMPLATE_DIR=templates     # 模板文件目录
STATIC_DIR=static          # 静态资源目录

# ===========================================
# ngrok 公网映射配置（可选）
# ===========================================
NGROK_TOKEN=your_token_here # ngrok 令牌（用于公网访问）
NGROK_REGION=us            # ngrok 服务器区域
NGROK_SUBDOMAIN=           # 自定义子域名（需要付费账户）
```

### ⚙️ 系统配置文件 (config.json)
高级用户可以通过修改 `config.json` 文件来调整系统行为：

```json
{
  "system": {
    "platform": "auto",           // 自动检测平台
    "python_version": "3.8+",     // 最低 Python 版本要求
    "virtual_env": true,          // 使用虚拟环境
    "auto_start": true           // 自动启动服务
  },
  "services": {
    "tts_service": {
      "enabled": true,            // 启用 TTS 服务
      "port": 5001,              // TTS 服务端口
      "host": "127.0.0.1",       // TTS 服务主机
      "auto_start": true,         // 自动启动
      "max_concurrent": 5         // 最大并发数
    },
    "web_dashboard": {
      "enabled": true,            // 启用 Web 控制台
      "port": 8000,              // Web 控制台端口
      "host": "127.0.0.1",       // Web 控制台主机
      "auto_start": true,         // 自动启动
      "templates": ["classic", "modern", "index"]  // 可用模板
    }
  },
  "tts": {
    "default_voice": "Lior",     // 默认语音模型
    "supported_voices": ["Lior", "Allison", "Aria", "Davis", "Emma"],
    "emotions": {                 // 情绪参数映射
      "Calm": {"rate": "-6%", "pitch": "-2%", "volume": "0dB"},
      "Friendly": {"rate": "+2%", "pitch": "+2%", "volume": "0dB"},
      "Confident": {"rate": "+4%", "pitch": "+1%", "volume": "+1dB"},
      "Playful": {"rate": "+6%", "pitch": "+3%", "volume": "+1dB"},
      "Excited": {"rate": "+10%", "pitch": "+4%", "volume": "+2dB"},
      "Urgent": {"rate": "+12%", "pitch": "+3%", "volume": "+2dB"}
    }
  },
  "paths": {
    "input_dir": "input",         // 输入目录
    "output_dir": "outputs",      // 输出目录
    "log_dir": "logs",           // 日志目录
    "template_dir": "templates", // 模板目录
    "static_dir": "static"       // 静态资源目录
  },
  "features": {
    "batch_processing": true,     // 启用批量处理
    "excel_support": true,       // 启用 Excel 支持
    "web_interface": true,       // 启用 Web 界面
    "api_endpoints": true,       // 启用 API 接口
    "ngrok_support": true        // 启用 ngrok 支持
  }
}
```

## 🔍 安装验证与测试

安装完成后，系统会自动进行以下验证步骤：

### ✅ 自动验证项目
1. **依赖包检查**: 验证所有 Python 包是否正确安装
2. **服务启动测试**: 测试 TTS 服务和 Web 控制台是否能正常启动
3. **文件完整性检查**: 检查关键文件是否存在且可访问
4. **权限验证**: 确认文件权限设置正确
5. **端口可用性**: 检查配置的端口是否被占用

### 🧪 手动验证方法
如果自动验证失败，您可以手动运行验证脚本：

```bash
# macOS/Linux
cd /path/to/installation
python scripts/validate_installation.py .

# Windows
cd C:\path\to\installation
python scripts\validate_installation.py .
```

### 📊 验证成功标志
- ✅ 所有必需文件存在
- ✅ Python 包正确安装
- ✅ 虚拟环境工作正常
- ✅ 配置文件格式正确
- ✅ 启动脚本可执行

## 🚨 故障排除指南

### ❓ 常见问题及解决方案

#### 🔧 Python 相关问题
**Q: Python 版本不兼容**
- **问题**: 提示需要 Python 3.8+ 但系统版本过低
- **解决方案**: 
  - macOS: `brew install python3` 或从 [python.org](https://www.python.org/downloads/) 下载
  - Windows: 从 [python.org](https://www.python.org/downloads/) 下载最新版本
  - 确保安装时勾选 "Add Python to PATH"

**Q: pip 命令不存在**
- **问题**: 提示 'pip' 不是内部或外部命令
- **解决方案**:
  - Windows: 重新安装 Python 并勾选 "Add Python to PATH"
  - macOS: `python3 -m ensurepip --upgrade`
  - Linux: `sudo apt install python3-pip` 或 `sudo yum install python3-pip`

#### 📦 依赖包问题
**Q: 依赖包安装失败**
- **问题**: pip install 过程中出现网络错误或超时
- **解决方案**:
  ```bash
  # 使用国内镜像源
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
  
  # 或使用阿里云镜像
  pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
  
  # 增加超时时间
  pip install -r requirements.txt --timeout 1000
  ```

**Q: edge-tts 安装失败**
- **问题**: edge-tts 包安装时出现错误
- **解决方案**:
  ```bash
  # 先安装依赖
  pip install aiohttp websockets
  
  # 再安装 edge-tts
  pip install edge-tts
  ```

#### 🌐 网络和端口问题
**Q: 服务启动失败**
- **问题**: TTS 服务或 Web 控制台无法启动
- **解决方案**:
  1. 检查端口是否被占用:
     ```bash
     # macOS/Linux
     lsof -i :5001
     lsof -i :8000
     
     # Windows
     netstat -ano | findstr :5001
     netstat -ano | findstr :8000
     ```
  2. 修改配置文件中的端口号
  3. 重启系统释放端口

**Q: 无法访问 Web 控制台**
- **问题**: 浏览器无法打开 http://127.0.0.1:8000
- **解决方案**:
  1. 检查防火墙设置
  2. 确认服务是否正常启动
  3. 尝试使用 http://localhost:8000
  4. 检查浏览器代理设置

#### 🔐 权限问题
**Q: 权限不足**
- **问题**: macOS 提示权限不足，Windows 提示需要管理员权限
- **解决方案**:
  - macOS: 使用 `sudo` 运行安装脚本
  - Windows: 右键选择"以管理员身份运行"
  - 检查文件夹权限设置

**Q: 文件写入失败**
- **问题**: 无法创建文件或写入配置
- **解决方案**:
  ```bash
  # macOS/Linux 设置权限
  chmod -R 755 /path/to/installation
  
  # Windows 检查文件夹权限
  # 右键文件夹 -> 属性 -> 安全 -> 编辑权限
  ```

#### 🗂️ 文件路径问题
**Q: 找不到文件或目录**
- **问题**: 安装过程中提示文件不存在
- **解决方案**:
  1. 确保安装程序完整下载
  2. 检查文件路径中是否包含中文字符
  3. 避免使用过长的路径名
  4. 确保有足够的磁盘空间

### 📋 日志文件位置
遇到问题时，请查看以下日志文件：
- **安装日志**: `installer/logs/install.log`
- **系统日志**: `logs/system.log`
- **错误日志**: `logs/error.log`
- **TTS 服务日志**: `logs/tts_service.log`
- **Web 控制台日志**: `logs/web_dashboard.log`

## 📞 技术支持

如遇到安装问题，请提供以下信息：
- 操作系统版本
- Python 版本
- 错误日志
- 安装步骤

## 🔄 卸载程序

### macOS 卸载
```bash
./uninstall_mac.sh
```

### Windows 卸载
```cmd
uninstall_windows.bat
```

## 📝 更新日志

- **v1.0.0**: 初始版本，支持 macOS 和 Windows
- 跨平台安装程序
- 自动依赖管理
- 服务自动启动
