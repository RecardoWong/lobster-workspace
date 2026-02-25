#!/bin/bash
# Twitter 推送包装脚本 - 确保环境正确

export PATH=/root/.nvm/versions/node/v22.22.0/bin:$PATH
export HOME=/root

cd /root/.openclaw/workspace/lobster-workspace
source .env.twitter.cookie

python3 scripts/twitter_hourly_push.py >> logs/twitter_push.log 2>&1
