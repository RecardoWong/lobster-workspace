#!/bin/bash
# CRON安装脚本

echo "🔧 安装投资Agent CRON任务..."

WORK_DIR=/root/.openclaw/workspace/learning/fund_manager

# 1. 创建日志目录
mkdir -p $WORK_DIR/logs
mkdir -p $WORK_DIR/reports

# 2. 设置权限
chmod +x $WORK_DIR/cron/*.py
chmod +x $WORK_DIR/skills/*.py

# 3. 备份当前crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d).txt 2>/dev/null || echo "无现有crontab"

# 4. 安装新crontab
crontab $WORK_DIR/crontab_config.txt

echo "✅ CRON任务安装完成!"
echo ""
echo "📋 任务列表:"
crontab -l | grep -v "^#" | grep -v "^$"
echo ""
echo "⏰ 时间安排:"
echo "  • 每天 8:00  - 全球市场摘要 (手机推送)"
echo "  • 每天 10:00 - 美股盘前分析"
echo "  • 每周一 9:00 - 上周市场复盘"
echo ""
echo "🔴 实时监控需要手动启动:"
echo "   python3 $WORK_DIR/cron/realtime_monitor.py &"
echo ""
echo "📊 查看日志:"
echo "   tail -f $WORK_DIR/logs/cron_morning.log"
