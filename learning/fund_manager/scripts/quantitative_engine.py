#!/usr/bin/env python3
"""
量化投资决策引擎
用API成本替代人力成本
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os

class SignalType(Enum):
    STRONG_BUY = "STRONG_BUY"  # 综合评分 >= 80
    BUY = "BUY"                # 综合评分 >= 75
    HOLD = "HOLD"              # 综合评分 50-75
    SELL = "SELL"              # 综合评分 < 50 或评分下降
    STOP_LOSS = "STOP_LOSS"    # 触发止损

@dataclass
class InvestmentSignal:
    ticker: str
    signal: SignalType
    score: float
    position_size: float  # 建议仓位比例
    confidence: str       # HIGH/MEDIUM/LOW
    reasons: List[str]    # 信号原因
    timestamp: datetime

class QuantitativeEngine:
    """量化决策引擎"""
    
    def __init__(self):
        # 因子权重配置
        self.weights = {
            'fundamental': 0.25,
            'technical': 0.20,
            'macro': 0.20,
            'sentiment': 0.15,
            'risk': 0.20
        }
        
        # 评分缓存
        self.score_cache = {}
        self.cache_ttl = timedelta(hours=1)
        
        # 持仓记录
        self.positions = {}
        
    # ==================== 核心评分系统 ====================
    
    def calculate_comprehensive_score(self, ticker: str) -> Dict:
        """
        计算综合投资评分 (0-100)
        替代人工判断的核心算法
        """
        # 检查缓存
        if ticker in self.score_cache:
            cached = self.score_cache[ticker]
            if datetime.now() - cached['timestamp'] < self.cache_ttl:
                return cached['data']
        
        # 计算各维度评分
        scores = {
            'fundamental': self._calculate_fundamental_score(ticker),
            'technical': self._calculate_technical_score(ticker),
            'macro': self._calculate_macro_score(),
            'sentiment': self._calculate_sentiment_score(ticker),
            'risk': self._calculate_risk_score(ticker)
        }
        
        # 加权计算总分
        total_score = sum(
            scores[k] * self.weights[k]
            for k in scores
        )
        
        result = {
            'ticker': ticker,
            'total_score': round(total_score, 2),
            'component_scores': scores,
            'timestamp': datetime.now().isoformat()
        }
        
        # 更新缓存
        self.score_cache[ticker] = {
            'data': result,
            'timestamp': datetime.now()
        }
        
        return result
    
    def _calculate_fundamental_score(self, ticker: str) -> float:
        """
        基本面评分 (0-100)
        替代人工财务分析
        """
        # 模拟数据 - 实际应从API获取
        mock_data = self._fetch_fundamental_mock(ticker)
        
        score = 0.0
        
        # 1. 盈利增长 (25分)
        earnings_growth = mock_data.get('earnings_growth', 0)
        if earnings_growth > 0.30:
            score += 25
        elif earnings_growth > 0.20:
            score += 20
        elif earnings_growth > 0.10:
            score += 15
        elif earnings_growth > 0:
            score += 5
        
        # 2. 收入增长 (20分)
        revenue_growth = mock_data.get('revenue_growth', 0)
        if revenue_growth > 0.30:
            score += 20
        elif revenue_growth > 0.20:
            score += 16
        elif revenue_growth > 0.10:
            score += 12
        elif revenue_growth > 0:
            score += 4
        
        # 3. 利润率 (15分)
        profit_margin = mock_data.get('profit_margin', 0)
        if profit_margin > 0.30:
            score += 15
        elif profit_margin > 0.20:
            score += 10
        elif profit_margin > 0.10:
            score += 5
        
        # 4. ROE (15分)
        roe = mock_data.get('roe', 0)
        if roe > 0.25:
            score += 15
        elif roe > 0.20:
            score += 12
        elif roe > 0.15:
            score += 8
        elif roe > 0.10:
            score += 4
        
        # 5. 负债率 (10分) - 越低越好
        debt_ratio = mock_data.get('debt_ratio', 1)
        if debt_ratio < 0.20:
            score += 10
        elif debt_ratio < 0.40:
            score += 7
        elif debt_ratio < 0.60:
            score += 4
        
        # 6. 现金流 (10分)
        fcf = mock_data.get('free_cash_flow', 0)
        if fcf > 10000000000:  # > $10B
            score += 10
        elif fcf > 1000000000:  # > $1B
            score += 7
        elif fcf > 0:
            score += 4
        
        # 7. 估值 (5分)
        pe_ratio = mock_data.get('pe_ratio', 100)
        industry_avg_pe = mock_data.get('industry_avg_pe', 25)
        if pe_ratio < industry_avg_pe * 0.8:
            score += 5  # 显著低估
        elif pe_ratio < industry_avg_pe:
            score += 3  # 轻度低估
        
        return min(score, 100)
    
    def _calculate_technical_score(self, ticker: str) -> float:
        """
        技术面评分 (0-100)
        替代人工看图分析
        """
        mock_data = self._fetch_technical_mock(ticker)
        
        score = 0.0
        price = mock_data.get('price', 0)
        sma20 = mock_data.get('sma20', price)
        sma50 = mock_data.get('sma50', price)
        sma200 = mock_data.get('sma200', price)
        
        # 1. 趋势方向 (25分)
        if price > sma20 > sma50 > sma200:
            score += 25  # 完美多头排列
        elif price > sma20 > sma50:
            score += 20  # 中期多头
        elif price > sma20:
            score += 12  # 短期多头
        elif price < sma20 < sma50 < sma200:
            score += 0   # 完美空头排列
        else:
            score += 8   # 震荡
        
        # 2. RSI (20分)
        rsi = mock_data.get('rsi', 50)
        if 40 < rsi < 60:
            score += 20  # 健康区间
        elif 30 <= rsi <= 40 or 60 <= rsi <= 70:
            score += 15  # 轻度超买/卖
        elif rsi < 30:
            score += 12  # 超卖 (可能反弹)
        else:  # rsi > 70
            score += 5   # 超买 (可能回调)
        
        # 3. MACD (20分)
        macd = mock_data.get('macd', 0)
        macd_signal = mock_data.get('macd_signal', 0)
        if macd > macd_signal and macd > 0:
            score += 20  # 强势上涨
        elif macd > macd_signal:
            score += 15  # 金叉
        elif macd < macd_signal and macd < 0:
            score += 5   # 弱势下跌
        else:
            score += 8   # 死叉
        
        # 4. 成交量 (20分)
        volume = mock_data.get('volume', 0)
        avg_volume = mock_data.get('avg_volume', 1)
        vol_ratio = volume / avg_volume
        if vol_ratio > 1.5:
            score += 20  # 放量
        elif vol_ratio > 1.2:
            score += 15
        elif vol_ratio > 1.0:
            score += 10
        elif vol_ratio > 0.8:
            score += 5
        
        # 5. 波动性 (15分)
        atr = mock_data.get('atr', price * 0.02)
        atr_pct = atr / price
        if 0.015 < atr_pct < 0.025:
            score += 15  # 适中波动
        elif atr_pct < 0.015:
            score += 10  # 波动太低
        elif atr_pct < 0.035:
            score += 8
        else:
            score += 3   # 波动太高
        
        return min(score, 100)
    
    def _calculate_macro_score(self) -> float:
        """
        宏观环境评分 (0-100)
        替代人工宏观判断
        """
        mock_data = self._fetch_macro_mock()
        
        score = 50.0  # 中性起点
        
        # 1. 美联储政策 (30分)
        fed_rate = mock_data.get('fed_rate', 5.5)
        rate_trend = mock_data.get('rate_trend', 'holding')
        
        if rate_trend == 'cutting':
            score += 30  # 降息周期 = 大利好
        elif rate_trend == 'pausing' and fed_rate > 4.0:
            score += 15  # 暂停加息 = 边际改善
        elif rate_trend == 'hiking':
            score -= 30  # 加息周期 = 利空
        
        # 2. 通胀 (25分)
        cpi = mock_data.get('cpi', 3.0)
        cpi_trend = mock_data.get('cpi_trend', 'falling')
        
        if cpi_trend == 'falling' and cpi < 2.5:
            score += 25  # 通胀回落到目标区间
        elif cpi_trend == 'falling' and cpi < 3.0:
            score += 15
        elif cpi_trend == 'rising' and cpi > 4.0:
            score -= 25  # 通胀恶化
        elif cpi > 3.5:
            score -= 15
        
        # 3. 就业市场 (20分)
        unemployment = mock_data.get('unemployment', 3.7)
        nfp = mock_data.get('nfp', 200000)
        
        if unemployment < 4.0 and nfp > 200000:
            score += 20  # 就业强劲
        elif unemployment < 4.5:
            score += 10
        elif unemployment > 5.5:
            score -= 20  # 就业恶化
        elif unemployment > 4.5:
            score -= 10
        
        # 4. 10年期美债收益率 (15分)
        treasury_10y = mock_data.get('treasury_10y', 4.3)
        if treasury_10y < 3.5:
            score += 15  # 低利率利好成长股
        elif treasury_10y < 4.0:
            score += 10
        elif treasury_10y > 5.0:
            score -= 15  # 高利率压制估值
        elif treasury_10y > 4.5:
            score -= 5
        
        # 5. VIX恐慌指数 (10分)
        vix = mock_data.get('vix', 15)
        if vix < 15:
            score += 10  # 低波动 = 风险偏好高
        elif vix < 20:
            score += 5
        elif vix > 30:
            score -= 10  # 高波动 = 恐慌
        elif vix > 25:
            score -= 5
        
        return min(max(score, 0), 100)
    
    def _calculate_sentiment_score(self, ticker: str) -> float:
        """
        市场情绪评分 (0-100)
        替代人工情绪判断
        """
        mock_data = self._fetch_sentiment_mock(ticker)
        
        score = 50.0  # 中性起点
        
        # 1. 新闻情感 (35分)
        news_sentiment = mock_data.get('news_sentiment', 0)
        if news_sentiment > 0.4:
            score += 35  # 高度正面
        elif news_sentiment > 0.2:
            score += 25
        elif news_sentiment > 0.1:
            score += 15
        elif news_sentiment < -0.4:
            score -= 35  # 高度负面
        elif news_sentiment < -0.2:
            score -= 25
        elif news_sentiment < -0.1:
            score -= 15
        
        # 2. 社交媒体情绪 (25分)
        social_sentiment = mock_data.get('social_sentiment', 0.5)
        score += (social_sentiment - 0.5) * 50
        
        # 3. 分析师评级 (25分)
        analyst_buy = mock_data.get('analyst_buy_pct', 0.6)
        if analyst_buy > 0.70:
            score += 25
        elif analyst_buy > 0.60:
            score += 18
        elif analyst_buy > 0.50:
            score += 10
        elif analyst_buy < 0.30:
            score -= 25
        elif analyst_buy < 0.40:
            score -= 15
        
        # 4. 机构资金流向 (15分)
        inst_flow = mock_data.get('institutional_flow', 0)
        if inst_flow > 1000000000:  # > $1B流入
            score += 15
        elif inst_flow > 100000000:  # > $100M流入
            score += 10
        elif inst_flow > 0:
            score += 5
        elif inst_flow < -1000000000:
            score -= 15
        elif inst_flow < -100000000:
            score -= 10
        elif inst_flow < 0:
            score -= 5
        
        return min(max(score, 0), 100)
    
    def _calculate_risk_score(self, ticker: str) -> float:
        """
        风险控制评分 (0-100)
        扣分制 - 分数越高风险越低
        """
        mock_data = self._fetch_risk_mock(ticker)
        
        score = 100.0  # 满分起点，逐步扣分
        
        # 1. 波动率风险 (扣0-25分)
        volatility = mock_data.get('volatility', 0.3)
        if volatility > 0.50:
            score -= 25  # 极高波动
        elif volatility > 0.40:
            score -= 18
        elif volatility > 0.30:
            score -= 10
        elif volatility > 0.20:
            score -= 5
        
        # 2. 流动性风险 (扣0-20分)
        avg_volume = mock_data.get('avg_daily_volume', 1000000)
        if avg_volume < 100000:
            score -= 20  # 流动性极差
        elif avg_volume < 500000:
            score -= 15
        elif avg_volume < 1000000:
            score -= 10
        
        # 3. 财务风险 (扣0-20分)
        current_ratio = mock_data.get('current_ratio', 1.5)
        if current_ratio < 1.0:
            score -= 20  # 短期偿债能力不足
        elif current_ratio < 1.2:
            score -= 10
        
        debt_to_equity = mock_data.get('debt_to_equity', 0.5)
        if debt_to_equity > 1.0:
            score -= 20  # 高杠杆
        elif debt_to_equity > 0.6:
            score -= 10
        
        # 4. 集中度风险 (扣0-15分)
        top10_holdings = mock_data.get('top10_holder_pct', 0.5)
        if top10_holdings > 0.85:
            score -= 15  # 高度集中
        elif top10_holdings > 0.70:
            score -= 8
        
        # 5. 估值风险 (扣0-10分)
        pe_ratio = mock_data.get('pe_ratio', 25)
        pb_ratio = mock_data.get('pb_ratio', 3)
        if pe_ratio > 50 or pb_ratio > 10:
            score -= 10  # 估值泡沫风险
        elif pe_ratio > 40 or pb_ratio > 7:
            score -= 5
        
        # 6. 行业风险 (扣0-10分)
        sector = mock_data.get('sector', '')
        high_risk_sectors = ['Biotech', 'Crypto', 'Meme Stocks']
        if sector in high_risk_sectors:
            score -= 10
        
        return max(score, 0)
    
    # ==================== 信号生成 ====================
    
    def generate_signal(self, ticker: str) -> InvestmentSignal:
        """
        生成交易信号
        替代人工买卖决策
        """
        score_data = self.calculate_comprehensive_score(ticker)
        total_score = score_data['total_score']
        components = score_data['component_scores']
        
        # 检查现有持仓
        current_position = self.positions.get(ticker, {})
        entry_score = current_position.get('entry_score', 0)
        
        reasons = []
        
        # 买入逻辑
        if total_score >= 80:
            signal = SignalType.STRONG_BUY
            position_size = 0.15  # 15%仓位
            confidence = 'HIGH'
            reasons.append(f'综合评分优秀 ({total_score})')
            
        elif total_score >= 75:
            signal = SignalType.BUY
            position_size = 0.10  # 10%仓位
            confidence = 'MEDIUM'
            reasons.append(f'综合评分良好 ({total_score})')
            
        # 卖出逻辑
        elif current_position and (entry_score - total_score) > 20:
            signal = SignalType.SELL
            position_size = 0
            confidence = 'HIGH'
            reasons.append(f'评分大幅下降 ({entry_score} -> {total_score})')
            
        elif total_score < 40:
            signal = SignalType.SELL
            position_size = 0
            confidence = 'MEDIUM'
            reasons.append(f'综合评分过低 ({total_score})')
            
        else:
            signal = SignalType.HOLD
            position_size = current_position.get('size', 0)
            confidence = 'LOW'
            reasons.append(f'评分中性 ({total_score})')
        
        # 添加详细原因
        if components['fundamental'] > 80:
            reasons.append('基本面强劲')
        if components['technical'] > 75:
            reasons.append('技术面看多')
        if components['macro'] > 70:
            reasons.append('宏观环境有利')
        if components['risk'] < 60:
            reasons.append('注意风险较高')
        
        return InvestmentSignal(
            ticker=ticker,
            signal=signal,
            score=total_score,
            position_size=position_size,
            confidence=confidence,
            reasons=reasons,
            timestamp=datetime.now()
        )
    
    def generate_portfolio_signals(self, watchlist: List[str]) -> List[InvestmentSignal]:
        """
        为整个观察列表生成信号
        替代人工逐个分析
        """
        signals = []
        
        for ticker in watchlist:
            try:
                signal = self.generate_signal(ticker)
                signals.append(signal)
            except Exception as e:
                print(f"Error generating signal for {ticker}: {e}")
        
        # 按信号强度排序
        signal_priority = {
            SignalType.STRONG_BUY: 4,
            SignalType.BUY: 3,
            SignalType.SELL: 2,
            SignalType.STOP_LOSS: 1,
            SignalType.HOLD: 0
        }
        
        signals.sort(
            key=lambda x: (signal_priority[x.signal], x.score),
            reverse=True
        )
        
        return signals
    
    # ==================== 模拟数据获取 (实际应替换为API) ====================
    
    def _fetch_fundamental_mock(self, ticker: str) -> Dict:
        """模拟基本面数据"""
        # 根据ticker返回不同的模拟数据
        mock_db = {
            'AAPL': {
                'earnings_growth': 0.15,
                'revenue_growth': 0.08,
                'profit_margin': 0.25,
                'roe': 0.30,
                'debt_ratio': 0.40,
                'free_cash_flow': 100000000000,
                'pe_ratio': 28,
                'industry_avg_pe': 25
            },
            'MSFT': {
                'earnings_growth': 0.20,
                'revenue_growth': 0.12,
                'profit_margin': 0.35,
                'roe': 0.35,
                'debt_ratio': 0.30,
                'free_cash_flow': 65000000000,
                'pe_ratio': 32,
                'industry_avg_pe': 28
            },
            'NVDA': {
                'earnings_growth': 2.50,  # 250%!
                'revenue_growth': 2.00,
                'profit_margin': 0.55,
                'roe': 0.50,
                'debt_ratio': 0.20,
                'free_cash_flow': 25000000000,
                'pe_ratio': 65,
                'industry_avg_pe': 30
            }
        }
        return mock_db.get(ticker, mock_db['AAPL'])
    
    def _fetch_technical_mock(self, ticker: str) -> Dict:
        """模拟技术面数据"""
        import random
        base_price = {'AAPL': 185, 'MSFT': 420, 'NVDA': 700}.get(ticker, 100)
        
        return {
            'price': base_price,
            'sma20': base_price * 0.98,
            'sma50': base_price * 0.95,
            'sma200': base_price * 0.90,
            'rsi': random.randint(35, 65),
            'macd': 2.5,
            'macd_signal': 1.8,
            'volume': 50000000,
            'avg_volume': 45000000,
            'atr': base_price * 0.025
        }
    
    def _fetch_macro_mock(self) -> Dict:
        """模拟宏观数据"""
        return {
            'fed_rate': 5.5,
            'rate_trend': 'holding',  # cutting/pausing/hiking
            'cpi': 3.1,
            'cpi_trend': 'falling',
            'unemployment': 3.7,
            'nfp': 353000,
            'treasury_10y': 4.3,
            'vix': 15
        }
    
    def _fetch_sentiment_mock(self, ticker: str) -> Dict:
        """模拟情绪数据"""
        return {
            'news_sentiment': 0.25,
            'social_sentiment': 0.65,
            'analyst_buy_pct': 0.75,
            'institutional_flow': 500000000  # $500M流入
        }
    
    def _fetch_risk_mock(self, ticker: str) -> Dict:
        """模拟风险数据"""
        return {
            'volatility': 0.25,
            'avg_daily_volume': 50000000,
            'current_ratio': 1.8,
            'debt_to_equity': 0.40,
            'top10_holder_pct': 0.55,
            'pe_ratio': 30,
            'pb_ratio': 5,
            'sector': 'Technology'
        }

# ==================== 使用示例 ====================

def main():
    """运行示例"""
    engine = QuantitativeEngine()
    
    # 观察列表
    watchlist = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA']
    
    print("="*70)
    print("🤖 量化投资决策引擎")
    print("="*70)
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 生成所有信号
    signals = engine.generate_portfolio_signals(watchlist)
    
    # 显示买入信号
    print("\n📈 买入信号:")
    print("-"*70)
    for signal in signals:
        if signal.signal in [SignalType.STRONG_BUY, SignalType.BUY]:
            print(f"\n{signal.ticker}")
            print(f"  信号: {signal.signal.value}")
            print(f"  评分: {signal.score}/100")
            print(f"  建议仓位: {signal.position_size*100:.0f}%")
            print(f"  置信度: {signal.confidence}")
            print(f"  原因: {', '.join(signal.reasons)}")
    
    # 显示卖出信号
    print("\n\n📉 卖出信号:")
    print("-"*70)
    for signal in signals:
        if signal.signal == SignalType.SELL:
            print(f"\n{signal.ticker}")
            print(f"  信号: {signal.signal.value}")
            print(f"  评分: {signal.score}/100")
            print(f"  原因: {', '.join(signal.reasons)}")
    
    # 显示详细评分
    print("\n\n📊 详细评分:")
    print("-"*70)
    for ticker in watchlist:
        score_data = engine.calculate_comprehensive_score(ticker)
        comp = score_data['component_scores']
        print(f"\n{ticker}:")
        print(f"  总分: {score_data['total_score']:.1f}")
        print(f"  ├─ 基本面: {comp['fundamental']:.1f}")
        print(f"  ├─ 技术面: {comp['technical']:.1f}")
        print(f"  ├─ 宏观环境: {comp['macro']:.1f}")
        print(f"  ├─ 情绪面: {comp['sentiment']:.1f}")
        print(f"  └─ 风险控制: {comp['risk']:.1f}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
