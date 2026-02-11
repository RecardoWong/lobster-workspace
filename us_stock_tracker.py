#!/usr/bin/env python3
"""
美股数据抓取工具 - Yahoo Finance
支持：纳微(NVTS)、德州仪器(TXN)、英飞凌(IFNNY)
策略：低频请求，避免429限流
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
from typing import Dict, List

class USStockTracker:
    """美股追踪器 - Yahoo Finance"""
    
    # 美股代码映射
    TICKERS = {
        '纳微': 'NVTS',
        '德州仪器': 'TXN',
        '英飞凌': 'IFNNY',  # OTC
        '英伟达': 'NVDA',
    }
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        self.delay_between_calls = 15  # 秒，避免限流
    
    def get_stock_data(self, symbol: str) -> Dict:
        """获取单只股票数据"""
        try:
            encoded = urllib.parse.quote(symbol)
            url = f"{self.base_url}{encoded}?interval=1d&range=5d"  # 取5天数据
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://finance.yahoo.com/',
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return self._parse_data(data, symbol)
                
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def _parse_data(self, data: Dict, symbol: str) -> Dict:
        """解析返回数据"""
        try:
            result = data.get('chart', {}).get('result', [{}])[0]
            meta = result.get('meta', {})
            
            # 获取最新价格
            timestamps = result.get('timestamp', [])
            close_prices = result.get('indicators', {}).get('quote', [{}])[0].get('close', [])
            volumes = result.get('indicators', {}).get('quote', [{}])[0].get('volume', [])
            
            if not close_prices:
                return {'error': 'No price data', 'symbol': symbol}
            
            # 取最新有效数据
            current_price = None
            current_volume = 0
            for i in range(len(close_prices) - 1, -1, -1):
                if close_prices[i] is not None:
                    current_price = close_prices[i]
                    current_volume = volumes[i] if i < len(volumes) and volumes[i] else 0
                    break
            
            if current_price is None:
                return {'error': 'No valid price', 'symbol': symbol}
            
            # 获取前收盘价
            prev_close = meta.get('previousClose') or meta.get('chartPreviousClose', 0)
            change = current_price - prev_close if prev_close else 0
            change_pct = (change / prev_close * 100) if prev_close else 0
            
            # 计算5日高低
            valid_closes = [c for c in close_prices if c is not None]
            high_5d = max(valid_closes) if valid_closes else current_price
            low_5d = min(valid_closes) if valid_closes else current_price
            
            return {
                'symbol': symbol,
                'name': meta.get('shortName', meta.get('longName', symbol)),
                'current_price': round(current_price, 2),
                'previous_close': round(prev_close, 2) if prev_close else None,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'volume': int(current_volume),
                'high_5d': round(high_5d, 2),
                'low_5d': round(low_5d, 2),
                'currency': meta.get('currency', 'USD'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as e:
            return {'error': f'Parse error: {e}', 'symbol': symbol}
    
    def track_competitors(self) -> List[Dict]:
        """追踪氮化镓竞争对手"""
        symbols = ['NVTS', 'TXN', 'IFNNY']
        results = []
        
        for symbol in symbols:
            data = self.get_stock_data(symbol)
            results.append(data)
            
            # 请求间隔，避免限流
            if symbol != symbols[-1]:
                print(f"  等待{self.delay_between_calls}秒...")
                time.sleep(self.delay_between_calls)
        
        return results
    
    def format_report(self, data: Dict) -> str:
        """格式化报告"""
        if 'error' in data:
            return f"❌ {data.get('symbol', 'N/A')}: {data.get('error')}"
        
        change_emoji = "📈" if data.get('change', 0) >= 0 else "📉"
        
        return f"""
{'='*50}
📊 {data.get('name', data.get('symbol'))} ({data.get('symbol')})
{'='*50}
💰 当前价格: {data.get('current_price')} {data.get('currency')}
📊 涨跌: {change_emoji} {data.get('change', 0):+.2f} ({data.get('change_pct', 0):+.2f}%)
📊 成交量: {data.get('volume', 0):,}
📈 5日高点: {data.get('high_5d')}
📉 5日低点: {data.get('low_5d')}
⏰ 更新时间: {data.get('timestamp')}
{'='*50}
"""
    
    def generate_summary(self, results: List[Dict]) -> str:
        """生成汇总报告"""
        lines = [
            "="*60,
            "📊 氮化镓竞争对手监控报告",
            f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*60,
            "",
        ]
        
        for data in results:
            if 'error' in data:
                lines.append(f"❌ {data.get('symbol', 'N/A')}: {data.get('error')}")
            else:
                change_emoji = "📈" if data.get('change', 0) >= 0 else "📉"
                lines.append(
                    f"• {data.get('name', data.get('symbol'))}: "
                    f"${data.get('current_price')} "
                    f"{change_emoji} {data.get('change_pct', 0):+.2f}%"
                )
        
        lines.extend([
            "",
            "💡 对英诺赛科的影响分析:",
        ])
        
        # 自动分析
        nvts = next((r for r in results if r.get('symbol') == 'NVTS'), {})
        txn = next((r for r in results if r.get('symbol') == 'TXN'), {})
        
        if nvts and 'error' not in nvts:
            if nvts.get('change_pct', 0) > 5:
                lines.append("  • 纳微大涨，氮化镓板块热度上升，利好英诺赛科")
            elif nvts.get('change_pct', 0) < -5:
                lines.append("  • 纳微大跌，需关注氮化镓行业情绪")
        
        if txn and 'error' not in txn:
            if txn.get('change_pct', 0) > 0:
                lines.append("  • 德州仪器上涨，传统功率半导体强势")
            else:
                lines.append("  • 德州仪器下跌，GaN替代逻辑增强")
        
        lines.append("")
        lines.append("="*60)
        
        return "\n".join(lines)


def main():
    """测试运行"""
    tracker = USStockTracker()
    
    print("🔍 开始获取美股竞争对手数据...")
    print("(每只间隔15秒，避免触发限流)\n")
    
    results = tracker.track_competitors()
    
    # 打印详细报告
    for data in results:
        print(tracker.format_report(data))
    
    # 打印汇总
    print(tracker.generate_summary(results))


if __name__ == "__main__":
    main()
