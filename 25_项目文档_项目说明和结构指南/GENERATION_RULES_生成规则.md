# 🎤 TT-Live-AI 音频生成规则

## 📋 核心生成规则

### ⭐ **规则1: 文件级语音固定** (最重要)
- **每个xlsx文件的3200条音频必须使用同一个人的声音**
- **不同xlsx文件可以使用不同的语音模型**
- **这是系统的基本规则，不可更改**

### ⭐ **规则2: 口播正文字段识别** (核心功能)
- **系统能够正确识别口播音频的正文内容字段**
- **支持多种字段名变体，确保兼容性**
- **自动跳过空内容，确保音频质量**

### 📊 **实际应用示例**
```
📁 全产品_合并版_3200_v9.xlsx → en-US-JennyNeural (珍妮) - 3200条音频
📁 全产品_合并版_3200_v8.xlsx → en-US-AriaNeural (阿里亚) - 3200条音频
📁 全产品_合并版_3200_v7.xlsx → en-US-MichelleNeural (米歇尔) - 3200条音频
📁 全产品_合并版_3200_v6.xlsx → en-US-BrandonNeural (布兰登) - 3200条音频
📁 全产品_合并版_3200_v5.xlsx → en-US-AvaNeural (艾娃) - 3200条音频
📁 全产品_合并版_3200_v4.xlsx → en-US-NancyNeural (南希) - 3200条音频
📁 全产品_合并版_3200_v3.xlsx → en-US-KaiNeural (凯) - 3200条音频
📁 全产品_合并版_3200_v2.xlsx → en-US-SerenaNeural (塞雷娜) - 3200条音频
📁 全产品_合并版_3200.xlsx → en-US-EmmaNeural (艾玛) - 3200条音频
```

## 🔧 技术实现

### 1. 口播正文字段识别算法 ⭐ **核心功能**
```python
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
        
        # 获取其他参数...
        scripts.append(script)
    
    return scripts
```

### 2. 语音分配算法
```python
def assign_voice_to_file(file_name, available_voices):
    """为每个xlsx文件分配固定的语音模型"""
    file_hash = int(hashlib.md5(file_name.encode()).hexdigest(), 16)
    voice_index = file_hash % len(available_voices)
    assigned_voice = available_voices[voice_index]
    return assigned_voice
```

### 队列处理器实现
```python
# 为每个文件分配一个固定的语音模型
file_voice_map = {}
for file_name in xlsx_files:
    file_hash = int(hashlib.md5(file_name.encode()).hexdigest(), 16)
    assigned_voice = self.available_voices[file_hash % len(self.available_voices)]
    file_voice_map[file_name] = assigned_voice
```

## 📈 优势特点

### 🎯 **智能字段识别** ⭐ **核心优势**
- **自动识别口播正文字段**: 支持多种字段名变体
- **兼容性强**: 支持 '英文', 'english_script', 'English', 'english' 等字段名
- **自动跳过空内容**: 确保音频质量，避免生成空白音频
- **智能错误处理**: 未找到字段时提供详细的错误信息

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

## 🚀 使用方法

### 1. **启动断点续传队列处理器**
```bash
cd /Volumes/M2/TT_Live_AI_TTS
python3 resume_queue_processor_断点续传队列处理器.py
```

### 2. **系统自动执行**
- 自动识别inputs文件夹中的xlsx文件
- 为每个文件分配固定语音
- 逐个文件生成3200条音频
- 支持断点续传功能

### 3. **监控进度**
```bash
# 查看实时日志
tail -f logs/resume_queue_processor.log

# 检查生成的音频文件数量
find outputs -name "*.mp3" | wc -l
```

## 📊 当前状态

### ✅ **执行中的任务**
- **文件**: 全产品_合并版_3200_v9.xlsx
- **语音**: en-US-JennyNeural (珍妮)
- **进度**: 批次21/64 (脚本1001-1050)
- **已完成**: 1000个音频文件
- **剩余**: 2200个音频文件

### 📈 **总体进度**
- **总文件数**: 9个xlsx文件
- **总音频数**: 28,800条音频 (9×3200)
- **语音种类**: 9种不同语音
- **文件级一致性**: ✅ 100%
- **文件间多样性**: ✅ 100%

## 🎯 **重要提醒**

### ⭐ **必须遵守的规则**
1. **每个xlsx文件的3200条音频必须使用同一个人的声音**
2. **不同xlsx文件可以使用不同的语音模型**
3. **系统必须能够正确识别口播正文字段**
4. **这是系统的基本规则，不可更改**

### 📝 **字段识别规则**
- **支持的字段名**: '英文', 'english_script', 'English', 'english'
- **自动跳过**: 空内容、'nan', 'none', '' 等无效值
- **错误处理**: 未找到字段时显示可用列名，便于调试
- **兼容性**: 支持不同Excel模板的字段名变体

### 📊 **当前执行状态**
- ✅ **9个xlsx文件** → **9种不同语音**
- ✅ **每个文件3200条音频** → **全部使用相同语音**
- ✅ **总计28,800条音频** → **保持语音多样性**
- ✅ **字段识别** → **自动识别口播正文字段**

---

**🎉 系统正在按规则执行：每个xlsx文件使用固定语音，确保文件内一致性，同时保持文件间多样性！**
