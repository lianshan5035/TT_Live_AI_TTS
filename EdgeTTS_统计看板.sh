#!/bin/bash
# EdgeTTS 输出数量统计时间看板 - 自动刷新版本

cd /Volumes/M2/TT_Live_AI_TTS

while true; do
    clear
    echo "📊 EdgeTTS 输出数量统计时间看板"
    echo "=========================================="
    echo "🕐 当前时间: $(date)"
    echo ""
    
    # 总体统计
    echo "📈 总体统计:"
    total_count=$(find 20_输出文件_处理完成的音频文件/ -name "*.mp3" | wc -l)
    echo "🎵 总音频文件: $total_count 个"
    echo "🎯 目标总数: 35,200 个"
    progress=$(echo "scale=2; $total_count * 100 / 35200" | bc)
    echo "📊 完成进度: $progress%"
    
    # 计算剩余时间
    if [ $total_count -gt 0 ]; then
        remaining_files=$((35200 - total_count))
        echo "📅 剩余文件: $remaining_files 个"
        
        # 估算剩余时间 (基于当前处理速度)
        current_time=$(date +%s)
        if [ -f "/tmp/edgetts_start_time" ]; then
            start_time=$(cat /tmp/edgetts_start_time)
        else
            echo $current_time > /tmp/edgetts_start_time
            start_time=$current_time
        fi
        
        elapsed_seconds=$((current_time - start_time))
        if [ $elapsed_seconds -gt 0 ]; then
            rate=$(echo "scale=2; $total_count * 60 / $elapsed_seconds" | bc)
            echo "⚡ 生成速度: $rate 个/分钟"
            
            if [ $(echo "$rate > 0" | bc) -eq 1 ]; then
                remaining_minutes=$(echo "scale=0; $remaining_files / $rate" | bc)
                remaining_hours=$((remaining_minutes / 60))
                remaining_mins=$((remaining_minutes % 60))
                echo "⏳ 剩余时间: ${remaining_hours}小时${remaining_mins}分钟"
                
                # 计算预计完成时间
                completion_time=$(date -d "+${remaining_minutes} minutes" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -v+${remaining_minutes}M "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "无法计算")
                echo "⏰ 预计完成: $completion_time"
            fi
        fi
    fi
    echo ""
    
    # 各文件处理进度
    echo "📁 各文件处理进度:"
    echo "----------------------------------------"
    find 20_输出文件_处理完成的音频文件/ -type d -name "*全产品*" | while read dir; do
        file_name=$(basename "$dir")
        count=$(ls "$dir"/*.mp3 2>/dev/null | wc -l)
        progress=$(echo "scale=1; $count * 100 / 3200" | bc)
        voice=$(ls "$dir"/*.mp3 2>/dev/null | head -1 | xargs basename | sed 's/.*_\([^_]*\)\.mp3$/\1/')
        printf "%-25s | %4d 个 | %5.1f%% | %s\n" "$file_name" "$count" "$progress" "$voice"
    done | sort -k3 -nr
    echo ""
    
    # 语音分配统计
    echo "🎤 语音分配统计:"
    echo "----------------------------------------"
    find 20_输出文件_处理完成的音频文件/ -type d -name "*全产品*" | while read dir; do
        voice=$(ls "$dir"/*.mp3 2>/dev/null | head -1 | xargs basename | sed 's/.*_\([^_]*\)\.mp3$/\1/')
        echo "$voice"
    done | sort | uniq -c | sort -nr | while read count voice; do
        printf "%-35s | %d 个文件\n" "$voice" "$count"
    done
    echo ""
    
    echo "🔄 看板每30秒自动刷新 | 按 Ctrl+C 退出"
    echo "=========================================="
    
    sleep 30
done
