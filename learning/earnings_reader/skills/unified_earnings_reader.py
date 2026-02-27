#!/usr/bin/env python3
"""
统一财报速读器
支持港股、美股、A股自动识别
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/earnings_reader/skills')
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager/skills')

from typing import Dict, Optional
from hk_earnings_reader import HKStockEarningsReader as HKEarningsReader
from us_earnings_reader import USEarningsReader
from a_share_earnings_reader import AShareEarningsReader
from cninfo_akshare_reader import CNInfoAKShareReader
from tencent_finance_hk import get_hk_stock_quote_tencent

class UnifiedEarningsReader:
    """统一财报速读器 - 支持多市场"""
    
    def __init__(self):
        self.hk_reader = HKEarningsReader()
        self.us_reader = USEarningsReader()
        self.a_reader = AShareEarningsReader()
        self.cninfo_reader = CNInfoAKShareReader()  # 巨潮资讯网
    
    def detect_market(self, symbol: str) -> str:
        """
        自动识别市场
        
        Returns:
            'hk' | 'us' | 'a' | 'unknown'
        """
        symbol = symbol.upper().strip()
        
        # A股：6位数字
        if symbol.isdigit() and len(symbol) == 6:
            if symbol.startswith(('600', '601', '602', '603', '605', '688')):
                return 'a'  # 上海
            elif symbol.startswith(('000', '001', '002', '003', '300', '301')):
                return 'a'  # 深圳
            elif symbol.startswith(('8', '4')):
                return 'a'  # 北交所
        
        # 港股：5位数字
        if symbol.isdigit() and len(symbol) == 5:
            return 'hk'
        
        # 港股：代码.HK 或 纯数字
        if symbol.endswith('.HK') or (symbol.isdigit() and len(symbol) == 4):
            return 'hk'
        
        # 美股：字母代码
        if symbol.isalpha() and 1 <= len(symbol) <= 5:
            return 'us'
        
        # 带后缀的
        if '.US' in symbol or '.OQ' in symbol or '.NY' in symbol:
            return 'us'
        
        return 'unknown'
    
    def get_realtime_quote(self, symbol: str) -> Dict:
        """获取实时行情"""
        market = self.detect_market(symbol)
        
        if market == 'hk':
            # 去除.HK后缀
            code = symbol.replace('.HK', '').replace('.hk', '')
            return get_hk_stock_quote_tencent(code)
        
        elif market == 'us':
            code = symbol.replace('.US', '').replace('.us', '')
            return self.us_reader.get_stock_quote_yahoo(code)
        
        elif market == 'a':
            return self.a_reader.get_company_info(symbol)
        
        else:
            return {'error': f'无法识别市场: {symbol}'}
    
    def get_earnings_summary(self, symbol: str, use_mock: bool = True) -> str:
        """获取财报摘要"""
        market = self.detect_market(symbol)
        
        if market == 'hk':
            code = symbol.replace('.HK', '').replace('.hk', '')
            quote = get_hk_stock_quote_tencent(code)
            if 'error' not in quote:
                return f"📊 {quote['name']} ({code})\n💰 价格: ${quote['price']}\n📈 涨跌: {quote['change_pct']}%"
            else:
                return f"❌ 获取失败: {quote.get('error')}"
        
        elif market == 'us':
            code = symbol.replace('.US', '').replace('.us', '')
            if use_mock:
                # 使用模拟数据演示
                sample = {
                    "company": code,
                    "symbol": code,
                    "period": "FY2024 Q4",
                    "revenue": 221,
                    "revenue_growth_yoy": 265,
                    "net_profit": 123,
                    "profit_growth_yoy": 769,
                    "gross_margin": 76.0,
                    "net_margin": 55.6,
                    "eps": 4.93,
                    "eps_beat_percent": 12.0
                }
                analysis = self.us_reader.analyze_earnings(sample)
                return self.us_reader.format_report(analysis)
            else:
                return f"美股财报数据需接入真实数据源 (Yahoo Finance/SEC EDGAR)"
        
        elif market == 'a':
            return self.a_reader.format_summary(symbol)
        
        else:
            return f"❌ 无法识别股票代码: {symbol}"
    
    def get_dividend_history(self, symbol: str) -> str:
        """获取分红历史"""
        market = self.detect_market(symbol)
        
        if market == 'a':
            # 使用巨潮资讯网获取分红数据
            df = self.cninfo_reader.get_stock_dividend(symbol)
            if not df.empty and 'error' not in df.columns:
                lines = [f"📊 {symbol} 分红历史 ({len(df)}次):"]
                for _, row in df.head(5).iterrows():
                    lines.append(f"   • {row.get('报告时间', 'N/A')}: {row.get('实施方案分红说明', 'N/A')}")
                return "\n".join(lines)
            else:
                return f"{symbol} 无分红记录或获取失败"
        
        elif market == 'hk':
            return f"港股分红数据需接入港交所披露易"
        
        else:
            return f"美股分红数据需接入Yahoo Finance"


def demo():
    """演示统一财报速读器"""
    print("=" * 70)
    print("📊 统一财报速读器 - 多市场支持")
    print("   港股 | 美股 | A股")
    print("=" * 70)
    
    reader = UnifiedEarningsReader()
    
    # 测试1: A股
    print("\n🇨🇳 A股 - 平安银行 (000001):")
    print("-" * 70)
    print(f"市场识别: {reader.detect_market('000001')}")
    print(reader.get_dividend_history('000001'))
    
    # 测试2: 港股
    print("\n🇭🇰 港股 - 英诺赛科 (02577):")
    print("-" * 70)
    print(f"市场识别: {reader.detect_market('02577')}")
    quote = reader.get_realtime_quote('02577')
    if 'error' not in quote:
        print(f"当前价格: ${quote.get('price')}")
        print(f"涨跌: {quote.get('change_pct')}%")
    
    # 测试3: 美股
    print("\n🇺🇸 美股 - NVIDIA (NVDA):")
    print("-" * 70)
    print(f"市场识别: {reader.detect_market('NVDA')}")
    print(reader.get_earnings_summary('NVDA'))
    
    print("\n" + "=" * 70)
    print("💡 使用方式:")
    print("   reader.get_realtime_quote('000001')    # A股")
    print("   reader.get_realtime_quote('02577')     # 港股")
    print("   reader.get_realtime_quote('NVDA')      # 美股")
    print("=" * 70)


if __name__ == "__main__":
    demo()
