#!/usr/bin/env python3
"""
美股市场热点监控
包含：大盘指数 + 板块热点 + 个股热度排行
"""

import urllib.request
import json
from datetime import datetime
from typing import List, Dict

class USMarketHotMonitor:
    """美股市场热点监控器"""
    
    def __init__(self):
        self.api_key = "73c7acfe931d452c82eda0af4c99300f"
        
        # 大盘指数
        self.indices = {
            'IXIC': {'name': '纳斯达克', 'type': '科技成长'},
            'GSPC': {'name': '标普500', 'type': '大盘蓝筹'},
            'DJI': {'name': '道琼斯', 'type': '传统行业'}
        }
        
        # 半导体板块重点股票
        self.semi_stocks = [
            'NVTS', 'NVDA', 'AMD', 'TXN', 'QCOM', 
            'AVGO', 'INTC', 'MU', 'ON', 'MRVL'
        ]
    
    def get_index_data(self, symbol: str) -> Dict:
        """获取指数数据"""
        try:
            url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={self.api_key}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                return {
                    'price': float(data.get('close', 0)),
                    'change': float(data.get('change', 0)),
                    'change_percent': float(data.get('percent_change', 0)),
                    'name': self.indices.get(symbol, {}).get('name', symbol)
                }
        except Exception as e:
            return {'error': str(e)}
    
    def get_stock_data(self, symbol: str) -> Dict:
        """获取个股数据"""
        try:
            url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={self.api_key}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return {
                    'symbol': symbol,
                    'price': float(data.get('close', 0)),
                    'change_percent': float(data.get('percent_change', 0)),
                    'volume': int(data.get('volume', 0))
                }
        except:
            return None
    
    def get_sector_movers(self) -> Dict:
        """获取板块涨跌（简化版，实际应该调用Sector API）"""
        # 获取半导体板块代表股的平均涨跌
        semi_changes = []
        for symbol in ['NVDA', 'AMD', 'TXN', 'QCOM']:
            data = self.get_stock_data(symbol)
            if data:
                semi_changes.append(data['change_percent'])
        
        if semi_changes:
            avg_change = sum(semi_changes) / len(semi_changes)
            return {
                'semiconductor': {
                    'change': avg_change,
                    'stocks': semi_changes
                }
            }
        return {}
    
    def get_hot_stocks(self, stocks: List[str], top_n: int = 5) -> List[Dict]:
        """获取最热的股票（涨幅排行）"""
        all_data = []
        for symbol in stocks:
            data = self.get_stock_data(symbol)
            if data:
                all_data.append(data)
        
        # 按涨跌幅排序
        all_data.sort(key=lambda x: x['change_percent'], reverse=True)
        return all_data[:top_n]
    
    def detect_market_sentiment(self, nasdaq_change: float) -> str:
        """检测市场情绪"""
        if nasdaq_change > 2:
            return "🔥🔥🔥 极度贪婪"
        elif nasdaq_change > 1:
            return "🔥🔥 贪婪"
        elif nasdaq_change > 0:
            return "🔥 乐观"
        elif nasdaq_change > -1:
            return "❄️ 谨慎"
        elif nasdaq_change > -2:
            return "❄️❄️ 恐慌"
        else:
            return "❄️❄️❄️ 极度恐慌"
    
    def generate_market_hot_report(self) -> str:
        """生成市场热点报告"""
        lines = [
            "="*70,
            "🔥 美股市场热点监控",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} 北京时间",
            "="*70,
            ""
        ]
        
        # 1. 大盘指数
        lines.append("📊 一、大盘指数")
        lines.append("-"*70)
        
        nasdaq_change = 0
        for symbol, info in self.indices.items():
            data = self.get_index_data(symbol)
            if 'error' not in data:
                change = data.get('change_percent', 0)
                if symbol == 'IXIC':
                    nasdaq_change = change
                
                emoji = "📈" if change > 0 else "📉"
                lines.append(f"{emoji} {info['name']} ({symbol})")
                lines.append(f"   点数: {data.get('price', 0):,.2f}")
                lines.append(f"   涨跌: {change:+.2f}%")
                lines.append("")
        
        # 市场情绪
        sentiment = self.detect_market_sentiment(nasdaq_change)
        lines.append(f"🎭 市场情绪: {sentiment}")
        lines.append("")
        
        # 2. 半导体板块热点
        lines.append("="*70)
        lines.append("💎 二、半导体板块热点")
        lines.append("-"*70)
        
        sector = self.get_sector_movers()
        if sector:
            semi = sector.get('semiconductor', {})
            avg = semi.get('change', 0)
            lines.append(f"🔸 板块平均涨跌: {avg:+.2f}%")
            lines.append("")
        
        # 涨幅榜
        hot_stocks = self.get_hot_stocks(self.semi_stocks, top_n=5)
        if hot_stocks:
            lines.append("🔥 涨幅榜 TOP5:")
            for i, s in enumerate(hot_stocks, 1):
                change = s['change_percent']
                fire = "🔥" if change > 3 else "📈" if change > 0 else "📉"
                lines.append(f"   {i}. {s['symbol']}: {change:+.2f}% {fire}")
        
        lines.append("")
        
        # 3.  our focus stocks
        lines.append("="*70)
        lines.append("🎯 三、重点关注股票")
        lines.append("-"*70)
        
        focus_stocks = ['NVTS', 'TXN']
        for symbol in focus_stocks:
            data = self.get_stock_data(symbol)
            if data:
                change = data['change_percent']
                status = "🔥 大涨" if change > 5 else "📈 上涨" if change > 0 else "📉 下跌"
                lines.append(f"{symbol}: ${data['price']:.2f} ({change:+.2f}%) {status}")
        
        lines.extend([
            "",
            "="*70,
            "💡 四、市场洞察",
            "="*70,
            "• 纳微关注: 10kW平台发布后续影响",
            "• 英飞凌: 涨价公告对行业影响",
            "• 英诺赛科: 港股表现与南向资金",
            "• AI需求: 数据中心电源市场增长",
            "="*70
        ])
        
        return "\n".join(lines)


def main():
    monitor = USMarketHotMonitor()
    print(monitor.generate_market_hot_report())


if __name__ == "__main__":
    main()
