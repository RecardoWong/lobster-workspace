---
priority: P1
created: 2026-02-22
tags: [twitter, cron, completed]
---

# Twitter定时推送系统

## 任务描述
建立Twitter自动抓取和推送系统：
1. 每小时抓取一次，推送最新推文
2. 每天早上8点总结昨天所有推文

## 已完成配置

### 1. 每小时推送
- 任务ID: `6e3b6f54-e026-4049-9f85-08a3e79e76a6`
- 脚本: `/root/.openclaw/workspace/lobster-workspace/scripts/twitter_hourly_push.py`
- 时间: 每小时整点 (Asia/Shanghai)
- 功能: 抓取4个账号最新推文，推送到Telegram
- 监控账号: elonmusk, jdhasoptions, xiaomucrypto, aistocksavvy

### 2. 每日总结
- 任务ID: `0151e609-91b3-48be-afdb-7d72d6fb588e`
- 脚本: `/root/.openclaw/workspace/lobster-workspace/scripts/twitter_daily_summary.py`
- 时间: 每天8:00 AM (Asia/Shanghai)
- 功能: 总结昨日所有推文，按作者分组统计

### 3. 删除旧任务
- 已删除: `twitter-auto-deploy` (只部署不抓取)

## 工作流程
1. 每小时整点 → 抓取1小时内的新推文 → 推送至Telegram
2. 推文数据保存到 `/tmp/twitter_monitor/daily_YYYYMMDD.json`
3. 每天早上8点 → 读取昨日数据 → 生成总结报告

## 监控账号
- **Elon Musk** (@elonmusk) - 市场风向标
- **jdhasoptions** - 期权交易观点
- **xiaomucrypto** - 加密货币动态
- **AI Stock Savvy** (@aistocksavvy) - AI投资分析

## 推送格式
### 每小时推送
```
🐦 Twitter 更新
📅 14:00
==============================
👤 Elon Musk @elonmusk
⏰ 30分钟前
💬 Inverse Cramer is rarely wrong...
```

### 每日总结
```
📊 Twitter 昨日总结
📅 2026-02-21
📈 共 15 条推文
==============================
👤 Elon Musk (@elonmusk) - 5条
  1. Inverse Cramer is rarely wrong...
  2. Progress...
...
🔥 昨日推文旅密度高，市场可能有重要事件
```

## 状态
- [x] 每小时推送脚本
- [x] 每日总结脚本
- [x] CRON任务配置
- [x] 删除旧任务
done
