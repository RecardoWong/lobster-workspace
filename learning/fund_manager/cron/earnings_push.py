#!/usr/bin/env python3
"""
财报速读定时推送示例
用法: python3 cron/earnings_push.py AAPL
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from earnings_reader.earnings_reader import EarningsReader


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 earnings_push.py <股票代码>")
        print("示例:")
        print("  python3 earnings_push.py AAPL    # 美股")
        print("  python3 earnings_push.py 00700   # 港股")
        print("  python3 earnings_push.py 600519  # A股")
        return 1
    
    ticker = sys.argv[1]
    
    print(f"📊 财报速读推送 - {ticker}")
    print("=" * 60)
    
    # 初始化财报速读
    reader = EarningsReader()
    
    # 分析并推送
    print(f"\n🔍 分析 {ticker} 财报...")
    report = reader.analyze(ticker, push_to_telegram=True)
    
    if report:
        # 同时打印到本地
        reader.print_report(report)
        print("\n✅ 推送成功")
        return 0
    else:
        print("\n❌ 分析失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
