#!/bin/bash
# Crabby Rathbun 动态监控脚本

echo "🔍 检查 Crabby Rathbun 的最新动态..."

# 检查 GitHub 最新活动
echo "📊 GitHub 活动:"
curl -s "https://api.github.com/users/crabby-rathbun/events/public" | head -50

# 检查博客 RSS/更新
echo ""
echo "📝 博客更新:"
curl -s "https://crabby-rathbun.github.io/mjrathbun-website/blog.html" | grep -o '<h2>.*</h2>' | head -5

# 尝试获取 Moltbook 最新帖子（如果有权限）
echo ""
echo "🦀 Moltbook 动态:"
cd /root/.openclaw/workspace/skills/moltbook-agi
./scripts/moltbook.sh hot 50 2>/dev/null | grep -i "rathbun\|crabby" || echo "暂无 Moltbook 动态"

echo ""
echo "✅ 检查完成"
