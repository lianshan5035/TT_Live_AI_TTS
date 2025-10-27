# TT-Live-AI 音频生成系统使用指南

## 🎯 系统概述

**TT-Live-AI 音频生成系统** 是专门为衔接GPTs生成的Excel文件而设计的本地音频生成工具。它能够智能解析GPTs生成的各种格式的Excel文件，并自动转换为高质量的MP3音频文件。

### ✨ 核心特性

- **完美衔接GPTs**：支持GPTs生成的所有Excel格式和字段名
- **智能解析**：自动识别产品名称、情绪和语音参数
- **A3标准合规**：完全符合GPTs-A3文档规范
- **批量处理**：支持单文件和批量文件处理
- **高质量输出**：基于Edge-TTS的高质量语音合成

## 📁 支持的文件格式

### Excel文件格式
- **.xlsx** - Excel 2007+ 格式
- **.xls** - Excel 97-2003 格式
- **.csv** - 逗号分隔值文件
- **.tsv** - 制表符分隔值文件
- **.txt** - 文本文件（Markdown表格、纯文本表格）

### 编码支持
- UTF-8, UTF-8-BOM, GBK, GB2312, Latin1

## 🔍 支持的字段名（50+种变体）

### 英文文案字段（必需）
系统会自动识别以下字段名变体：

#### 标准字段名
- `english_script`, `English Script`, `english`, `English`
- `script`, `Script`, `文案`, `英文文案`
- `english_text`, `English Text`

#### GPTs常用字段名
- `Content`, `content`, `English Content`, `english_content`
- `Text`, `text`, `English Text`, `english_text`
- `Description`, `description`, `English Description`, `english_description`
- `Copy`, `copy`, `English Copy`, `english_copy`
- `Scripts`, `scripts`, `English Scripts`, `english_scripts`
- `Prompts`, `prompts`, `English Prompts`, `english_prompts`
- `Messages`, `messages`, `English Messages`, `english_messages`
- `Posts`, `posts`, `English Posts`, `english_posts`
- `Ads`, `ads`, `English Ads`, `english_ads`
- `Marketing`, `marketing`, `English Marketing`, `english_marketing`
- `Sales`, `sales`, `English Sales`, `english_sales`
- `Copywriting`, `copywriting`, `English Copywriting`, `english_copywriting`
- `Headlines`, `headlines`, `English Headlines`, `english_headlines`
- `Taglines`, `taglines`, `English Taglines`, `english_taglines`
- `Slogans`, `slogans`, `English Slogans`, `english_slogans`
- `Captions`, `captions`, `English Captions`, `english_captions`
- `Titles`, `titles`, `English Titles`, `english_titles`
- `Subtitles`, `subtitles`, `English Subtitles`, `english_subtitles`
- `Body`, `body`, `English Body`, `english_body`
- `Main`, `main`, `English Main`, `english_main`
- `Primary`, `primary`, `English Primary`, `english_primary`
- `Core`, `core`, `English Core`, `english_core`
- `Key`, `key`, `English Key`, `english_key`
- `Essential`, `essential`, `English Essential`, `english_essential`
- `Important`, `important`, `English Important`, `english_important`

### 中文翻译字段（可选）
- `chinese_translation`, `Chinese Translation`, `chinese`, `Chinese`
- `translation`, `Translation`, `中文翻译`, `翻译`
- `Chinese Content`, `chinese_content`, `中文内容`, `中文`
- `Chinese Text`, `chinese_text`, `中文文本`, `中文文案`
- `Chinese Description`, `chinese_description`, `中文描述`, `描述`
- `Chinese Copy`, `chinese_copy`, `中文副本`, `副本`
- `Chinese Scripts`, `chinese_scripts`, `中文脚本`, `脚本`
- `Chinese Prompts`, `chinese_prompts`, `中文提示`, `提示`
- `Chinese Messages`, `chinese_messages`, `中文消息`, `消息`
- `Chinese Posts`, `posts`, `中文帖子`, `帖子`
- `Chinese Ads`, `chinese_ads`, `中文广告`, `广告`
- `Chinese Marketing`, `chinese_marketing`, `中文营销`, `营销`
- `Chinese Sales`, `sales`, `中文销售`, `销售`
- `Chinese Copywriting`, `chinese_copywriting`, `中文文案`, `文案`
- `Chinese Headlines`, `chinese_headlines`, `中文标题`, `标题`
- `Chinese Taglines`, `chinese_taglines`, `中文标语`, `标语`
- `Chinese Slogans`, `chinese_slogans`, `中文口号`, `口号`
- `Chinese Captions`, `captions`, `中文说明`, `说明`
- `Chinese Descriptions`, `descriptions`, `中文描述`, `描述`
- `Chinese Titles`, `titles`, `中文标题`, `标题`
- `Chinese Subtitles`, `chinese_subtitles`, `中文副标题`, `副标题`
- `Chinese Body`, `chinese_body`, `中文正文`, `正文`
- `Chinese Main`, `chinese_main`, `中文主要`, `主要`
- `Chinese Primary`, `chinese_primary`, `中文主要`, `主要`
- `Chinese Core`, `core`, `中文核心`, `核心`
- `Chinese Key`, `key`, `中文关键`, `关键`
- `Chinese Essential`, `essential`, `中文必要`, `必要`
- `Chinese Important`, `important`, `中文重要`, `重要`

## 📝 文件名解析规则

系统支持多种文件名格式来提取产品名称：

### 1. 日期_产品名_数字
- `2025-01-27美白产品_800.xlsx` → 产品名: `美白产品`
- `2025-01-27Dark Spot Patch_800.xlsx` → 产品名: `Dark Spot Patch`

### 2. 日期_产品名_合并
- `2025-01-27美白产品_合并.xlsx` → 产品名: `美白产品`

### 3. 日期_产品名_模板
- `2025-01-27美白产品_模板.xlsx` → 产品名: `美白产品`

### 4. 产品名_日期
- `美白产品_2025-01-27.xlsx` → 产品名: `美白产品`

### 5. 产品名_数字
- `美白产品_800.xlsx` → 产品名: `美白产品`

### 6. 产品名_合并
- `美白产品_合并.xlsx` → 产品名: `美白产品`

### 7. 产品名_模板
- `美白产品_模板.xlsx` → 产品名: `美白产品`

### 8. 产品名_GPT
- `美白产品_GPT.txt` → 产品名: `美白产品`

### 9. 产品名_AI
- `美白产品_AI.xlsx` → 产品名: `美白产品`

### 10. 产品名_生成
- `美白产品_生成.csv` → 产品名: `美白产品`

## 🎵 情绪自动匹配

系统会根据产品名称中的关键词自动选择最佳情绪：

| 关键词 | 情绪 | 适用产品类型 |
|--------|------|-------------|
| 美白、淡斑、亮白、brightening | Excited | 新品/促销/美妆 |
| 抗老、紧致、firming、anti-aging | Confident | 高端/科技/专业 |
| 保湿、补水、滋润、moisturizing | Calm | 家居/教育/舒缓 |
| 维生素、vitamin、精华、serum | Playful | 美妆/时尚/年轻 |
| 胶原蛋白、collagen、健康、health | Empathetic | 护肤/健康/关怀 |
| 瘦身、减肥、fitness、weight | Motivational | 健身/减肥/激励 |
| 护发、hair、柔顺、smooth | Soothing | 护发/柔顺/舒缓 |
| 眼部、eye、温和、gentle | Gentle | 眼部护理/温和 |

## 🚀 使用方法

### 方式1：交互式处理
```bash
python3 excel_to_audio_generator.py
```
然后选择：
1. 处理单个Excel文件
2. 处理多个文件
3. 处理目录中的所有Excel文件

### 方式2：命令行处理
```bash
# 处理单个文件
python3 drag_drop_generator.py file1.xlsx

# 处理多个文件
python3 drag_drop_generator.py file1.xlsx file2.xlsx file3.xlsx

# 处理目录中的所有Excel文件
python3 drag_drop_generator.py --directory /path/to/excel/files
```

### 方式3：检查TTS服务状态
```bash
python3 drag_drop_generator.py --check-service
```

## 📊 输出结果

### 音频文件
- **格式**：MP3
- **时长**：35-60秒/条
- **质量**：Edge-TTS高质量合成
- **命名**：`tts_{序号:04d}_{情绪}.mp3`
- **目录**：`audio_outputs/{产品名称}/`

### 生成报告
```json
{
  "generation_time": "2025-01-27T10:30:00",
  "original_file": "Lior2025-01-27美白产品_800.xlsx",
  "result": {
    "success": true,
    "product_name": "美白产品",
    "total_scripts": 80,
    "emotion": "Excited",
    "voice": "en-US-JennyNeural",
    "audio_directory": "audio_outputs/美白产品/",
    "audio_params": [
      {
        "script_id": 1,
        "script": "Transform your skin with our revolutionary...",
        "emotion": "Excited",
        "voice": "en-US-JennyNeural",
        "rate": "+15%",
        "pitch": "+12%",
        "volume": "+15dB",
        "audio_file": "tts_0001_Excited.mp3"
      }
    ]
  }
}
```

## 🎯 A3标准合规

### 情绪参数映射
| 情绪 | Rate | Pitch | Volume | 适用产品 |
|------|------|-------|--------|----------|
| Excited | +15% | +12% | +15% | 新品/促销 |
| Confident | +8% | +5% | +8% | 高端/科技 |
| Empathetic | -12% | -8% | -10% | 护肤/健康 |
| Calm | -10% | -3% | 0% | 家居/教育 |
| Playful | +18% | +15% | +5% | 美妆/时尚 |
| Urgent | +22% | +8% | +18% | 限时/秒杀 |

### 动态参数算法
- **正弦波 + 斐波那契 + 素数序列**组合算法
- **防检测机制**：动态速率平衡 ±10%
- **语义重复率** >10% 自动替换子句

### 语音模型选择
- **主要语音**：en-US-JennyNeural, en-US-GuyNeural, en-US-DavisNeural
- **自动匹配**：根据产品类型和情绪自动选择最佳语音
- **轮换机制**：≥3种声线轮换，避免单一化

## 📋 使用示例

### 示例1：标准Excel文件
```
文件名：Lior2025-01-27美白产品_800.xlsx
字段：english_script, chinese_translation
结果：自动识别为"美白产品"，选择"Excited"情绪
```

### 示例2：GPTs生成的Content字段
```
文件名：Lior2025-01-27美白产品_800_Content.xlsx
字段：Content, Chinese
结果：自动映射到english_script和chinese_translation
```

### 示例3：Markdown表格文件
```
文件名：Lior2025-01-27美白产品_800_Markdown.txt
格式：| English Script | Chinese Translation |
结果：自动解析Markdown表格格式
```

### 示例4：CSV文件
```
文件名：Lior2025-01-27美白产品_800.csv
字段：script, translation
结果：自动识别字段并生成音频
```

## ⚠️ 注意事项

1. **TTS服务**：使用前请确保TTS服务正在运行（`python3 run_tts.py`）
2. **文件格式**：确保Excel文件包含英文文案字段
3. **文件编码**：系统会自动尝试多种编码格式
4. **产品名称**：文件名应包含产品相关信息以便自动匹配情绪
5. **文案长度**：建议每条文案50-1000字符，符合35-60秒口播时长

## 🔧 故障排除

### 常见问题

1. **TTS服务未运行**
   ```
   错误：❌ TTS服务未运行
   解决：python3 run_tts.py
   ```

2. **文件解析失败**
   ```
   错误：Excel文件缺少英文文案字段
   解决：检查文件是否包含english_script或Content等字段
   ```

3. **编码问题**
   ```
   错误：无法读取文件
   解决：系统会自动尝试多种编码，如仍有问题请检查文件编码
   ```

4. **音频生成失败**
   ```
   错误：TTS服务错误: 500
   解决：检查TTS服务状态和网络连接
   ```

## 📞 技术支持

如有问题，请检查：
1. TTS服务是否正常运行
2. Excel文件格式是否正确
3. 文件是否包含必需的英文文案字段
4. 网络连接是否正常

---

**TT-Live-AI 音频生成系统** - 完美衔接GPTs，一键生成高质量音频！
