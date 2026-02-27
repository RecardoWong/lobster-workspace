#!/usr/bin/env python3
"""
市场数据抓取工具
使用 Yahoo Finance API 获取实时数据
"""

import requests
import json
from datetime import datetime

class YahooFinanceAPI:
    """Yahoo Finance 数据接口"""
    
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_quote(self, symbol: str) -> dict:
        """获取股票报价"""
        try:
            url = f"{self.BASE_URL}{symbol}"
            params = {
                'interval': '1d',
                'range': '1d'
            }
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result['meta']
                
                return {
                    'symbol': symbol,
                    'price': meta.get('regularMarketPrice', 0),
                    'previous_close': meta.get('previousClose', 0),
                    'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
                    'change_pct': ((meta.get('regularMarketPrice', 0) / meta.get('previousClose', 1)) - 1) * 100,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
        
        return None
    
    def get_market_summary(self) -> dict:
        """获取市场摘要"""
        indices = {
            '^GSPC': 'S&P 500',
            '^IXIC': 'NASDAQ',
            '^DJI': 'Dow Jones',
            '^VIX': 'VIX',
            '^TNX': '10Y Treasury'
        }
        
        results = {}
        for symbol, name in indices.items():
            data = self.get_quote(symbol)
            if data:
                results[name] = data
        
        return results

if __name__ == '__main__':
    api = YahooFinanceAPI()
    
    # 测试获取市场数据
    print("获取市场摘要...")
    market_data = api.get_market_summary()
    print(json.dumps(market_data, indent=2))
    
    # 测试获取个股
    print("\n获取个股数据...")
    for symbol in ['AAPL', 'MSFT', 'NVDA', 'TSLA']:
        data = api.get_quote(symbol)
        if data:
            print(f"{symbol}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
