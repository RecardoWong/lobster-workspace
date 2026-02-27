#!/bin/bash
# AI 日志压缩触发脚本
# 每天凌晨 4:30 触发 AI 分析超过7天的日志

LOG_DIR="/root/.openclaw/workspace/lobster-workspace/logs"
MEMORY_FILE="/root/.openclaw/workspace/memory/2026-02-20.md"
ARCHIVE_DIR="/root/.openclaw/workspace/lobster-workspace/logs/archive"

# 确保归档目录存在
mkdir -p "$ARCHIVE_DIR"

# 查找超过7天的日志文件
find "$LOG_DIR" -name "*.log" -type f -mtime +7 | while read logfile; do
    filename=$(basename "$logfile")
    
    # 跳过已压缩的标记文件
    if [ -f "${logfile}.compressed" ]; then
        continue
    fi
    
    # 创建压缩请求文件
    request_file="/tmp/compress_request_$(date +%s).txt"
    
    cat > "$request_file" << EOF
请压缩以下日志文件，提取精华并生成记忆条目。

文件: $filename
路径: $logfile
归档目录: $ARCHIVE_DIR
记忆文件: $MEMORY_FILE

任务:
1. 读取日志文件内容
2. 提取关键信息（错误、完成的功能、重要决策）
3. 生成不超过15条记忆条目，格式: - [P1/P2][YYYY-MM-DD] 内容
4. 追加到记忆文件
5. 移动原文到归档目录
6. 创建 .compressed 标记文件

请执行压缩任务。
EOF

    # 通过 Telegram 发送请求（或其他方式通知 AI）
    echo "触发 AI 压缩: $filename"
    
    # 标记为待压缩
    touch "${logfile}.pending"
done
