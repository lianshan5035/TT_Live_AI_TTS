# EdgeTTS 输入输出规则执行器详细说明

## 📋 规则执行文件
**文件名**: `EdgeTTS_输入输出规则执行器.py`
**位置**: `/Volumes/M2/TT_Live_AI_TTS/EdgeTTS_输入输出规则执行器.py`

## 🎯 核心规则

### 规则1: 内容提取规则
- **目标**: 只处理"英文"字段的内容
- **实现**: 
  ```python
  english_field_content = str(row.get('英文', ''))
  ```
- **验证**: 
  ```python
  if not english_field_content or english_field_content == '英文':
      print("英文")
      continue
  ```
- **清理**: 移除多余空白字符，处理空值和'nan'值

### 规则2: 语音选择规则
- **目标**: 忽略每个 xlsx 文件中所有行的 Voice 字段
- **实现**: 
  ```python
  def get_default_voice(self):
      # 使用固定的默认语音，不读取Excel文件中的Voice字段
      default_voice = "en-US-JennyNeural"
      return default_voice
  ```
- **特点**: 所有音频使用统一的默认语音，不分析Excel文件中的Voice字段

### 规则3: 文件夹结构规则
- **目标**: 每个 xlsx 文件在输出目录下创建同名文件夹
- **实现**: 
  ```python
  file_base = os.path.splitext(os.path.basename(file_path))[0]
  file_output_dir = os.path.join(self.output_dir, file_base)
  ```
- **结果**: 
  ```
  /Volumes/M2/TT_Live_AI_TTS/20_输出文件_处理完成的音频文件/
  ├── 全产品_合并版_3200_v1/
  │   ├── english_field_0001_JennyNeural.mp3
  │   ├── english_field_0002_JennyNeural.mp3
  │   └── ...
  ├── 全产品_合并版_3200_v2/
  │   ├── english_field_0001_JennyNeural.mp3
  │   └── ...
  └── ...
  ```

### 规则4: 文件命名规则
- **目标**: 文件名格式为 `english_field_{行号}_{默认voice}.mp3`
- **实现**: 
  ```python
  voice_name = default_voice.split('-')[-1] if '-' in default_voice else 'Unknown'
  output_filename = f"english_field_{index+1:04d}_{voice_name}.mp3"
  output_file = os.path.join(file_output_dir, output_filename)
  ```
- **示例**: `english_field_0001_JennyNeural.mp3`

## 🔧 技术实现细节

### 1. 输入处理流程
```
Excel文件扫描 → 字段识别 → 英文字段提取 → 内容验证 → 清理处理
```

### 2. 输出处理流程
```
默认语音选择 → 同名文件夹创建 → 音频生成 → 文件保存 → 质量检查
```

### 3. 错误处理机制
- **字段验证**: 检查"英文"字段是否为空或为'英文'
- **文件检查**: 验证音频文件大小 > 1000 bytes
- **异常捕获**: 完整的错误日志记录
- **跳过机制**: 无效数据自动跳过，继续处理下一行

### 4. 性能优化
- **延迟控制**: 每行处理间隔3秒，文件间间隔5秒
- **目录创建**: 使用 `os.makedirs(..., exist_ok=True)` 确保目录存在
- **内存管理**: 逐行处理，避免大量数据加载

## 📊 执行示例

### 输入文件结构
```
/Volumes/M2/TT_Live_AI_TTS/18_批量输入_批量文件输入目录/
├── 全产品_合并版_3200_v1.xlsx
├── 全产品_合并版_3200_v2.xlsx
└── ...
```

### 输出文件结构
```
/Volumes/M2/TT_Live_AI_TTS/20_输出文件_处理完成的音频文件/
├── 全产品_合并版_3200_v1/
│   ├── english_field_0001_JennyNeural.mp3
│   ├── english_field_0002_JennyNeural.mp3
│   ├── english_field_0003_JennyNeural.mp3
│   └── ... (3200个音频文件)
├── 全产品_合并版_3200_v2/
│   ├── english_field_0001_JennyNeural.mp3
│   ├── english_field_0002_JennyNeural.mp3
│   └── ... (3200个音频文件)
└── ...
```

## 🚀 使用方法

### 1. 直接运行
```bash
cd /Volumes/M2/TT_Live_AI_TTS
python3 EdgeTTS_输入输出规则执行器.py
```

### 2. 后台运行
```bash
cd /Volumes/M2/TT_Live_AI_TTS
nohup python3 EdgeTTS_输入输出规则执行器.py > processing.log 2>&1 &
```

### 3. 监控进度
```bash
# 查看输出文件夹
ls -la 20_输出文件_处理完成的音频文件/

# 查看同名文件夹
find 20_输出文件_处理完成的音频文件/ -type d -name "*全产品*"

# 统计音频文件数量
find 20_输出文件_处理完成的音频文件/ -name "*.mp3" | wc -l
```

## 📈 预期结果

### 处理统计
- **输入文件**: 11个xlsx文件
- **总行数**: 约35,200行（11 × 3200）
- **输出音频**: 约35,200个MP3文件
- **文件夹数**: 11个同名文件夹
- **处理时间**: 约29-35小时（每行3秒延迟）

### 质量指标
- **成功率**: >95%（正常音频文件 > 1000 bytes）
- **文件格式**: MP3，44.1kHz，128kbps
- **语音一致性**: 所有音频使用 en-US-JennyNeural
- **内容准确性**: 只处理"英文"字段内容

## ⚠️ 注意事项

1. **存储空间**: 确保有足够磁盘空间（约50-100GB）
2. **处理时间**: 完整处理需要29-35小时
3. **网络连接**: EdgeTTS需要稳定的网络连接
4. **系统资源**: 建议在系统空闲时运行
5. **中断恢复**: 支持中断后重新运行，会跳过已生成的文件

## 🔍 故障排除

### 常见问题
1. **音频文件过小**: 检查网络连接和EdgeTTS服务状态
2. **文件夹创建失败**: 检查输出目录权限
3. **Excel文件读取失败**: 检查文件格式和编码
4. **内存不足**: 减少并发处理数量

### 日志查看
```bash
# 查看处理日志
tail -f processing.log

# 查看系统日志
tail -f 19_日志文件_系统运行日志和错误记录/tts_service.log
```
