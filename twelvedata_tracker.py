#!/usr/bin/env python3
"""
Twelve Data 股票监控工具
支持：美股实时数据
免费额度：800次/天，8次/分钟
"""

import os
import urllib.request
import json
import time
from datetime import datetime
from typing import Dict, List

class TwelveDataTracker:
    """Twelve Data股票追踪器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.twelvedata.com"
        self.daily_limit = 800
        self.minute_limit = 8
        self.call_count = 0
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """发起API请求"""
        try:
            # 构建URL
            query_parts = [f"{k}={v}" for k, v in params.items()]
            query = "&".join(query_parts)
            url = f"{self.base_url}/{endpoint}?{query}&apikey={self.api_key}"
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                self.call_count += 1
                return data
        except Exception as e:
            return {'error': str(e)}
    
    def get_quote(self, symbol: str) -> Dict:
        """获取实时报价"""
        data = self._make_request('quote', {'symbol': symbol})
        
        if 'error' in data or 'code' in data:
            return {
                'symbol': symbol,
                'error': data.get('message', data.get('error', 'Unknown error')),
                'status': 'failed'
            }
        
        return {
            'symbol': symbol,
            'name': data.get('name', 'N/A'),
            'exchange': data.get('exchange', 'N/A'),
            'currency': data.get('currency', 'USD'),
            'current_price': float(data.get('close', 0)),
            'open': float(data.get('open', 0)),
            'high': float(data.get('high', 0)),
            'low': float(data.get('low', 0)),
            'previous_close': float(data.get('previous_close', 0)),
            'change': float(data.get('change', 0)),
            'change_pct': float(data.get('percent_change', 0)),
            'volume': int(data.get('volume', 0)),
            'timestamp': data.get('datetime', datetime.now().isoformat()),
            'status': 'success'
        }
    
    def track_competitors(self) -> List[Dict]:
        """追踪氮化镓竞争对手"""
        symbols = [
            ('NVTS', '纳微半导体'),
            ('TXN', '德州仪器'),
            ('IFNNY', '英飞凌'),
        ]
        
        results = []
        for symbol, cn_name in symbols:
            print(f"  获取 {cn_name} ({symbol})...")
            data = self.get_quote(symbol)
            data['cn_name'] = cn_name
            results.append(data)
            
            # 控制频率：每分钟8次，间隔7.5秒
            if symbol != symbols[-1][0]:
                time.sleep(7.5)
        
        return results
    
    def test_hk_stock(self, symbol: str = '02577') -> Dict:
        """测试港股支持"""
        print(f"\n  测试港股支持: {symbol}")
        
        # 尝试不同格式
        formats = [f"{symbol}.HK", f"HK:{symbol}", symbol]
        
        for fmt in formats:
            data = self._make_request('quote', {'symbol': fmt})
            if 'code' not in data:
                return {'symbol': fmt, 'status': 'success', 'data': data}
        
        return {
            'symbol': symbol,
            'status': 'failed',
            'message': '港股不支持（Basic计划仅限3个市场）'
        }
    
    def format_report(self, data: Dict) -> str:
        """格式化报告"""
        if data.get('status') == 'failed':
            return f"❌ {data.get('symbol', 'N/A')}: {data.get('error', 'Unknown error')}"
        
        change_emoji = "📈" if data.get('change', 0) >= 0 else "📉"
        cn_name = data.get('cn_name', data.get('name', data.get('symbol')))
        
        return f"""
{'='*50}
📊 {cn_name} ({data.get('symbol')})
{'='*50}
💰 当前价格: ${data.get('current_price')} {data.get('currency')}
📊 涨跌: {change_emoji} {data.get('change', 0):+.2f} ({data.get('change_pct', 0):+.2f}%)
📈 今高: ${data.get('high')}  今低: ${data.get('low')}
📊 成交量: {data.get('volume', 0):,}
🏢 交易所: {data.get('exchange')}
⏰ 时间: {data.get('timestamp')}
{'='*50}
"""
    
    def generate_summary(self, results: List[Dict]) -> str:
        """生成汇总报告"""
        lines = [
            "="*60,
            "📊 氮化镓竞争对手监控报告 (Twelve Data)",
            f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"📊 API调用: {self.call_count}/800 次",
            "="*60,
            "",
        ]
        
        for data in results:
            if data.get('status') == 'failed':
                lines.append(f"❌ {data.get('cn_name', data.get('symbol'))}: {data.get('error', 'Error')}")
            else:
                change_emoji = "📈" if data.get('change', 0) >= 0 else "📉"
                lines.append(
                    f"• {data.get('cn_name', data.get('name'))}: "
                    f"${data.get('current_price')} "
                    f"{change_emoji} {data.get('change_pct', 0):+.2f}%"
                )
        
        # 分析
        lines.extend(["", "💡 竞争格局分析:"])
        
        nvts = next((r for r in results if r.get('symbol') == 'NVTS'), None)
        txn = next((r for r in results if r.get('symbol') == 'TXN'), None)
        ifnn = next((r for r in results if r.get('symbol') == 'IFNNY'), None)
        
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
        
        if ifnn and ifnn.get('status') == 'success':
            lines.append(f"  • 英飞凌涨{ifnn.get('change_pct', 0):+.2f}%，欧洲GaN龙头动态")
        
        lines.extend(["", "="*60])
        return "\n".join(lines)


def main():
    """完整测试"""
    # API Key
    API_KEY = os.getenv('TWELVE_DATA_API_KEY')
    if not API_KEY:
        print("❌ 请设置 TWELVE_DATA_API_KEY 环境变量")
        return
    
    print("="*60)
    print("Twelve Data API 完整测试")
    print("="*60)
    
    tracker = TwelveDataTracker(api_key=API_KEY)
    
    # 1. 测试美股
    print("\n📊 测试美股竞争对手...")
    results = tracker.track_competitors()
    
    for data in results:
        print(tracker.format_report(data))
    
    # 2. 测试港股
    print("\n📊 测试港股支持...")
    hk_test = tracker.test_hk_stock('02577')
    if hk_test.get('status') == 'failed':
        print(f"  ❌ {hk_test.get('message')}")
    else:
        print(f"  ✅ 港股支持！")
        print(f"     名称: {hk_test.get('data', {}).get('name', 'N/A')}")
        print(f"     价格: ${hk_test.get('data', {}).get('close', 'N/A')}")
    
    # 3. 生成汇总报告
    print("\n" + tracker.generate_summary(results))
    
    # 4. 测试其他美股
    print("\n📊 额外测试...")
    extra_symbols = ['NVDA', 'AAPL']
    for symbol in extra_symbols:
        print(f"  获取 {symbol}...")
        data = tracker.get_quote(symbol)
        if data.get('status') == 'success':
            print(f"    ✅ {data.get('name')}: ${data.get('current_price')}")
        else:
            print(f"    ❌ {data.get('error', 'Error')}")
        time.sleep(7.5)
    
    print(f"\n📊 总API调用: {tracker.call_count}/800 次")
    print("="*60)


if __name__ == "__main__":
    main()
