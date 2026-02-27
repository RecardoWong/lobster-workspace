#!/usr/bin/env python3
"""
港股财报速读器 - 真实数据版
接入东方财富实时行情数据
"""

import json
import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager/skills')

from datetime import datetime
from typing import Dict, List, Optional
from hk_earnings_connector import HKEarningsDataConnector

class HKEarningsReaderReal:
    """港股财报速读器 - 真实数据版"""
    
    # 评分权重
    WEIGHTS = {
        "growth": 0.30,
        "profitability": 0.25,
        "efficiency": 0.20,
        "safety": 0.15,
        "valuation": 0.10
    }
    
    def __init__(self):
        self.data_connector = HKEarningsDataConnector()
    
    def get_real_time_analysis(self, stock_code: str) -> Dict:
        """获取实时分析"""
        # 获取实时行情
        quote = self.data_connector.get_stock_quote_eastmoney(stock_code)
        
        # 获取公司资料
        profile = self.data_connector.get_company_profile(stock_code)
        
        # 构建分析结果
        analysis = {
            "stock_code": stock_code,
            "company_name": profile.get("name", ""),
            "sector": profile.get("sector", ""),
            "analysis_time": datetime.now().isoformat(),
            "quote": quote,
            "profile": profile,
            "market_data": {}
        }
        
        # 添加市场数据解读
        if "error" not in quote:
            price = quote.get("price", 0)
            change_pct = quote.get("change_pct", 0)
            
            analysis["market_data"] = {
                "current_price": price,
                "daily_change_pct": change_pct,
                "trend": "上涨" if change_pct > 0 else "下跌" if change_pct < 0 else "平盘",
                "volatility": "高" if abs(change_pct) > 5 else "中" if abs(change_pct) > 2 else "低"
            }
        
        return analysis
    
    def format_realtime_report(self, analysis: Dict) -> str:
        """格式化实时报告"""
        lines = [
            f"📊 {analysis['company_name']} ({analysis['stock_code']}) 实时行情",
            f"📅 分析时间: {analysis['analysis_time'][:19]}",
            "=" * 60,
            ""
        ]
        
        # 公司资料
        profile = analysis.get("profile", {})
        lines.extend([
            "🏢 公司资料",
            f"• 行业: {profile.get('sector', 'N/A')} - {profile.get('sub_sector', 'N/A')}",
            f"• 上市日期: {profile.get('listing_date', 'N/A')}",
            f"• 市值: {profile.get('market_cap_hkd', 'N/A')}",
            ""
        ])
        
        # 实时行情
        quote = analysis.get("quote", {})
        if "error" not in quote:
            price = quote.get("price", 0)
            change_pct = quote.get("change_pct", 0)
            emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
            
            lines.extend([
                "💹 实时行情",
                f"{emoji} 当前价格: ${price:.2f}",
                f"   涨跌: {change_pct:+.2f}%",
                f"   成交量: {quote.get('volume', 'N/A')}",
                ""
            ])
        else:
            lines.extend([
                "💹 实时行情",
                f"⚠️ 获取失败: {quote.get('error', 'Unknown')}",
                ""
            ])
        
        # 市场解读
        market_data = analysis.get("market_data", {})
        if market_data:
            lines.extend([
                "📈 市场解读",
                f"• 今日趋势: {market_data.get('trend', 'N/A')}",
                f"• 波动程度: {market_data.get('volatility', 'N/A')}",
                ""
            ])
        
        # 备注（如果是关注股票）
        if profile.get("description"):
            lines.extend([
                "💡 公司简介",
                f"{profile.get('description')}",
                ""
            ])
        
        if profile.get("key_products"):
            lines.extend([
                "🎯 核心产品",
                f"• {', '.join(profile.get('key_products', []))}",
                ""
            ])
        
        lines.extend([
            "=" * 60,
            "💡 数据来源: 东方财富 + 港交所披露易"
        ])
        
        return "\n".join(lines)
    
    def get_watchlist_report(self) -> str:
        """获取关注列表报告"""
        stocks = self.data_connector.get_stock_list_hk()
        
        lines = [
            "📋 港股关注列表 - 实时行情",
            f"📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            ""
        ]
        
        # 按行业分组
        sectors = {}
        for stock in stocks:
            sector = stock.get("sector", "其他")
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(stock)
        
        # 获取行情并显示
        for sector, sector_stocks in sectors.items():
            lines.append(f"\n【{sector}】")
            
            for stock in sector_stocks[:3]:  # 每个行业显示前3个
                code = stock["code"]
                quote = self.data_connector.get_stock_quote_eastmoney(code)
                
                if "error" not in quote:
                    price = quote.get("price", 0)
                    change_pct = quote.get("change_pct", 0)
                    emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
                    focus = " ⭐" if stock.get("focus") else ""
                    
                    lines.append(f"  {emoji} {stock['name']}({code}): ${price:.2f} ({change_pct:+.2f}%){focus}")
                else:
                    lines.append(f"  ⚠️ {stock['name']}({code}): 数据获取失败")
        
        lines.extend([
            "",
            "=" * 60,
            "💡 数据来源: 东方财富"
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 测试财报速读器（真实数据版）"""
    print("=" * 60)
    print("📊 港股财报速读器 - 真实数据版")
    print("   接入东方财富实时行情")
    print("=" * 60)
    
    reader = HKEarningsReaderReal()
    
    # 测试1: 英诺赛科实时分析
    print("\n🔍 英诺赛科(02577) 实时分析:")
    print("-" * 60)
    analysis = reader.get_real_time_analysis("02577")
    report = reader.format_realtime_report(analysis)
    print(report)
    
    # 测试2: 关注列表报告
    print("\n" + "=" * 60)
    print("\n📋 关注列表报告:")
    print("-" * 60)
    watchlist_report = reader.get_watchlist_report()
    print(watchlist_report)
    
    # 保存数据
    import os
    output_dir = "/root/.openclaw/workspace/learning/earnings_reader/data"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存英诺赛科分析
    output_path = f"{output_dir}/innoscience_realtime_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 数据已保存: {output_path}")


if __name__ == "__main__":
    main()
