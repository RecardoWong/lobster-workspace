# 🤖 算法化投资决策引擎

## 💡 核心思想
**用算法规则替代人工判断，用API成本替代人力成本**

## 📊 成本对比

| 项目 | 人力成本 | API成本 | 节省 |
|------|---------|---------|------|
| 新闻监控 (20,000条/天) | 2名分析师 ($10,000/月) | NewsAPI ($50/月) | 99.5% |
| 财报分析 (50家公司) | 1名研究员 ($6,000/月) | OpenAI API ($100/月) | 98% |
| 宏观跟踪 (30指标) | 0.5名宏观分析师 ($3,000/月) | FRED API (免费) | 100% |
| 交易执行 | 1名交易员 ($8,000/月) | 券商API (免费) | 100% |
| **总计** | **$27,000/月** | **$150/月** | **99.4%** |

## 🎯 判断框架算法化

### 1. 多因子评分系统 (0-100分)

```python
class InvestmentScore:
    def __init__(self):
        self.weights = {
            'fundamental': 0.25,    # 基本面
            'technical': 0.20,      # 技术面
            'macro': 0.20,          # 宏观环境
            'sentiment': 0.15,      # 市场情绪
            'risk': 0.20            # 风险控制
        }
    
    def calculate_score(self, ticker: str) -> float:
        scores = {
            'fundamental': self._fundamental_score(ticker),
            'technical': self._technical_score(ticker),
            'macro': self._macro_score(),
            'sentiment': self._sentiment_score(ticker),
            'risk': self._risk_score(ticker)
        }
        
        total_score = sum(
            scores[k] * self.weights[k] 
            for k in scores
        )
        
        return min(max(total_score, 0), 100)
```

### 2. 基本面评分 (0-100)

**因子权重**:
```python
fundamental_factors = {
    'earnings_growth': 0.25,        # 盈利增长 (YoY)
    'revenue_growth': 0.20,         # 收入增长 (YoY)
    'profit_margin': 0.15,          # 利润率
    'roe': 0.15,                    # ROE
    'debt_ratio': 0.10,             # 负债率
    'cash_flow': 0.10,              # 现金流
    'valuation': 0.05               # 估值合理性
}
```

**评分规则**:
```python
def _fundamental_score(self, ticker: str) -> float:
    data = self.fetch_fundamental_data(ticker)
    
    score = 0
    
    # 盈利增长 > 20% = 25分, > 10% = 15分, > 0 = 5分
    if data['earnings_growth'] > 0.20:
        score += 25
    elif data['earnings_growth'] > 0.10:
        score += 15
    elif data['earnings_growth'] > 0:
        score += 5
    
    # 收入增长 > 20% = 20分, > 10% = 12分, > 0 = 4分
    if data['revenue_growth'] > 0.20:
        score += 20
    elif data['revenue_growth'] > 0.10:
        score += 12
    elif data['revenue_growth'] > 0:
        score += 4
    
    # 利润率 > 30% = 15分, > 20% = 10分, > 10% = 5分
    if data['profit_margin'] > 0.30:
        score += 15
    elif data['profit_margin'] > 0.20:
        score += 10
    elif data['profit_margin'] > 0.10:
        score += 5
    
    # ROE > 20% = 15分, > 15% = 10分, > 10% = 5分
    if data['roe'] > 0.20:
        score += 15
    elif data['roe'] > 0.15:
        score += 10
    elif data['roe'] > 0.10:
        score += 5
    
    # 负债率 < 30% = 10分, < 50% = 5分
    if data['debt_ratio'] < 0.30:
        score += 10
    elif data['debt_ratio'] < 0.50:
        score += 5
    
    # 现金流为正 = 10分
    if data['free_cash_flow'] > 0:
        score += 10
    
    # 估值 (PE < 行业平均 = 5分)
    if data['pe_ratio'] < data['industry_avg_pe']:
        score += 5
    
    return score
```

### 3. 技术面评分 (0-100)

```python
def _technical_score(self, ticker: str) -> float:
    data = self.fetch_technical_data(ticker)
    
    score = 0
    
    # 趋势方向 (20分)
    # 价格 > 50日均线 > 200日均线 = 牛市 = 20分
    if data['price'] > data['sma50'] > data['sma200']:
        score += 20
    # 价格 > 50日均线 = 多头 = 10分
    elif data['price'] > data['sma50']:
        score += 10
    # 价格 < 50日均线 < 200日均线 = 熊市 = 0分
    elif data['price'] < data['sma50'] < data['sma200']:
        score += 0
    
    # RSI (20分)
    # 30 < RSI < 70 = 正常区间 = 20分
    if 30 < data['rsi'] < 70:
        score += 20
    # RSI < 30 = 超卖 = 15分 (可能反弹)
    elif data['rsi'] < 30:
        score += 15
    # RSI > 70 = 超买 = 5分 (可能回调)
    elif data['rsi'] > 70:
        score += 5
    
    # MACD (20分)
    # MACD > 信号线且 > 0 = 强势 = 20分
    if data['macd'] > data['macd_signal'] and data['macd'] > 0:
        score += 20
    # MACD > 信号线 = 金叉 = 15分
    elif data['macd'] > data['macd_signal']:
        score += 15
    # MACD < 信号线 = 死叉 = 5分
    else:
        score += 5
    
    # 成交量 (20分)
    # 成交量 > 20日均量 = 放量 = 20分
    if data['volume'] > data['avg_volume_20d'] * 1.2:
        score += 20
    elif data['volume'] > data['avg_volume_20d']:
        score += 10
    
    # 波动性 (20分)
    # ATR适中 = 风险可控 = 20分
    atr_pct = data['atr'] / data['price']
    if 0.01 < atr_pct < 0.03:
        score += 20
    elif atr_pct < 0.01:
        score += 10  # 波动太低
    else:
        score += 5   # 波动太高
    
    return score
```

### 4. 宏观环境评分 (0-100)

```python
def _macro_score(self) -> float:
    """宏观环境评分 - 影响所有股票"""
    score = 50  # 中性起点
    
    # 美联储政策 (30分)
    fed_data = self.fetch_fed_data()
    if fed_data['rate_trend'] == 'cutting':
        score += 30  # 降息周期 = 利好
    elif fed_data['rate_trend'] == 'hiking':
        score -= 30  # 加息周期 = 利空
    elif fed_data['rate_trend'] == 'pausing':
        score += 10  # 暂停 = 边际改善
    
    # 通胀趋势 (20分)
    cpi_data = self.fetch_cpi_data()
    if cpi_data['trend'] == 'falling'] and cpi_data['current'] < 3.0:
        score += 20  # 通胀回落到3%以下 = 利好
    elif cpi_data['trend'] == 'rising':
        score -= 20  # 通胀上升 = 利空
    
    # 就业市场 (20分)
    nfp_data = self.fetch_nfp_data()
    if nfp_data['unemployment'] < 4.0 and nfp_data['jobs_added'] > 200000:
        score += 20  # 就业强劲 = 利好
    elif nfp_data['unemployment'] > 5.0:
        score -= 20  # 就业恶化 = 利空
    
    # 10年期美债收益率 (20分)
    treasury_data = self.fetch_treasury_data()
    if treasury_data['yield_10y'] < 4.0:
        score += 20  # 收益率低于4% = 利好成长股
    elif treasury_data['yield_10y'] > 5.0:
        score -= 20  # 收益率过高 = 利空
    
    # VIX恐慌指数 (10分)
    vix_data = self.fetch_vix_data()
    if vix_data['vix'] < 20:
        score += 10  # 低波动 = 利好
    elif vix_data['vix'] > 30:
        score -= 10  # 高波动 = 利空
    
    return min(max(score, 0), 100)
```

### 5. 情绪面评分 (0-100)

```python
def _sentiment_score(self, ticker: str) -> float:
    """市场情绪评分"""
    score = 50  # 中性起点
    
    # 新闻情感 (40分)
    news_data = self.fetch_news_sentiment(ticker)
    if news_data['avg_sentiment'] > 0.3:
        score += 40  # 高度正面
    elif news_data['avg_sentiment'] > 0.1:
        score += 20  # 轻度正面
    elif news_data['avg_sentiment'] < -0.3:
        score -= 40  # 高度负面
    elif news_data['avg_sentiment'] < -0.1:
        score -= 20  # 轻度负面
    
    # 社交媒体情绪 (30分)
    social_data = self.fetch_social_sentiment(ticker)
    score += social_data['bullish_pct'] * 0.3 - 15
    
    # 分析师评级 (20分)
    analyst_data = self.fetch_analyst_ratings(ticker)
    buy_ratio = analyst_data['buy'] / analyst_data['total']
    score += (buy_ratio - 0.5) * 40  # 50%为中性基准
    
    # 机构持仓变化 (10分)
    institutional_data = self.fetch_institutional_flow(ticker)
    if institutional_data['net_flow'] > 0:
        score += 10  # 机构增持
    else:
        score -= 10  # 机构减持
    
    return min(max(score, 0), 100)
```

### 6. 风险控制评分 (0-100)

```python
def _risk_score(self, ticker: str) -> float:
    """风险控制评分 - 扣分制，满分100表示无风险"""
    score = 100
    
    # 波动率风险 (25分)
    vol_data = self.fetch_volatility_data(ticker)
    if vol_data['annualized_vol'] > 0.50:
        score -= 25  # 波动率过高
    elif vol_data['annualized_vol'] > 0.40:
        score -= 15
    elif vol_data['annualized_vol'] > 0.30:
        score -= 5
    
    # 流动性风险 (20分)
    liquidity_data = self.fetch_liquidity_data(ticker)
    if liquidity_data['avg_daily_volume'] < 1000000:
        score -= 20  # 日均成交量低于100万
    elif liquidity_data['avg_daily_volume'] < 5000000:
        score -= 10
    
    # 集中度风险 (20分)
    concentration_data = self.fetch_concentration_data(ticker)
    if concentration_data['top10_holder_pct'] > 0.80:
        score -= 20  # 前10大股东持股超80%
    elif concentration_data['top10_holder_pct'] > 0.60:
        score -= 10
    
    # 财务风险 (20分)
    financial_data = self.fetch_financial_risk(ticker)
    if financial_data['current_ratio'] < 1.0:
        score -= 20  # 流动比率小于1
    elif financial_data['current_ratio'] < 1.5:
        score -= 10
    
    if financial_data['debt_to_equity'] > 1.0:
        score -= 20  # 负债权益比大于1
    elif financial_data['debt_to_equity'] > 0.5:
        score -= 10
    
    # 行业风险 (15分)
    if ticker in ['_crypto', '_meme_stocks']:
        score -= 15  # 高风险行业
    
    return max(score, 0)
```

## 🎯 决策引擎

### 买入信号 (综合评分 > 75)

```python
def generate_buy_signal(self, ticker: str) -> dict:
    score = self.calculate_score(ticker)
    
    if score >= 80:
        return {
            'signal': 'STRONG_BUY',
            'score': score,
            'position_size': 0.15,  # 15%仓位
            'confidence': 'HIGH'
        }
    elif score >= 75:
        return {
            'signal': 'BUY',
            'score': score,
            'position_size': 0.10,  # 10%仓位
            'confidence': 'MEDIUM'
        }
    else:
        return {'signal': 'HOLD', 'score': score}
```

### 卖出信号 (评分下降或触发止损)

```python
def generate_sell_signal(self, ticker: str, entry_score: float) -> dict:
    current_score = self.calculate_score(ticker)
    price_data = self.fetch_price_data(ticker)
    
    # 评分下降超过20分
    if entry_score - current_score > 20:
        return {
            'signal': 'SELL',
            'reason': 'SCORE_DEGRADATION',
            'score_drop': entry_score - current_score
        }
    
    # 止损触发 (-8%)
    if price_data['unrealized_pnl_pct'] < -0.08:
        return {
            'signal': 'STOP_LOSS',
            'reason': 'STOP_LOSS_TRIGGERED',
            'loss_pct': price_data['unrealized_pnl_pct']
        }
    
    # 止盈 (+20%)
    if price_data['unrealized_pnl_pct'] > 0.20:
        return {
            'signal': 'TAKE_PROFIT',
            'reason': 'PROFIT_TARGET_REACHED',
            'profit_pct': price_data['unrealized_pnl_pct']
        }
    
    return {'signal': 'HOLD'}
```

## 🤖 自动化流程

```
06:30 ├─ 抓取隔夜新闻 (NewsAPI)
      ├─ 更新股价数据 (Yahoo Finance API)
      ├─ 获取宏观数据 (FRED API)
      └─ 计算所有股票评分

06:45 ├─ 生成买入清单 (Score > 75)
      ├─ 检查卖出信号
      └─ 计算仓位调整

07:00 ├─ 发送交易指令 (券商API)
      ├─ 记录决策日志
      └─ 生成日报 (OpenAI API)

全天 ├─ 实时监控 (价格/新闻/情绪)
     ├─ 异常检测 (波动率突增)
     └─ 自动风控 (止损执行)
```

## 💰 API成本明细

| API | 用途 | 月成本 |
|-----|------|--------|
| OpenAI GPT-4 | 财报分析、新闻摘要、报告生成 | $100 |
| Yahoo Finance | 股价、财务数据 | 免费 |
| FRED | 宏观数据 | 免费 |
| NewsAPI | 新闻聚合 | $50 |
| Twitter API | 社交媒体情绪 | $100 |
| 券商API | 交易执行 | 免费 |
| **总计** | | **$250/月** |

**vs 人工成本 $27,000/月 = 节省 99%**

## 📈 回测验证

```python
class Backtester:
    def run_backtest(self, start_date: str, end_date: str):
        """回测策略有效性"""
        results = {
            'total_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'avg_profit_per_trade': 0
        }
        
        # 模拟历史交易
        for date in date_range(start_date, end_date):
            signals = self.generate_signals(date)
            
            for signal in signals:
                if signal['type'] == 'BUY':
                    self.simulate_buy(signal)
                elif signal['type'] == 'SELL':
                    pnl = self.simulate_sell(signal)
                    results['total_return'] += pnl
        
        return results
```

---
*算法框架 v1.0 - 2026-02-22*
