#!/usr/bin/env python3
"""
🦞 英诺赛科股价监控系统
数据来源：腾讯财经API（实时、稳定）
监控标的：英诺赛科(02577.HK) + 上游供应商
"""

import requests
import re
import json
from datetime import datetime
import os

class StockPriceMonitor:
    """实时股价监控"""
    
    def __init__(self):
        # 监控列表
        self.stocks = {
            # 英诺赛科
            'hk02577': {'name': '英诺赛科', 'market': '港股'},
            
            # A股上游供应商
            'sh600703': {'name': '三安光电', 'market': 'A股', 'business': 'GaN衬底/外延'},
            'sh601600': {'name': '中国铝业', 'market': 'A股', 'business': '金属镓原材料'},
            'sz002371': {'name': '北方华创', 'market': 'A股', 'business': 'MOCVD设备'},
            'sz300346': {'name': '南大光电', 'market': 'A股', 'business': '特气MO源'},
            'sz300487': {'name': '蓝晓科技', 'market': 'A股', 'business': '镓提取树脂'},
            'sh688012': {'name': '中微公司', 'market': 'A股', 'business': 'MOCVD设备'},
            'sh688396': {'name': '华润微', 'market': 'A股', 'business': '功率半导体'},
        }
        
        self.report_file = "/root/.openclaw/workspace/reports/innoscience_daily_price.json"
        
    def fetch_prices(self):
        """获取实时股价"""
        code_str = ','.join(self.stocks.keys())
        
        try:
            url = f'http://qt.gtimg.cn/q={code_str}'
            resp = requests.get(url, timeout=10)
            resp.encoding = 'gb2312'
            
            results = {}
            for line in resp.text.strip().split(';'):
                if 'v_' in line and '=' in line:
                    match = re.search(r'v_([a-z]+\d+)=\"([^\"]+)\"', line)
                    if match:
                        code, data = match.groups()
                        fields = data.split('~')
                        
                        # 腾讯字段解析
                        # 1=名字, 2=代码, 3=现价, 4=昨收, 5=今开, 6=成交量(手), 32=涨跌幅%, 30=时间
                        if len(fields) > 32:
                            info = self.stocks.get(code, {})
                            name = info.get('name', fields[1])
                            business = info.get('business', '')
                            
                            price = float(fields[3]) if fields[3] else 0
                            prev = float(fields[4]) if fields[4] else 0
                            change_pct = float(fields[32]) if fields[32] else 0
                            change_val = price - prev
                            volume = fields[6] if len(fields) > 6 else '0'
                            time_str = fields[30] if len(fields) > 30 else ''
                            
                            results[code] = {
                                'name': name,
                                'code': code,
                                'price': price,
                                'prev_close': prev,
                                'change_value': round(change_val, 2),
                                'change_pct': round(change_pct, 2),
                                'volume': volume,
                                'business': business,
                                'update_time': time_str
                            }
            
            return results
            
        except Exception as e:
            print(f"❌ 获取股价失败: {e}")
            return {}
    
    def generate_report(self):
        """生成报告"""
        data = self.fetch_prices()
        if not data:
            return None
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'stocks': data
        }
        
        # 保存到文件
        os.makedirs(os.path.dirname(self.report_file), exist_ok=True)
        with open(self.report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return self.format_report(data)
    
    def format_report(self, data):
        """格式化输出"""
        lines = []
        lines.append("=" * 65)
        lines.append(f"📊 英诺赛科及上游供应商实时股价")
        lines.append(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 65)
        lines.append(f"{'股票':<10} {'现价':<10} {'涨跌':<8} {'涨幅':<8} {'业务':<20}")
        lines.append("-" * 65)
        
        # 英诺赛科放第一
        if 'hk02577' in data:
            s = data['hk02577']
            emoji = '📈' if s['change_pct'] > 0 else '📉' if s['change_pct'] < 0 else '➖'
            lines.append(f"🦞{s['name']:<9} ¥{s['price']:<9} {s['change_value']:+6.2f}   {emoji} {s['change_pct']:+.2f}%  {'GaN功率芯片':<20}")
            lines.append("-" * 65)
        
        # 上游供应商
        for code, s in data.items():
            if code == 'hk02577':
                continue
            emoji = '📈' if s['change_pct'] > 0 else '📉' if s['change_pct'] < 0 else '➖'
            lines.append(f"{s['name']:<10} ¥{s['price']:<9} {s['change_value']:+6.2f}   {emoji} {s['change_pct']:+.2f}%  {s.get('business', ''):<20}")
        
        lines.append("=" * 65)
        
        # 统计
        up = sum(1 for s in data.values() if s['change_pct'] > 0)
        down = sum(1 for s in data.values() if s['change_pct'] < 0)
        flat = len(data) - up - down
        lines.append(f"📈 上涨: {up} | 📉 下跌: {down} | ➖ 平盘: {flat}")
        lines.append("")
        
        return '\n'.join(lines)
    
    def check_alerts(self, data):
        """检查预警条件"""
        alerts = []
        
        # 英诺赛科关键价格监控
        if 'hk02577' in data:
            inn = data['hk02577']
            price = inn['price']
            
            # 关键价位
            if price >= 76:
                alerts.append(f"🚨 英诺赛科突破76 HKD！到达'抢跑区'，考虑减仓10-15%")
            elif price >= 82:
                alerts.append(f"🚨 英诺赛科突破82 HKD！到达'确认区'，考虑减仓15-20%")
            elif price >= 90:
                alerts.append(f"🚨 英诺赛科突破90 HKD！进入'泡沫区'，建议清仓")
            elif price <= 53:
                alerts.append(f"💡 英诺赛科跌至53 HKD以下！接近SK成本线，可能有机会")
        
        # 上游供应商异常波动（>3%）
        for code, s in data.items():
            if code == 'hk02577':
                continue
            if abs(s['change_pct']) > 3:
                emoji = '📈' if s['change_pct'] > 0 else '📉'
                alerts.append(f"{emoji} {s['name']} 异常波动: {s['change_pct']:+.2f}%")
        
        return alerts

if __name__ == '__main__':
    monitor = StockPriceMonitor()
    report = monitor.generate_report()
    
    if report:
        print(report)
        
        # 检查预警
        data = monitor.fetch_prices()
        alerts = monitor.check_alerts(data)
        if alerts:
            print("\n🚨 预警提醒:")
            for alert in alerts:
                print(f"  {alert}")
    else:
        print("❌ 获取数据失败")
