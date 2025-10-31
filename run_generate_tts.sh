#!/bin/zsh
set -euo pipefail

ROOT_DIR="/Volumes/M2/TT_Live_AI_TTS/18_批量输入_批量文件输入目录"
# 新的输出根目录（保持与之前相同的内部结构）
OUT_DIR="/Volumes/M2/TT_Live_AI_TTS/20.1_输出文件_处理完成的音频文件"

# 配置参数（可按需修改）
# 方案1：全批次固定一个 voice（默认）
VOICE="en-US-NancyNeural"

# 方案2（可选）：为每个 XLSX 按顺序轮换 voice 列表（开启请把上面 VOICE 注释掉，并取消 VOICES 注释）
# VOICES=(
#   "en-US-JennyNeural"
#   "en-US-AriaNeural"
#   "en-US-DavisNeural"
# )
RATE="0%"      # 负值示例：-25%
VOLUME="0%"    # 负值示例：-10%
PITCH="0Hz"    # 负值示例：-50Hz
SIL_MS=600

SCRIPT="/Volumes/M2/TT_Live_AI_TTS/generate_tts_from_xlsx.py"

echo "输出目录: $OUT_DIR"
mkdir -p "$OUT_DIR"

idx=0
for f in "$ROOT_DIR"/*.xlsx; do
  echo "处理: $f"

  use_voice="$VOICE"
  if [ -z "${use_voice:-}" ] && [ -n "${VOICES:-}" ]; then
    # 若未设置 VOICE 而设置了 VOICES 数组，则按文件顺序轮换
    use_voice=${VOICES[$(( (idx % ${#VOICES[@]}) + 1 ))]}
  fi

  python3 "$SCRIPT" "$f" \
    --out "$OUT_DIR" \
    --voice "$use_voice" \
    --rate="$RATE" \
    --volume="$VOLUME" \
    --pitch="$PITCH" \
    --silence-ms "$SIL_MS"

  idx=$((idx+1))
done

echo "全部完成。"


