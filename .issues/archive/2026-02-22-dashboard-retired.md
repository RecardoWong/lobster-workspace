---
priority: P1
created: 2026-02-22
tags: [dashboard, decision, completed]
---

# Dashboard停用决策

## 决策内容
停用Dashboard系统，改为Telegram直接推送。

## 原因
1. **维护成本高** - 需要维护服务器、处理部署、解决浏览器兼容问题
2. **效果一般** - 用户实际使用频率不高
3. **Cookie频繁过期** - Twitter抓取需要频繁更新Cookie，维护繁琐
4. **Telegram推送更直接** - 消息直接送达，无需打开网页

## 历史
- 2026-02-17: Dashboard v4.2 上线，三栏布局
- 2026-02-19: 尝试修复Twitter更新问题
- 2026-02-22: 决定停用，转向Telegram推送

## 替代方案
- Twitter监控 → Telegram每小时推送 + 每日复盘
- FRED宏观数据 → Telegram每日8点摘要
- 股价/币价 → Telegram定时推送

## 保留资源
- Dashboard代码保留在 `/lobster-workspace/dashboard/`
- 服务器继续运行（用于其他用途）
- 数据文件保留供参考

## 状态
done
