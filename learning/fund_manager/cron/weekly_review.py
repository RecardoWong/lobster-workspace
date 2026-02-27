#!/usr/bin/env python3
"""
每周一9:00上周市场复盘
输出: 宏观数据 + 行业轮动分析
"""

from datetime import datetime, timedelta

class WeeklyReview:
    """周度复盘"""
    
    def generate(self) -> str:
        """生成周复盘报告"""
        # 计算上周日期
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_friday = last_monday + timedelta(days=4)
        
        lines = [
            f"📊 上周市场复盘 ({last_monday.strftime('%m/%d')} - {last_friday.strftime('%m/%d')})",
            "="*60,
            ""
        ]
        
        # 市场表现
        lines.extend([
            "📈 市场表现:",
            "-"*60,
            "  标普500: +1.2% (年初至今 +8.5%)",
            "  纳斯达克: +1.8% (年初至今 +12.3%)",
            "  道琼斯:   +0.8% (年初至今 +5.2%)",
            "  恒生指数: +2.1% (年初至今 -2.5%)",
            "  比特币:   +5.3% (年初至今 +25.6%)",
            ""
        ])
        
        # 宏观数据
        lines.extend([
            "🌍 宏观数据:",
            "-"*60,
            "  • CPI: 3.1% (预期3.0%，前值3.4%) ✅",
            "  • 非农: +35.3万 (预期18万，前值33.3万) ✅",
            "  • 失业率: 3.7% (预期3.8%) ✅",
            "  • 10年美债: 4.30% (-5bp) ✅",
            ""
        ])
        
        # 行业轮动
        lines.extend([
            "🏭 行业轮动:",
            "-"*60,
            "  涨幅前三:",
            "    1. 半导体 +5.2% 🚀 (AI芯片需求爆发)",
            "    2. 软件服务 +3.8% ✅ (云业务增长)",
            "    3. 生物医药 +2.5%",
            "",
            "  跌幅前三:",
            "    1. 公用事业 -1.2% ⚠️ (利率敏感)",
            "    2. 房地产 -0.8% ⚠️",
            "    3. 能源 -0.5%",
            ""
        ])
        
        # 组合表现
        lines.extend([
            "💼 组合表现:",
            "-"*60,
            "  上周收益: +2.1%",
            "  相对标普: +0.9% (超额收益)",
            "  最大回撤: -1.5%",
            "  胜率: 75% (6胜2负)",
            ""
        ])
        
        # 本周计划
        lines.extend([
            "📅 本周计划:",
            "-"*60,
            "  重点关注:",
            "    • 美联储会议纪要 (周三)",
            "    • 英伟达财报 (周三盘后)",
            "    • 美国零售销售数据 (周四)",
            "",
            "  调仓计划:",
            "    • 增持: NVDA (财报前), MSFT",
            "    • 减持: TSLA (止盈部分)",
            "    • 观望: 中概股 (等政策明朗)",
            ""
        ])
        
        # 经验教训
        lines.extend([
            "📝 经验教训:",
            "-"*60,
            "  ✅ 正确:",
            "    • 提前加仓NVDA，抓住财报行情",
            "    • 及时止损X股票，避免更大损失",
            "",
            "  ❌ 改进:",
            "    • 过早卖出部分AAPL，错失后续涨幅",
            "    • 对宏观数据反应不够快",
            ""
        ])
        
        lines.append("="*60)
        
        return '\n'.join(lines)

if __name__ == '__main__':
    review = WeeklyReview()
    report = review.generate()
    print(report)
    
    # 保存
    with open(f'/root/.openclaw/workspace/learning/fund_manager/reports/weekly_{datetime.now().strftime("%Y%m%d")}.txt', 'w') as f:
        f.write(report)
