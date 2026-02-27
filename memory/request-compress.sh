#!/bin/bash
# 触发 AI 执行日志压缩
# 这个脚本会创建一个标记文件，AI 在 heartbeat 或下次对话时检测并执行

MARKER_FILE="/tmp/ai_compress_logs_requested"
LOG_DIR="/root/.openclaw/workspace/lobster-workspace/logs"

# 查找超过7天的日志
old_logs=$(find "$LOG_DIR" -name "*.log" -type f -mtime +7 2>/dev/null | wc -l)

if [ "$old_logs" -gt 0 ]; then
    # 创建标记文件，包含日志数量和路径
    echo "$old_logs" > "$MARKER_FILE"
    echo "检测到 $old_logs 个旧日志文件待压缩"
    echo "标记已创建: $MARKER_FILE"
else
    echo "没有超过7天的日志文件"
fi
