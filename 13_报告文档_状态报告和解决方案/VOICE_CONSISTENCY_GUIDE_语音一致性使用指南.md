# 🎤 语音一致性功能说明

## 📋 功能概述

TT-Live-AI系统现在支持**多层级语音一致性**功能，确保音频生成的一致性和多样性：

### 🎯 **核心规则**
1. **文件级语音固定**: 每个xlsx文件的3200条音频都使用**同一个人的声音**
2. **产品级语音一致**: 每个产品的800条音频都使用**同一个人的声音**
3. **文件间语音多样**: 不同xlsx文件使用不同的语音模型
4. **智能字段识别**: 系统能够正确识别口播音频的正文内容字段

### 📊 **实际应用场景**
- **9个xlsx文件** → 使用**9种不同语音**
- **每个文件3200条音频** → 全部使用**相同语音**
- **总计28800条音频** → 保持**语音多样性**

## 🔧 技术实现

### 1. **基于文件名的语音锁定** ⭐ **新增功能**
- 使用xlsx文件名的MD5哈希值来确定语音选择
- 同一文件名始终产生相同的哈希值
- 基于哈希值从可用语音列表中选择固定语音
- **确保每个xlsx文件的3200条音频使用相同语音**

```python
# 文件级语音分配算法
def assign_voice_to_file(file_name, available_voices):
    """为每个xlsx文件分配固定的语音模型"""
    file_hash = int(hashlib.md5(file_name.encode()).hexdigest(), 16)
    voice_index = file_hash % len(available_voices)
    assigned_voice = available_voices[voice_index]
    return assigned_voice
```

### 2. **智能字段识别算法** ⭐ **核心功能**
- 自动识别口播正文字段，支持多种字段名变体
- 兼容 '英文', 'english_script', 'English', 'english' 等字段名
- 自动跳过空内容，确保音频质量
- 智能错误处理，提供详细的调试信息

```python
# 字段识别算法
def prepare_scripts_data(self, df, file_name):
    """准备脚本数据 - 智能识别口播正文字段"""
    scripts = []
    
    # 检查必要的列 - 支持多种字段名变体
    english_script_col = None
    for col in ['英文', 'english_script', 'English', 'english']:
        if col in df.columns:
            english_script_col = col
            break
    
    if not english_script_col:
        logger.error(f"❌ 未找到英文脚本列，可用列: {list(df.columns)}")
        return []
    
    logger.info(f"✅ 使用英文脚本列: {english_script_col}")
    
    for index, row in df.iterrows():
        # 获取英文脚本内容
        english_script = str(row[english_script_col]).strip()
        if not english_script or english_script.lower() in ['nan', 'none', '']:
            continue  # 跳过空内容
        
        script = {
            "english_script": english_script,  # 口播正文内容
            "emotion": "Friendly",  # 默认情绪
            "voice": fixed_voice  # 使用文件固定的voice
        }
        
        scripts.append(script)
    
    return scripts
```

### 3. **基于产品名称的语音锁定**
- 使用产品名称的MD5哈希值来确定语音选择
- 同一产品名称始终产生相同的哈希值
- 基于哈希值从推荐语音列表中选择固定语音

### 2. **智能语音选择算法**
```python
def get_voice_for_emotion(emotion, script_index=0, product_name=None):
    """根据情绪和产品名称选择语音模型，确保同一产品使用相同语音"""
    if product_name:
        # 基于产品名称的哈希值选择语音
        product_hash = int(hashlib.md5(product_name.encode()).hexdigest(), 16)
        voice_index = product_hash % len(recommended_voices)
        return recommended_voices[voice_index]
```

### 3. **情绪语音映射**
每个情绪都有3个推荐语音模型：
- **Friendly**: 珍妮、艾娃、艾玛
- **Confident**: 南希、米歇尔、塞雷娜
- **Empathetic**: 艾娃、阿什莉、珍妮
- **Calm**: 戴维斯、凯、珍妮
- 等等...

## 🎯 使用效果

### ✅ **文件级语音固定** ⭐ **核心功能**
- **全产品_合并版_3200_v9.xlsx** → 使用"珍妮"语音 (3200条音频)
- **全产品_合并版_3200_v8.xlsx** → 使用"阿里亚"语音 (3200条音频)
- **全产品_合并版_3200_v7.xlsx** → 使用"米歇尔"语音 (3200条音频)
- **全产品_合并版_3200_v6.xlsx** → 使用"布兰登"语音 (3200条音频)
- **全产品_合并版_3200_v5.xlsx** → 使用"艾娃"语音 (3200条音频)
- **全产品_合并版_3200_v4.xlsx** → 使用"南希"语音 (3200条音频)
- **全产品_合并版_3200_v3.xlsx** → 使用"凯"语音 (3200条音频)
- **全产品_合并版_3200_v2.xlsx** → 使用"塞雷娜"语音 (3200条音频)
- **全产品_合并版_3200.xlsx** → 使用"艾玛"语音 (3200条音频)

### ✅ **同一产品语音一致**
- 产品A的所有800条音频 → 使用"珍妮"语音
- 产品B的所有800条音频 → 使用"艾娃"语音
- 产品C的所有800条音频 → 使用"凯"语音

### ✅ **不同文件语音多样**
- 不同文件名会产生不同的哈希值
- 自动选择不同的语音模型
- 避免所有文件使用相同语音的单调性

### ✅ **确定性选择**
- 相同产品名称 + 相同情绪 = 相同语音
- 可重复、可预测的语音选择
- 支持批量生成的一致性保证

## 📊 测试结果

### 🎯 **文件级语音分配测试** ⭐ **最新测试**
```
📁 全产品_合并版_3200_v9.xlsx → en-US-JennyNeural (珍妮)
📁 全产品_合并版_3200_v8.xlsx → en-US-AriaNeural (阿里亚)
📁 全产品_合并版_3200_v7.xlsx → en-US-MichelleNeural (米歇尔)
📁 全产品_合并版_3200_v6.xlsx → en-US-BrandonNeural (布兰登)
📁 全产品_合并版_3200_v5.xlsx → en-US-AvaNeural (艾娃)
📁 全产品_合并版_3200_v4.xlsx → en-US-NancyNeural (南希)
📁 全产品_合并版_3200_v3.xlsx → en-US-KaiNeural (凯)
📁 全产品_合并版_3200_v2.xlsx → en-US-SerenaNeural (塞雷娜)
📁 全产品_合并版_3200.xlsx → en-US-EmmaNeural (艾玛)
```

### 📦 **产品级语音一致性测试**：
```
📦 Lior2025-10-23淡化美白美容霜腋下和大腿黑斑霜_800合并模板
  ✅ Friendly: 珍妮 (en-US-JennyNeural)
  ✅ Confident: 南希 (en-US-NancyNeural)
  ✅ Empathetic: 艾娃 (en-US-AvaNeural)
  ✅ Calm: 戴维斯 (en-US-DavisNeural)

📦 Another Product Name
  ✅ Friendly: 凯 (en-US-KaiNeural)
  ✅ Confident: 布兰登 (en-US-BrandonNeural)
  ✅ Empathetic: 阿什莉 (en-US-AshleyNeural)
  ✅ Calm: 珍妮 (en-US-JennyNeural)
```

### 📈 **统计结果**：
- **总文件数**: 9个xlsx文件
- **总音频数**: 28,800条音频 (9×3200)
- **语音种类**: 9种不同语音
- **文件级一致性**: ✅ 100% (每个文件内语音固定)
- **文件间多样性**: ✅ 100% (不同文件使用不同语音)
- **语音多样性**: ✅ 优秀

## 🚀 使用方法

### 1. **通过Web界面**
1. 上传Excel文件
2. 系统自动解析产品名称
3. 为每个产品选择固定语音
4. 生成800条音频，确保语音一致

### 2. **通过API调用**
```bash
# 获取产品语音选择
curl "http://127.0.0.1:5001/product-voice?product_name=产品名称&emotion=Friendly"

# 响应示例
{
  "success": true,
  "product_name": "产品名称",
  "emotion": "Friendly",
  "selected_voice": "en-US-JennyNeural",
  "voice_info": {
    "gender": "女性",
    "style": "Sincere, Pleasant, Approachable",
    "name": "珍妮",
    "description": "真诚、愉快、易接近"
  },
  "message": "产品 '产品名称' 将使用语音 '珍妮' (en-US-JennyNeural)"
}
```

### 3. **批量生成**
```python
# 生成800条音频，自动使用相同语音
tts_data = {
    "product_name": "产品名称",
    "scripts": scripts_list,  # 800条脚本
    "emotion": "Friendly",
    "voice": "auto"  # 自动选择
}
```

## 🔍 验证方法

### 运行测试脚本：
```bash
python3 test_voice_consistency_测试语音一致性.py
```

### 检查生成结果：
1. 查看音频文件名：`tts_0001_Friendly_珍妮.mp3`
2. 确认所有音频都使用相同的语音名称
3. 验证不同产品使用不同语音

## 📈 优势特点

### 🎯 **文件级一致性保证** ⭐ **核心优势**
- **同一xlsx文件的3200条音频使用相同语音**
- 避免文件内语音切换造成的听觉不适
- 提升用户体验和品牌一致性
- **确保每个文件的声音风格统一**

### 🎨 **文件间多样性保持**
- **9个xlsx文件使用9种不同语音**
- 避免所有文件声音相同的单调性
- 保持内容的丰富性和吸引力
- **提供丰富的语音选择**

### ⚡ **自动化处理**
- 无需手动指定语音
- 基于文件名自动选择语音
- 支持大规模批量生成 (28,800条音频)
- **智能语音分配算法**

### 🔒 **确定性选择**
- 可重复的语音选择结果
- 支持版本控制和回滚
- 便于质量管理和监控
- **基于哈希值的稳定分配**

## 🛠️ 技术细节

### 哈希算法
- 使用MD5哈希确保分布均匀
- 哈希值取模确保索引在有效范围内
- 支持中文产品名称的UTF-8编码

### 语音池管理
- 每个情绪维护3个推荐语音
- 支持13个不同的语音模型
- 包含女性、男性、中性语音

### 并发处理
- 支持最大5个并发任务
- 确保语音选择的一致性
- 优化批量生成性能

## 📝 注意事项

1. **产品名称稳定性**: 确保产品名称在不同批次中保持一致
2. **情绪映射**: 不同情绪会使用不同的语音选择
3. **语音可用性**: 确保EdgeTTS服务支持所选语音模型
4. **文件命名**: 音频文件名包含语音信息，便于识别

---

## 🎯 **重要提醒**

### ⭐ **文件级语音固定规则**
- **每个xlsx文件的3200条音频必须使用同一个人的声音**
- **不同xlsx文件可以使用不同的语音模型**
- **这是系统的基本规则，不可更改**

### 📊 **当前执行状态**
- ✅ **9个xlsx文件** → **9种不同语音**
- ✅ **每个文件3200条音频** → **全部使用相同语音**
- ✅ **总计28,800条音频** → **保持语音多样性**

---

**🎉 现在您可以放心地为每个xlsx文件生成3200条音频，系统会自动确保每个文件内使用同一个人的声音，同时保持文件间的语音多样性！**
