#!/bin/bash
# EdgeTTS 剩余时间统计器

cd /Volumes/M2/TT_Live_AI_TTS

# 获取当前统计
total_count=$(find 20_输出文件_处理完成的音频文件/ -name "*.mp3" | wc -l)
target_total=35200
remaining_files=$((target_total - total_count))
progress=$(echo "scale=2; $total_count * 100 / $target_total" | bc)

echo "📊 EdgeTTS 剩余时间统计"
echo "=========================================="
echo "🕐 当前时间: $(date)"
echo ""
echo "📈 进度统计:"
echo "🎵 已生成: $total_count 个音频文件"
echo "🎯 目标总数: $target_total 个"
echo "📊 完成进度: $progress%"
echo "📅 剩余文件: $remaining_files 个"
echo ""

# 计算处理速度
if [ $total_count -gt 0 ]; then
    # 获取启动时间
    if [ -f "/tmp/edgetts_start_time" ]; then
        start_time=$(cat /tmp/edgetts_start_time)
    else
        start_time=$(date +%s)
        echo $start_time > /tmp/edgetts_start_time
    fi
    
    current_time=$(date +%s)
    elapsed_seconds=$((current_time - start_time))
    elapsed_minutes=$((elapsed_seconds / 60))
    
    if [ $elapsed_seconds -gt 0 ]; then
        rate=$(echo "scale=2; $total_count * 60 / $elapsed_seconds" | bc)
        echo "⚡ 处理速度: $rate 个/分钟"
        echo "⏱️  已运行时间: ${elapsed_minutes} 分钟"
        
        if [ $(echo "$rate > 0" | bc) -eq 1 ]; then
            # 计算剩余时间
            remaining_minutes=$(echo "scale=0; $remaining_files / $rate" | bc)
            remaining_hours=$((remaining_minutes / 60))
            remaining_mins=$((remaining_minutes % 60))
            
            echo ""
            echo "⏳ 剩余时间统计:"
            echo "📅 剩余文件: $remaining_files 个"
            echo "⏰ 剩余时间: ${remaining_hours}小时${remaining_mins}分钟"
            
            # 计算预计完成时间
            completion_timestamp=$((current_time + remaining_minutes * 60))
            completion_time=$(date -r $completion_timestamp "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "@$completion_timestamp" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "无法计算")
            echo "🎯 预计完成: $completion_time"
            
            # 计算各时间段的预计进度
            echo ""
            echo "📅 预计进度时间表:"
            echo "----------------------------------------"
            for hours in 1 2 3 4 5 6 7 8; do
                future_count=$(echo "scale=0; $total_count + $rate * $hours * 60" | bc)
                future_count_int=$(echo "$future_count" | cut -d. -f1)
                if [ $future_count_int -lt $target_total ]; then
                    future_progress=$(echo "scale=1; $future_count * 100 / $target_total" | bc)
                    future_timestamp=$((current_time + hours * 3600))
                    future_time=$(date -r $future_timestamp "+%H:%M" 2>/dev/null || date -d "@$future_timestamp" "+%H:%M" 2>/dev/null || echo "无法计算")
                    echo "${hours}小时后 ($future_time): $future_count_int 个文件 ($future_progress%)"
                fi
            done
        fi
    fi
fi

echo ""
echo "=========================================="
