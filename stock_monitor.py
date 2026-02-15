#!/usr/bin/env python3
"""
股票监控整合系统
- 美股（纳微/德州仪器/英飞凌）：Twelve Data API
- 港股（英诺赛科）：Brave Search
- 输出：统一格式的监控报告
"""

import urllib.request
import json
import time
from datetime import datetime
from typing import Dict, List

# API Keys
TWELVE_DATA_API_KEY = '73c7acfe931d452c82eda0af4c99300f'
BRAVE_API_KEY = 'BSA5gm2J8fUK-1VTQJZVu_IFnFFdW6P'

class StockMonitor:
    """股票监控系统"""
    
    def __init__(self):
        self.twelve_data_calls = 0
        self.brave_calls = 0
    
    def get_us_stock_twelvedata(self, symbol: str, name: str) -> Dict:
        """通过Twelve Data获取美股数据"""
        try:
            url = f'https://api.twelvedata.com/quote?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                self.twelve_data_calls += 1
                
                if 'code' in data:
                    return {
                        'symbol': symbol,
                        'name': name,
                        'market': 'US',
                        'status': 'error',
                        'error': data.get('message', 'API Error')
                    }
                
                return {
                    'symbol': symbol,
                    'name': name,
                    'market': 'US',
                    'status': 'success',
                    'current_price': float(data.get('close', 0)),
                    'previous_close': float(data.get('previous_close', 0)),
                    'change': float(data.get('change', 0)),
                    'change_pct': float(data.get('percent_change', 0)),
                    'volume': int(data.get('volume', 0)),
                    'high': float(data.get('high', 0)),
                    'low': float(data.get('low', 0)),
                    'currency': data.get('currency', 'USD'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
        except Exception as e:
            return {
                'symbol': symbol,
                'name': name,
                'market': 'US',
                'status': 'error',
                'error': str(e)
            }
    
    def get_us_competitors(self) -> List[Dict]:
        """获取美股竞争对手数据"""
        stocks = [
            ('NVTS', '纳微半导体'),
            ('TXN', '德州仪器'),
            ('IFNNY', '英飞凌'),
        ]
        
        results = []
        for symbol, name in stocks:
            result = self.get_us_stock_twelvedata(symbol, name)
            results.append(result)
            if symbol != stocks[-1][0]:
                time.sleep(1)
        
        return results
    
    def get_hk_stock_brave(self, symbol: str, name: str) -> Dict:
        """通过Brave Search获取港股数据"""
        try:
            query = f"{symbol} {name} 港股 股价 最新"
            encoded_query = urllib.parse.quote(query)
            url = f'https://api.search.brave.com/res/v1/web/search?q={encoded_query}&count=5'
            
            req = urllib.request.Request(url, headers={
                'Accept': 'application/json',
                'X-Subscription-Token': BRAVE_API_KEY
            })
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                self.brave_calls += 1
                
                results = data.get('web', {}).get('results', [])
                
                return {
                    'symbol': symbol,
                    'name': name,
                    'market': 'HK',
                    'status': 'success',
                    'news': [r.get('title', '') for r in results[:3]],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'data_source': 'Brave Search (15-30min delay)',
                }
        except Exception as e:
            return {
                'symbol': symbol,
                'name': name,
                'market': 'HK',
                'status': 'error',
                'error': str(e)
            }
    
    def generate_full_report(self) -> str:
        """生成完整监控报告"""
        lines = [
            "="*60,
            "📊 氮化镓竞争对手监控报告",
            f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*60,
            "",
        ]
        
        # 美股部分
        lines.extend(["🇺🇸 美股竞争对手 (Twelve Data实时)", "-"*40])
        us_stocks = self.get_us_competitors()
        
        for stock in us_stocks:
            if stock.get('status') == 'success':
                emoji = "📈" if stock.get('change', 0) >= 0 else "📉"
                lines.append(
                    f"• {stock['name']} ({stock['symbol']}): "
                    f"${stock['current_price']} {emoji} "
                    f"{stock['change_pct']:+.2f}%"
                )
            else:
                lines.append(f"• {stock['name']} ({stock['symbol']}): ❌ {stock.get('error', 'Error')}")
        
        # 分析
        lines.extend(["", "💡 竞争格局分析:"])
        nvts = next((s for s in us_stocks if s.get('symbol') == 'NVTS'), None)
        txn = next((s for s in us_stocks if s.get('symbol') == 'TXN'), None)
        
        if nvts and nvts.get('status') == 'success':
            if nvts.get('change_pct', 0) > 5:
                lines.append("  • 纳微大涨，GaN板块热度上升，利好英诺赛科")
            elif nvts.get('change_pct', 0) < -5:
                lines.append("  • 纳微大跌，关注GaN行业情绪变化")
            else:
                lines.append(f"  • 纳微涨{nvts.get('change_pct', 0):+.2f}%，GaN板块情绪中性")
        
        if txn and txn.get('status') == 'success':
            if txn.get('change_pct', 0) > 0:
                lines.append("  • 德州仪器上涨，传统功率半导体强势")
            else:
                lines.append("  • 德州仪器下跌，GaN替代逻辑增强")
        
        # API调用统计
        lines.extend([
            "",
            "-"*40,
            f"📊 API调用统计:",
            f"  • Twelve Data: {self.twelve_data_calls} 次",
            f"  • Brave Search: {self.brave_calls} 次",
            "="*60,
        ])
        
        return "\n".join(lines)


def main():
    """主函数"""
    monitor = StockMonitor()
    report = monitor.generate_full_report()
    print(report)
    
    # 保存到文件
    with open('/tmp/stock_monitor_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 报告已保存: /tmp/stock_monitor_report.txt")


if __name__ == "__main__":
    main()
