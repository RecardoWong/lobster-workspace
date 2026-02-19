#!/bin/bash
# Twitter 数据自动部署脚本
# 在 twitter_cookie_monitor_v2.py 后调用

echo "🚀 部署 Twitter 数据到服务器..."

cd /root/.openclaw/workspace/lobster-workspace

# 检查数据文件是否存在
if [ ! -f "data/twitter_translated.json" ]; then
    echo "❌ 数据文件不存在，跳过部署"
    exit 1
fi

# 复制到 dashboard
cp data/twitter_translated.json dashboard/data/

# 部署到服务器
scp -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no dashboard/data/twitter_translated.json ubuntu@43.160.229.161:/home/ubuntu/ 2>/dev/null

if [ $? -eq 0 ]; then
    ssh -i /root/.ssh/lobster_deploy -o StrictHostKeyChecking=no ubuntu@43.160.229.161 'sudo cp /home/ubuntu/twitter_translated.json /var/www/html/data/ && sudo chown www-data:www-data /var/www/html/data/twitter_translated.json && echo "✅ Twitter数据已部署"' 2>/dev/null
    echo "✅ 部署完成"
else
    echo "❌ 部署失败"
fi
