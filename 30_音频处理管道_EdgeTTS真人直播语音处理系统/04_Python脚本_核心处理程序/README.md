# 04_Python脚本_核心处理程序

## 📁 文件夹说明

此目录包含EdgeTTS真人直播语音处理系统的所有核心Python脚本，提供完整的音频处理功能。

## 🐍 脚本文件列表

### 🎛️ 规则管理脚本
- `rules_manager.py` - 完整规则管理器，支持命令行和交互式操作
- `quick_rules_editor.py` - 快速规则编辑器，提供图形化菜单界面
- `rules_loader.py` - 规则加载器，用于程序运行时加载配置

### 🎤 音频处理脚本
- `live_speech_analyzer.py` - 真人直播语音分析器
- `live_speech_generator.py` - 真人直播语音生成器
- `live_speech_test_case.py` - 测试案例执行脚本

### 🎧 辅助工具脚本
- `audio_listening_helper.py` - 音频试听助手
- `rule_usage_example.py` - 规则使用示例

## 🔧 脚本功能说明

### rules_manager.py
**功能**: 完整的规则管理系统
- 支持命令行操作
- 提供交互式界面
- 支持规则验证和备份
- 支持批量规则修改

**使用方法**:
```bash
python3 rules_manager.py interactive  # 交互式模式
python3 rules_manager.py list-rules   # 列出所有规则
python3 rules_manager.py validate     # 验证规则
```

### quick_rules_editor.py
**功能**: 快速规则编辑器
- 图形化菜单界面
- 中文提示和说明
- 实时参数验证
- 自动保存功能

**使用方法**:
```bash
python3 quick_rules_editor.py
```

### rules_loader.py
**功能**: 规则加载器
- 运行时加载配置
- 支持热重载
- 提供规则摘要
- 类型安全的数据访问

**使用方法**:
```python
from rules_loader import get_rules_loader
loader = get_rules_loader()
tempo_range = loader.get_tempo_range()
```

### live_speech_analyzer.py
**功能**: 真人直播语音分析器
- 分析真人直播语音特点
- 生成处理参数
- 创建对比音频
- 支持多种场景

**使用方法**:
```bash
python3 live_speech_analyzer.py
```

### live_speech_generator.py
**功能**: 真人直播语音生成器
- 支持多种直播场景
- 生成场景特定音频
- 批量处理功能
- 完整的对比音频集

**使用方法**:
```bash
python3 live_speech_generator.py
```

### live_speech_test_case.py
**功能**: 测试案例执行脚本
- 运行完整测试案例
- 生成测试报告
- 统计处理结果
- 创建对比音频

**使用方法**:
```bash
python3 live_speech_test_case.py
```

### audio_listening_helper.py
**功能**: 音频试听助手
- 自动扫描音频文件
- 提供试听建议
- 支持对比试听
- 交互式操作界面

**使用方法**:
```bash
python3 audio_listening_helper.py
```

### rule_usage_example.py
**功能**: 规则使用示例
- 展示规则使用方法
- 提供代码示例
- 演示参数调整
- 测试规则效果

**使用方法**:
```bash
python3 rule_usage_example.py
```

## 🚀 快速开始

### 1. 运行测试案例
```bash
python3 live_speech_test_case.py
```

### 2. 调整规则参数
```bash
python3 quick_rules_editor.py
```

### 3. 试听音频效果
```bash
python3 audio_listening_helper.py
```

### 4. 验证规则配置
```bash
python3 rules_manager.py validate
```

## 🔧 脚本依赖

### Python模块
- `json` - JSON配置文件处理
- `pathlib` - 文件路径操作
- `subprocess` - FFmpeg命令执行
- `logging` - 日志记录
- `random` - 随机参数生成
- `datetime` - 时间处理
- `click` - 命令行界面
- `tqdm` - 进度条显示

### 外部工具
- `FFmpeg` - 音频处理核心
- `ffprobe` - 音频信息获取

## 📊 脚本特点

### 功能特点
- **模块化设计**: 每个脚本功能独立
- **中文支持**: 完整的中文界面和提示
- **错误处理**: 完善的异常处理机制
- **日志记录**: 详细的处理日志
- **参数验证**: 自动验证输入参数

### 技术特点
- **面向对象**: 使用类和对象设计
- **类型提示**: 完整的类型注解
- **文档字符串**: 详细的函数说明
- **代码规范**: 遵循PEP8规范
- **可扩展性**: 易于扩展和修改

## 🎯 使用建议

### 新手用户
1. 先运行 `live_speech_test_case.py` 了解系统功能
2. 使用 `quick_rules_editor.py` 调整参数
3. 使用 `audio_listening_helper.py` 试听效果

### 高级用户
1. 使用 `rules_manager.py` 进行高级规则管理
2. 使用 `live_speech_generator.py` 批量生成音频
3. 使用 `rule_usage_example.py` 学习编程接口

### 开发者
1. 查看 `rules_loader.py` 了解规则加载机制
2. 参考 `live_speech_analyzer.py` 了解处理逻辑
3. 使用所有脚本了解完整系统架构

## 📞 技术支持

如果脚本运行遇到问题，请：
1. 检查Python版本和依赖模块
2. 确认FFmpeg安装和配置
3. 查看错误日志和提示信息
4. 参考文档资料了解使用方法

---

**注意**: 所有脚本都包含详细的中文注释和错误处理，建议按照使用建议逐步学习使用。
