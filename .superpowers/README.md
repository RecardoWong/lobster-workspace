# Superpowers for Dashboard 项目

## 项目简介

Dashboard v4.1 - 实时投资监控面板
- 技术栈: HTML + CSS + JavaScript (纯静态)
- 部署: 腾讯云服务器 (43.160.229.161)
- 自动更新: Cron定时任务

## 可用的 Skills

| Skill | 触发条件 | 功能 |
|-------|---------|------|
| dashboard-planning | "我要添加/修改功能" | 规划设计和创建文档 |
| dashboard-layout | "布局乱了" "跑到下面" | 修复响应式布局问题 |
| dashboard-data | "数据不显示" "怎么获取" | 数据源和定时任务 |
| dashboard-implementation | "开始实施" "去做吧" | 执行编码和部署 |

## 快速开始

### 添加新功能

1. **规划阶段**
   ```
   用户: "我要在右边添加一个显示AI新闻的板块"
   → 触发 dashboard-planning
   → 创建设计文档
   → 用户确认
   ```

2. **实施阶段**
   ```
   用户: "开始实施"
   → 触发 dashboard-implementation
   → 逐个执行任务
   → 频繁部署验证
   ```

### 修复布局问题

```
用户: "这个卡片怎么跑到下面去了"
→ 触发 dashboard-layout
→ 诊断问题
→ 修复并验证
```

## 项目结构

```
lobster-workspace/
├── dashboard/
│   ├── index.html          # 主页面
│   ├── data/               # JSON数据文件
│   └── tweets.html         # Twitter详情页
├── scripts/
│   ├── update_prices.py    # 股价更新
│   ├── twitter_auto_deploy.py  # Twitter更新
│   └── finance_news_v2.py  # 新闻聚合
├── designs/                # 设计文档
├── plans/                  # 实施计划
└── .superpowers/
    └── skills/             # Skill定义
```

## 关键配置

### 响应式断点

- < 1600px: 2列
- < 900px: 1列
- >= 1600px: 3列

### 定时任务

```bash
# 查看所有定时任务
crontab -l

# 股价更新 - 每5分钟
*/5 * * * * python3 scripts/update_prices.py

# Twitter - 每小时
0 * * * * python3 scripts/twitter_auto_deploy.py

# 新闻 - 每30分钟
*/30 * * * * python3 scripts/finance_news_v2.py
```

## 访问地址

- Dashboard: http://43.160.229.161/
- GitHub: https://github.com/RecardoWong/lobster-workspace

## 最佳实践

1. **先规划后编码** - 不要跳过设计文档
2. **小步快跑** - 每个任务5分钟内完成
3. **频繁验证** - 部署后立即验证
4. **用户确认** - 关键决策必须确认
5. **记录问题** - 复杂问题记录在案

## 历史教训

### 布局问题记录

| 问题 | 原因 | 解决 |
|------|------|------|
| 财经要报跑到下面 | 响应式断点1200px过低 | 改为1600px |
| Twitter嵌套 | div标签未闭合 | 恢复v4.1重新添加 |
| 第三栏空白 | 卡片结构损坏 | 从git恢复 |

### 数据问题记录

| 问题 | 原因 | 解决 |
|------|------|------|
| 纳斯达克显示假数据 | 没有可用免费API | 显示"数据获取受限" |
| Twitter不更新 | 抓取任务被注释 | 恢复cron任务 |

## 更新 Skills

Skills存储在 `.superpowers/skills/` 目录下。

要更新 skill：
1. 编辑对应 `SKILL.md` 文件
2. 测试新流程
3. 记录改进

## 获取帮助

- 布局问题 → 查看 dashboard-layout skill
- 数据问题 → 查看 dashboard-data skill  
- 实施问题 → 查看 dashboard-implementation skill
