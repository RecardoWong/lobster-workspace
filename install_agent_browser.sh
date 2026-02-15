#!/bin/bash
# 🦞 龙虾Agent自主安装 agent-browser

echo "🦞 龙虾自主安装 agent-browser..."
echo "================================"

# 方法1: npm安装
echo "📦 方法1: 尝试npm安装..."
npm install -g agent-browser

if [ $? -eq 0 ]; then
    echo "✅ npm安装成功！"
    agent-browser --version 2>/dev/null || echo "📥 需要运行 'agent-browser install' 下载Chromium"
else
    echo "⚠️ npm安装失败，尝试方法2..."
    
    # 方法2: 从GitHub下载预编译版本
    echo "📥 方法2: 从GitHub下载预编译版本..."
    
    # 检测系统架构
    ARCH=$(uname -m)
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    
    if [ "$ARCH" == "x86_64" ]; then
        TARGET="x64"
    elif [ "$ARCH" == "aarch64" ]; then
        TARGET="arm64"
    else
        TARGET="x64"
    fi
    
    DOWNLOAD_URL="https://github.com/vercel-labs/agent-browser/releases/latest/download/agent-browser-${OS}-${TARGET}"
    
    echo "📥 下载: $DOWNLOAD_URL"
    curl -L -o /usr/local/bin/agent-browser "$DOWNLOAD_URL" 2>/dev/null
    chmod +x /usr/local/bin/agent-browser
    
    if [ -f /usr/local/bin/agent-browser ]; then
        echo "✅ 下载成功！"
        agent-browser --version 2>/dev/null || echo "⚠️ 下载文件可能有问题"
    else
        echo "❌ 下载失败"
        exit 1
    fi
fi

echo ""
echo "🧪 测试安装..."
if command -v agent-browser &> /dev/null; then
    echo "✅ agent-browser 已安装！"
    agent-browser --version 2>/dev/null || echo "版本信息获取失败"
    
    echo ""
    echo "📥 下一步: 运行 'agent-browser install' 下载Chromium"
    echo "📖 使用说明:"
    echo "   agent-browser --help     查看帮助"
    echo "   agent-browser install    安装浏览器"
    echo "   agent-browser https://example.com  抓取网页"
else
    echo "❌ 安装失败"
    exit 1
fi

echo ""
echo "🦞 龙虾自主安装完成！"
