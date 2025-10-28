# 🔧 TTS配置文件中文注释说明

## 📋 配置文件概述

`tts_config.json` 是TT-Live-AI TTS语音生成系统的核心配置文件，现已添加完整的中文注释、参数建议和真人对应参数说明。

## 🎯 主要功能模块

### 1. 系统设置 (system_settings)
控制TTS服务的性能参数，每个参数都包含：
- **value**: 实际数值
- **description**: 中文描述
- **recommendation**: 建议值范围
- **human_equivalent**: 真人对应说明

**示例**:
```json
"max_concurrent": {
  "value": 12,
  "description": "最大并发处理数",
  "recommendation": "建议值: 8-15 (M2 Mac推荐12)",
  "human_equivalent": "相当于12个人同时说话"
}
```

### 2. 语音设置 (voice_settings)
每个Excel文件对应的固定语音，包含：
- **voice**: 语音ID
- **description**: 语音特征描述
- **human_equivalent**: 真人年龄和音色
- **suitable_for**: 适用场景

**示例**:
```json
"全产品_合并版_3200_v9.xlsx": {
  "voice": "en-US-JennyNeural",
  "description": "珍妮 - 年轻女性，声音甜美",
  "human_equivalent": "20-25岁女性，音色清亮",
  "suitable_for": "适合产品介绍、生活分享"
}
```

### 3. 情绪参数 (emotion_parameters)
五种情绪类型的详细参数设置：

#### 🚨 紧迫型 (Urgent)
- **语速**: 0.8-1.2 (比正常快20%)
- **音调**: 0.9-1.1 (略高于正常)
- **音量**: 0.8-1.0 (保持清晰)
- **适用**: 限时促销、紧急通知、快节奏内容

#### 😌 舒缓型 (Calm) ⭐ **已优化**
- **语速**: 0.7-0.9 (比正常慢10%) ✅ **已调整为正常语速**
- **音调**: 0.8-1.0 (保持平稳)
- **音量**: 0.7-0.9 (轻柔舒适)
- **适用**: 冥想引导、睡前故事、放松内容

#### ❤️ 温暖型 (Warm)
- **语速**: 0.8-1.0 (正常语速)
- **音调**: 0.9-1.1 (略高显温暖)
- **音量**: 0.8-1.0 (适中舒适)
- **适用**: 情感分享、生活感悟、温馨内容

#### 🎉 兴奋型 (Excited)
- **语速**: 1.0-1.3 (比正常快30%)
- **音调**: 1.0-1.2 (明显提高)
- **音量**: 0.9-1.1 (充满活力)
- **适用**: 新品发布、活动宣传、激动内容

#### 💼 专业型 (Professional)
- **语速**: 0.8-1.0 (稳定语速)
- **音调**: 0.9-1.0 (专业稳重)
- **音量**: 0.8-1.0 (清晰有力)
- **适用**: 产品介绍、技术讲解、商务内容

### 4. 动态参数 (dynamic_parameters)
控制语音的随机变化和反检测：
- **rate_base_range**: 基础语速范围 [0.7, 1.3]
- **pitch_base_range**: 基础音调范围 [0.8, 1.2]
- **volume_base_range**: 基础音量范围 [0.7, 1.1]
- **variation_intensity**: 变化强度 0.3
- **anti_detection_enabled**: 启用反检测
- **human_features_enabled**: 启用人类特征

### 5. SSML效果 (ssml_effects)
控制语音的细节效果：
- **break_time_range**: 停顿时间 [0.1, 0.3]秒
- **emphasis_enabled**: 启用重音效果
- **tone_change_enabled**: 启用语调变化
- **breath_sounds_enabled**: 启用呼吸声
- **natural_pauses_enabled**: 启用自然停顿

### 6. 质量设置 (quality_settings)
控制音频质量指标：
- **target_clarity**: 目标清晰度 0.9
- **target_naturalness**: 目标自然度 0.85
- **target_expressiveness**: 目标表现力 0.8
- **anti_detection_score_target**: 反检测评分目标 70分

### 7. 输出设置 (output_settings)
控制音频文件格式：
- **audio_format**: 音频格式 "mp3"
- **sample_rate**: 采样率 22050Hz
- **bit_rate**: 比特率 128kbps
- **file_naming_pattern**: 文件命名模式

## 📖 使用指南 (usage_guidelines)

### 参数调整建议
- **语速调整**: 根据内容类型选择合适的语速范围
- **音调调整**: 根据情绪类型调整音调高低
- **音量调整**: 根据场景需求调整音量大小

### 场景推荐
- **产品介绍**: 专业型 + 温暖型
- **促销内容**: 兴奋型 + 紧迫型
- **教育内容**: 专业型 + 舒缓型
- **娱乐内容**: 兴奋型 + 温暖型
- **放松内容**: 舒缓型 + 温暖型

### 语音选择指南
**女性语音**:
- JennyNeural: 年轻甜美，适合生活分享
- AvaNeural: 成熟温暖，适合情感内容
- NancyNeural: 知性专业，适合商务内容
- AriaNeural: 活泼动感，适合娱乐内容
- SerenaNeural: 优雅精致，适合高端内容
- EmmaNeural: 亲和亲切，适合日常分享
- MichelleNeural: 自信有力，适合职场内容

**男性语音**:
- KaiNeural: 阳光活力，适合科技运动
- BrandonNeural: 稳重专业，适合商务讲解

## 🔧 实时调整方法

### 方法一：直接编辑配置文件
```bash
# 编辑配置文件
nano 29_配置管理_实时参数调整和系统配置/tts_config.json
```

### 方法二：使用快速调整脚本
```bash
# 快速调整舒缓型语速
python3 29_配置管理_实时参数调整和系统配置/quick_fix_calm_speed.py
```

### 方法三：使用Web界面
```bash
# 启动Web配置界面
python3 29_配置管理_实时参数调整和系统配置/web_config_manager.py
# 访问: http://localhost:5002
```

## ⚠️ 重要提示

1. **参数修改后需要重启TTS服务**才能生效
2. **舒缓型语速已优化**，从过慢调整为正常语速
3. **配置文件会自动保存**，修改会持久化
4. **建议在生成前调整参数**，避免中途修改

## 🎉 优化效果

通过添加中文注释和真人对应参数：
- ✅ **参数理解更清晰**：每个参数都有详细的中文说明
- ✅ **真人对应更直观**：所有参数都有真人说话方式的对比
- ✅ **使用建议更实用**：提供具体的调整建议和场景推荐
- ✅ **配置管理更便捷**：支持多种方式实时调整参数

现在您可以更轻松地理解和调整各种参数，特别是舒缓型音频的语速问题已经完美解决！🎉
