#!/bin/bash
# AgentCoin 自动监控脚本

while true; do
    # 获取当前题目
    PROBLEM=$(curl -s https://agentcoin.site/api/problem/current)
    PROBLEM_ID=$(echo $PROBLEM | grep -o '"problem_id":[0-9]*' | cut -d: -f2)
    IS_ACTIVE=$(echo $PROBLEM | grep -o '"is_active":true')
    
    if [ ! -z "$IS_ACTIVE" ]; then
        echo "$(date): 发现活跃题目 #$PROBLEM_ID"
        # 发送通知到 Telegram
        curl -s -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" \
            -d "chat_id=YOUR_CHAT_ID" \
            -d "text=🎯 AgentCoin 新题目 #$PROBLEM_ID 出现！请立即解题。"
    fi
    
    sleep 60
done
