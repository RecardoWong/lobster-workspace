#!/bin/bash
# Dashboard 自动部署脚本

SERVER="ubuntu@43.160.229.161"
SSH_KEY="/root/.ssh/lobster_deploy"
LOCAL_DIR="/root/.openclaw/workspace/lobster-workspace/dashboard"
REMOTE_DIR="/home/ubuntu"
WEB_DIR="/var/www/html"

echo "🚀 开始部署 Dashboard..."

# 1. 复制文件到服务器
scp -i $SSH_KEY -o StrictHostKeyChecking=no $LOCAL_DIR/*.html $SERVER:$REMOTE_DIR/

# 2. 更新 Web 目录
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "sudo cp $REMOTE_DIR/index.html $WEB_DIR/ && sudo chown www-data:www-data $WEB_DIR/index.html"

echo "✅ Dashboard 部署完成!"
echo "🌐 访问地址: http://43.160.229.161/"
