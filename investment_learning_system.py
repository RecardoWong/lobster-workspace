#!/usr/bin/env python3
"""
投资学习系统 - 主控脚本
整合所有功能：财报、技术、市场监控、产业链
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/earnings_reader/skills')
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager/skills')
sys.path.insert(0, '/root/.openclaw/workspace/learning/technical_analysis/skills')
sys.path.insert(0, '/root/.openclaw/workspace/learning/industry_chain/skills')

from unified_earnings_reader import UnifiedEarningsReader
from a_share_market_monitor import AShareMarketMonitor
from kpattern_recognizer import KPatternRecognizer, Candle
from ma_system_analyzer import MASystemAnalyzer
from volume_price_analyzer import VolumePriceAnalyzer, PriceVolumeData
from ai_datacenter_analyzer_real import AIDataCenterChain
import akshare as ak
import json
from datetime import datetime

class InvestmentLearningSystem:
    """投资学习系统主控"""
    
    def __init__(self):
        self.earnings_reader = UnifiedEarningsReader()
        self.market_monitor = AShareMarketMonitor()
        self.kpattern = KPatternRecognizer()
        self.ma_analyzer = MASystemAnalyzer()
        self.vp_analyzer = VolumePriceAnalyzer()
        self.chain_analyzer = AIDataCenterChain()
    
    # ========== 1. 财报分析 ==========
    
    def analyze_stock(self, symbol: str) -> str:
        """综合分析一只股票"""
        lines = [
            f"\n{'='*70}",
            f"📊 股票综合分析: {symbol}",
            f"{'='*70}"
        ]
        
        # 基本信息
        lines.append("\n1️⃣ 基本信息:")
        quote = self.earnings_reader.get_realtime_quote(symbol)
        if 'error' not in quote:
            lines.append(f"   价格: {quote.get('price', 'N/A')}")
            lines.append(f"   涨跌: {quote.get('change_pct', 'N/A')}%")
        
        # 财报摘要
        lines.append("\n2️⃣ 财报摘要:")
        summary = self.earnings_reader.get_earnings_summary(symbol)
        lines.append(summary[:500] + "..." if len(summary) > 500 else summary)
        
        # 分红历史 (仅A股)
        market = self.earnings_reader.detect_market(symbol)
        if market == 'a':
            lines.append("\n3️⃣ 分红历史:")
            dividend = self.earnings_reader.get_dividend_history(symbol)
            lines.append(dividend[:300] + "..." if len(dividend) > 300 else dividend)
        
        lines.append(f"\n{'='*70}\n")
        return "\n".join(lines)
    
    # ========== 2. 技术分析 ==========
    
    def technical_analysis(self, prices: list, volumes: list = None) -> str:
        """技术分析"""
        lines = [
            f"\n{'='*70}",
            f"📈 技术分析",
            f"{'='*70}"
        ]
        
        # K线形态
        if len(prices) >= 3:
            candles = [Candle(open=p, high=p*1.02, low=p*0.98, close=p) for p in prices[-3:]]
            patterns = self.kpattern.recognize(candles)
            
            lines.append("\n1️⃣ K线形态:")
            if patterns:
                for p in patterns:
                    lines.append(f"   • {p['name']} ({p['type']})")
                    lines.append(f"     信号: {p['signal']}")
            else:
                lines.append("   未识别到明显形态")
        
        # 均线分析
        if len(prices) >= 60:
            lines.append("\n2️⃣ 均线系统:")
            ma_result = self.ma_analyzer.analyze(prices)
            if 'error' not in ma_result:
                for signal in ma_result.get('signals', []):
                    lines.append(f"   • {signal.get('type', 'N/A')}")
        
        # 量价分析
        if volumes and len(volumes) == len(prices):
            lines.append("\n3️⃣ 量价关系:")
            data = [PriceVolumeData(price=p, volume=v) for p, v in zip(prices[-20:], volumes[-20:])]
            vp_result = self.vp_analyzer.analyze(data)
            if 'error' not in vp_result:
                lines.append(f"   趋势强度: {vp_result.get('trend_strength', 'N/A')}/100")
                for signal in vp_result.get('signals', []):
                    lines.append(f"   • {signal.get('type', 'N/A')}")
        
        lines.append(f"\n{'='*70}\n")
        return "\n".join(lines)
    
    # ========== 3. 市场监控 ==========
    
    def market_overview(self) -> str:
        """市场概览"""
        return self.market_monitor.get_market_sentiment_report()
    
    def fund_flow(self, stock_code: str = None) -> str:
        """资金流向分析"""
        lines = [
            f"\n{'='*70}",
            f"💰 资金流向分析",
            f"{'='*70}"
        ]
        
        if stock_code:
            # 个股资金流向
            lines.append(f"\n📊 {stock_code} 资金流向:")
            df = self.market_monitor.get_fund_flow_stock(stock_code)
            if not df.empty:
                lines.append(df.head().to_string())
        else:
            # 行业资金流向
            lines.append("\n📊 行业资金流向 (Top 5):")
            df = self.market_monitor.get_fund_flow_industry()
            if not df.empty:
                for _, row in df.head(5).iterrows():
                    name = row.get('名称', 'N/A')
                    lines.append(f"   • {name}")
        
        lines.append(f"\n{'='*70}\n")
        return "\n".join(lines)
    
    # ========== 4. 产业链分析 ==========
    
    def industry_chain(self, industry: str = "ai_datacenter") -> str:
        """产业链分析"""
        if industry == "ai_datacenter":
            result = self.chain_analyzer.analyze_chain()
            return self.chain_analyzer.format_report(result)
        else:
            return f"暂不支持 {industry} 产业链分析"
    
    # ========== 5. 快速查询 ==========
    
    def quick_query(self, symbol: str) -> dict:
        """快速查询所有信息"""
        return {
            "symbol": symbol,
            "market": self.earnings_reader.detect_market(symbol),
            "quote": self.earnings_reader.get_realtime_quote(symbol),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """演示投资学习系统"""
    print("=" * 80)
    print("🎓 投资学习系统 - 主控演示")
    print("   财报 | 技术 | 市场监控 | 产业链")
    print("=" * 80)
    
    system = InvestmentLearningSystem()
    
    # 演示1: A股分析
    print("\n📊 演示1: 平安银行 (000001) 综合分析")
    print(system.analyze_stock('000001'))
    
    # 演示2: 技术分析
    print("\n📈 演示2: 技术分析")
    sample_prices = [100, 102, 101, 105, 108, 110, 108, 105, 102, 100]
    sample_volumes = [1000, 1200, 1100, 1500, 2000, 1800, 1500, 1200, 1000, 800]
    print(system.technical_analysis(sample_prices, sample_volumes))
    
    # 演示3: 市场监控
    print("\n💰 演示3: 市场监控")
    print(system.market_overview())
    
    # 演示4: 产业链
    print("\n🏭 演示4: AI数据中心产业链")
    print(system.industry_chain())
    
    # 演示5: 港股
    print("\n📊 演示5: 英诺赛科 (02577)")
    print(system.analyze_stock('02577'))
    
    print("\n" + "=" * 80)
    print("✅ 演示完成!")
    print("\n使用示例:")
    print("  from investment_learning_system import InvestmentLearningSystem")
    print("  system = InvestmentLearningSystem()")
    print("  system.analyze_stock('000001')")
    print("  system.market_overview()")
    print("=" * 80)


if __name__ == "__main__":
    main()
