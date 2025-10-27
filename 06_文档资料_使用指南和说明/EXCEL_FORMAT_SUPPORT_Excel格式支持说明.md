# Excel格式支持说明

## 📋 支持的文件格式

### 1. Excel文件
- **.xlsx** - Excel 2007+ 格式
- **.xls** - Excel 97-2003 格式

### 2. 文本文件
- **.csv** - 逗号分隔值文件 (UTF-8编码)
- **.tsv** - 制表符分隔值文件 (UTF-8编码)
- **.txt** - 文本文件（支持Markdown表格和纯文本表格）

### 3. GPTs生成的文件格式
- **Markdown表格** - GPTs常用的表格格式
- **纯文本表格** - 空格或制表符分隔的文本
- **多种编码** - 自动检测UTF-8、GBK、GB2312、Latin1编码

## 🔍 支持的字段变体

### 英文文案字段 (必需)
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

### 中文翻译字段 (可选)
系统会自动识别以下字段名变体：
- `chinese_translation`
- `Chinese Translation`
- `chinese`
- `Chinese`
- `translation`
- `Translation`
- `中文翻译`
- `翻译`
- `chinese_text`
- `Chinese Text`

## 📝 文件名解析规则

系统支持多种文件名格式来提取产品名称：

### 1. 日期_产品名_数字
- `2025-10-27美白产品_800.xlsx` → 产品名: `美白产品`
- `2025-10-27Dark Spot Patch_800.xlsx` → 产品名: `Dark Spot Patch`

### 2. 日期_产品名_合并
- `2025-10-27美白产品_合并.xlsx` → 产品名: `美白产品`

### 3. 日期_产品名_模板
- `2025-10-27美白产品_模板.xlsx` → 产品名: `美白产品`

### 4. 产品名_日期
- `美白产品_2025-10-27.xlsx` → 产品名: `美白产品`

### 5. 产品名_数字
- `美白产品_800.xlsx` → 产品名: `美白产品`

### 6. 产品名_合并
- `美白产品_合并.xlsx` → 产品名: `美白产品`

### 7. 产品名_模板
- `美白产品_模板.xlsx` → 产品名: `美白产品`

## 🎯 自动情绪选择

系统会根据产品名称中的关键词自动选择合适的情绪：

### 美白/淡斑类产品
- 关键词: `美白`, `淡斑`, `亮白`, `brightening`, `whitening`
- 自动选择情绪: `Excited`

### 保湿/滋润类产品
- 关键词: `保湿`, `滋润`, `moisturizing`, `hydrating`
- 自动选择情绪: `Calm`

### 抗老/紧致类产品
- 关键词: `抗老`, `紧致`, `anti-aging`, `firming`
- 自动选择情绪: `Confident`

## ✅ A3标准合规检查

系统会自动检查以下合规项目：

1. **情绪有效性** - 检查选择的情绪是否符合A3标准
2. **语音有效性** - 检查语音模型是否有效
3. **文案长度** - 检查文案长度是否在50-1000字符范围内
4. **产品名称提取** - 检查是否成功从文件名提取产品名称
5. **文件格式支持** - 检查文件格式是否受支持
6. **字段映射** - 检查是否成功映射字段名

## 📊 使用示例

### 示例1: 标准Excel文件
```excel
English Script                    | Chinese Translation
----------------------------------|-------------------
Transform your skin with our...   | 用我们的革命性产品...
Say goodbye to dark spots...      | 告别黑斑...
```

### 示例2: CSV文件
```csv
script,translation
"Transform your skin with our...","用我们的革命性产品..."
"Say goodbye to dark spots...","告别黑斑..."
```

### 示例3: TSV文件
```tsv
english	chinese
Transform your skin with our...	用我们的革命性产品...
Say goodbye to dark spots...	告别黑斑...
```

### 示例4: 中文字段名
```excel
文案                    | 翻译
----------------------|-------------------
Transform your skin...| 用我们的革命性产品...
Say goodbye to dark...| 告别黑斑...
```

## 🔧 错误处理

如果文件解析失败，系统会返回详细的错误信息：

- **文件格式不支持**: 显示支持的文件格式列表
- **字段缺失**: 显示可用字段和支持的字段变体
- **文件为空**: 提示文件内容为空
- **编码问题**: 自动尝试不同编码格式

## 🚀 最佳实践

1. **文件命名**: 使用标准格式 `日期_产品名_数字.xlsx`
2. **字段命名**: 使用标准字段名 `english_script` 和 `chinese_translation`
3. **编码格式**: CSV/TSV文件使用UTF-8编码
4. **内容长度**: 确保文案长度在50-1000字符之间
5. **产品名称**: 在文件名中包含清晰的产品名称

## 📈 性能优化

- 支持大文件处理
- 自动编码检测
- 智能字段映射
- 批量处理优化
- 内存使用优化
