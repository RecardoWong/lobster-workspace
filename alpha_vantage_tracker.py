#!/usr/bin/env python3
"""
Alpha Vantage 股票数据抓取工具
支持美股实时数据、全球股票延迟数据
免费额度：25次/天，5次/分钟
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class AlphaVantageTracker:
    """Alpha Vantage股票数据追踪器"""
    
    # 股票代码映射（Alpha Vantage格式）
    TICKER_MAP = {
        # 美股
        '英飞凌': 'IFNNY',      # OTC市场
        '纳微': 'NVTS',
        '德州仪器': 'TXN',
        '英伟达': 'NVDA',
        '苹果': 'AAPL',
        '特斯拉': 'TSLA',
        
        # 港股（需要添加.HK后缀）
        '英诺赛科': '02577.HK',
        '腾讯': '0700.HK',
        '阿里': '9988.HK',
        '美团': '3690.HK',
        '小米': '1810.HK',
        
        # A股（上海/深圳）
        '茅台': '600519.SS',    # 上海
        '比亚迪': '002594.SZ',  # 深圳
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.call_count = 0
        self.max_calls_per_day = 25
        self.delay_between_calls = 12  # 秒，控制每分钟不超过5次
    
    def _make_request(self, params: Dict) -> Dict:
        """发起API请求（带限流控制）"""
        if self.call_count >= self.max_calls_per_day:
            return {'error': 'Daily API limit reached (25 calls/day)'}
        
        try:
            # 添加延迟控制频率
            time.sleep(self.delay_between_calls)
            
            # 添加API Key
            params['apikey'] = self.api_key
            
            # 构建URL
            query_string = urllib.parse.urlencode(params)
            url = f"{self.base_url}?{query_string}"
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                self.call_count += 1
                
                # 检查API错误
                if 'Error Message' in data:
                    return {'error': data['Error Message']}
                if 'Note' in data and 'API call frequency' in data['Note']:
                    return {'error': f"Rate limit: {data['Note']}"}
                
                return data
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_global_quote(self, symbol: str) -> Dict:
        """
        获取全球股票实时报价（免费版延迟15-20分钟）
        功能：当前价格、涨跌、成交量
        成本：1次API调用
        """
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
        }
        
        data = self._make_request(params)
        
        if 'error' in data:
            return {'error': data['error'], 'symbol': symbol}
        
        try:
            quote = data.get('Global Quote', {})
            
            if not quote:
                return {'error': 'No data returned', 'symbol': symbol}
            
            # 解析数据
            price = float(quote.get('05. price', 0))
            change = float(quote.get('09. change', 0))
            change_pct = quote.get('10. change percent', '0%').replace('%', '')
            volume = int(quote.get('06. volume', 0))
            
            return {
                'symbol': symbol,
                'name': self._get_name_from_symbol(symbol),
                'current_price': round(price, 3),
                'change': round(change, 3),
                'change_pct': round(float(change_pct), 2),
                'volume': volume,
                'latest_trading_day': quote.get('07. latest trading day', 'N/A'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_source': 'Alpha Vantage (15-20min delay)',
                'api_calls_used': self.call_count,
            }
        except Exception as e:
            return {'error': f'Parse error: {e}', 'symbol': symbol}
    
    def get_intraday(self, symbol: str, interval: str = '5min') -> Dict:
        """
        获取日内数据（仅美股，免费版最近100条）
        功能：日内价格走势
        成本：1次API调用
        """
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'outputsize': 'compact',  # 最近100条
        }
        
        data = self._make_request(params)
        
        if 'error' in data:
            return {'error': data['error'], 'symbol': symbol}
        
        try:
            time_series_key = f'Time Series ({interval})'
            time_series = data.get(time_series_key, {})
            
            if not time_series:
                return {'error': 'No intraday data', 'symbol': symbol}
            
            # 转换为列表
            intraday_data = []
            for timestamp, values in time_series.items():
                intraday_data.append({
                    'timestamp': timestamp,
                    'open': float(values.get('1. open', 0)),
                    'high': float(values.get('2. high', 0)),
                    'low': float(values.get('3. low', 0)),
                    'close': float(values.get('4. close', 0)),
                    'volume': int(values.get('5. volume', 0)),
                })
            
            # 按时间排序
            intraday_data.sort(key=lambda x: x['timestamp'])
            
            return {
                'symbol': symbol,
                'interval': interval,
                'data': intraday_data[:20],  # 返回最近20条
                'count': len(intraday_data),
                'api_calls_used': self.call_count,
            }
        except Exception as e:
            return {'error': f'Parse error: {e}', 'symbol': symbol}
    
    def get_daily(self, symbol: str, outputsize: str = 'compact') -> Dict:
        """
        获取日线历史数据
        功能：技术分析、均线计算
        成本：1次API调用
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize,  # compact=最近100天, full=全部历史
        }
        
        data = self._make_request(params)
        
        if 'error' in data:
            return {'error': data['error'], 'symbol': symbol}
        
        try:
            time_series = data.get('Time Series (Daily)', {})
            
            if not time_series:
                return {'error': 'No daily data', 'symbol': symbol}
            
            # 转换为列表
            daily_data = []
            for date, values in time_series.items():
                daily_data.append({
                    'date': date,
                    'open': float(values.get('1. open', 0)),
                    'high': float(values.get('2. high', 0)),
                    'low': float(values.get('3. low', 0)),
                    'close': float(values.get('4. close', 0)),
                    'volume': int(values.get('5. volume', 0)),
                })
            
            # 按日期排序（最新在前）
            daily_data.sort(key=lambda x: x['date'], reverse=True)
            
            # 计算均线
            closes = [d['close'] for d in daily_data]
            ma5 = sum(closes[:5]) / 5 if len(closes) >= 5 else None
            ma10 = sum(closes[:10]) / 10 if len(closes) >= 10 else None
            ma20 = sum(closes[:20]) / 20 if len(closes) >= 20 else None
            
            return {
                'symbol': symbol,
                'data': daily_data[:30],  # 返回最近30天
                'ma5': round(ma5, 2) if ma5 else None,
                'ma10': round(ma10, 2) if ma10 else None,
                'ma20': round(ma20, 2) if ma20 else None,
                'high_20d': round(max([d['high'] for d in daily_data[:20]]), 2) if len(daily_data) >= 20 else None,
                'low_20d': round(min([d['low'] for d in daily_data[:20]]), 2) if len(daily_data) >= 20 else None,
                'api_calls_used': self.call_count,
            }
        except Exception as e:
            return {'error': f'Parse error: {e}', 'symbol': symbol}
    
    def track_innoscience(self) -> Dict:
        """专门追踪英诺赛科"""
        symbol = self.TICKER_MAP['英诺赛科']
        
        # 获取当前价格
        quote = self.get_global_quote(symbol)
        
        # 获取日线数据（用于技术分析）
        daily = self.get_daily(symbol, outputsize='compact')
        
        return {
            'current': quote,
            'technical': daily if 'error' not in daily else None,
            'total_api_calls': self.call_count,
        }
    
    def track_gan_competitors(self) -> List[Dict]:
        """追踪氮化镓竞争对手（仅美股）"""
        symbols = [
            self.TICKER_MAP['英飞凌'],
            self.TICKER_MAP['纳微'],
            self.TICKER_MAP['德州仪器'],
        ]
        
        results = []
        for symbol in symbols:
            data = self.get_global_quote(symbol)
            results.append(data)
        
        return results
    
    def _get_name_from_symbol(self, symbol: str) -> str:
        """根据代码反查名称"""
        for name, code in self.TICKER_MAP.items():
            if code == symbol:
                return name
        return symbol
    
    def format_report(self, data: Dict, detailed: bool = False) -> str:
        """格式化报告输出"""
        if 'error' in data and 'current_price' not in data:
            return f"❌ 获取失败: {data.get('error', 'Unknown error')}"
        
        if 'current' in data:  # 英诺赛科详细报告
            c = data['current']
            if 'error' in c:
                return f"❌ {c.get('symbol', 'N/A')}: {c.get('error')}"
            
            change_emoji = "📈" if c.get('change', 0) >= 0 else "📉"
            
            report = f"""
{'='*50}
📊 英诺赛科 (02577.HK) Alpha Vantage追踪
{'='*50}
⏰ 更新时间: {c.get('timestamp', 'N/A')}
📅 最近交易日: {c.get('latest_trading_day', 'N/A')}
💰 当前价格: {c.get('current_price', 'N/A')}
📊 涨跌: {change_emoji} {c.get('change', 0):+.2f} ({c.get('change_pct', 0):+.2f}%)
📊 成交量: {c.get('volume', 0):,}

{'='*50}
"""
            
            # 添加技术分析
            tech = data.get('technical')
            if tech and 'error' not in tech:
                report += f"""
📈 技术分析:
• MA5: {tech.get('ma5', 'N/A')}
• MA10: {tech.get('ma10', 'N/A')}
• MA20: {tech.get('ma20', 'N/A')}
• 20日高点: {tech.get('high_20d', 'N/A')}
• 20日低点: {tech.get('low_20d', 'N/A')}
"""
            
            report += f"""
⚠️ {c.get('data_source', '')}
📊 API调用: {c.get('api_calls_used', 0)}/25
{'='*50}
"""
            return report
        else:  # 简单价格报告
            if 'error' in data:
                return f"❌ {data.get('symbol', 'N/A')}: {data.get('error')}"
            change_emoji = "📈" if data.get('change', 0) >= 0 else "📉"
            return f"  • {data.get('name', data.get('symbol', 'N/A'))}: {data.get('current_price', 'N/A')} {change_emoji} {data.get('change_pct', 0):+.2f}%"


def main():
    """测试运行 - 需要填入你的API Key"""
    
    # ⚠️ 请在这里填入你的Alpha Vantage API Key
    # 申请地址: https://www.alphavantage.co/support/#api-key
    API_KEY = "YOUR_API_KEY_HERE"
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️ 请先申请Alpha Vantage API Key")
        print("申请地址: https://www.alphavantage.co/support/#api-key")
        print("免费额度: 25次/天")
        return
    
    tracker = AlphaVantageTracker(api_key=API_KEY)
    
    print("="*60)
    print("Alpha Vantage 股票数据抓取测试")
    print("="*60)
    
    # 测试美股（实时）
    print("\n🔍 获取美股数据...")
    nvda = tracker.get_global_quote('NVDA')
    print(tracker.format_report(nvda))
    
    # 测试竞争对手
    print("\n🔍 获取氮化镓竞争对手...")
    competitors = tracker.track_gan_competitors()
    print("\n📊 竞争对手股价:")
    for comp in competitors:
        print(tracker.format_report(comp))
    
    # 测试英诺赛科（港股）
    print("\n🔍 获取英诺赛科数据...")
    print("(港股数据可能有延迟或不支持，需测试)")
    # innoscience = tracker.track_innoscience()
    # print(tracker.format_report(innoscience))
    
    print(f"\n📊 今日API调用统计: {tracker.call_count}/25")


if __name__ == "__main__":
    main()
