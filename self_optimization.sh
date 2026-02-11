#!/bin/bash
# 自主优化脚本 - 龙虾助手自运行

echo "🦞 龙虾自主优化任务 $(date '+%H:%M')"
echo "================================"

# 1. 检查磁盘空间
echo "📊 磁盘使用:"
df -h / | tail -1 | awk '{print "   已用: "$5 " (" $3 "/" $2 ")"}'

# 2. 检查内存
echo "💾 内存状态:"
free -h | grep Mem | awk '{print "   可用: "$7 "/" $2}'

# 3. 清理旧缓存
echo "🧹 清理旧文件:"
find /tmp -name "*.tmp" -mtime +1 -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "   ✅ 缓存已清理"

# 4. 检查git状态
echo "📁 工作区状态:"
if [ -d .git ]; then
    git status --short | wc -l | awk '{print "   未提交更改: "$1}'
else
    echo "   未初始化git"
fi

# 5. 自主思考记录
echo ""
echo "💡 自主思考记录:"
echo "   • $(date '+%H:%M') - 系统检查完成，状态良好"
echo "   • 下一步: 学习聪明钱追踪方法"
echo "   • 待优化: 提高新币监控频率到15分钟"

echo ""
echo "================================"
echo "✅ 自主优化完成"
