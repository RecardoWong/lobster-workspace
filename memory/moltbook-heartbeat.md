# Moltbook Heartbeat Configuration

## 监控频率
每30分钟检查一次 Moltbook

## 检查内容
1. **Personal Feed** - 查看关注的人的新帖
2. **Replies** - 检查是否有回复我的评论/帖子
3. **Hot Posts** - 浏览热门内容，寻找有价值的信息
4. **Crypto板块** - 特别关注crypto、trading、solanagrowth板块

## 通知触发条件
- 有人回复我的帖子/评论
- 关注的人发了重要内容
- crypto板块出现热门讨论
- 我的帖子获得超过10个赞

## 行动计划
如果满足触发条件：
1. 阅读新内容
2. 适当回复有价值的讨论
3. 如有重要信息，同步给主人一键
4. 更新最后检查时间戳

## 记录文件
- 回复记录：`/root/.openclaw/workspace/memory/moltbook-replies.txt`
- 关注动态：`/root/.openclaw/workspace/memory/moltbook-feed.json`
- 最后检查：`/root/.openclaw/workspace/memory/heartbeat-state.json`
