# GPTs Excel文件格式规范 - TT-Live-AI语音生成系统

## 📋 概述

本文档详细说明了GPTs生成的Excel文件在TT-Live-AI语音生成系统中的格式要求和字段规范。

---

## 🎯 必需字段

### 1. **english_script** (必需)
**用途**: 语音生成的英文脚本内容  
**说明**: 这是生成音频的核心字段，系统会读取此列的所有内容进行语音合成

**支持的字段名变体**:
```
english_script, English Script, english, English, script, Script
文案, 英文文案, english_text, English Text
English Content, english_content, Content, content
English Text, english_text, Text, text
English Description, english_description, Description, description
English Copy, english_copy, Copy, copy
English Scripts, english_scripts, Scripts, scripts
English Prompts, english_prompts, Prompts, prompts
English Messages, english_messages, Messages, messages
English Posts, english_posts, Posts, posts
English Ads, english_ads, Ads, ads
English Marketing, english_marketing, Marketing, marketing
English Sales, english_sales, Sales, sales
English Copywriting, english_copywriting, Copywriting, copywriting
English Headlines, english_headlines, Headlines, headlines
English Taglines, english_taglines, Taglines, taglines
English Slogans, english_slogans, Slogans, slogans
English Captions, english_captions, Captions, captions
English Descriptions, english_descriptions, Descriptions, descriptions
English Titles, english_titles, Titles, titles
English Subtitles, english_subtitles, Subtitles, subtitles
English Body, english_body, Body, body
English Main, english_main, Main, main
English Primary, english_primary, Primary, primary
English Core, english_core, Core, core
English Key, english_key, Key, key
English Essential, english_essential, Essential, essential
English Important, english_important, Important, important
```

### 2. **chinese_translation** (可选)
**用途**: 中文翻译参考，仅用于显示和参考  
**说明**: 此字段不会用于语音生成，仅作为参考信息

**支持的字段名变体**:
```
chinese_translation, Chinese Translation, chinese, Chinese
translation, Translation, 中文翻译, 翻译, chinese_text, Chinese Text
Chinese Content, chinese_content, 中文内容, 中文
Chinese Text, chinese_text, 中文文本, 中文文案
Chinese Description, chinese_description, 中文描述, 描述
Chinese Copy, chinese_copy, 中文副本, 副本
Chinese Scripts, chinese_scripts, 中文脚本, 脚本
Chinese Prompts, chinese_prompts, 中文提示, 提示
Chinese Messages, chinese_messages, 中文消息, 消息
Chinese Posts, chinese_posts, 中文帖子, 帖子
Chinese Ads, chinese_ads, 中文广告, 广告
Chinese Marketing, chinese_marketing, 中文营销, 营销
Chinese Sales, chinese_sales, 中文销售, 销售
Chinese Copywriting, chinese_copywriting, 中文文案, 文案
Chinese Headlines, chinese_headlines, 中文标题, 标题
Chinese Taglines, chinese_taglines, 中文标语, 标语
Chinese Slogans, chinese_slogans, 中文口号, 口号
Chinese Captions, chinese_captions, 中文说明, 说明
Chinese Descriptions, chinese_descriptions, 中文描述, 描述
Chinese Titles, chinese_titles, 中文标题, 标题
Chinese Subtitles, chinese_subtitles, 中文副标题, 副标题
Chinese Body, chinese_body, 中文正文, 正文
Chinese Main, chinese_main, 中文主要, 主要
Chinese Primary, chinese_primary, 中文主要, 主要
Chinese Core, chinese_core, 中文核心, 核心
Chinese Key, chinese_key, 中文关键, 关键
Chinese Essential, chinese_essential, 中文必要, 必要
Chinese Important, chinese_important, 中文重要, 重要
```

---

## 🎵 声音参数配置

### A3标准情绪配置

系统支持12种情绪类型，每种情绪都有对应的声音参数：

| 情绪类型 | 语速(rate) | 音调(pitch) | 音量(volume) | 风格(style) | 适用产品 |
|---------|-----------|------------|------------|-----------|---------|
| **Excited** | +15% | +12% | +15% | cheerful | 新品/促销 |
| **Confident** | +8% | +5% | +8% | assertive | 高端/科技 |
| **Empathetic** | -12% | -8% | -10% | friendly | 护肤/健康 |
| **Calm** | -10% | -3% | 0% | soothing | 家居/教育 |
| **Playful** | +18% | +15% | +5% | friendly | 美妆/时尚 |
| **Urgent** | +22% | +8% | +18% | serious | 限时/秒杀 |
| **Authoritative** | +5% | +3% | +10% | serious | 投资/专业 |
| **Friendly** | +12% | +8% | +5% | friendly | 日用/社群 |
| **Inspirational** | +10% | +10% | +12% | cheerful | 自提升/健身 |
| **Serious** | 0% | 0% | +5% | serious | 金融/公告 |
| **Mysterious** | -8% | +5% | -5% | serious | 预告/悬念 |
| **Grateful** | +5% | +8% | +8% | friendly | 感谢/复购 |

### 动态参数生成

系统会根据A3标准自动生成动态参数：

1. **语速动态调整**: 基于正弦波和随机噪声
2. **音调动态调整**: 基于斐波那契序列和对数扰动
3. **音量动态调整**: 基于素数序列和余弦波

### 语音选择

**默认语音**: `en-US-JennyNeural` (美式英语，女性)

**其他可用语音**:
- `en-US-GuyNeural` (美式英语，男性)
- `en-US-AriaNeural` (美式英语，女性)
- `en-US-DavisNeural` (美式英语，男性)
- `en-US-JaneNeural` (美式英语，女性)
- `en-US-JasonNeural` (美式英语，男性)
- `en-US-NancyNeural` (美式英语，女性)
- `en-US-RogerNeural` (美式英语，男性)
- `en-US-SaraNeural` (美式英语，女性)
- `en-US-TonyNeural` (美式英语，男性)

---

## 📁 支持的文件格式

### Excel格式
- `.xlsx` - Excel 2007+格式 (推荐)
- `.xls` - Excel 97-2003格式

### 文本格式
- `.csv` - 逗号分隔值
- `.tsv` - 制表符分隔值
- `.txt` - 纯文本表格 (Markdown表格或空格分隔)

---

## 🎯 产品名称识别

系统会从文件名中自动提取产品名称，支持以下模式：

1. **标准模式**: `产品名_数量.xlsx`
2. **GPTs模式**: `GPTs-产品名_数量.xlsx`
3. **日期模式**: `产品名_日期_数量.xlsx`
4. **复杂模式**: `产品名_描述_数量.xlsx`

**示例**:
- `Lior2025-10-23淡化美白美容霜腋下和大腿黑斑霜_800合并模板.xlsx`
- `GPTs-新品推广_100.xlsx`
- `护肤产品_2025-10-27_50.xlsx`

---

## 🔧 情绪自动匹配

系统会根据产品名称中的关键词自动选择情绪：

| 关键词 | 推荐情绪 | 说明 |
|-------|---------|------|
| 新品, 促销, 限时, 秒杀 | Excited | 兴奋激动 |
| 高端, 科技, 专业 | Confident | 自信权威 |
| 护肤, 健康, 美容 | Empathetic | 温和体贴 |
| 家居, 教育, 学习 | Calm | 平静舒缓 |
| 美妆, 时尚, 潮流 | Playful | 活泼有趣 |
| 投资, 金融, 公告 | Serious | 严肃正式 |
| 预告, 悬念, 神秘 | Mysterious | 神秘吸引 |
| 感谢, 复购, 回馈 | Grateful | 感恩感谢 |

---

## 📝 Excel文件示例

### 标准格式示例
```excel
| english_script | chinese_translation |
|----------------|-------------------|
| Welcome to our new skincare line! | 欢迎来到我们的新护肤系列！ |
| Experience the power of natural ingredients. | 体验天然成分的力量。 |
| Transform your skin in just 7 days. | 仅需7天改变您的肌肤。 |
```

### GPTs生成格式示例
```excel
| English Content | Chinese Content |
|----------------|----------------|
| Discover the secret to radiant skin! | 发现光彩肌肤的秘密！ |
| Our advanced formula works overnight. | 我们的先进配方整夜工作。 |
| Join thousands of satisfied customers. | 加入数千名满意的客户。 |
```

---

## ⚙️ 系统处理流程

1. **文件上传**: 支持拖拽或点击上传
2. **格式检测**: 自动识别文件格式和编码
3. **字段映射**: 智能匹配字段名到标准字段
4. **产品识别**: 从文件名提取产品名称
5. **情绪匹配**: 根据产品关键词选择情绪
6. **参数生成**: 应用A3标准动态参数
7. **语音合成**: 使用EdgeTTS生成音频
8. **文件输出**: 保存到指定目录

---

## 🎯 最佳实践建议

### 1. 文件命名
- 使用描述性的产品名称
- 包含数量信息便于管理
- 避免特殊字符和空格

### 2. 内容质量
- 确保英文脚本语法正确
- 内容长度适中 (建议50-200字符)
- 避免过于复杂的句子结构

### 3. 批量处理
- 单次处理建议不超过1000条
- 大量数据建议分批处理
- 定期检查生成结果

### 4. 情绪选择
- 根据产品特性选择合适情绪
- 考虑目标受众的偏好
- 保持品牌调性一致

---

## 🔍 故障排除

### 常见问题

1. **字段识别失败**
   - 检查字段名是否在支持列表中
   - 确保字段名拼写正确
   - 尝试使用标准字段名

2. **产品名称提取失败**
   - 检查文件名格式
   - 确保包含产品关键词
   - 避免过于复杂的文件名

3. **情绪匹配不准确**
   - 在产品名称中添加关键词
   - 手动指定情绪类型
   - 检查情绪配置

4. **音频生成失败**
   - 检查网络连接
   - 确保TTS服务正常运行
   - 查看错误日志

---

## 📞 技术支持

如有问题，请检查：
1. 系统日志文件
2. 错误提示信息
3. 文件格式和内容
4. 网络连接状态

---

*文档更新时间: 2025-10-27*  
*版本: v1.0*  
*适用系统: TT-Live-AI语音生成系统*
