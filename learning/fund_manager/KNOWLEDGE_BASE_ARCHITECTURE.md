# 🏛️ 投研知识库架构 (Research Knowledge Base)

## 第一层：历史数据库 (Historical Data)

### 1.1 宏观经济数据库
```
macro_db/
├── fed_policy/                    # 美联储政策
│   ├── interest_rates.csv         # 2014-2024利率历史
│   ├── fomc_statements/           # FOMC声明全文
│   ├── powell_speeches/           # 鲍威尔讲话
│   └── dot_plots/                 # 点阵图历史
│
├── inflation/                     # 通胀数据
│   ├── cpi_monthly.csv            # CPI月度数据
│   ├── cpi_categories/            # CPI分项数据
│   ├── pce_monthly.csv            # PCE数据
│   └── inflation_expectations.csv # 通胀预期
│
├── employment/                    # 就业数据
│   ├── nonfarm_payrolls.csv       # 非农数据
│   ├── unemployment_rate.csv      # 失业率
│   ├── jobless_claims.csv         # 初请失业金
│   ├── adp_employment.csv         # ADP就业
│   └── labor_force_participation.csv
│
├── gdp_growth/                    # GDP增长
│   ├── quarterly_gdp.csv          # 季度GDP
│   ├── gdp_components/            # GDP构成
│   └── leading_indicators.csv     # 领先指标
│
└── market_rates/                  # 市场利率
    ├── treasury_yields.csv        # 美债收益率
    ├── credit_spreads.csv         # 信用利差
    ├── libor_history.csv          # LIBOR历史
    └── real_rates.csv             # 实际利率
```

### 1.2 公司财报数据库
```
earnings_db/
├── annual_reports/                # 年报存档
│   ├── AAPL/
│   │   ├── 2023_10K.pdf
│   │   ├── 2022_10K.pdf
│   │   └── key_metrics.csv
│   ├── MSFT/
│   ├── NVDA/
│   └── ... (Top 50公司)
│
├── quarterly_earnings/            # 季度财报
│   ├── transcripts/               # 电话会议记录
│   │   ├── AAPL_Q4_2023.txt
│   │   ├── MSFT_Q4_2023.txt
│   │   └── ...
│   │
│   ├── key_metrics/               # 关键指标
│   │   ├── revenue_growth.csv
│   │   ├── profit_margins.csv
│   │   ├── cash_flow.csv
│   │   └── guidance_history.csv
│   │
│   └── surprises/                 # 超预期/低于预期
│       ├── earnings_surprises.csv
│       └── price_reaction.csv
│
└── competitor_analysis/           # 竞争对比
    ├── tech_sector/
    ├── semiconductor/
    └── ...
```

### 1.3 重大事件复盘库
```
events_db/
├── 2008_financial_crisis/
│   ├── timeline.md                # 完整时间线
│   ├── key_events/                # 关键事件
│   │   ├── lehman_brothers_bankruptcy.md
│   │   ├── bear_sterns_collapse.md
│   │   └── aig_bailout.md
│   ├── market_reaction/
│   │   ├── sp500_chart.png
│   │   ├── vix_spike.csv
│   │   └── sector_performance.csv
│   ├── policy_response/
│   │   ├── tarp_details.md
│   │   ├── fed_actions.csv
│   │   └── stress_test_results.md
│   └── lessons_learned.md
│
├── 2020_covid_pandemic/
│   ├── timeline.md
│   ├── market_crash_march_2020.md
│   ├── fed_emergency_cuts.md
│   ├── recovery_analysis/
│   └── sector_winners_losers.md
│
├── 2022_rate_hike_cycle/
│   ├── timeline.md
│   ├── inflation_surge_analysis.md
│   ├── tech_selloff_analysis.md
│   └── crypto_winter.md
│
└── other_events/
    ├── 2018_trade_war/
    ├── 2016_brexit/
    ├── 2015_china_devaluation/
    └── template.md                # 事件复盘模板
```

---

## 第二层：实时信息流 (Real-time Intelligence)

### 2.1 财经媒体监控
```
news_feeds/
├── tier1_sources/                 # 一级信源 (必看)
│   ├── bloomberg_terminal/        # Bloomberg API
│   ├── reuters_terminal/          # Reuters API
│   ├── wsj_opinion/               # 华尔街日报观点
│   └── ft_lex/                    # 金融时报Lex专栏
│
├── tier2_sources/                 # 二级信源
│   ├── cnbc_breaking/             # CNBC突发
│   ├── marketwatch/               # MarketWatch
│   ├── seeking_alpha/             # Seeking Alpha
│   └── barrons/                   # 巴伦周刊
│
├── chinese_sources/               # 中文信源
│   ├── wallstreetcn/              # 华尔街见闻
│   ├── caijing/                   # 财新
│   ├── xinhua_finance/            # 新华财经
│   └── caixin/                    # 财新
│
└── crypto_sources/                # 加密货币
    ├── coinDesk/
    ├── theBlock/
    └── cryptoTwitter/
```

### 2.2 Twitter监控列表 (50个账号)
```
twitter_watchlist/
├── macro_analysts/                # 宏观分析师 (15个)
│   ├── @tracyalloway              # Tracy Alloway
│   ├── @biancoresearch            # Bianco Research
│   ├── @LizAnnSonders             # Liz Ann Sonders
│   ├── @DougKass                  # Doug Kass
│   ├── @michaeljburry             # Michael Burry
│   ├── @JohnAuthers               # John Authers
│   └── ... (9 more)
│
├── fund_managers/                 # 基金经理 (15个)
│   ├── @chamath                   # Chamath Palihapitiya
│   ├── @howardmarksbook           # Howard Marks
│   ├── @BillAckman                # Bill Ackman
│   ├── @davidein                  # David Einhorn
│   ├── @guyadami                  # Guy Adami
│   └── ... (10 more)
│
├── traders/                       # 交易员 (10个)
│   ├── @unusual_whales            # Unusual Whales
│   ├── @KobeissiLetter            # Kobeissi Letter
│   ├── @firstsquawk               # First Squawk
│   ├── @DeItaone                  # DeItaone
│   └── ... (6 more)
│
├── crypto_analysts/               # 加密分析师 (5个)
│   ├── @woonomic                  # Willy Woo
│   ├── @glassnode                 # Glassnode
│   └── ... (3 more)
│
└── tech_ceos/                     # 科技CEO (5个)
    ├── @elonmusk
    ├── @sundarpichai
    ├── @satyanadella
    ├── @tim_cook
    └── @JeffBezos
```

### 2.3 财报日历与宏观日历
```
calendars/
├── earnings_calendar/             # 财报日历
│   ├── upcoming_week.csv          # 本周财报
│   ├── month_preview.csv          # 整月预览
│   ├── my_watchlist_alerts/       # 持仓预警
│   └── historical_beat_rate/      # 历史超预期率
│
├── macro_calendar/                # 宏观日历
│   ├── fed_meetings_2024.csv      # 美联储会议
│   ├── cpi_release_dates.csv      # CPI发布日
│   ├── nfp_release_dates.csv      # 非农发布日
│   ├── gdp_release_dates.csv      # GDP发布日
│   └── global_central_banks/      # 全球央行
│
└── important_dates/               # 重要日期
    ├── opex_dates.csv             # 期权到期日
    ├── quadruple_witching.csv     # 四巫日
    ├── fed_speakers_this_week.csv # 本周联储讲话
    └── treasury_auctions.csv      # 美债拍卖
```

### 2.4 行业数据跟踪
```
sector_data/
├── technology/
│   ├── semiconductor/
│   │   ├── wafers_shipments.csv   # 晶圆出货
│   │   ├── memory_prices.csv      # 内存价格
│   │   └── foundry_utilization.csv # 代工产能利用率
│   │
│   ├── cloud_computing/
│   │   ├── aws_growth.csv
│   │   ├── azure_growth.csv
│   │   └── gcp_growth.csv
│   │
│   └── ai_ml/
│       ├── ai_chip_shipments.csv
│       └── model_training_costs.csv
│
├── energy/
│   ├── oil_inventory.csv          # 原油库存
│   ├── natural_gas_storage.csv    # 天然气库存
│   └── rig_counts.csv             # 钻井平台数
│
├── financials/
│   ├── bank_deposits.csv          # 银行存款
│   ├── loan_growth.csv            # 贷款增长
│   └── net_interest_margin.csv    # 净息差
│
└── consumer/
    ├── retail_sales.csv           # 零售销售
    ├── consumer_confidence.csv    # 消费者信心
    └── credit_card_spending.csv   # 信用卡支出
```

---

## 第三层：个人经验库 (Personal Experience)

### 3.1 投资决策记录
```
investment_decisions/
├── decision_log.csv               # 所有决策记录
│   # 字段: date, ticker, action, price, size, reasoning, 
│   #        expected_return, time_horizon, risk_level
│
├── by_year/
│   ├── 2024_decisions/
│   │   ├── Q1/
│   │   ├── Q2/
│   │   └── ...
│   ├── 2023_decisions/
│   └── 2019_2022_decisions/
│
└── by_ticker/
    ├── AAPL_decisions.md          # 单只股票的所有操作
    ├── NVDA_decisions.md
    └── ...
```

### 3.2 复盘笔记
```
review_notes/
├── weekly_reviews/                # 周复盘
│   ├── 2024_W01_review.md
│   ├── 2024_W02_review.md
│   └── template.md
│
├── monthly_reviews/               # 月复盘
│   ├── 2024_Jan_review.md
│   └── template.md
│
├── quarterly_reviews/             # 季度复盘
│   ├── Q4_2023_review.md
│   └── template.md
│
├── trade_reviews/                 # 单笔交易复盘
│   ├── winning_trades/
│   │   ├── AAPL_20240115_win.md
│   │   └── pattern_recognition.md # 赚钱模式总结
│   │
│   └── losing_trades/
│       ├── TSLA_20240201_loss.md
│       └── mistake_catalog.md     # 错误清单
│
└── strategy_reviews/              # 策略复盘
    ├── value_strategy_review.md
    ├── momentum_strategy_review.md
    └── macro_timing_review.md
```

### 3.3 知识沉淀
```
knowledge_base/
├── frameworks/                    # 决策框架
│   ├── my_investment_philosophy.md
│   ├── stock_selection_criteria.md
│   ├── position_sizing_rules.md
│   └── exit_strategy_rules.md
│
├── patterns/                      # 模式识别
│   ├── earnings_patterns.md       # 财报季模式
│   ├── fed_meeting_patterns.md    # 联储会议模式
│   ├── vix_spike_patterns.md      # VIX飙升模式
│   └── crypto_halving_cycles.md   # 比特币减半周期
│
├── watchlists/                    # 观察名单
│   ├── core_holdings.md           # 核心持仓
│   ├── watchlist_tech.md          # 科技股观察
│   ├── watchlist_value.md         # 价值股观察
│   └── watchlist_emerging.md      # 新兴机会
│
└── tools_and_resources/           # 工具资源
    ├── data_sources.md            # 数据来源汇总
    ├── calculation_tools/         # 计算工具
    └── reading_list.md            # 阅读清单
```

---

## 🔗 数据流与反馈闭环

```
┌─────────────────────────────────────────────────────────────┐
│                        实时信息流                             │
│  (新闻/Twitter/财报日历/宏观日历)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                       Skills层 (分析引擎)                     │
│                                                             │
│  输入: 实时数据 + 历史数据库 + 个人经验                        │
│                                                             │
│  处理:                                                      │
│  1. 价值投资框架 → 评分选股                                  │
│  2. 比特币抄底模型 → 链上信号                                │
│  3. 情绪监控 → 市场情绪判断                                  │
│  4. 宏观监控 → 流动性评估                                    │
│                                                             │
│  输出: 交易信号 + 仓位建议 + 风险提示                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                       CRON层 (执行层)                         │
│                                                             │
│  • 每日摘要 (06:30)                                         │
│  • 盘前分析 (07:00)                                         │
│  • 周度复盘 (周日)                                          │
│  • 实时预警 (触发式)                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 交易执行 + 结果记录
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    个人经验库 (反馈学习)                       │
│                                                             │
│  • 记录每笔交易的决策过程和结果                               │
│  • 定期复盘，总结对错原因                                     │
│  • 提取模式，优化Skills参数                                   │
│  • 沉淀为自己的投资知识                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 使用示例

**早上6:30 - 每日自动摘要**:
```
1. 系统读取实时新闻 (昨夜20条重要新闻)
2. 扫描50个Twitter账号 (发现3条重要观点)
3. 检查财报日历 (今日5家公司发布财报)
4. 查询宏观日历 (今日CPI数据发布)
5. 调用价值投资框架分析持仓
6. 调用情绪监控评估市场
7. 生成报告发送给用户
```

**你的决策流程**:
```
1. 阅读系统生成的摘要 (3分钟)
2. 查看重点公司的盘后表现 (5分钟)
3. 根据信号调整策略 (10分钟)
4. 执行交易计划
5. 记录决策到经验库
```

---

*知识库架构 v1.0 - 2026-02-22*
