#!/bin/bash
# X平台真实采集器安装脚本

echo "🔧 安装X平台真实采集器..."

WORK_DIR=/root/.openclaw/workspace/content_analyzer

# 1. 检查Cookie
echo "📋 检查Cookie..."
if [ -f "$WORK_DIR/.twitter_cookies.json" ]; then
    echo "  ✅ Cookie文件已存在"
    COOKIE_COUNT=$(cat $WORK_DIR/.twitter_cookies.json | grep -c '"name"')
    echo "  📊 Cookie数量: $COOKIE_COUNT"
else
    echo "  ❌ Cookie文件不存在"
    echo "  请先提供Cookie文件到: $WORK_DIR/.twitter_cookies.json"
    exit 1
fi

# 2. 检查Playwright
echo "📦 检查Playwright..."
if ! command -v playwright &> /dev/null; then
    echo "  ⬇️  安装Playwright..."
    pip install playwright
    playwright install chromium
else
    echo "  ✅ Playwright已安装"
fi

# 3. 设置权限
echo "🔐 设置权限..."
chmod +x $WORK_DIR/x_real_collector.py

# 4. 创建日志目录
mkdir -p $WORK_DIR/logs
mkdir -p $WORK_DIR/data

# 5. 安装CRON
echo "⏰ 安装CRON任务..."
crontab $WORK_DIR/crontab_real_collector.txt

echo ""
echo "✅ 安装完成！"
echo ""
echo "📅 任务安排:"
echo "  • 每天 6:00  - 采集时间线"
echo "  • 每天 18:00 - 二次采集"
echo "  • 每周一 7:00 - 更新公式库"
echo "  • 每周三 9:00 - 检查Cookie有效期"
echo ""
echo "🚀 立即测试:"
echo "  cd $WORK_DIR && python3 x_real_collector.py"
echo ""
echo "📊 查看日志:"
echo "  tail -f $WORK_DIR/logs/real_collect.log"
