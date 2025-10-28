# EdgeTTS音频处理规则管理系统 - 使用指南

## 🎯 系统概述

这是一个完整的EdgeTTS音频处理规则管理系统，允许您实时修改音频处理的各项参数，无需重新编译代码。系统采用模块化设计，支持热重载，非常适合TikTok直播等需要大量音频处理的场景。

## 📁 系统架构

```
audio_pipeline/
├── rules_config.json          # 主规则配置文件
├── rules_manager.py          # 完整规则管理器
├── quick_rules_editor.py     # 快速规则编辑器
├── rules_loader.py           # 规则加载器
├── rule_usage_example.py     # 使用示例
└── README_RULES.md          # 使用指南
```

## 🚀 快速开始

### 1. 使用快速编辑器（推荐新手）

```bash
cd /Volumes/M2/TT_Live_AI_TTS/audio_pipeline
python3 quick_rules_editor.py
```

**特点：**
- 图形化菜单界面
- 中文提示
- 实时验证输入
- 自动保存

### 2. 使用完整规则管理器（推荐高级用户）

```bash
cd /Volumes/M2/TT_Live_AI_TTS/audio_pipeline
python3 rules_manager.py interactive
```

**特点：**
- 命令行交互
- 支持复杂规则修改
- 批量操作
- 规则验证

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

## ⚙️ 核心规则配置

### 1. 📊 语速调整规则

```json
{
  "tempo_adjustment": {
    "enabled": true,
    "base_range": [0.88, 1.12],
    "voice_type_adjustments": {
      "excited": {"range": [1.05, 1.15]},
      "calm": {"range": [0.95, 1.05]},
      "serious": {"range": [0.90, 1.00]},
      "friendly": {"range": [1.00, 1.10]}
    }
  }
}
```

**作用：** 控制EdgeTTS生成音频的语速变化，模拟不同场次的直播效果。

**修改建议：**
- 基础范围：`[0.88, 1.12]` - 适合大多数场景
- 兴奋型：`[1.05, 1.15]` - 模拟激动情绪
- 平静型：`[0.95, 1.05]` - 保持稳定
- 严肃型：`[0.90, 1.00]` - 略微减速

### 2. 🎵 音高调整规则

```json
{
  "pitch_adjustment": {
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
}
```

**作用：** 控制音频的音高变化，保持语音特征的同时增加变化。

**修改建议：**
- 基础范围：`[-0.4, 0.4]` - 轻微变化
- 兴奋型：`[0.1, 0.3]` - 轻微升调
- 平静型：`[-0.1, 0.1]` - 保持原调
- 严肃型：`[-0.3, -0.1]` - 轻微降调

### 3. 🌍 背景音效规则

```json
{
  "background_sounds": {
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
}
```

**作用：** 添加环境音效，模拟真实直播场景。

**修改建议：**
- 概率：`0.8` - 80%概率添加背景音效
- 音量范围：`[0.15, 0.35]` - 不影响主语音
- 环境选择：根据直播内容选择合适环境

### 4. 🔊 事件音效规则

```json
{
  "event_sounds": {
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
}
```

**作用：** 添加随机事件音效，增加直播真实感。

**修改建议：**
- 概率：`0.15` - 15%概率触发
- 最大事件数：`2` - 每个文件最多2个事件
- 音量范围：根据事件类型调整

### 5. ⚡ 音频增强规则

```json
{
  "audio_enhancement": {
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
}
```

**作用：** 提升音频质量，优化直播效果。

**修改建议：**
- 压缩器阈值：`-18dB` - 适合语音
- EQ频段：250Hz和3.5kHz - 语音关键频段
- 高通滤波器：`80Hz` - 去除低频噪音

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

## 🔧 高级功能

### 1. 规则热重载

```python
from rules_loader import reload_rules

# 重新加载规则
if reload_rules():
    print("规则已重新加载")
```

### 2. 规则摘要

```python
from rules_loader import get_rules_loader

loader = get_rules_loader()
summary = loader.get_rules_summary()
print(summary)
```

### 3. 自定义规则验证

```python
from rules_manager import RulesManager

manager = RulesManager()
if manager.validate_rules():
    print("规则验证通过")
```

## 📞 技术支持

如果遇到问题，请：

1. 检查规则配置是否正确
2. 查看错误日志
3. 尝试重置为默认规则
4. 联系技术支持

## 🎉 总结

这个规则管理系统提供了：

- **灵活性**: 实时修改处理参数
- **易用性**: 多种操作方式
- **可靠性**: 自动验证和备份
- **可扩展性**: 模块化设计
- **专业性**: 针对TikTok直播优化

通过这个系统，您可以轻松调整EdgeTTS音频处理的各项参数，实现最佳的直播效果，有效避免TikTok AI检测为录播。

---

**注意**: 修改规则后，建议先用小批量音频测试效果，确认满意后再进行大批量处理。
