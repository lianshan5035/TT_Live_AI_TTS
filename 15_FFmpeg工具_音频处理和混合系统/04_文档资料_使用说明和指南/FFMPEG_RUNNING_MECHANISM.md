# FFmpeg 识别和运行机制详解

## 🔍 FFmpeg 识别机制

### 1. 系统级识别

FFmpeg通过以下方式被系统识别：

#### 🖥️ 命令行检查
```bash
# 检查FFmpeg是否安装
command -v ffmpeg &> /dev/null

# 获取FFmpeg版本信息
ffmpeg -version | head -n1 | cut -d' ' -f3
```

#### 🐍 Python代码中的识别
```python
def _check_ffmpeg(self) -> bool:
    """检查 FFmpeg 是否安装"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("FFmpeg 已安装")
            return True
        else:
            logger.error("FFmpeg 未正确安装")
            return False
    except FileNotFoundError:
        logger.error("FFmpeg 未安装，请先安装 FFmpeg")
        return False
```

### 2. 启动脚本中的识别流程

#### 📋 启动脚本检查步骤
```bash
# 1. 检查FFmpeg安装
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

# 2. 检查白噪音模板
check_white_noise_template() {
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

# 3. 检查Python环境
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python已安装: $PYTHON_VERSION"
        return 0
    else
        log_error "Python未安装"
        return 1
    fi
}
```

## 🚀 FFmpeg 运行机制

### 1. 初始化阶段

#### 🏗️ 处理器初始化
```python
class FFmpegAudioProcessor:
    def __init__(self, output_dir: str = "processed_audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 背景音效目录
        self.background_sounds_dir = Path("background_sounds")
        self.background_sounds_dir.mkdir(exist_ok=True)
        
        # 检查 FFmpeg 是否安装
        self._check_ffmpeg()
        
        # 初始化背景音效配置
        self.background_sounds = {...}
```

### 2. 音频处理流程

#### 🎵 单个音频处理流程
```python
def process_single_audio(self, input_file: str, output_file: str = None,
                       background_combination: List[str] = None,
                       main_volume: float = 1.0) -> bool:
    # 1. 验证输入文件
    if not os.path.exists(input_file):
        logger.error(f"输入文件不存在: {input_file}")
        return False
    
    # 2. 构建 FFmpeg 命令
    cmd = self._build_ffmpeg_command(
        input_file, str(output_file), 
        background_combination, main_volume
    )
    
    # 3. 执行处理
    start_time = datetime.now()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = datetime.now()
    
    # 4. 处理结果
    if result.returncode == 0:
        self.stats['success_count'] += 1
        logger.info(f"音频处理成功: {output_file}")
        return True
    else:
        self.stats['failed_count'] += 1
        logger.error(f"音频处理失败: {result.stderr}")
        return False
```

### 3. FFmpeg 命令构建

#### 🔧 命令构建过程
```python
def _build_ffmpeg_command(self, input_file: str, output_file: str,
                        background_combination: List[str],
                        main_volume: float) -> List[str]:
    # 1. 获取主音频时长
    main_duration = self.get_audio_duration(input_file)
    logger.info(f"主音频时长: {main_duration:.2f} 秒")
    
    # 2. 基础命令
    cmd = ['ffmpeg', '-y']
    
    # 3. 添加输入文件
    cmd.extend(['-i', input_file])
    
    # 4. 添加背景音效输入
    for i, sound_name in enumerate(background_combination):
        if sound_name in self.background_sounds:
            sound_file = self.background_sounds_dir / self.background_sounds[sound_name]['file']
            if sound_file.exists():
                cmd.extend(['-i', str(sound_file)])
                volume = self.background_sounds[sound_name]['volume']
                
                # 白噪音：截取模式
                if sound_name == "white_noise":
                    background_filters.append(f'[{i+1}:a]volume={volume},atrim=duration={main_duration}[bg{i}]')
                else:
                    # 其他音效：循环模式
                    background_filters.append(f'[{i+1}:a]volume={volume},aloop=loop=-1:size=2e+09,atrim=duration={main_duration}[bg{i}]')
    
    # 5. 构建滤镜链
    filter_parts = []
    filter_parts.append(f'[0:a]volume={main_volume},aresample=44100[main]')
    
    # 6. 混合背景音效
    if background_filters:
        filter_parts.extend(background_filters)
        filter_parts.append('[main][bgmix]amix=inputs=2:duration=first:weights=1 0.3[final]')
    
    # 7. 添加滤镜
    cmd.extend(['-filter_complex', ';'.join(filter_parts)])
    
    # 8. 输出设置
    cmd.extend(['-map', '[final]'])
    cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
    cmd.extend(['-ar', '44100', '-ac', '2'])
    cmd.extend(['-f', 'mp4'])
    cmd.append(output_file)
    
    return cmd
```

### 4. 音频时长检测

#### ⏱️ 时长检测机制
```python
def get_audio_duration(self, audio_file: str) -> float:
    """获取音频文件时长"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', audio_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
        else:
            logger.error(f"获取音频时长失败: {result.stderr}")
            return 0.0
    except Exception as e:
        logger.error(f"获取音频时长异常: {e}")
        return 0.0
```

## 🔄 完整运行流程

### 1. 系统启动流程

```
启动脚本 → 检查FFmpeg → 检查Python → 检查模板文件 → 创建目录 → 运行测试 → 准备就绪
    ↓           ↓           ↓           ↓           ↓         ↓         ↓
  start.sh   ffmpeg -v   python3 -v   白噪音文件    temp/   功能测试   可用状态
```

### 2. 音频处理流程

```
输入音频 → 时长检测 → 命令构建 → FFmpeg执行 → 结果验证 → 输出文件
    ↓         ↓         ↓         ↓         ↓         ↓
  TTS音频   获取时长   构建命令   子进程执行   检查结果   混合音频
```

### 3. 白噪音处理流程

```
2h白噪音模板 → 复制到工作目录 → 根据主音频时长截取 → 与其他音效混合
      ↓              ↓                ↓                ↓
   原始模板       white_noise.wav    截取片段        最终混合
```

## 🎯 关键特性

### 1. 智能白噪音截取
- **模板使用**: 使用2小时白噪音模板 (`/Volumes/M2/白噪声/2h白噪声.WAV`)
- **动态截取**: 根据TTS音频长度自动截取相应片段
- **唯一性**: 每个音频都有独特的白噪音片段

### 2. 背景音效混合
- **多种音效**: 支持10种背景音效
- **智能组合**: 5种默认音效组合
- **音量平衡**: 精确控制主音频和背景音效的音量比例

### 3. 高质量输出
- **格式**: M4A (AAC编码)
- **参数**: 44.1kHz, 立体声, 128kbps
- **容器**: MP4格式

## ⚠️ 依赖要求

### 1. 系统依赖
- **FFmpeg**: >=4.0版本
- **Python**: >=3.8版本
- **ffprobe**: FFmpeg套件的一部分

### 2. 文件依赖
- **白噪音模板**: `/Volumes/M2/白噪声/2h白噪声.WAV`
- **背景音效**: `background_sounds/` 目录中的音效文件

### 3. 权限要求
- **执行权限**: FFmpeg和Python的执行权限
- **读写权限**: 输入输出目录的读写权限

## 🚀 启动方式

### 1. 直接启动
```bash
cd /Volumes/M2/TT_Live_AI_TTS/"15_FFmpeg工具_音频处理和混合系统"
./start_ffmpeg_tool.sh
```

### 2. Python调用
```python
from ffmpeg_audio_processor import FFmpegAudioProcessor

# 创建处理器
processor = FFmpegAudioProcessor("output_dir")

# 处理音频
success = processor.process_single_audio(
    input_file="input.mp3",
    output_file="output.m4a",
    background_combination=["white_noise", "room_tone"],
    main_volume=0.85
)
```

### 3. 集成调用
```python
from audio_mixer import AudioMixer

# 创建混合器
mixer = AudioMixer("mixed_audio")

# 文本转混合音频
success = await mixer.process_text_to_mixed_audio(
    text="测试文本",
    output_file="output.m4a",
    mix_config="natural_live"
)
```

这个FFmpeg识别和运行机制确保了系统的稳定性和可靠性，通过多重检查和处理流程，保证了音频处理的质量和成功率。
