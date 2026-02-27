#!/usr/bin/env python3
"""
基金经理系统定时推送脚本
每天早上8:00推送每日市场扫描
支持手动运行: python3 cron/daily_fund_manager_push.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fund_manager import FundManager
from datetime import datetime


def main():
    """主函数"""
    print(f"🚀 基金经理系统定时推送 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 初始化基金经理系统
    manager = FundManager()
    
    # 执行每日市场扫描并推送
    print("\n📊 开始每日市场扫描...")
    report = manager.daily_market_scan(push_to_telegram=True)
    
    # 同时打印到本地
    manager.print_daily_report(report)
    
    print("\n✅ 推送完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
