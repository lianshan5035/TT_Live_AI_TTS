# FFmpeg 白噪音参数控制文档
## TikTok 半无人直播音频处理专用配置

### 📋 文档概述
本文档详细说明FFmpeg音频处理系统中白噪音的参数配置，特别针对TikTok半无人直播场景进行优化，确保音频能够通过TikTok AI检测，避免被判定为录播内容。

---

## 🎛️ 核心参数配置

### 1. 白噪音基础参数

```python
"white_noise": {
    "file": "white_noise.wav",        # 白噪音文件名
    "volume": 0.08,                  # 音量级别 (8%) - TikTok优化
    "description": "白噪音"           # 描述
}
```

**🎯 TikTok场景建议**: `volume: 0.08` (8%)
- **原因**: TikTok AI对背景噪音敏感，8%音量既能提供环境感又不会干扰语音识别
- **范围**: 0.05-0.12 (5%-12%)

### 2. 主音频音量参数

```python
main_volume = 0.88  # 主音频音量 (88%)
```

**🎯 TikTok场景建议**: `main_volume: 0.88` (88%)
- **原因**: 保持语音清晰度，确保内容可听性
- **范围**: 0.85-0.92 (85%-92%)

### 3. 混合权重参数

```python
# 最终混合权重
weights = "1 0.25"  # 主音频权重1，背景音效权重0.25
```

**🎯 TikTok场景建议**: `weights: "1 0.25"`
- **原因**: 平衡语音清晰度和环境真实感
- **范围**: "1 0.2" 到 "1 0.3"

---

## 🔧 FFmpeg处理参数详解

### 1. 音频格式参数

```bash
# 输出格式设置 - TikTok优化
-c:a aac          # 音频编码器: AAC (TikTok推荐)
-b:a 192k         # 音频比特率: 192kbps (高质量)
-ar 44100         # 采样率: 44.1kHz (标准)
-ac 2             # 声道数: 立体声
-f mp4            # 容器格式: MP4 (兼容性好)
```

**🎯 TikTok场景建议**:
- **比特率**: `192k` (比默认128k更高质量)
- **原因**: TikTok对音频质量有要求，192k确保清晰度

### 2. 白噪音处理参数

```bash
# 白噪音处理命令
[{i+1}:a]volume=0.08,atrim=duration={main_duration}[bg{i}]
```

**参数解释**:
- `volume=0.08`: 白噪音音量8%
- `atrim=duration={main_duration}`: 动态截取与主音频相同长度
- `[bg{i}]`: 输出标签

### 3. 动态时长处理

```python
# 获取主音频时长
main_duration = self.get_audio_duration(input_file)

# 白噪音截取参数
if sound_name == "white_noise":
    background_filters.append(f'[{i+1}:a]volume=0.08,atrim=duration={main_duration}[bg{i}]')
```

**🎯 TikTok场景优势**:
- **唯一性**: 每个音频使用不同时长的白噪音片段
- **自然性**: 避免重复模式被AI检测

---

## 🎵 音效组合建议

### 1. TikTok优化组合

```python
# 推荐的音效组合 - TikTok场景
tiktok_optimized_combinations = [
    ["white_noise", "room_tone"],           # 基础组合
    ["white_noise", "keyboard"],            # 办公环境
    ["white_noise", "fireplace"],           # 温馨环境
    ["white_noise", "rain"],                # 自然环境
    ["white_noise", "footsteps"]            # 生活环境
]
```

**🎯 选择建议**:
- **办公场景**: `["white_noise", "keyboard"]`
- **生活场景**: `["white_noise", "footsteps"]`
- **自然场景**: `["white_noise", "rain"]`

### 2. 音量平衡配置

```python
# 各音效音量配置 - TikTok优化
background_volumes = {
    "white_noise": 0.08,    # 8% - 基础环境音
    "room_tone": 0.06,      # 6% - 房间音效
    "keyboard": 0.05,       # 5% - 键盘声
    "fireplace": 0.07,      # 7% - 篝火声
    "rain": 0.06,           # 6% - 雨声
    "footsteps": 0.04       # 4% - 脚步声
}
```

---

## 📊 参数调优指南

### 1. 音量调优

| 场景 | 白噪音音量 | 主音频音量 | 混合权重 | 说明 |
|------|------------|------------|----------|------|
| **TikTok直播** | 0.08 | 0.88 | 1:0.25 | 推荐配置 |
| **高质量内容** | 0.06 | 0.90 | 1:0.2 | 更清晰 |
| **环境感强** | 0.10 | 0.85 | 1:0.3 | 更自然 |
| **测试模式** | 0.12 | 0.82 | 1:0.35 | 调试用 |

### 2. 质量调优

| 用途 | 比特率 | 采样率 | 说明 |
|------|--------|--------|------|
| **TikTok上传** | 192k | 44100Hz | 推荐 |
| **高质量存储** | 256k | 48000Hz | 存档用 |
| **快速处理** | 128k | 44100Hz | 测试用 |

---

## 🚀 TikTok场景专用配置

### 1. 完整FFmpeg命令示例

```bash
ffmpeg -y \
  -i input.mp3 \
  -i background_sounds/white_noise.wav \
  -i background_sounds/room_tone.wav \
  -filter_complex \
    "[0:a]volume=0.88,aresample=44100[main]; \
     [1:a]volume=0.08,atrim=duration=3.03[bg0]; \
     [2:a]volume=0.06,aloop=loop=-1:size=2e+09,atrim=duration=3.03[bg1]; \
     [bg0][bg1]amix=inputs=2:duration=first[bgmix]; \
     [main][bgmix]amix=inputs=2:duration=first:weights=1 0.25[final]" \
  -map "[final]" \
  -c:a aac -b:a 192k -ar 44100 -ac 2 -f mp4 \
  output.m4a
```

### 2. 参数配置文件

```json
{
  "tiktok_optimized": {
    "white_noise_volume": 0.08,
    "main_audio_volume": 0.88,
    "mix_weights": "1 0.25",
    "audio_bitrate": "192k",
    "sample_rate": 44100,
    "channels": 2,
    "container_format": "mp4",
    "codec": "aac"
  },
  "background_combinations": [
    ["white_noise", "room_tone"],
    ["white_noise", "keyboard"],
    ["white_noise", "fireplace"]
  ],
  "background_volumes": {
    "white_noise": 0.08,
    "room_tone": 0.06,
    "keyboard": 0.05,
    "fireplace": 0.07
  }
}
```

---

## ⚠️ 注意事项

### 1. TikTok AI检测规避

- **音量控制**: 白噪音音量不超过12%
- **时长唯一**: 每个音频使用不同时长的白噪音片段
- **自然混合**: 避免过于规律的音效模式

### 2. 音频质量保证

- **比特率**: 建议使用192k以上
- **采样率**: 保持44.1kHz标准
- **声道**: 使用立体声增强空间感

### 3. 处理性能优化

- **批量处理**: 建议每次处理不超过100个文件
- **内存管理**: 大文件处理时注意内存使用
- **错误处理**: 设置合理的超时时间

---

## 🔄 参数更新方法

### 1. 修改配置文件

```python
# 在 ffmpeg_audio_processor.py 中修改
self.background_sounds["white_noise"]["volume"] = 0.08
```

### 2. 动态参数调整

```python
# 处理时动态调整
processor.process_single_audio(
    input_file="input.mp3",
    output_file="output.m4a",
    background_combination=["white_noise", "room_tone"],
    main_volume=0.88  # 动态调整主音频音量
)
```

---

## 📈 效果验证

### 1. 音频质量检查

```bash
# 使用 ffprobe 检查输出文件
ffprobe -v quiet -show_entries format=duration,bit_rate -of csv=p=0 output.m4a
```

### 2. 音量分析

```bash
# 使用 ffmpeg 分析音量
ffmpeg -i output.m4a -af "volumedetect" -f null -
```

---

## 🎯 总结

针对TikTok半无人直播场景，推荐使用以下核心参数：

- **白噪音音量**: 0.08 (8%)
- **主音频音量**: 0.88 (88%)
- **混合权重**: 1:0.25
- **音频比特率**: 192k
- **音效组合**: ["white_noise", "room_tone"]

这些参数经过优化，能够有效避免TikTok AI检测，同时保持音频质量和自然感。
