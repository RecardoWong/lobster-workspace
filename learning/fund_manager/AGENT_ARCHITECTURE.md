# 🏗️ 个人业务Agent化系统架构 v2.0

## 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         知识库层 (Knowledge Base)                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  历史数据库      │   实时数据流     │      个人经验库              │
│                 │                 │                             │
│ • 股价历史       │ • 行情API       │ • 交易记录                   │
│ • 财报存档       │ • 新闻流        │ • 胜败分析                   │
│ • 宏观数据       │ • 情绪指标      │ • 策略迭代                   │
│ • 事件复盘       │ • 资金流向      │ • 参数优化                   │
└────────┬────────┴────────┬────────┴────────────┬────────────────┘
         │                 │                     │
         │    数据支撑      │                     │
         └─────────────────┘                     │
                         │                        │
                         ▼                        │
┌─────────────────────────────────────────────────────────────────┐
│                         Skills层 (Capabilities)                   │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ 价值投资框架     │  比特币抄底模型   │   美股市场情绪监控           │
│                 │                 │                             │
│ • 多因子评分     │ • 链上数据       │ • VIX恐慌指数               │
│ • 财报分析       │ • 矿工行为       │ •  put/call比率             │
│ • 估值模型       │ • 交易所流出     │ •  散户情绪                  │
│ • 仓位管理       │ • 周期分析       │ •  机构流向                  │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                    宏观流动性监控                                  │
│                                                                  │
│ • 美联储政策      • 利率期限结构     • 美元流动性                  │
│ • 央行资产负债表   • 信用利差        • 跨境资本流                   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ 能力调用
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CRON层 (Automation)                       │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   每日摘要       │    盘前分析      │      周度复盘               │
│   (06:30)       │    (07:00)      │      (周日)                 │
│                 │                 │                             │
│ • 隔夜市场       │ • 宏观数据       │ • 组合表现                   │
│ • 重要新闻       │ • 个股扫描       │ • 策略有效性                 │
│ • 持仓变化       │ • 交易信号       │ • 参数调优                   │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                      实时预警 (Real-time)                          │
│                                                                  │
│ • 价格异动        • 新闻突发        • 风险触发                     │
│ • 财报超预期      • 宏观数据公布     • 组合回撤超限                  │
└─────────────────────────────────────────────────────────────────┘
         │
         │ 结果反馈
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      回到知识库层 (闭环)                           │
└─────────────────────────────────────────────────────────────────┘
```

## 三层详解

### 第一层：知识库层
**作用**: 存储所有数据和经验，为决策提供依据

**历史数据库**:
```
market_data/           # 股价历史
├── stocks/           # 个股数据
├── crypto/           # 加密货币
└── indices/          # 指数数据

earnings_archive/      # 财报存档
├── reports/          # 季度财报
├── transcripts/      # 电话会议
└── guidance/         # 业绩指引

macro_data/           # 宏观数据
├── fed/              # 美联储
├── cpi/              # 通胀数据
├── employment/       # 就业数据
└── gdp/              # GDP数据

events/               # 事件复盘
├── 2008_crisis/      # 2008危机
├── 2020_covid/       # 2020疫情
├── 2022_rate_hikes/  # 2022加息
└── trade_log/        # 个人交易记录
```

**实时数据流**:
- Yahoo Finance API (股价)
- NewsAPI (新闻)
- FRED API (宏观)
- Twitter API (情绪)
- 链上数据 (比特币)

**个人经验库**:
- 每笔交易的记录和反思
- 策略回测结果
- 参数优化历史
- 胜率和盈亏比统计

---

### 第二层：Skills层
**作用**: 核心决策算法，替代人工判断

#### Skill 1: 价值投资框架 (Value Investing)
```python
class ValueInvestingSkill:
    """基于之前的多因子评分系统"""
    
    def analyze(self, ticker: str) -> dict:
        # 1. 基本面分析
        fundamental_score = self.fundamental_analysis(ticker)
        
        # 2. 估值模型
        valuation = self.dcf_model(ticker)
        
        # 3. 安全边际
        margin_of_safety = self.calculate_mos(ticker)
        
        # 4. 仓位建议
        position_size = self.position_sizing(
            score=fundamental_score,
            mos=margin_of_safety,
            conviction='high'
        )
        
        return {
            'ticker': ticker,
            'score': fundamental_score,
            'fair_value': valuation,
            'current_price': self.get_price(ticker),
            'discount': margin_of_safety,
            'position_size': position_size,
            'signal': self.generate_signal()
        }
```

#### Skill 2: 比特币抄底模型 (BTC Bottom Detector)
```python
class BTCBottomSkill:
    """链上数据 + 周期分析"""
    
    indicators = {
        'mvrv_z_score': 'MVRV Z-Score < 0 = 超卖',
        'nupl': 'NUPL < 0 = 亏损状态',
        'pi_cycle': 'Pi周期顶部/底部指标',
        'miner_position': '矿工持仓变化',
        'exchange_outflow': '交易所流出量',
        'long_term_holder': '长期持有者行为'
    }
    
    def analyze(self) -> dict:
        # 收集链上数据
        onchain_data = self.fetch_onchain_data()
        
        # 计算抄底信号强度
        bottom_probability = self.calculate_bottom_prob(onchain_data)
        
        # 分批建仓建议
        accumulation_plan = self.generate_dca_plan(bottom_probability)
        
        return {
            'bottom_probability': bottom_probability,
            'signal_strength': self.get_signal_strength(),
            'accumulation_plan': accumulation_plan,
            'risk_level': self.assess_risk()
        }
```

#### Skill 3: 美股市场情绪监控 (Market Sentiment)
```python
class SentimentMonitorSkill:
    """多维度情绪监控"""
    
    def analyze(self) -> dict:
        # 1. VIX恐慌指数
        vix_data = self.fetch_vix()
        
        # 2. Put/Call比率
        putcall_ratio = self.fetch_putcall()
        
        # 3. 散户情绪 (AAII)
        retail_sentiment = self.fetch_aaii()
        
        # 4. 机构资金流向
        institutional_flow = self.fetch_institutional_flow()
        
        # 5. 恐惧贪婪指数
        fear_greed_index = self.calculate_fear_greed(
            vix_data,
            putcall_ratio,
            retail_sentiment,
            institutional_flow
        )
        
        return {
            'fear_greed_index': fear_greed_index,
            'vix': vix_data,
            'putcall_ratio': putcall_ratio,
            'retail_sentiment': retail_sentiment,
            'institutional_flow': institutional_flow,
            'interpretation': self.interpret_sentiment(fear_greed_index)
        }
```

#### Skill 4: 宏观流动性监控 (Macro Liquidity)
```python
class MacroLiquiditySkill:
    """美联储 + 全球流动性"""
    
    def analyze(self) -> dict:
        # 1. 美联储政策
        fed_policy = self.analyze_fed_policy()
        
        # 2. 利率期限结构
        yield_curve = self.analyze_yield_curve()
        
        # 3. 全球流动性
        global_liquidity = self.calculate_global_liquidity()
        
        # 4. 信用利差
        credit_spreads = self.fetch_credit_spreads()
        
        # 5. 美元流动性
        dollar_liquidity = self.analyze_dollar_liquidity()
        
        # 综合判断
        liquidity_score = self.calculate_liquidity_score(
            fed_policy,
            yield_curve,
            global_liquidity,
            credit_spreads,
            dollar_liquidity
        )
        
        return {
            'liquidity_score': liquidity_score,
            'fed_policy': fed_policy,
            'yield_curve': yield_curve,
            'credit_spreads': credit_spreads,
            'signal': self.generate_signal(liquidity_score)
        }
```

---

### 第三层：CRON层
**作用**: 自动化执行，定时触发Skills

#### 定时任务

**每日摘要 (06:30)**
```bash
# cron: 30 6 * * 1-5
daily_summary.py:
  1. 抓取隔夜市场数据
  2. 扫描重要新闻 (Top 50)
  3. 检查持仓变化
  4. 生成摘要报告
  5. 发送到用户
```

**盘前分析 (07:00)**
```bash
# cron: 0 7 * * 1-5
pre_market_analysis.py:
  1. 调用价值投资框架扫描股票池
  2. 调用情绪监控获取市场情绪
  3. 调用宏观流动性评估环境
  4. 生成交易信号
  5. 输出今日交易计划
```

**周度复盘 (周日)**
```bash
# cron: 0 9 * * 0
weekly_review.py:
  1. 计算本周组合表现
  2. 分析每笔交易的胜败原因
  3. 评估策略有效性
  4. 参数优化建议
  5. 更新知识库经验
  6. 生成复盘报告
```

**实时预警 (持续运行)**
```python
# 守护进程 real_time_monitor.py
while True:
    # 每5分钟检查一次
    time.sleep(300)
    
    # 价格异动
    price_alerts = check_price_movement(threshold=5%)
    
    # 新闻突发
    breaking_news = check_breaking_news(sources=[' bloomberg', 'reuters'])
    
    # 风险触发
    risk_alerts = check_risk_triggers(
        portfolio_drawdown=8%,
        single_stock_loss=10%,
        vix_spike=30%
    )
    
    # 发送预警
    if price_alerts or breaking_news or risk_alerts:
        send_alert_to_user()
```

---

## 反馈闭环

```
CRON执行结果 → 分析效果 → 记录到知识库 → 优化Skills参数 → 下次执行改进

Example:
1. 今日盘前分析建议买入AAPL
2. 实际走势上涨3%
3. 记录: "信号有效，增加该场景权重"
4. 调整: 技术面评分权重 +5%
5. 下次同类信号置信度提高
```

## 实施路线图

### Phase 1: 基础搭建 (1-2周)
- [ ] 搭建知识库结构
- [ ] 接入基础API (Yahoo, FRED)
- [ ] 实现价值投资框架

### Phase 2: Skills完善 (2-4周)
- [ ] 实现比特币抄底模型
- [ ] 实现情绪监控系统
- [ ] 实现宏观流动性监控

### Phase 3: 自动化 (1-2周)
- [ ] 配置CRON任务
- [ ] 实现预警系统
- [ ] 建立反馈机制

### Phase 4: 优化迭代 (持续)
- [ ] 回测验证
- [ ] 参数调优
- [ ] 新Skill开发

---
*架构设计: 2026-02-22*
