#!/usr/bin/env python3
"""
投资Agent主控制器
整合所有Skills，统一输出投资决策
"""

import asyncio
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

# 导入所有Skills
from skills.value_investing import ValueInvestingSkill
from skills.btc_bottom import BTCBottomSkill
from skills.market_sentiment import MarketSentimentSkill
from skills.macro_liquidity import MacroLiquiditySkill
from skills.earnings_analyzer import EarningsAnalyzerSkill
from skills.technical_analysis import TechnicalAnalysisSkill

@dataclass
class InvestmentDecision:
    ticker: str
    overall_signal: str      # STRONG_BUY/BUY/HOLD/SELL
    confidence: str          # HIGH/MEDIUM/LOW
    target_allocation: float # 目标仓位
    current_allocation: float # 当前仓位
    action: str              # ADD/REDUCE/HOLD/EXIT
    entry_price: float
    stop_loss: float
    take_profit: float
    reasons: List[str]
    risk_level: str

class InvestmentAgent:
    """
    投资Agent主控制器
    协调所有Skills，生成最终投资决策
    """
    
    def __init__(self):
        # 初始化所有Skills
        self.value_skill = ValueInvestingSkill()
        self.btc_skill = BTCBottomSkill()
        self.sentiment_skill = MarketSentimentSkill()
        self.macro_skill = MacroLiquiditySkill()
        self.earnings_skill = EarningsAnalyzerSkill()
        self.technical_skill = TechnicalAnalysisSkill()
        
        # Skills权重配置
        self.skill_weights = {
            'value': 0.30,        # 基本面权重最高
            'technical': 0.25,    # 技术面次之
            'macro': 0.20,        # 宏观环境
            'sentiment': 0.15,    # 情绪面
            'earnings': 0.10      # 财报季动态调整
        }
    
    def analyze_stock(self, ticker: str, is_earnings_season: bool = False) -> InvestmentDecision:
        """
        分析单只股票，整合所有Skills信号
        """
        print(f"\n🔍 分析 {ticker}...")
        
        # 1. 基本面分析
        print("  ├─ 基本面分析...")
        value_signal = self.value_skill.analyze(ticker)
        
        # 2. 技术面分析
        print("  ├─ 技术面分析...")
        tech_signal = self.technical_skill.analyze(ticker)
        
        # 3. 情绪面分析 (对个股用整体市场情绪)
        print("  ├─ 情绪面分析...")
        sentiment_signal = self.sentiment_skill.analyze()
        
        # 4. 财报分析 (如果是财报季)
        earnings_score = 50  # 中性默认值
        if is_earnings_season:
            print("  ├─ 财报分析...")
            try:
                earnings_signal = self.earnings_skill.analyze(ticker)
                if earnings_signal.surprise_type.value == 'BEAT_BOTH':
                    earnings_score = 85
                elif 'BEAT' in earnings_signal.surprise_type.value:
                    earnings_score = 70
                elif 'MISS' in earnings_signal.surprise_type.value:
                    earnings_score = 30
            except:
                pass
        
        # 5. 宏观环境 (全局影响)
        print("  └─ 宏观环境...")
        macro_signal = self.macro_skill.analyze()
        
        # 综合评分
        composite_score = self._calculate_composite_score(
            value_signal, tech_signal, sentiment_signal, 
            macro_signal, earnings_score, is_earnings_season
        )
        
        # 生成最终决策
        decision = self._generate_decision(
            ticker, composite_score, value_signal, tech_signal, 
            earnings_score if is_earnings_season else None
        )
        
        return decision
    
    def _calculate_composite_score(self, value, technical, sentiment, macro, earnings, is_earnings) -> float:
        """计算综合评分"""
        # 标准化各维度到0-100
        value_score = value.score
        tech_score = 70 if technical.signal_strength == 'STRONG' else \
                     50 if technical.signal_strength == 'MEDIUM' else 30
        sentiment_score = sentiment.fear_greed_index
        macro_score = macro.liquidity_score
        
        # 动态权重
        weights = self.skill_weights.copy()
        if is_earnings:
            weights['earnings'] = 0.20  # 财报季提高财报权重
            weights['value'] = 0.25
        
        # 情绪逆向调整 (极度贪婪时降低情绪权重)
        if sentiment_score > 80:
            weights['sentiment'] = 0.05
        
        # 计算加权得分
        composite = (
            value_score * weights['value'] +
            tech_score * weights['technical'] +
            sentiment_score * weights['sentiment'] +
            macro_score * weights['macro'] +
            earnings * weights['earnings']
        )
        
        return min(max(composite, 0), 100)
    
    def _generate_decision(self, ticker, composite_score, value, technical, earnings) -> InvestmentDecision:
        """生成投资决策"""
        
        # 确定信号类型
        if composite_score >= 80:
            signal = 'STRONG_BUY'
            confidence = 'HIGH'
            target_alloc = 0.15
        elif composite_score >= 70:
            signal = 'BUY'
            confidence = 'MEDIUM'
            target_alloc = 0.10
        elif composite_score >= 50:
            signal = 'HOLD'
            confidence = 'LOW'
            target_alloc = 0.05
        else:
            signal = 'SELL'
            confidence = 'HIGH'
            target_alloc = 0
        
        # 确定操作
        current_alloc = 0.08  # 假设当前仓位8%
        if target_alloc > current_alloc + 0.03:
            action = 'ADD'
        elif target_alloc < current_alloc - 0.03:
            action = 'REDUCE'
        else:
            action = 'HOLD'
        
        # 风险等级
        risk = 'LOW' if composite_score > 70 and technical.trend.value.startswith('UP') else \
               'MEDIUM' if composite_score > 50 else 'HIGH'
        
        # 原因汇总
        reasons = []
        if value.discount > 0:
            reasons.append(f"估值合理，折扣{value.discount*100:.1f}%")
        if technical.trend.value.startswith('UP'):
            reasons.append(f"技术面向好：{technical.trend.value}")
        if earnings and earnings > 70:
            reasons.append("财报超预期")
        
        return InvestmentDecision(
            ticker=ticker,
            overall_signal=signal,
            confidence=confidence,
            target_allocation=target_alloc,
            current_allocation=current_alloc,
            action=action,
            entry_price=technical.entry_price,
            stop_loss=technical.stop_loss,
            take_profit=technical.take_profit,
            reasons=reasons,
            risk_level=risk
        )
    
    def analyze_crypto(self) -> Dict:
        """分析加密货币"""
        return self.btc_skill.analyze()
    
    def generate_daily_report(self, watchlist: List[str]) -> str:
        """生成每日投资报告"""
        report_lines = [
            "="*70,
            f"📊 投资Agent每日报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "="*70
        ]
        
        # 宏观环境
        macro = self.macro_skill.analyze()
        report_lines.extend([
            "\n🌍 宏观环境:",
            f"  流动性评分: {macro.liquidity_score:.0f}/100",
            f"  美联储立场: {macro.fed_policy}",
            f"  配置建议: {macro.signal}"
        ])
        
        # 市场情绪
        sentiment = self.sentiment_skill.analyze()
        report_lines.extend([
            "\n📈 市场情绪:",
            f"  恐惧贪婪指数: {sentiment.fear_greed_index:.0f}/100",
            f"  VIX: {sentiment.vix}",
            f"  解读: {sentiment.interpretation}"
        ])
        
        # 加密货币
        btc = self.analyze_crypto()
        report_lines.extend([
            "\n₿ 加密货币:",
            f"  BTC底部概率: {btc.bottom_probability:.0f}%",
            f"  信号强度: {btc.signal_strength}",
            f"  建议: {btc.accumulation_plan.get('strategy', 'WAIT')}"
        ])
        
        # 个股分析
        report_lines.extend(["\n📋 股票分析:"])
        
        buy_list = []
        hold_list = []
        sell_list = []
        
        for ticker in watchlist:
            decision = self.analyze_stock(ticker)
            
            if decision.overall_signal in ['STRONG_BUY', 'BUY']:
                buy_list.append(decision)
            elif decision.overall_signal == 'SELL':
                sell_list.append(decision)
            else:
                hold_list.append(decision)
        
        # 输出买入建议
        if buy_list:
            report_lines.append("\n🟢 买入建议:")
            for d in sorted(buy_list, key=lambda x: x.target_allocation, reverse=True):
                report_lines.append(f"  {d.ticker}: {d.overall_signal} "
                                   f"(仓位{d.target_allocation*100:.0f}%, 置信度{d.confidence})")
                report_lines.append(f"    原因: {', '.join(d.reasons)}")
                report_lines.append(f"    入场: ${d.entry_price:.2f}, 止损: ${d.stop_loss:.2f}")
        
        # 输出卖出建议
        if sell_list:
            report_lines.append("\n🔴 卖出建议:")
            for d in sell_list:
                report_lines.append(f"  {d.ticker}: {d.overall_signal}")
        
        report_lines.extend(["\n" + "="*70])
        
        return '\n'.join(report_lines)

# 测试
if __name__ == '__main__':
    agent = InvestmentAgent()
    
    print("="*70)
    print("🤖 投资Agent - 整合测试")
    print("="*70)
    
    watchlist = ['AAPL', 'MSFT', 'NVDA', 'TSLA']
    
    # 生成完整报告
    report = agent.generate_daily_report(watchlist)
    print(report)
    
    # 详细分析一只股票
    print("\n" + "="*70)
    print("📊 NVDA 详细分析")
    print("="*70)
    
    nvda = agent.analyze_stock('NVDA', is_earnings_season=True)
    print(f"\n综合信号: {nvda.overall_signal}")
    print(f"置信度: {nvda.confidence}")
    print(f"目标仓位: {nvda.target_allocation*100:.0f}%")
    print(f"操作建议: {nvda.action}")
    print(f"入场价: ${nvda.entry_price:.2f}")
    print(f"止损: ${nvda.stop_loss:.2f}")
    print(f"止盈: ${nvda.take_profit:.2f}")
    print(f"原因: {', '.join(nvda.reasons)}")
