#!/usr/bin/env python3
"""
每日10:00美股盘前分析
输出: 重点标的 + 今日策略
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager')

from datetime import datetime
from skills.value_investing_v2 import ValueInvestingSkill
from skills.technical_analysis import TechnicalAnalysisSkill
from skills.market_sentiment_v2 import MarketSentimentSkill

class PremarketAnalyzer:
    """盘前分析器"""
    
    def __init__(self):
        self.value = ValueInvestingSkill()
        self.technical = TechnicalAnalysisSkill()
        self.sentiment = MarketSentimentSkill()
        
        # 核心持仓列表
        self.watchlist = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'AMZN', 'META', 'AMD']
    
    def analyze(self) -> str:
        """生成盘前分析报告"""
        lines = [
            f"📈 美股盘前分析 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "="*50,
            ""
        ]
        
        # 市场情绪
        sentiment = self.sentiment.analyze()
        lines.extend([
            f"🎯 市场情绪: {sentiment.overall_rating}",
            f"💰 建议仓位: 股票{sentiment.target_equity_ratio*100:.0f}%",
            f"⚠️ 预警指标: {sentiment.warning_count}/5",
            ""
        ])
        
        # 个股扫描
        lines.append("📊 重点标的扫描:")
        lines.append("-"*50)
        
        buy_signals = []
        hold_signals = []
        sell_signals = []
        
        for ticker in self.watchlist:
            try:
                value = self.value.analyze(ticker)
                tech = self.technical.analyze(ticker)
                
                # 综合判断
                if value.rating in ['A', 'B'] and tech.trend.value.startswith('UP'):
                    buy_signals.append((ticker, value, tech))
                elif value.rating == 'D' or tech.trend.value.startswith('DOWN'):
                    sell_signals.append((ticker, value, tech))
                else:
                    hold_signals.append((ticker, value, tech))
            except Exception as e:
                lines.append(f"  {ticker}: 分析失败 ({e})")
        
        # 输出买入信号
        if buy_signals:
            lines.append("\n🟢 买入/增持:")
            for ticker, value, tech in sorted(buy_signals, key=lambda x: x[1].score, reverse=True)[:3]:
                lines.append(f"  {ticker}: 评级{value.rating} | 趋势{tech.trend.value} | 目标仓位{value.score/100*15:.0f}%")
                if value.reasons:
                    lines.append(f"    └─ {value.reasons[0]}")
        
        # 输出卖出信号
        if sell_signals:
            lines.append("\n🔴 卖出/减持:")
            for ticker, value, tech in sell_signals:
                lines.append(f"  {ticker}: 评级{value.rating} | 趋势{tech.trend.value}")
                if value.red_flags:
                    lines.append(f"    └─ {value.red_flags[0]}")
        
        # 今日策略
        lines.extend([
            "",
            "💡 今日策略:",
            "-"*50,
            f"1. {sentiment.position_adjustment}",
            "2. 关注盘前新闻和期货走势",
            "3. 财报季注意个股波动",
            "",
            f"⏰ 关键时间点:",
            f"  • 21:30 美股开盘",
            f"  • 22:30 美国经济数据",
            f"  • 盘后 英伟达等财报",
        ])
        
        return '\n'.join(lines)
    
    def send_report(self, report: str):
        """发送报告"""
        print(report)
        # TODO: Telegram推送

if __name__ == '__main__':
    analyzer = PremarketAnalyzer()
    report = analyzer.analyze()
    analyzer.send_report(report)
    
    # 保存
    with open(f'/root/.openclaw/workspace/learning/fund_manager/reports/premarket_{datetime.now().strftime("%Y%m%d")}.txt', 'w') as f:
        f.write(report)
