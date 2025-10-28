# EdgeTTS Web API

基于 EdgeTTS 的语音合成 Web API，支持 GPTs 插件调用。

## 功能特性

- 🎵 **单个语音生成**: 将文本转换为高质量语音文件
- 📦 **批量处理**: 支持批量生成多个语音文件
- 🎭 **多情绪支持**: 支持 6 种情绪模式（Calm, Friendly, Confident, Playful, Excited, Urgent）
- 🗣️ **多语音模型**: 支持多种语言和语音模型
- 📊 **Excel 报告**: 自动生成处理结果报告
- 🔌 **GPTs 插件**: 完全兼容 GPTs 插件协议

## API 接口

### 单个语音生成
```bash
POST /generate
Content-Type: application/json

{
  "text": "Hello, this is a test message.",
  "voice": "en-US-JennyNeural",
  "emotion": "Friendly",
  "format": "mp3"
}
```

### 批量语音生成
```bash
POST /batch
Content-Type: application/json

{
  "texts": ["Hello world", "This is a test", "Another message"],
  "voice": "en-US-JennyNeural",
  "emotion": "Friendly",
  "format": "mp3"
}
```

### 健康检查
```bash
GET /health
```

### 获取支持的语音列表
```bash
GET /voices
```

## 支持的语音模型

### 英语
- `en-US-JennyNeural` (女性)
- `en-US-GuyNeural` (男性)
- `en-US-AriaNeural` (女性)
- `en-US-DavisNeural` (男性)
- `en-US-EmmaNeural` (女性)
- `en-US-BrandonNeural` (男性)

### 中文
- `zh-CN-XiaoxiaoNeural` (女性)
- `zh-CN-YunyangNeural` (男性)
- `zh-CN-YunxiNeural` (男性)

## 支持的情绪

- **Calm**: 平静、舒缓
- **Friendly**: 友好、亲切
- **Confident**: 自信、坚定
- **Playful**: 活泼、有趣
- **Excited**: 兴奋、激动
- **Urgent**: 紧急、紧迫

## 本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

3. 测试 API：
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"测试语音","voice":"zh-CN-XiaoxiaoNeural"}' \
  --output test.mp3
```

## 部署到 Cloudflare Pages

1. 推送代码到 GitHub
2. 在 Cloudflare Pages 中连接 GitHub 仓库
3. 配置构建命令：`pip install -r requirements.txt`
4. 部署完成后访问：`https://your-domain.pages.dev`

## GPTs 插件配置

在 GPTs 中添加插件时，使用以下 URL：
```
https://your-domain.com/.well-known/ai-plugin.json
```

## 许可证

MIT License
