# 02_配置文件_规则和参数设置

## 📁 文件夹说明

此目录包含EdgeTTS音频处理系统的所有配置文件和参数设置，支持实时修改和热重载。

## ⚙️ 配置文件列表

### 🎛️ 主配置文件
- `rules_config.json` - 主规则配置文件，包含所有音频处理参数
- `SAMPLE_PARAMS.json` - 示例参数文件，展示配置格式

### 📊 测试报告
- `test_report_20251028_103546.json` - 测试案例执行报告，包含详细统计信息

## 🔧 配置文件说明

### rules_config.json
主要的规则配置文件，包含以下模块：

#### 📊 语速调整规则
- `tempo_adjustment` - 语速调整参数
- `base_range` - 基础语速范围
- `voice_type_adjustments` - 不同语音类型的调整

#### 🎵 音高调整规则  
- `pitch_adjustment` - 音高调整参数
- `preserve_formant` - 保持共振峰特征

#### 🌍 背景音效规则
- `background_sounds` - 背景音效配置
- `environments` - 环境音效设置
- `probability` - 添加概率

#### 🔊 事件音效规则
- `event_sounds` - 事件音效配置
- `events` - 具体事件音效设置

#### ⚡ 音频增强规则
- `audio_enhancement` - 音频增强参数
- `compressor` - 动态压缩器设置
- `equalizer` - EQ均衡器设置

#### 📁 输出设置规则
- `output_settings` - 输出格式和编码设置
- `codec_priority` - 编码器优先级

#### 🔧 处理设置规则
- `processing_settings` - 处理性能参数
- `max_workers` - 最大并行处理数

#### 🎲 随机化规则
- `randomization` - 随机化参数
- `variation_level` - 变化程度

## 🛠️ 使用方法

### 修改配置
```bash
# 使用规则管理器修改
python3 rules_manager.py set tempo_adjustment.base_range "[0.95,1.05]"

# 使用快速编辑器修改
python3 quick_rules_editor.py
```

### 验证配置
```bash
python3 rules_manager.py validate
```

### 备份配置
```bash
python3 rules_manager.py backup
```

## 📈 配置特点

- **实时修改**: 无需重启程序即可生效
- **热重载**: 支持运行时重新加载配置
- **自动验证**: 确保配置格式正确
- **备份恢复**: 支持配置备份和恢复
- **中文注释**: 所有参数都有中文说明
