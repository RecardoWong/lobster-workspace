#!/bin/bash
# FRED每日市场摘要推送
# 每天 8:00 AM 执行

cd /root/.openclaw/workspace/learning/fund_manager

# 生成摘要
SUMMARY=$(python3 daily_summary.py 2>&1)

# 推送到Telegram
if command -v openclaw &> /dev/null; then
    echo "$SUMMARY" | openclaw message send --channel telegram --target "5440939697"
else
    echo "[$(date)] Summary generated but openclaw not available"
    echo "$SUMMARY"
fi
