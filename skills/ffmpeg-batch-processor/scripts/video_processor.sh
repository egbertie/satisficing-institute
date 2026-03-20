#!/bin/bash
# FFmpeg Video Processor - Main Script
# 视频处理主控脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPERATION="${1:-help}"
INPUT="${2:-}"

show_help() {
    cat << EOF
FFmpeg Video Processor

Usage: $0 [operation] [input] [options]

Operations:
  cut [input] --start TIME --end TIME    Cut video segment
  convert [input] [format]               Convert format
  compress [input] [--quality N]         Compress video
  resize [input] [WIDTHxHEIGHT]          Resize video
  extract-audio [input] [format]         Extract audio
  remove-audio [input]                   Remove audio track
  speed [input] [factor]                 Change speed (0.5-2.0)
  gif [input] --start TIME --duration N  Create GIF
  screenshot [input] [TIME]              Capture frame
  watermark [input] [logo.png]           Add watermark

Examples:
  $0 cut video.mp4 --start 00:01:21 --end 00:01:35
  $0 convert video.avi mp4
  $0 compress video.mp4 --quality 23
  $0 resize video.mp4 1920x1080

EOF
}

# 解析参数
shift 2 || true
START_TIME=""
END_TIME=""
QUALITY=23
DURATION=""
LOGO=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --start)
            START_TIME="$2"
            shift 2
            ;;
        --end)
            END_TIME="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --quality)
            QUALITY="$2"
            shift 2
            ;;
        *)
            EXTRA_ARG="$1"
            shift
            ;;
    esac
done

# 检查输入文件
if [ -n "$INPUT" ] && [ ! -f "$INPUT" ]; then
    echo "❌ 错误: 找不到输入文件 '$INPUT'"
    exit 1
fi

# 生成输出文件名
generate_output() {
    local input="$1"
    local suffix="$2"
    local ext="$3"
    local base=$(basename "$input" | sed 's/\.[^.]*$//')
    echo "${base}_${suffix}.${ext}"
}

case "$OPERATION" in
    cut)
        if [ -z "$START_TIME" ] || [ -z "$END_TIME" ]; then
            echo "❌ 错误: 剪切操作需要 --start 和 --end 参数"
            exit 1
        fi
        OUTPUT=$(generate_output "$INPUT" "trimmed" "mp4")
        echo "✂️  剪切视频: $INPUT ($START_TIME 到 $END_TIME)"
        ffmpeg -y -hide_banner -i "$INPUT" -ss "$START_TIME" -to "$END_TIME" -c copy "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        ;;
    
    convert)
        FORMAT="${EXTRA_ARG:-mp4}"
        OUTPUT=$(generate_output "$INPUT" "converted" "$FORMAT")
        echo "🔄 转换格式: $INPUT → $FORMAT"
        
        case "$FORMAT" in
            mp4)
                ffmpeg -y -hide_banner -i "$INPUT" -c:v libx264 -c:a aac "$OUTPUT"
                ;;
            mkv)
                ffmpeg -y -hide_banner -i "$INPUT" -c copy "$OUTPUT"
                ;;
            webm)
                ffmpeg -y -hide_banner -i "$INPUT" -c:v libvpx-vp9 -c:a libopus "$OUTPUT"
                ;;
            *)
                ffmpeg -y -hide_banner -i "$INPUT" "$OUTPUT"
                ;;
        esac
        echo "✅ 输出: $OUTPUT"
        ;;
    
    compress)
        OUTPUT=$(generate_output "$INPUT" "compressed" "mp4")
        echo "🗜️  压缩视频: $INPUT (CRF=$QUALITY)"
        ffmpeg -y -hide_banner -i "$INPUT" -c:v libx264 -crf "$QUALITY" -preset medium -c:a aac -b:a 128k "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        
        # 显示大小对比
        ORIG_SIZE=$(du -h "$INPUT" | cut -f1)
        NEW_SIZE=$(du -h "$OUTPUT" | cut -f1)
        echo "📊 文件大小: $ORIG_SIZE → $NEW_SIZE"
        ;;
    
    resize)
        RESOLUTION="${EXTRA_ARG:-1280x720}"
        OUTPUT=$(generate_output "$INPUT" "resized" "mp4")
        WIDTH=$(echo "$RESOLUTION" | cut -d'x' -f1)
        HEIGHT=$(echo "$RESOLUTION" | cut -d'x' -f2)
        echo "📐 调整分辨率: $INPUT → ${WIDTH}x${HEIGHT}"
        ffmpeg -y -hide_banner -i "$INPUT" -vf "scale=${WIDTH}:${HEIGHT}" -c:a copy "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        ;;
    
    extract-audio)
        FORMAT="${EXTRA_ARG:-mp3}"
        OUTPUT=$(generate_output "$INPUT" "audio" "$FORMAT")
        echo "🎵 提取音频: $INPUT → $FORMAT"
        
        case "$FORMAT" in
            mp3)
                CODEC="libmp3lame"
                ;;
            aac)
                CODEC="aac"
                ;;
            wav)
                CODEC="pcm_s16le"
                ;;
            flac)
                CODEC="flac"
                ;;
            *)
                CODEC="copy"
                ;;
        esac
        
        ffmpeg -y -hide_banner -i "$INPUT" -vn -acodec "$CODEC" "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        ;;
    
    remove-audio)
        OUTPUT=$(generate_output "$INPUT" "silent" "mp4")
        echo "🔇 移除音频: $INPUT"
        ffmpeg -y -hide_banner -i "$INPUT" -an -c:v copy "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        ;;
    
    speed)
        FACTOR="${EXTRA_ARG:-1.5}"
        OUTPUT=$(generate_output "$INPUT" "${FACTOR}x" "mp4")
        echo "⚡ 调整速度: $INPUT → ${FACTOR}x"
        
        # 计算视频和音频参数
        PTS_FACTOR=$(awk "BEGIN {printf \"%.2f\", 1/$FACTOR}")
        
        ffmpeg -y -hide_banner -i "$INPUT" \
            -filter_complex "[0:v]setpts=${PTS_FACTOR}*PTS[v];[0:a]atempo=$FACTOR[a]" \
            -map "[v]" -map "[a]" "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        ;;
    
    gif)
        if [ -z "$START_TIME" ]; then
            START_TIME="00:00:00"
        fi
        if [ -z "$DURATION" ]; then
            DURATION=5
        fi
        OUTPUT=$(generate_output "$INPUT" "gif" "gif")
        echo "🎞️  生成GIF: $INPUT (从 $START_TIME, 持续 ${DURATION}s)"
        ffmpeg -y -hide_banner -i "$INPUT" -ss "$START_TIME" -t "$DURATION" \
            -vf "fps=15,scale=480:-1:flags=lanczos" -loop 0 "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        ;;
    
    screenshot)
        TIME="${EXTRA_ARG:-00:00:01}"
        OUTPUT=$(generate_output "$INPUT" "screenshot" "jpg")
        echo "📸 截图: $INPUT @ $TIME"
        ffmpeg -y -hide_banner -i "$INPUT" -ss "$TIME" -frames:v 1 "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        ;;
    
    watermark)
        LOGO="${EXTRA_ARG:-logo.png}"
        if [ ! -f "$LOGO" ]; then
            echo "❌ 错误: 找不到水印图片 '$LOGO'"
            exit 1
        fi
        OUTPUT=$(generate_output "$INPUT" "watermarked" "mp4")
        echo "🏷️  添加水印: $INPUT + $LOGO"
        ffmpeg -y -hide_banner -i "$INPUT" -i "$LOGO" \
            -filter_complex "overlay=W-w-10:10" "$OUTPUT"
        echo "✅ 输出: $OUTPUT"
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        echo "❌ 未知操作: $OPERATION"
        show_help
        exit 1
        ;;
esac
