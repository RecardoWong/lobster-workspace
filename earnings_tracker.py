#!/usr/bin/env python3
"""
AI Earnings Tracker
追踪科技/AI公司财报，提供预告、提醒和摘要
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class EarningsCalendar:
    """财报日历"""
    
    def __init__(self):
        self.earnings_data = {
            'NVTS': {
                'name': '纳微半导体',
                'symbol': 'NVTS',
                'exchange': 'NASDAQ',
                'next_earnings': '2026-02-24',
                'quarter': 'Q4 2025',
                'time': 'after_market_close',  # 收盘后
                'description': '氮化镓功率半导体',
                'importance': 'high',  # 与英诺赛科直接竞争
            },
            '02577': {
                'name': '英诺赛科',
                'symbol': '02577.HK',
                'exchange': 'HKEX',
                'next_earnings': None,  # 待查
                'quarter': '年报 2025',
                'time': None,
                'description': '全球氮化镓龙头',
                'importance': 'high',
            }
        }
    
    def get_upcoming_earnings(self, days: int = 30) -> List[Dict]:
        """获取未来N天的财报"""
        upcoming = []
        today = datetime.now().date()
        
        for symbol, data in self.earnings_data.items():
            if data.get('next_earnings'):
                earnings_date = datetime.strptime(data['next_earnings'], '%Y-%m-%d').date()
                days_until = (earnings_date - today).days
                
                if 0 <= days_until <= days:
                    upcoming.append({
                        **data,
                        'days_until': days_until,
                        'date_obj': earnings_date
                    })
        
        # 按日期排序
        upcoming.sort(key=lambda x: x['date_obj'])
        return upcoming
    
    def generate_report(self) -> str:
        """生成财报追踪报告"""
        upcoming = self.get_upcoming_earnings(days=60)
        
        lines = [
            "="*60,
            "📊 AI Earnings Tracker | 财报追踪",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "="*60,
            ""
        ]
        
        if upcoming:
            lines.append(f"🔔 未来60天内有 {len(upcoming)} 场重要财报:\n")
            
            for item in upcoming:
                days = item['days_until']
                date_str = item['date_obj'].strftime('%m月%d日')
                
                # 提醒级别
                if days <= 3:
                    alert = "🚨 紧急"
                elif days <= 7:
                    alert = "⚠️ 临近"
                else:
                    alert = "📅 计划中"
                
                lines.extend([
                    f"{alert} {item['name']} ({item['symbol']})",
                    f"   日期: {date_str} ({days}天后)",
                    f"   季度: {item['quarter']}",
                    f"   时间: {item.get('time', 'TBA')}",
                    f"   重要性: {'🔴 高' if item['importance'] == 'high' else '🟡 中'}"
                ])
                
                if item.get('description'):
                    lines.append(f"   业务: {item['description']}")
                
                lines.append("")
        else:
            lines.append("📭 未来60天内无已知财报日程")
        
        # 添加关注建议
        lines.extend([
            "="*60,
            "💡 关注建议",
            "="*60,
            "• 财报前1-3天: 设置提醒",
            "• 财报当天: 监控股价异动",
            "• 财报后: 自动摘要关键数据",
            "• 对比分析: 纳微vs英诺赛科业绩",
            "="*60
        ])
        
        return "\n".join(lines)


def main():
    """主函数"""
    calendar = EarningsCalendar()
    print(calendar.generate_report())


if __name__ == "__main__":
    main()
