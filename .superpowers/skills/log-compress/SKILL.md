# Log Compress Skill
# AI 日志压缩任务

## 任务触发条件
- 每天凌晨 4:30 执行
- 或通过 heartbeat 检测到旧日志时执行

## 执行步骤

### 1. 扫描日志
```bash
find /root/.openclaw/workspace/lobster-workspace/logs -name "*.log" -type f -mtime +7
```

### 2. 分析每个旧日志
读取日志内容，提取：
- ❌ 错误和失败信息 → P1
- ✅ 完成的功能和部署 → P2  
- ⚠️ 警告和重要发现 → P1/P2
- 💡 关键决策和教训 → P2

### 3. 生成记忆条目
格式：`- [Px][YYYY-MM-DD] 一句话总结`

目标：100-200行日志 → 5-15条精华

### 4. 更新文件
- 追加到 `memory/2026-02-20.md`
- 移动原文到 `logs/archive/`

## 示例

原始日志 (120行):
```
[2026-02-01 08:00] Starting Twitter monitor...
[2026-02-01 08:00] Fetching data from Twitter API
[2026-02-01 08:00] Got 10 tweets from @elonmusk
...
[2026-02-01 08:05] ERROR: Network timeout when deploying
[2026-02-01 08:06] Retrying deployment...
[2026-02-01 08:07] ✅ Deploy successful!
```

压缩后 (3条):
```
- [P1][2026-02-01] Twitter监控部署失败：网络超时，重试后成功
- [P2][2026-02-01] 成功抓取@elonmusk 10条推文并部署
```

## 执行命令
当收到 "压缩日志" 指令时：
1. 扫描超过7天的日志
2. 逐个分析并压缩
3. 报告压缩结果
