# TT-Live-AI A3-TK
## 🚀 快速启动
### 1. 安装依赖
```bash
pip install -r requirements.txt
```
### 2. 启动服务
```bash
python run_tts.py
```
### 3. 测试接口
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
        "product_name": "Acne Patch",
        "discount": "20% OFF",
        "scripts": [
          {"english_script": "This patch clears pimples overnight!", "emotion": "Excited"},
          {"english_script": "Gentle, effective, and invisible!", "emotion": "Friendly"}
        ]
      }'
```

### 4. 健康检查
```bash
curl http://localhost:5000/health
```

### 5. 系统状态
```bash
curl http://localhost:5000/status
```

## 📁 项目结构

```
TT_Live_AI_TTS/
├── run_tts.py               # Flask 主服务
├── batch_tts.py             # 批量 Excel 处理
├── start_ngrok.py           # ngrok 公网映射
├── requirements.txt         # Python 依赖
├── .env                     # 配置文件
├── input/                   # 输入 Excel 文件
├── outputs/                 # 输出音频和 Excel
└── logs/                    # 日志文件
```

## 🎚️ 语音参数映射

| 情绪 | 语速 | 音调 | 音量 |
|------|------|------|------|
| Calm | -6% | -2% | 0dB |
| Friendly | +2% | +2% | 0dB |
| Confident | +4% | +1% | +1dB |
| Playful | +6% | +3% | +1dB |
| Excited | +10% | +4% | +2dB |
| Urgent | +12% | +3% | +2dB |

## 🔗 API 接口

### POST /generate
生成语音内容

**请求示例:**
```json
{
  "product_name": "Dark Spot Patch",
  "discount": "Buy 2 Get 1 Free",
  "scripts": [
    {"english_script": "Hey bestie, this patch really works!", "emotion": "Excited"},
    {"english_script": "Gentle and fast, this patch is amazing.", "emotion": "Confident"}
  ]
}
```

**响应示例:**
```json
{
  "product_name": "Dark Spot Patch",
  "total_scripts": 2,
  "output_excel": "outputs/Dark_Spot_Patch/Lior_2025-10-25_Dark_Spot_Patch_Batch1_Voice.xlsx",
  "audio_directory": "outputs/Dark_Spot_Patch/",
  "sample_audios": [
    "outputs/Dark_Spot_Patch/tts_0001_Excited.mp3",
    "outputs/Dark_Spot_Patch/tts_0002_Confident.mp3"
  ],
  "summary": {
    "successful": 2,
    "failed": 0,
    "duration_seconds": 5.2
  }
}
```

## 🌐 公网映射

### 启动 ngrok 映射
```bash
python start_ngrok.py
```

### 配置 ngrok token
在 `.env` 文件中设置:
```
NGROK_TOKEN=your_ngrok_token_here
```

## 📊 批量处理

### 处理 Excel 文件
```bash
python batch_tts.py
```

### 创建示例 Excel
```bash
python -c "from batch_tts import create_sample_excel; create_sample_excel()"
```

## 🎯 集成 GPTs

1. 启动服务: `python run_tts.py`
2. 启动映射: `python start_ngrok.py`
3. 获取公网地址
4. 配置 GPTs Actions 使用该地址
5. 测试完整流程

## 📝 日志

- 服务日志: `logs/tts_service.log`
- 批量处理日志: `logs/batch_tts.log`
- ngrok 日志: `logs/ngrok.log`

## 🔧 配置

在 `.env` 文件中配置:
- `MAX_CONCURRENT`: 最大并发数 (默认: 5)
- `DEFAULT_VOICE`: 默认语音模型
- `OUTPUT_DIR`: 输出目录
- `LOG_DIR`: 日志目录
