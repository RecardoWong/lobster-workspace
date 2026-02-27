#!/usr/bin/env python3
"""
Skills层 - 价值投资框架
基于多因子评分的价值投资决策
"""

import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ValueSignal:
    ticker: str
    score: float
    fair_value: float
    current_price: float
    discount: float  # 折扣率，正数表示低估
    position_size: float
    signal: str
    reasons: List[str]

class ValueInvestingSkill:
    """
    价值投资框架
    替代人工基本面分析
    """
    
    def __init__(self):
        self.weights = {
            'earnings_growth': 0.25,
            'revenue_growth': 0.20,
            'profit_margin': 0.15,
            'roe': 0.15,
            'debt_ratio': 0.10,
            'cash_flow': 0.10,
            'valuation': 0.05
        }
    
    def analyze(self, ticker: str) -> ValueSignal:
        """
        分析单个股票
        """
        # 获取数据
        data = self._fetch_data(ticker)
        
        # 计算基本面评分
        fundamental_score = self._calculate_fundamental_score(data)
        
        # DCF估值
        fair_value = self._dcf_valuation(data)
        current_price = data.get('current_price', 0)
        
        # 计算安全边际
        discount = (fair_value - current_price) / current_price if current_price > 0 else 0
        
        # 仓位建议
        position_size = self._position_sizing(fundamental_score, discount)
        
        # 生成信号
        signal, reasons = self._generate_signal(fundamental_score, discount)
        
        return ValueSignal(
            ticker=ticker,
            score=fundamental_score,
            fair_value=fair_value,
            current_price=current_price,
            discount=discount,
            position_size=position_size,
            signal=signal,
            reasons=reasons
        )
    
    def _fetch_data(self, ticker: str) -> Dict:
        """从知识库获取数据"""
        # TODO: 从数据库/API获取真实数据
        # 当前使用模拟数据
        mock_data = {
            'AAPL': {
                'current_price': 185.0,
                'earnings_growth': 0.15,
                'revenue_growth': 0.08,
                'profit_margin': 0.25,
                'roe': 0.30,
                'debt_ratio': 0.40,
                'free_cash_flow': 100e9,
                'pe_ratio': 28,
                'industry_avg_pe': 25,
                'eps': 6.5,
                'growth_rate': 0.12,
                'terminal_growth': 0.03,
                'wacc': 0.09
            },
            'MSFT': {
                'current_price': 420.0,
                'earnings_growth': 0.20,
                'revenue_growth': 0.12,
                'profit_margin': 0.35,
                'roe': 0.35,
                'debt_ratio': 0.30,
                'free_cash_flow': 65e9,
                'pe_ratio': 32,
                'industry_avg_pe': 28,
                'eps': 13.0,
                'growth_rate': 0.15,
                'terminal_growth': 0.03,
                'wacc': 0.09
            },
            'NVDA': {
                'current_price': 700.0,
                'earnings_growth': 2.50,
                'revenue_growth': 2.00,
                'profit_margin': 0.55,
                'roe': 0.50,
                'debt_ratio': 0.20,
                'free_cash_flow': 25e9,
                'pe_ratio': 65,
                'industry_avg_pe': 30,
                'eps': 10.8,
                'growth_rate': 0.50,
                'terminal_growth': 0.03,
                'wacc': 0.10
            }
        }
        return mock_data.get(ticker, mock_data['AAPL'])
    
    def _calculate_fundamental_score(self, data: Dict) -> float:
        """计算基本面评分 (0-100)"""
        score = 0.0
        
        # 盈利增长
        eg = data.get('earnings_growth', 0)
        if eg > 0.30: score += 25
        elif eg > 0.20: score += 20
        elif eg > 0.10: score += 15
        elif eg > 0: score += 5
        
        # 收入增长
        rg = data.get('revenue_growth', 0)
        if rg > 0.30: score += 20
        elif rg > 0.20: score += 16
        elif rg > 0.10: score += 12
        elif rg > 0: score += 4
        
        # 利润率
        pm = data.get('profit_margin', 0)
        if pm > 0.30: score += 15
        elif pm > 0.20: score += 10
        elif pm > 0.10: score += 5
        
        # ROE
        roe = data.get('roe', 0)
        if roe > 0.25: score += 15
        elif roe > 0.20: score += 12
        elif roe > 0.15: score += 8
        elif roe > 0.10: score += 4
        
        # 负债率
        dr = data.get('debt_ratio', 1)
        if dr < 0.20: score += 10
        elif dr < 0.40: score += 7
        elif dr < 0.60: score += 4
        
        # 现金流
        fcf = data.get('free_cash_flow', 0)
        if fcf > 50e9: score += 10
        elif fcf > 10e9: score += 7
        elif fcf > 0: score += 4
        
        # 估值
        pe = data.get('pe_ratio', 100)
        avg_pe = data.get('industry_avg_pe', 25)
        if pe < avg_pe * 0.8: score += 5
        elif pe < avg_pe: score += 3
        
        return min(score, 100)
    
    def _dcf_valuation(self, data: Dict) -> float:
        """
        DCF估值模型
        简化版：两阶段增长模型
        """
        eps = data.get('eps', 0)
        growth = data.get('growth_rate', 0.10)
        terminal_growth = data.get('terminal_growth', 0.03)
        wacc = data.get('wacc', 0.09)
        
        # 预测未来5年现金流
        fcf_list = []
        current_fcf = eps
        
        for year in range(1, 6):
            current_fcf *= (1 + growth)
            fcf_list.append(current_fcf)
        
        # 折现
        pv = 0
        for i, fcf in enumerate(fcf_list, 1):
            pv += fcf / ((1 + wacc) ** i)
        
        # 终值
        terminal_value = fcf_list[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        pv_terminal = terminal_value / ((1 + wacc) ** 5)
        
        fair_value = pv + pv_terminal
        return fair_value
    
    def _position_sizing(self, score: float, discount: float) -> float:
        """仓位管理"""
        # 基础仓位由评分决定
        if score >= 80: base_size = 0.15
        elif score >= 70: base_size = 0.10
        elif score >= 60: base_size = 0.05
        else: base_size = 0
        
        # 安全边际调整
        if discount > 0.30: multiplier = 1.5  # 深度低估，加大仓位
        elif discount > 0.15: multiplier = 1.2
        elif discount > 0: multiplier = 1.0
        else: multiplier = 0.5  # 高估，减仓
        
        return min(base_size * multiplier, 0.20)  # 单只股票最大20%
    
    def _generate_signal(self, score: float, discount: float) -> tuple:
        """生成投资信号"""
        reasons = []
        
        if score >= 80 and discount > 0.15:
            signal = 'STRONG_BUY'
            reasons.append(f'基本面优秀 ({score}分)')
            reasons.append(f'深度低估 ({discount*100:.1f}%)')
        elif score >= 70 and discount > 0:
            signal = 'BUY'
            reasons.append(f'基本面良好 ({score}分)')
            reasons.append(f'存在折扣 ({discount*100:.1f}%)')
        elif score >= 60:
            signal = 'HOLD'
            reasons.append('基本面尚可，等待更好价格')
        else:
            signal = 'SELL'
            reasons.append('基本面一般或高估')
        
        return signal, reasons
    
    def scan_watchlist(self, tickers: List[str]) -> List[ValueSignal]:
        """扫描观察列表"""
        results = []
        for ticker in tickers:
            try:
                signal = self.analyze(ticker)
                results.append(signal)
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
        
        # 按评分排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results

# 测试
if __name__ == '__main__':
    skill = ValueInvestingSkill()
    
    print("="*70)
    print("🎯 价值投资框架 - 信号扫描")
    print("="*70)
    
    watchlist = ['AAPL', 'MSFT', 'NVDA']
    signals = skill.scan_watchlist(watchlist)
    
    for signal in signals:
        print(f"\n{signal.ticker}")
        print(f"  信号: {signal.signal}")
        print(f"  评分: {signal.score}/100")
        print(f"  公允价值: ${signal.fair_value:.2f}")
        print(f"  当前价格: ${signal.current_price:.2f}")
        print(f"  折扣率: {signal.discount*100:+.1f}%")
        print(f"  建议仓位: {signal.position_size*100:.0f}%")
        print(f"  原因: {', '.join(signal.reasons)}")
    
    print("\n" + "="*70)
