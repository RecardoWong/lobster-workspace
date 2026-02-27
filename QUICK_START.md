# 🎓 投资学习系统 - 快速使用手册

## 📦 系统组成

```
learning/
├── earnings_reader/
│   ├── unified_earnings_reader.py      # 统一财报读取 (港股/美股/A股)
│   ├── cninfo_akshare_reader.py        # 巨潮资讯网数据 (分红/配股)
│   └── a_share_earnings_reader.py      # A股财报基础
├── fund_manager/
│   └── skills/
│       ├── a_share_market_monitor.py   # 市场监控 (龙虎榜/资金流向/两融)
│       ├── value_investing_v2.py       # 价值投资框架
│       ├── btc_bottom_v2.py            # 比特币抄底模型
│       ├── market_sentiment_v2.py      # 市场情绪监控
│       └── macro_liquidity_v2.py       # 宏观流动性
├── technical_analysis/
│   ├── kpattern_recognizer.py          # K线形态识别 (15种形态)
│   ├── ma_system_analyzer.py           # 均线系统分析
│   └── volume_price_analyzer.py        # 量价关系分析
└── industry_chain/
    └── ai_datacenter_analyzer_real.py  # AI数据中心产业链
```

---

## 🚀 快速开始

### 1. 分析一只股票 (通用接口)

```python
# 方法1: 使用统一财报读取器
from learning.earnings_reader.skills.unified_earnings_reader import UnifiedEarningsReader

reader = UnifiedEarningsReader()

# A股
reader.get_realtime_quote('000001')      # 平安银行
reader.get_earnings_summary('000001')
reader.get_dividend_history('000001')

# 港股
reader.get_realtime_quote('02577')       # 英诺赛科

# 美股
reader.get_earnings_summary('NVDA')      # 英伟达
```

### 2. 市场监控 (资金流向/龙虎榜)

```python
from learning.fund_manager.skills.a_share_market_monitor import AShareMarketMonitor

monitor = AShareMarketMonitor()

# 市场情绪报告
monitor.get_market_sentiment_report()

# 个股资金流向
monitor.get_fund_flow_stock('000001')

# 龙虎榜
monitor.get_dragon_tiger_list()

# 融资融券
monitor.get_margin_trading('szse')

# 北向资金
monitor.get_northbound_fund_flow()
```

### 3. 技术分析

```python
from learning.technical_analysis.skills.kpattern_recognizer import KPatternRecognizer, Candle
from learning.technical_analysis.skills.ma_system_analyzer import MASystemAnalyzer

# K线形态识别
kpattern = KPatternRecognizer()
candles = [
    Candle(open=100, high=102, low=98, close=99),
    Candle(open=99, high=100, low=90, close=98),   # 锤子线
]
patterns = kpattern.recognize(candles)

# 均线系统
ma = MASystemAnalyzer()
prices = [100, 102, 101, 105, 108, 110, 108, 105, 102, 100]
result = ma.analyze(prices)
```

### 4. 产业链分析

```python
from learning.industry_chain.skills.ai_datacenter_analyzer_real import AIDataCenterChain

chain = AIDataCenterChain()
result = chain.analyze_chain()
report = chain.format_report(result)
print(report)
```

---

## 📊 使用场景

### 场景1: 早盘决策 (每天8:00)
```python
# 获取市场简报
monitor = AShareMarketMonitor()
print(monitor.get_market_sentiment_report())

# 查看个股
reader = UnifiedEarningsReader()
reader.get_realtime_quote('02577')  # 英诺赛科
```

### 场景2: 选股分析
```python
# 分析A股
reader.analyze_earnings({'symbol': '000001', ...})

# 技术分析
kpattern.recognize(candles)
ma.analyze(prices)
```

### 场景3: 行业研究
```python
# AI产业链
chain.analyze_chain()

# 资金流向
monitor.get_fund_flow_industry()
```

---

## 📈 输出示例

### 财报速读输出:
```
📊 平安银行 (000001) 财报速读
🎯 综合评级: B+
📈 核心指标:
  • 营收: 12.3亿 (+45% YoY)
  • 毛利率: 28.5%
  • EPS: 超预期 12%
🔍 异常预警: 经营现金流持续为负
💡 总结: 稳健增长，盈利承压
```

### 技术分析输出:
```
📈 均线系统分析
📊 均线数值:
   🟢 MA5: $151.19 (+1.27%)
   🔴 MA60: $154.41 (-0.85%)
🔔 技术信号:
   • 死叉 - 短期卖出信号
   • 空头排列 - 下跌趋势
💡 操作建议: 观望或减仓
```

### 市场监控输出:
```
📊 A股市场情绪报告
💰 深市融资融券:
   融资余额: 7077.67亿
   融券余额: 157.3亿
📈 行业资金流向:
   • 电子: 主力净流入
   • 半导体: 主力净流入
🌏 北向资金:
   净流入: 25.6亿
```

---

## 🔧 定时任务 (已配置)

```bash
# 查看所有定时任务
openclaw cron list

# 主要任务:
# - 财经新闻更新: 每小时
# - Twitter监控: 每小时
# - 市场简报: 每天8:00
# - 代码巡查: 每天6:30/22:00
# - 冥想提醒: 每天2:00
```

---

## 📚 学习路径建议

### 第1周: 财报分析
- 学习 `unified_earnings_reader.py`
- 掌握: 营收/利润/现金流/ROE

### 第2周: 技术分析
- 学习 `kpattern_recognizer.py`
- 学习 `ma_system_analyzer.py`
- 掌握: K线形态/均线/量价关系

### 第3周: 市场情绪
- 学习 `a_share_market_monitor.py`
- 掌握: 龙虎榜/资金流向/两融

### 第4周: 产业链
- 学习 `ai_datacenter_analyzer_real.py`
- 掌握: 上下游分析/瓶颈识别

---

## 💡 进阶用法

### 自定义分析流程
```python
# 创建自己的分析流程
class MyStrategy:
    def analyze(self, stock_code):
        # 1. 基本面筛选
        earnings = reader.get_earnings_summary(stock_code)
        if earnings['rating'] < 'B':
            return "跳过: 基本面不合格"
        
        # 2. 技术面确认
        prices = get_prices(stock_code)
        tech = ma.analyze(prices)
        if '空头排列' in tech['signals']:
            return "跳过: 趋势向下"
        
        # 3. 资金面确认
        fund = monitor.get_fund_flow_stock(stock_code)
        if fund['main_flow'] < 0:
            return "跳过: 主力流出"
        
        return "✅ 符合条件"
```

---

## ❓ 常见问题

**Q: 为什么某个API返回空数据?**
A: 可能是:
1. akshare版本需要更新: `pip install -U akshare`
2. 该股票确实无数据
3. 数据源暂时不可用

**Q: 如何更新数据?**
A: 大部分数据是实时获取的，无需更新

**Q: 如何添加新功能?**
A: 在对应目录下创建新文件，参考现有代码结构

---

## 📞 帮助

需要帮助时:
1. 查看 `SKILL.md` 文件
2. 查看代码注释
3. 运行 `python3 script_name.py` 看演示
