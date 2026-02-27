#!/usr/bin/env python3
"""
历史估值对比工具
查看财报发布时的估值 vs 当前估值
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class HistoricalValuation:
    """历史估值分析器"""
    
    def __init__(self):
        self.earnings_dates = {
            # 主要公司2024年报发布日期（实际日期以公告为准）
            '600519': '2025-04-02',  # 茅台
            '000858': '2025-04-28',  # 五粮液
            '600036': '2025-03-25',  # 招行
            '300750': '2025-03-15',  # 宁德时代
            '000001': '2025-03-24',  # 平安银行
            '600809': '2025-04-26',  # 山西汾酒
        }
    
    def get_price_on_date(self, symbol: str, date: str) -> Optional[float]:
        """获取某日收盘价"""
        try:
            # 获取历史行情
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=date.replace('-', ''), end_date=date.replace('-', ''), adjust="qfq")
            if not df.empty:
                return df['收盘'].values[0]
            return None
        except:
            return None
    
    def get_eps_on_date(self, symbol: str, date: str) -> Optional[float]:
        """获取某日的TTM EPS"""
        try:
            # 简化处理：用当时的PE反推EPS
            # 实际应该用季度累计数据
            price = self.get_price_on_date(symbol, date)
            if not price:
                return None
            
            # 获取当时的PE（简化，用最新PE近似）
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == symbol]
            if not row.empty:
                current_pe = row['市盈率-动态'].values[0]
                # 简化：假设PE变化不大，用当前PE估算
                eps = price / current_pe if current_pe > 0 else None
                return eps
            return None
        except:
            return None
    
    def compare_valuation(self, symbol: str) -> Dict:
        """对比历史估值 vs 当前估值"""
        result = {
            'symbol': symbol,
            'name': '',
            'current': {},
            'at_earnings': {},
            'change': {},
            'conclusion': ''
        }
        
        # 获取当前数据
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == symbol]
            if not row.empty:
                result['name'] = row['名称'].values[0]
                current_price = row['最新价'].values[0]
                current_pe = row['市盈率-动态'].values[0]
                
                result['current'] = {
                    'price': current_price,
                    'pe': current_pe,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
        except:
            pass
        
        # 获取财报发布时数据
        earnings_date = self.earnings_dates.get(symbol)
        if earnings_date:
            price_then = self.get_price_on_date(symbol, earnings_date)
            if price_then:
                result['at_earnings'] = {
                    'price': price_then,
                    'date': earnings_date
                }
                
                # 计算变化
                if result['current'].get('price'):
                    price_change = (result['current']['price'] - price_then) / price_then * 100
                    result['change']['price_pct'] = price_change
                    
                    if price_change > 20:
                        result['conclusion'] = f"股价已涨{price_change:.1f}%，估值变贵，谨慎追高"
                    elif price_change < -20:
                        result['conclusion'] = f"股价已跌{price_change:.1f}%，估值变便宜，关注机会"
                    else:
                        result['conclusion'] = f"股价变动{price_change:.1f}%，估值合理区间"
        
        return result
    
    def format_report(self, result: Dict) -> str:
        """格式化报告"""
        lines = [
            f"\n{'='*70}",
            f"📊 {result.get('name', result['symbol'])} - 历史估值对比",
            f"{'='*70}",
            f"",
        ]
        
        current = result.get('current', {})
        at_earnings = result.get('at_earnings', {})
        change = result.get('change', {})
        
        if at_earnings:
            lines.extend([
                f"📅 财报发布时 ({at_earnings.get('date')}):",
                f"   股价: {at_earnings.get('price', 'N/A'):.2f}元",
                f"",
                f"📅 当前 ({current.get('date')}):",
                f"   股价: {current.get('price', 'N/A'):.2f}元",
                f"   PE: {current.get('pe', 'N/A'):.1f}倍",
                f"",
                f"📈 变动:",
                f"   股价变化: {change.get('price_pct', 0):+.1f}%",
                f"",
                f"💡 结论: {result.get('conclusion', '')}",
            ])
        else:
            lines.extend([
                f"📅 当前 ({current.get('date')}):",
                f"   股价: {current.get('price', 'N/A'):.2f}元",
                f"   PE: {current.get('pe', 'N/A'):.1f}倍",
                f"",
                f"⚠️ 暂无财报发布日历史数据",
            ])
        
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


def main():
    """演示"""
    print("=" * 70)
    print("📊 历史估值对比工具")
    print("对比财报发布时 vs 当前估值")
    print("=" * 70)
    
    analyzer = HistoricalValuation()
    
    # 测试股票
    test_stocks = ['600519', '000858', '300750']
    
    for symbol in test_stocks:
        result = analyzer.compare_valuation(symbol)
        print(analyzer.format_report(result))
    
    print("=" * 70)


if __name__ == "__main__":
    main()
