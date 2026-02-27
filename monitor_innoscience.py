#!/usr/bin/env python3
"""
港股监控 - 英诺赛科专用
专注跟踪英诺赛科(02577)的实时行情
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/learning/fund_manager/skills')
from tencent_finance_hk import get_hk_stock_quote_tencent
from datetime import datetime

def monitor_innoscience():
    """监控英诺赛科"""
    print("=" * 60)
    print(f"📊 英诺赛科 (02577) 实时监控")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = get_hk_stock_quote_tencent('02577')
    
    if 'error' not in result:
        price = result['price']
        change = result['change']
        change_pct = result['change_pct']
        open_price = result['open']
        high = result['high']
        low = result['low']
        volume = result['volume']
        
        emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
        
        print(f"\n{emoji} 当前价格: ${price:.2f}")
        print(f"   涨跌: {change:+.2f} ({change_pct:+.2f}%)")
        print(f"\n📊 今日行情:")
        print(f"   开盘: ${open_price:.2f}")
        print(f"   最高: ${high:.2f}")
        print(f"   最低: ${low:.2f}")
        print(f"\n💰 市值信息:")
        print(f"   总市值: {result['market_cap_total']:.0f}亿 HKD")
        print(f"   流通市值: {result['market_cap_float']:.0f}亿 HKD")
        print(f"\n📈 成交数据:")
        print(f"   成交量: {volume:,.0f} 股")
        
        # 判断涨跌幅度
        if change_pct > 5:
            print(f"\n🔥 强势上涨! 涨幅超过5%")
        elif change_pct > 0:
            print(f"\n✅ 稳步上涨")
        elif change_pct < -5:
            print(f"\n⚠️ 大幅回调，注意风险")
        elif change_pct < 0:
            print(f"\n📉 小幅下跌")
        else:
            print(f"\n➡️ 平盘")
    else:
        print(f"\n❌ 获取数据失败: {result.get('error', '未知错误')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    monitor_innoscience()
