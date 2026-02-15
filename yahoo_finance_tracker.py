#!/usr/bin/env python3
"""
Yahoo Finance 股票数据抓取工具 (纯Python实现)
支持港股、美股、A股实时数据（15分钟延迟）
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class YahooFinanceTracker:
    """Yahoo Finance股票数据追踪器"""
    
    # 股票代码映射
    TICKER_MAP = {
        # 港股 - 后缀 .HK
        '英诺赛科': '02577.HK',
        '腾讯': '0700.HK',
        '阿里': '9988.HK',
        '美团': '3690.HK',
        '小米': '1810.HK',
        
        # 美股
        '英飞凌': 'IFNNY',
        '纳微': 'NVTS',
        '德州仪器': 'TXN',
        '英伟达': 'NVDA',
        '苹果': 'AAPL',
        '特斯拉': 'TSLA',
        
        # A股 - Yahoo格式 .SS(上海) .SZ(深圳)
        '茅台': '600519.SS',
        '比亚迪': '002594.SZ',
    }
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        self.data_cache = {}
    
    def _fetch_data(self, symbol: str, interval: str = "1d", range_period: str = "1mo", retries: int = 3) -> Dict:
        """从Yahoo Finance获取数据（带重试）"""
        for attempt in range(retries):
            try:
                # 添加延迟避免限流
                if attempt > 0:
                    time.sleep(2)
                else:
                    time.sleep(0.5)  # 首次请求也延迟
                
                # 构建URL
                encoded_symbol = urllib.parse.quote(symbol)
                url = f"{self.base_url}{encoded_symbol}?interval={interval}&range={range_period}"
                
                # 添加请求头模拟浏览器
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                }
                
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    return data
                    
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < retries - 1:
                    print(f"  限流中，等待重试 ({attempt + 1}/{retries})...")
                    time.sleep(3 + attempt * 2)  # 递增延迟
                    continue
                return {'error': f'HTTP Error {e.code}: {e.reason}'}
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return {'error': str(e)}
        
        return {'error': 'Max retries exceeded'}
    
    def get_current_price(self, symbol: str) -> Dict:
        """获取当前股价"""
        data = self._fetch_data(symbol, interval="1m", range_period="1d")
        
        if 'error' in data:
            return {'error': data['error'], 'symbol': symbol}
        
        try:
            result = data.get('chart', {}).get('result', [{}])[0]
            meta = result.get('meta', {})
            
            # 获取最新价格
            timestamps = result.get('timestamp', [])
            close_prices = result.get('indicators', {}).get('quote', [{}])[0].get('close', [])
            volumes = result.get('indicators', {}).get('quote', [{}])[0].get('volume', [])
            highs = result.get('indicators', {}).get('quote', [{}])[0].get('high', [])
            lows = result.get('indicators', {}).get('quote', [{}])[0].get('low', [])
            
            if not close_prices:
                return {'error': 'No price data', 'symbol': symbol}
            
            # 取最新有效数据
            current_price = None
            current_volume = 0
            current_high = None
            current_low = None
            
            for i in range(len(close_prices) - 1, -1, -1):
                if close_prices[i] is not None:
                    current_price = close_prices[i]
                    current_volume = volumes[i] if i < len(volumes) and volumes[i] else 0
                    current_high = highs[i] if i < len(highs) and highs[i] else current_price
                    current_low = lows[i] if i < len(lows) and lows[i] else current_price
                    break
            
            if current_price is None:
                return {'error': 'No valid price data', 'symbol': symbol}
            
            # 获取前收盘价
            prev_close = meta.get('previousClose') or meta.get('chartPreviousClose', 0)
            
            change = current_price - prev_close if prev_close else 0
            change_pct = (change / prev_close * 100) if prev_close else 0
            
            # 货币单位
            currency = meta.get('currency', 'N/A')
            exchange = meta.get('exchangeName', 'N/A')
            
            # 股票名称
            short_name = meta.get('shortName', symbol)
            long_name = meta.get('longName', short_name)
            
            return {
                'symbol': symbol,
                'name': long_name or short_name,
                'current_price': round(current_price, 3),
                'previous_close': round(prev_close, 3) if prev_close else None,
                'change': round(change, 3),
                'change_pct': round(change_pct, 2),
                'volume': int(current_volume),
                'high': round(current_high, 3) if current_high else None,
                'low': round(current_low, 3) if current_low else None,
                'currency': currency,
                'exchange': exchange,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_delay': '约15分钟',
            }
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def get_history(self, symbol: str, range_period: str = "1mo") -> List[Dict]:
        """获取历史数据"""
        data = self._fetch_data(symbol, interval="1d", range_period=range_period)
        
        if 'error' in data:
            return []
        
        try:
            result = data.get('chart', {}).get('result', [{}])[0]
            timestamps = result.get('timestamp', [])
            close_prices = result.get('indicators', {}).get('quote', [{}])[0].get('close', [])
            opens = result.get('indicators', {}).get('quote', [{}])[0].get('open', [])
            highs = result.get('indicators', {}).get('quote', [{}])[0].get('high', [])
            lows = result.get('indicators', {}).get('quote', [{}])[0].get('low', [])
            volumes = result.get('indicators', {}).get('quote', [{}])[0].get('volume', [])
            
            history = []
            for i in range(len(timestamps)):
                if close_prices[i] is not None:
                    history.append({
                        'date': datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                        'open': round(opens[i], 3) if i < len(opens) and opens[i] else None,
                        'high': round(highs[i], 3) if i < len(highs) and highs[i] else None,
                        'low': round(lows[i], 3) if i < len(lows) and lows[i] else None,
                        'close': round(close_prices[i], 3),
                        'volume': int(volumes[i]) if i < len(volumes) and volumes[i] else 0,
                    })
            
            return history
        except Exception as e:
            print(f"Error parsing history: {e}")
            return []
    
    def get_multiple_prices(self, symbols: List[str]) -> List[Dict]:
        """批量获取多个股票的价格（带延迟）"""
        results = []
        for i, symbol in enumerate(symbols):
            data = self.get_current_price(symbol)
            results.append(data)
            # 批量请求间添加延迟
            if i < len(symbols) - 1:
                time.sleep(1.5)
        return results
    
    def track_innoscience(self) -> Dict:
        """专门追踪英诺赛科"""
        symbol = self.TICKER_MAP['英诺赛科']
        
        # 当前价格
        current = self.get_current_price(symbol)
        
        # 近期历史（用于分析支撑压力）
        history = self.get_history(symbol, range_period="3mo")
        
        if history:
            # 计算关键价位
            closes = [h['close'] for h in history if h['close']]
            volumes = [h['volume'] for h in history if h['volume']]
            highs = [h['high'] for h in history if h['high']]
            lows = [h['low'] for h in history if h['low']]
            
            recent_high = max(highs) if highs else None
            recent_low = min(lows) if lows else None
            avg_volume = sum(volumes) / len(volumes) if volumes else 0
            
            # 找到50-55区间的平均价格（SK减持密集区）
            support_prices = [h['close'] for h in history if h['close'] and h['close'] < 55]
            support_zone = sum(support_prices) / len(support_prices) if support_prices else None
            
            # 计算MA5、MA10、MA20
            if len(closes) >= 5:
                ma5 = sum(closes[-5:]) / 5
                ma10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else None
                ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
            else:
                ma5 = ma10 = ma20 = None
            
            analysis = {
                'current': current,
                '3m_high': round(recent_high, 2) if recent_high else None,
                '3m_low': round(recent_low, 2) if recent_low else None,
                'support_zone': round(support_zone, 2) if support_zone else None,
                'avg_volume': int(avg_volume),
                'ma5': round(ma5, 2) if ma5 else None,
                'ma10': round(ma10, 2) if ma10 else None,
                'ma20': round(ma20, 2) if ma20 else None,
            }
        else:
            analysis = {'current': current, 'error': 'No history data'}
        
        return analysis
    
    def track_gan_competitors(self) -> List[Dict]:
        """追踪氮化镓竞争对手"""
        symbols = [
            self.TICKER_MAP['英飞凌'],
            self.TICKER_MAP['纳微'],
            self.TICKER_MAP['德州仪器'],
        ]
        return self.get_multiple_prices(symbols)
    
    def format_report(self, data: Dict) -> str:
        """格式化报告输出"""
        if 'error' in data and 'current' not in data:
            return f"❌ 获取失败: {data.get('error', 'Unknown error')}"
        
        if 'current' in data:  # 英诺赛科详细报告
            c = data['current']
            if 'error' in c:
                return f"❌ {c.get('symbol', 'N/A')}: {c.get('error')}"
            
            change_emoji = "📈" if c.get('change', 0) >= 0 else "📉"
            
            report = f"""
{'='*50}
📊 英诺赛科 (02577.HK) 实时追踪
{'='*50}
⏰ 更新时间: {c.get('timestamp', 'N/A')}
💰 当前价格: {c.get('current_price', 'N/A')} {c.get('currency', '')}
📊 涨跌: {change_emoji} {c.get('change', 0):+.2f} ({c.get('change_pct', 0):+.2f}%)
📈 今高: {c.get('high', 'N/A')}  今低: {c.get('low', 'N/A')}
📊 成交量: {c.get('volume', 0):,}

🔍 技术分析参考:
• 3个月高点: {data.get('3m_high', 'N/A')}
• 3个月低点: {data.get('3m_low', 'N/A')}
• 支撑位(MA20): {data.get('ma20', 'N/A')}
• SK成本支撑区: {data.get('support_zone', 'N/A')} (53.8附近)

⚠️ 数据延迟: {c.get('data_delay', '约15分钟')}
{'='*50}
"""
            return report
        else:  # 简单价格报告
            if 'error' in data:
                return f"❌ {data.get('symbol', 'N/A')}: {data.get('error')}"
            change_emoji = "📈" if data.get('change', 0) >= 0 else "📉"
            return f"  • {data.get('name', data.get('symbol', 'N/A'))}: {data.get('current_price', 'N/A')} {change_emoji} {data.get('change_pct', 0):+.2f}%"


def main():
    """测试运行"""
    tracker = YahooFinanceTracker()
    
    print("="*60)
    print("Yahoo Finance 股票数据抓取测试")
    print("="*60)
    
    # 测试英诺赛科
    print("\n🔍 获取英诺赛科数据...")
    innoscience = tracker.track_innoscience()
    print(tracker.format_report(innoscience))
    
    # 测试竞争对手
    print("\n🔍 获取氮化镓竞争对手数据...")
    competitors = tracker.track_gan_competitors()
    print("\n📊 竞争对手股价:")
    for comp in competitors:
        print(tracker.format_report(comp))
    
    # 测试美股
    print("\n🔍 获取美股数据...")
    nvda = tracker.get_current_price('NVDA')
    print(tracker.format_report(nvda))
    
    # 保存数据到文件
    output = {
        'timestamp': datetime.now().isoformat(),
        'innoscience': innoscience,
        'competitors': competitors,
    }
    
    output_file = '/tmp/stock_data_latest.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 数据已保存到: {output_file}")


if __name__ == "__main__":
    main()
