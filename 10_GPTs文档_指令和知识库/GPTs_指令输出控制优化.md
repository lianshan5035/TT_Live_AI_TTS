# GPTs指令输出控制优化指南

## 🎯 目标
确保GPTs的输出能够完美配合TTS服务，实现端到端的语音生成流程。

## 📋 GPTs输出格式要求

### 1. **Excel文件结构**
GPTs必须输出包含以下字段的Excel文件：

#### 必需字段
- `english_script`: 英文语音脚本（50-1000字符）
- `chinese_translation`: 中文翻译（参考用）

#### 可选TTS参数字段
- `emotion`: 情绪类型（12种A3标准情绪之一）
- `voice`: 语音模型（推荐en-US-JennyNeural）
- `rate`: 语速参数（-50%到+200%）
- `pitch`: 音调参数（-50Hz到+50Hz）
- `volume`: 音量参数（-50%到+50%）
- `style`: 语调风格（cheerful/friendly/serious/soothing/assertive）
- `products`: 适用产品类型

### 2. **A3标准12种情绪**
```
Excited: 新品/促销 - 兴奋激动
Confident: 高端/科技 - 自信专业
Empathetic: 护肤/健康 - 共情温暖
Calm: 家居/教育 - 平静舒缓
Playful: 美妆/时尚 - 活泼有趣
Urgent: 限时/秒杀 - 紧急紧迫
Authoritative: 投资/专业 - 权威专业
Friendly: 日用/社群 - 友好亲切
Inspirational: 自提升/健身 - 激励鼓舞
Serious: 金融/公告 - 严肃正式
Mysterious: 预告/悬念 - 神秘悬念
Grateful: 感谢/复购 - 感恩感谢
```

### 3. **文件名规范**
- 格式：`产品名称_数量_合并模板.xlsx`
- 示例：`Lior2025-10-23淡化美白美容霜腋下和大腿黑斑霜_800合并模板.xlsx`
- 产品名称会自动提取用于情绪匹配

## 🔧 GPTs指令模板

### 基础指令模板
```
你是一个专业的语音脚本生成助手，需要为TTS语音生成服务创建Excel文件。

输出要求：
1. 创建Excel文件，包含以下列：
   - english_script: 英文语音脚本（50-1000字符）
   - chinese_translation: 中文翻译
   - emotion: 情绪类型（从12种A3标准情绪中选择）
   - voice: 语音模型（推荐en-US-JennyNeural）
   - rate: 语速参数（-50%到+200%）
   - pitch: 音调参数（-50Hz到+50Hz）
   - volume: 音量参数（-50%到+50%）

2. 根据产品类型自动选择合适情绪：
   - 新品/促销 → Excited
   - 高端/科技 → Confident
   - 护肤/健康 → Empathetic
   - 家居/教育 → Calm
   - 美妆/时尚 → Playful
   - 限时/秒杀 → Urgent
   - 投资/专业 → Authoritative
   - 日用/社群 → Friendly
   - 自提升/健身 → Inspirational
   - 金融/公告 → Serious
   - 预告/悬念 → Mysterious
   - 感谢/复购 → Grateful

3. 文件名格式：产品名称_数量_合并模板.xlsx

请为以下产品生成语音脚本：[产品描述]
```

### 高级指令模板（包含动态参数）
```
你是一个专业的语音脚本生成助手，需要为TTS语音生成服务创建Excel文件。

输出要求：
1. 创建Excel文件，包含以下列：
   - english_script: 英文语音脚本（50-1000字符）
   - chinese_translation: 中文翻译
   - emotion: 情绪类型（从12种A3标准情绪中选择）
   - voice: 语音模型（推荐en-US-JennyNeural）
   - rate: 语速参数（使用A3动态参数算法）
   - pitch: 音调参数（使用A3动态参数算法）
   - volume: 音量参数（使用A3动态参数算法）
   - style: 语调风格
   - products: 适用产品类型

2. A3动态参数算法：
   - 基础参数 + 动态变化
   - 使用正弦波、斐波那契数列、对数函数等数学算法
   - 确保每个脚本的参数都有细微差异

3. 情绪匹配规则：
   - 根据产品关键词自动选择情绪
   - 支持中英文关键词识别
   - 提供情绪说明和适用场景

4. 文件名格式：产品名称_数量_合并模板.xlsx

请为以下产品生成语音脚本：[产品描述]
```

## 📊 输出示例

### Excel文件示例
| english_script | chinese_translation | emotion | voice | rate | pitch | volume | style | products |
|---|---|---|---|---|---|---|---|---|
| "Discover the revolutionary skincare formula that transforms your skin in just 7 days!" | "发现革命性的护肤配方，仅需7天就能改变您的肌肤！" | Excited | en-US-JennyNeural | +15% | +12Hz | +15% | cheerful | 新品/促销 |
| "Our premium anti-aging serum uses advanced biotechnology to reduce fine lines and wrinkles." | "我们的高端抗衰老精华使用先进生物技术减少细纹和皱纹。" | Confident | en-US-JennyNeural | +8% | +5Hz | +8% | assertive | 高端/科技 |

## 🎨 情绪选择指南

### 产品类型 → 情绪映射
```
美容护肤 → Empathetic (共情温暖)
科技产品 → Confident (自信专业)
时尚美妆 → Playful (活泼有趣)
家居用品 → Calm (平静舒缓)
教育培训 → Calm (平静舒缓)
金融投资 → Authoritative (权威专业)
健康养生 → Empathetic (共情温暖)
运动健身 → Inspirational (激励鼓舞)
限时促销 → Urgent (紧急紧迫)
新品发布 → Excited (兴奋激动)
感谢回馈 → Grateful (感恩感谢)
官方公告 → Serious (严肃正式)
```

## 🔍 质量检查清单

### GPTs输出检查
- [ ] Excel文件包含所有必需字段
- [ ] 情绪类型符合A3标准12种情绪
- [ ] 语音脚本长度在50-1000字符之间
- [ ] 参数值在有效范围内
- [ ] 文件名格式正确
- [ ] 产品名称清晰可识别

### TTS服务兼容性检查
- [ ] 情绪参数格式正确（+15%, +12Hz, +15%）
- [ ] 语音模型名称有效
- [ ] 脚本内容适合语音合成
- [ ] 中文字符正确处理
- [ ] 特殊符号转义正确

## 🚀 优化建议

### 1. **GPTs指令优化**
- 明确输出格式要求
- 提供具体的字段说明
- 包含参数范围限制
- 给出情绪选择指导

### 2. **TTS服务增强**
- 支持更多GPTs字段
- 自动参数验证
- 错误处理和提示
- 批量处理优化

### 3. **端到端流程**
- 文件上传 → 解析 → 验证 → 生成
- 实时状态反馈
- 错误诊断和修复
- 结果预览和下载

## 📝 更新日志

### v1.0 (2025-10-27)
- 初始版本
- 基础GPTs指令模板
- A3标准12种情绪
- Excel输出格式规范

### v1.1 (2025-10-27)
- 增加动态参数算法
- 完善情绪选择指南
- 添加质量检查清单
- 优化端到端流程
