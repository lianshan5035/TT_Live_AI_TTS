# 01_核心程序_FFmpeg音频处理器

## 文件夹说明
这个文件夹包含FFmpeg音频处理的核心程序文件。

## 文件内容
- `ffmpeg_audio_processor.py` - FFmpeg音频处理器主程序
- `ffmpeg_multi_instance_processor.py` - 多实例处理器（需要psutil）
- `ffmpeg_multi_instance_simple.py` - 简化多实例处理器（无需额外依赖）
- `background_sounds/` - 背景音效文件存储目录

## 功能说明
- 音频混合处理
- 白噪音添加
- 背景音效混合
- 多实例并行处理
- 支持多种音频格式

## 使用场景
- TikTok直播音频处理
- 批量音频文件处理
- 音频质量优化
- 背景音效添加
