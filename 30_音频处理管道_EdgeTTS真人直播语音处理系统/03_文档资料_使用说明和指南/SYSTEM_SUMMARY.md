# EdgeTTS音频处理规则管理系统 - 功能总结

## 🎯 系统概述

我已经为您创建了一个完整的EdgeTTS音频处理规则管理系统，这是一个可实时修改的配置系统，让您无需重新编译代码就能调整音频处理的各项参数。

## 📁 系统文件结构

```
audio_pipeline/
├── rules_config.json          # 主规则配置文件
├── rules_manager.py          # 完整规则管理器
├── quick_rules_editor.py     # 快速规则编辑器
├── rules_loader.py           # 规则加载器
├── rule_usage_example.py     # 使用示例
├── README_RULES.md          # 规则说明文档
└── USAGE_GUIDE.md          # 使用指南
```

## 🚀 核心功能

### 1. 📊 语速调整规则
- **基础范围**: `[0.88, 1.12]` - 基础语速调整范围 ±12%
- **语音类型调整**: 
  - 兴奋型：`[1.05, 1.15]` - 轻微加速
  - 平静型：`[0.95, 1.05]` - 保持正常
  - 严肃型：`[0.90, 1.00]` - 轻微减速
  - 友好型：`[1.00, 1.10]` - 轻微加速
- **时长调整**: 根据音频长度自动调整范围

### 2. 🎵 音高调整规则
- **基础范围**: `[-0.4, 0.4]` - 基础音高调整范围 ±0.4半音
- **语音类型调整**:
  - 兴奋型：`[0.1, 0.3]` - 轻微升调
  - 平静型：`[-0.1, 0.1]` - 保持原调
  - 严肃型：`[-0.3, -0.1]` - 轻微降调
  - 友好型：`[0.0, 0.2]` - 轻微升调
- **共振峰保持**: 使用Rubberband保持语音特征

### 3. 🌍 背景音效规则
- **添加概率**: `0.8` - 80%概率添加背景音效
- **音量范围**: `[0.15, 0.35]` - 不影响主语音
- **环境音效**:
  - 咖啡厅：`cafe_ambient.wav`
  - 办公室：`office_ambient.wav`
  - 客厅：`living_room.wav`
  - 户外：`outdoor_ambient.wav`
  - 房间底噪：`room_tone.wav`
- **淡入淡出**: 2秒淡入淡出时间

### 4. 🔊 事件音效规则
- **添加概率**: `0.15` - 15%概率触发事件音效
- **最大事件数**: `2` - 每个文件最多2个事件
- **事件类型**:
  - 键盘打字：`keyboard_typing.wav`
  - 倒水声：`water_pour.wav`
  - 脚步声：`footsteps.wav`
  - 椅子吱嘎：`chair_creak.wav`
  - 纸张摩擦：`paper_rustle.wav`
- **触发时间**: 在音频的20%-80%处触发

### 5. ⚡ 音频增强规则
- **动态压缩器**: 阈值-18dB，压缩比3:1
- **EQ调整**: 250Hz和3.5kHz频段增强
- **高通滤波器**: 80Hz截止频率
- **响度归一化**: I=-19, TP=-2, LRA=9

### 6. 📁 输出设置规则
- **输出格式**: `m4a` - TikTok推荐格式
- **编码器优先级**: `libfdk_aac` > `libmp3lame` > `aac`
- **比特率**: `192kbps` - 高质量音频
- **采样率**: `48kHz` - 专业级采样率
- **声道**: `2` - 立体声

### 7. 🔧 处理设置规则
- **最大并行数**: `4` - 平衡性能和资源使用
- **超时时间**: `600秒` - 10分钟超时
- **内存限制**: `2GB` - 防止内存溢出
- **临时目录**: `temp_processing` - 临时文件存储

### 8. 🎲 随机化规则
- **变化程度**: `medium` - 中等变化程度
- **种子模式**: `auto` - 自动随机种子
- **特征保持**: `true` - 保持语音特征

## 🛠️ 操作方式

### 1. 快速编辑器（推荐新手）
```bash
python3 quick_rules_editor.py
```
- 图形化菜单界面
- 中文提示
- 实时验证输入
- 自动保存

### 2. 完整规则管理器（推荐高级用户）
```bash
python3 rules_manager.py interactive
```
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

## 🔄 规则应用流程

1. **修改规则**: 使用编辑器或命令行修改规则
2. **保存规则**: 规则自动保存到 `rules_config.json`
3. **重新加载**: 音频处理程序会自动重新加载规则
4. **应用规则**: 新的音频处理会使用更新后的规则

## 📊 规则验证

系统会自动验证规则配置的完整性：
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
- 先调整一个参数
- 测试效果
- 再调整下一个参数

### 2. 备份重要配置
- 重大修改前先备份
- 定期备份规则配置

### 3. 验证修改
- 每次修改后验证配置
- 确保规则格式正确

### 4. 测试小批量
- 修改规则后先用小批量测试
- 确认效果满意后再大批量处理

## 🚨 常见问题解决

### Q: 修改规则后没有生效？
A: 确保规则已保存、程序重新启动、配置验证通过

### Q: 如何重置为默认规则？
A: 使用 `python3 rules_manager.py reset`

### Q: 规则文件损坏怎么办？
A: 从备份恢复：`python3 rules_manager.py restore rules_backup_xxx.json`

### Q: 如何查看所有可用规则？
A: 使用 `python3 rules_manager.py list-rules`

## 🔧 高级功能

### 1. 规则热重载
```python
from rules_loader import reload_rules
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

## 🎉 系统优势

1. **灵活性**: 实时修改处理参数，无需重新编译
2. **易用性**: 多种操作方式，适合不同用户
3. **可靠性**: 自动验证和备份机制
4. **可扩展性**: 模块化设计，易于扩展
5. **专业性**: 针对TikTok直播场景优化

## 📞 技术支持

如果遇到问题，请：
1. 检查规则配置是否正确
2. 查看错误日志
3. 尝试重置为默认规则
4. 联系技术支持

---

**总结**: 这个规则管理系统为您提供了完整的EdgeTTS音频处理参数控制能力，通过实时修改规则，您可以轻松调整音频处理效果，实现最佳的TikTok直播效果，有效避免AI检测为录播。
