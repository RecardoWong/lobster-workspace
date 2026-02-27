#!/usr/bin/env python3
"""
每日市场摘要 - 整合FRED宏观数据 + 市场数据
定时任务: 每天 8:00 AM
推送: Telegram
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from fred_client import FREDClient, _load_env
from skills.macro_liquidity_v2 import MacroLiquiditySkill
import json

# 加载API Key
_load_env()

def get_fred_summary():
    """获取FRED宏观数据摘要"""
    skill = MacroLiquiditySkill()
    signal = skill.analyze()
    
    return {
        "rating": signal.overall_rating,
        "net_liquidity": signal.net_liquidity,
        "liquidity_change": signal.liquidity_change,
        "fed_assets": signal.fed_balance_sheet,
        "sofr": signal.sofr_rate,
        "yield_spread": signal.yield_spread,
        "risks": signal.risks,
        "action": signal.action,
    }

def format_daily_summary(fred_data):
    """格式化每日市场摘要"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"📊 每日市场摘要 ({now})",
        "=" * 40,
        "",
        "🌍 宏观流动性",
        f"  评级: {fred_data['rating']}",
        f"  美联储资产: ${fred_data['fed_assets']:.0f}B",
        f"  净流动性: ${fred_data['net_liquidity']:.0f}B",
    ]
    
    if fred_data['liquidity_change'] != 0:
        change = fred_data['liquidity_change'] * 100
        emoji = "📉" if change < 0 else "📈"
        lines.append(f"  周变化: {emoji} {change:+.2f}%")
    
    lines.extend([
        f"  SOFR利率: {fred_data['sofr']:.2f}%",
        f"  收益率利差: {fred_data['yield_spread']:+.2f}%",
        "",
        "💡 操作建议",
        f"  {fred_data['action']}",
    ])
    
    if fred_data['risks']:
        lines.extend([
            "",
            "⚠️ 风险提示",
        ])
        for risk in fred_data['risks']:
            lines.append(f"  {risk}")
    
    lines.extend([
        "",
        "=" * 40,
        "📈 查看详细数据:",
        "  https://fred.stlouisfed.org/",
    ])
    
    return "\n".join(lines)

def main():
    """主函数 - 生成并输出每日摘要"""
    try:
        print("正在获取FRED数据...")
        fred_data = get_fred_summary()
        
        summary = format_daily_summary(fred_data)
        print(summary)
        
        # 保存JSON供其他系统使用
        output = {
            "timestamp": datetime.now().isoformat(),
            "fred": fred_data,
        }
        
        output_path = os.path.expanduser("~/.openclaw/workspace/learning/fund_manager/data/daily_summary.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 数据已保存: {output_path}")
        
        return summary
        
    except Exception as e:
        error_msg = f"❌ 获取数据失败: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    main()
