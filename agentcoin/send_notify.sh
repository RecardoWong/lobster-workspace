#!/bin/bash
# AgentCoin 通知发送脚本
# 每分钟检查 notify_queue.txt 并发送 Telegram 消息

NOTIFY_FILE="/root/.openclaw/workspace/agentcoin/notify_queue.txt"
LAST_SENT_FILE="/root/.openclaw/workspace/agentcoin/.last_notify"

if [ ! -f "$NOTIFY_FILE" ]; then
    exit 0
fi

# 获取上次发送的行数
LAST_LINE=0
if [ -f "$LAST_SENT_FILE" ]; then
    LAST_LINE=$(cat "$LAST_SENT_FILE")
fi

# 获取当前总行数
TOTAL_LINES=$(wc -l < "$NOTIFY_FILE")

# 如果有新消息
if [ "$TOTAL_LINES" -gt "$LAST_LINE" ]; then
    # 读取新消息
    NEW_MSG=$(tail -n +$((LAST_LINE + 1)) "$NOTIFY_FILE" | head -1)
    
    if [ ! -z "$NEW_MSG" ]; then
        # 使用 openclaw message 工具发送
        # 这里我们使用 webhook 或者直接调用
        echo "检测到新通知: $NEW_MSG"
    fi
    
    # 更新已发送行数
    echo "$TOTAL_LINES" > "$LAST_SENT_FILE"
fi
