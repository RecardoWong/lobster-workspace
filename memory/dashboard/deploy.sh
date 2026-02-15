#!/bin/bash
# Dashboard 自动部署脚本
# 用法: ./deploy.sh

set -e

echo "🚀 Dashboard 自动部署开始..."

# 配置
SERVER_IP="43.160.229.161"
SERVER_USER="ubuntu"
REMOTE_DIR="/var/www/html"
LOCAL_DIR="/root/.openclaw/workspace/memory/dashboard"

# 检查本地目录是否存在
if [ ! -d "$LOCAL_DIR" ]; then
    echo "❌ 错误: 本地目录不存在 $LOCAL_DIR"
    exit 1
fi

echo "📁 本地目录: $LOCAL_DIR"
echo "🌐 服务器: $SERVER_USER@$SERVER_IP:$REMOTE_DIR"

# 使用 rsync 同步文件（需要配置 SSH 免密登录）
echo "📤 正在同步文件到服务器..."

# 方案1: 如果有 SSH 免密登录
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "echo 'SSH连接成功'" 2>/dev/null; then
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='*.md' \
        --exclude='screenshot.png' \
        "$LOCAL_DIR/" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"
    
    echo "✅ 文件同步完成"
    
    # 设置文件权限
    ssh "$SERVER_USER@$SERVER_IP" "sudo chown -R www-data:www-data $REMOTE_DIR && sudo chmod -R 755 $REMOTE_DIR"
    
    echo "✅ 权限设置完成"
else
    echo "⚠️ SSH 连接失败，尝试使用 scp 逐个传输..."
    
    # 方案2: 逐个复制关键文件
    for file in index.html index_v2.html mobile.html twitter.html; do
        if [ -f "$LOCAL_DIR/$file" ]; then
            echo "📄 传输 $file..."
            scp -o ConnectTimeout=5 "$LOCAL_DIR/$file" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/" 2>/dev/null || echo "⚠️ $file 传输失败"
        fi
    done
fi

echo ""
echo "🎉 部署完成！"
echo "🌐 访问地址: http://$SERVER_IP/"
echo "🌐 新版地址: http://$SERVER_IP/index_v2.html"

# 记录部署日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Dashboard deployed" >> "$LOCAL_DIR/../deploy.log"
