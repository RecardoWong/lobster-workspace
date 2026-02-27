---
priority: P2
created: 2026-02-22
tags: [twitter, workflow, decision]
---

# Twitter数据获取方式变更

## 决策
取消自动更新dashboard的Twitter数据，改为**手动按需推送**。

## 原因
- Dashboard维护成本高（cookie过期、页面结构变化、部署问题）
- 用户实际需求：想看的时再看，不需要24小时监控
- 减少无效抓取，降低被封风险

## 新工作流程
1. 用户想看推文 → 发送消息
2. 我手动运行抓取脚本 → `twitter_cookie_monitor_v2.py`
3. 翻译并整理 → 直接推送到Telegram
4. 不更新dashboard，省去部署环节

## 相关脚本
- 抓取: `/root/.openclaw/workspace/lobster-workspace/scripts/twitter_cookie_monitor_v2.py`
- 数据目录: `/tmp/twitter_monitor/`
- 监控账号: elonmusk, jdhasoptions, xiaomucrypto, aistocksavvy

## 备注
- 保留现有dashboard供静态查看（股价、新闻等）
- Twitter栏位可以留着显示最后更新的数据
- 如需恢复自动更新，可重新配置cron
