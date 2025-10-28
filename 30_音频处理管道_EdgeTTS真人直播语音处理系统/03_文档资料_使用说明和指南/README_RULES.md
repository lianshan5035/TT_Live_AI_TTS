# EdgeTTS音频处理规则管理系统

## 📋 概述

这是一个完整的规则管理系统，允许您实时修改EdgeTTS音频处理的各项参数，无需重新编译代码。

## 🗂️ 文件结构

```
audio_pipeline/
├── rules_config.json          # 主规则配置文件
├── rules_manager.py          # 完整规则管理器
├── quick_rules_editor.py     # 快速规则编辑器
└── README_RULES.md          # 本说明文档
```

## 🚀 快速开始

### 1. 使用快速编辑器（推荐新手）

```bash
cd /Volumes/M2/TT_Live_AI_TTS/audio_pipeline
python3 quick_rules_editor.py
```

### 2. 使用完整规则管理器（推荐高级用户）

```bash
cd /Volumes/M2/TT_Live_AI_TTS/audio_pipeline
python3 rules_manager.py interactive
```

### 3. 命令行操作

```bash
# 列出所有规则
python3 rules_manager.py list-rules

# 获取特定规则值
python3 rules_manager.py get tempo_adjustment.base_range

# 设置规则值
python3 rules_manager.py set tempo_adjustment.base_range "[0.90,1.10]"

# 验证规则配置
python3 rules_manager.py validate

# 备份规则
python3 rules_manager.py backup
```

## ⚙️ 主要规则类别

### 1. 📊 语速调整 (tempo_adjustment)

控制EdgeTTS生成音频的语速变化：

```json
{
  "enabled": true,
  "base_range": [0.88, 1.12],
  "voice_type_adjustments": {
    "excited": {"range": [1.05, 1.15]},
    "calm": {"range": [0.95, 1.05]},
    "serious": {"range": [0.90, 1.00]},
    "friendly": {"range": [1.00, 1.10]}
  }
}
```

**常用修改：**
- `base_range`: 基础语速调整范围
- `enabled`: 是否启用语速调整
- `voice_type_adjustments`: 不同语音类型的特殊调整

### 2. 🎵 音高调整 (pitch_adjustment)

控制音频的音高变化：

```json
{
  "enabled": true,
  "base_range": [-0.4, 0.4],
  "preserve_formant": true,
  "voice_type_adjustments": {
    "excited": {"range": [0.1, 0.3]},
    "calm": {"range": [-0.1, 0.1]},
    "serious": {"range": [-0.3, -0.1]},
    "friendly": {"range": [0.0, 0.2]}
  }
}
```

**常用修改：**
- `base_range`: 基础音高调整范围（半音）
- `preserve_formant`: 是否保持共振峰特征
- `voice_type_adjustments`: 不同语音类型的音高调整

### 3. 🌍 背景音效 (background_sounds)

控制背景环境音效的添加：

```json
{
  "enabled": true,
  "probability": 0.8,
  "volume_range": [0.15, 0.35],
  "environments": {
    "cafe": {"file": "cafe_ambient.wav", "volume_range": [0.15, 0.25]},
    "office": {"file": "office_ambient.wav", "volume_range": [0.12, 0.22]},
    "living_room": {"file": "living_room.wav", "volume_range": [0.10, 0.20]},
    "outdoor": {"file": "outdoor_ambient.wav", "volume_range": [0.18, 0.30]},
    "room_tone": {"file": "room_tone.wav", "volume_range": [0.08, 0.15]}
  }
}
```

**常用修改：**
- `probability`: 添加背景音效的概率
- `volume_range`: 背景音效音量范围
- `environments`: 不同环境音效的配置

### 4. 🔊 事件音效 (event_sounds)

控制随机事件音效的添加：

```json
{
  "enabled": true,
  "probability": 0.15,
  "max_events_per_file": 2,
  "events": {
    "keyboard": {"file": "keyboard_typing.wav", "volume_range": [0.15, 0.25]},
    "water_pour": {"file": "water_pour.wav", "volume_range": [0.12, 0.20]},
    "footsteps": {"file": "footsteps.wav", "volume_range": [0.10, 0.18]},
    "chair_creak": {"file": "chair_creak.wav", "volume_range": [0.08, 0.15]},
    "paper_rustle": {"file": "paper_rustle.wav", "volume_range": [0.06, 0.12]}
  }
}
```

**常用修改：**
- `probability`: 添加事件音效的概率
- `max_events_per_file`: 每个文件最多的事件数
- `events`: 不同事件音效的配置

### 5. ⚡ 音频增强 (audio_enhancement)

控制音频质量增强参数：

```json
{
  "compressor": {
    "threshold": -18,
    "ratio": 3,
    "attack": 15,
    "release": 180,
    "makeup": 3
  },
  "equalizer": {
    "bands": [
      {"frequency": 250, "gain_range": [1.5, 2.5]},
      {"frequency": 3500, "gain_range": [1.8, 2.8]}
    ]
  },
  "highpass_filter": {"frequency": 80},
  "loudnorm": {"I": -19, "TP": -2, "LRA": 9}
}
```

**常用修改：**
- `compressor.threshold`: 压缩器阈值
- `equalizer.bands`: EQ频段设置
- `highpass_filter.frequency`: 高通滤波器频率

### 6. 📁 输出设置 (output_settings)

控制输出文件格式和质量：

```json
{
  "format": "m4a",
  "codec_priority": ["libfdk_aac", "libmp3lame", "aac"],
  "bitrate": 192,
  "folder_structure": {
    "base_dir": "20.1_ffpmeg输出文件_处理完成的音频文件",
    "batch_prefix": "ffmpeg_"
  }
}
```

**常用修改：**
- `format`: 输出格式 (m4a/mp3/wav)
- `bitrate`: 比特率 (kbps)
- `codec_priority`: 编码器优先级

### 7. 🔧 处理设置 (processing_settings)

控制处理性能和资源使用：

```json
{
  "max_workers": 4,
  "timeout": 600,
  "memory_limit": "2GB",
  "temp_dir": "temp_processing"
}
```

**常用修改：**
- `max_workers`: 最大并行处理数
- `timeout`: 处理超时时间（秒）
- `memory_limit`: 内存限制

### 8. 🎲 随机化设置 (randomization)

控制随机化行为：

```json
{
  "variation_level": "medium",
  "seed_mode": "auto",
  "preserve_characteristics": true
}
```

**常用修改：**
- `variation_level`: 变化程度 (low/medium/high)
- `seed_mode`: 种子模式 (auto/固定/随机)
- `preserve_characteristics`: 是否保持语音特征

## 🛠️ 实际使用示例

### 示例1：调整语速范围

```bash
# 使用快速编辑器
python3 quick_rules_editor.py
# 选择 1 -> 输入新的语速范围: 0.95,1.05

# 或使用命令行
python3 rules_manager.py set tempo_adjustment.base_range "[0.95,1.05]"
```

### 示例2：增加背景音效概率

```bash
# 使用快速编辑器
python3 quick_rules_editor.py
# 选择 3 -> 输入新的添加概率: 0.9

# 或使用命令行
python3 rules_manager.py set background_sounds.probability 0.9
```

### 示例3：调整事件音效音量

```bash
# 使用快速编辑器
python3 quick_rules_editor.py
# 选择 4 -> 输入新的音量范围: 0.2,0.4

# 或使用命令行
python3 rules_manager.py set event_sounds.events.keyboard.volume_range "[0.2,0.4]"
```

### 示例4：修改输出格式

```bash
# 使用快速编辑器
python3 quick_rules_editor.py
# 选择 6 -> 输入新的输出格式: mp3

# 或使用命令行
python3 rules_manager.py set output_settings.format "mp3"
```

## 🔄 规则应用流程

1. **修改规则**: 使用编辑器或命令行修改规则
2. **保存规则**: 规则自动保存到 `rules_config.json`
3. **重新加载**: 音频处理程序会自动重新加载规则
4. **应用规则**: 新的音频处理会使用更新后的规则

## 📊 规则验证

系统会自动验证规则配置的完整性：

```bash
python3 rules_manager.py validate
```

验证项目包括：
- 必要规则段是否存在
- 数值范围是否合理
- 文件路径是否正确
- 配置格式是否正确

## 💾 备份与恢复

### 备份规则

```bash
python3 rules_manager.py backup
# 生成: rules_backup_20241028_143022.json
```

### 恢复规则

```bash
python3 rules_manager.py restore rules_backup_20241028_143022.json
```

## 🎯 最佳实践

### 1. 渐进式调整

不要一次性大幅修改多个参数，建议：
- 先调整一个参数
- 测试效果
- 再调整下一个参数

### 2. 备份重要配置

在重大修改前，先备份当前配置：

```bash
python3 rules_manager.py backup
```

### 3. 验证修改

每次修改后，验证配置：

```bash
python3 rules_manager.py validate
```

### 4. 测试小批量

修改规则后，先用小批量音频测试：

```bash
python3 process_audio.py --preview 5
```

## 🚨 常见问题

### Q: 修改规则后没有生效？

A: 确保：
1. 规则已保存
2. 音频处理程序重新启动
3. 规则配置验证通过

### Q: 如何重置为默认规则？

A: 使用重置命令：

```bash
python3 rules_manager.py reset
```

### Q: 规则文件损坏怎么办？

A: 从备份恢复：

```bash
python3 rules_manager.py restore rules_backup_xxx.json
```

### Q: 如何查看所有可用规则？

A: 使用列表命令：

```bash
python3 rules_manager.py list-rules
```

## 📞 技术支持

如果遇到问题，请：

1. 检查规则配置是否正确
2. 查看错误日志
3. 尝试重置为默认规则
4. 联系技术支持

---

**注意**: 修改规则后，建议先用小批量音频测试效果，确认满意后再进行大批量处理。
