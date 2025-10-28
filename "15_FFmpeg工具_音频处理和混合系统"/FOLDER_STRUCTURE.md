# FFmpeg工具文件夹结构说明

## 📁 15_FFmpeg工具_音频处理和混合系统

### 🎯 文件夹结构概览

```
15_FFmpeg工具_音频处理和混合系统/
├── README.md                                    # FFmpeg工具使用说明文档
├── config.json                                  # FFmpeg工具配置文件
├── start_ffmpeg_tool.sh                         # FFmpeg工具启动脚本
├── ffmpeg_audio_processor.py                    # FFmpeg音频处理器主文件
├── ffmpeg_audio_processor.cpython-313.pyc       # Python编译缓存文件
├── __pycache___Python编译缓存目录/               # Python编译缓存目录
├── background_sounds_背景音效文件存储目录/        # 背景音效文件存储目录
├── logs_FFmpeg处理日志文件目录/                  # FFmpeg处理日志文件目录
├── processed_audio_FFmpeg处理后音频输出目录/      # FFmpeg处理后音频输出目录
├── temp_ffmpeg_FFmpeg临时文件处理目录/           # FFmpeg临时文件处理目录
├── test_ffmpeg_output_FFmpeg测试输出目录/        # FFmpeg测试输出目录
└── test_output_测试音频输出目录/                 # 测试音频输出目录
```

### 📋 文件夹详细说明

| 文件夹名称 | 中文说明 | 用途 | 文件类型 |
|-----------|---------|------|---------|
| `__pycache___Python编译缓存目录` | Python编译缓存目录 | 存储Python编译后的字节码文件 | `.pyc` |
| `background_sounds_背景音效文件存储目录` | 背景音效文件存储目录 | 存储各种背景音效文件 | `.wav` |
| `logs_FFmpeg处理日志文件目录` | FFmpeg处理日志文件目录 | 存储FFmpeg处理过程的日志文件 | `.log` |
| `processed_audio_FFmpeg处理后音频输出目录` | FFmpeg处理后音频输出目录 | 存储FFmpeg处理后的音频文件 | `.m4a` |
| `temp_ffmpeg_FFmpeg临时文件处理目录` | FFmpeg临时文件处理目录 | 存储FFmpeg处理过程中的临时文件 | `.tmp`, `.m4a` |
| `test_ffmpeg_output_FFmpeg测试输出目录` | FFmpeg测试输出目录 | 存储FFmpeg功能测试的输出文件 | `.m4a` |
| `test_output_测试音频输出目录` | 测试音频输出目录 | 存储系统测试生成的音频文件 | `.m4a` |

### 🎵 背景音效文件说明

`background_sounds_背景音效文件存储目录` 中包含以下音效文件：

| 文件名 | 中文说明 | 用途 |
|--------|---------|------|
| `rain_light.wav` | 细雨声 | 营造自然氛围 |
| `footsteps_carpet.wav` | 脚步声 | 模拟真实环境 |
| `drinking_water.wav` | 喝水声 | 增加生活感 |
| `keyboard_typing.wav` | 键盘声 | 办公环境音效 |
| `fireplace_crackling.wav` | 篝火声 | 温馨氛围 |
| `white_noise.wav` | 白噪音 | 基础环境音（从2小时模板复制） |
| `room_tone.wav` | 房间音效 | 真实房间感 |
| `paper_rustle.wav` | 纸张摩擦声 | 细节音效 |
| `chair_creak.wav` | 椅子吱嘎声 | 生活细节 |
| `clock_tick.wav` | 时钟滴答声 | 时间感 |

### 🔄 文件处理流程

```
输入音频 → temp_ffmpeg_FFmpeg临时文件处理目录 → processed_audio_FFmpeg处理后音频输出目录 → 最终输出
    ↓                    ↓                              ↓                    ↓
  TTS音频           临时处理文件                    处理后音频文件        混合音频文件
```

### 📊 目录功能分类

#### 🎵 音频处理相关
- `processed_audio_FFmpeg处理后音频输出目录` - 处理后的音频输出
- `temp_ffmpeg_FFmpeg临时文件处理目录` - 临时处理文件
- `background_sounds_背景音效文件存储目录` - 背景音效存储

#### 🧪 测试相关
- `test_ffmpeg_output_FFmpeg测试输出目录` - FFmpeg功能测试输出
- `test_output_测试音频输出目录` - 系统测试输出

#### 📝 日志和缓存相关
- `logs_FFmpeg处理日志文件目录` - 处理日志记录
- `__pycache___Python编译缓存目录` - Python编译缓存

### ⚠️ 重要说明

1. **临时文件**: `temp_ffmpeg_FFmpeg临时文件处理目录` 中的文件会在处理完成后自动清理
2. **测试文件**: `test_*` 目录中的文件用于功能测试，可以手动清理
3. **日志文件**: `logs_FFmpeg处理日志文件目录` 中的日志文件会定期轮转
4. **背景音效**: `background_sounds_背景音效文件存储目录` 中的文件不要删除
5. **输出文件**: `processed_audio_FFmpeg处理后音频输出目录` 中的文件是最终处理结果

### 🔧 维护建议

1. **定期清理**: 定期清理临时文件和测试文件
2. **日志管理**: 定期轮转日志文件，避免文件过大
3. **空间监控**: 监控各目录的磁盘使用情况
4. **备份重要文件**: 备份重要的输出文件
5. **权限检查**: 确保各目录有正确的读写权限

### 🚀 使用流程

1. **启动工具**: 运行 `start_ffmpeg_tool.sh`
2. **输入音频**: 将音频文件放入处理队列
3. **临时处理**: 文件在 `temp_ffmpeg_FFmpeg临时文件处理目录` 中处理
4. **背景音效**: 从 `background_sounds_背景音效文件存储目录` 加载音效
5. **输出结果**: 处理后的文件保存到 `processed_audio_FFmpeg处理后音频输出目录`
6. **日志记录**: 处理过程记录到 `logs_FFmpeg处理日志文件目录`

这个文件夹结构设计确保了FFmpeg工具的有序运行和文件管理，每个目录都有明确的用途和中文说明。
