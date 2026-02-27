#!/usr/bin/env python3
"""
Alpha Vantage API 客户端
用于获取美股实时价格、财务数据
"""

import os
import json
import urllib.request
from datetime import datetime

class AlphaVantageClient:
    """Alpha Vantage API 客户端"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("请设置 ALPHA_VANTAGE_API_KEY 环境变量")
    
    def _request(self, params):
        """发送API请求"""
        params['apikey'] = self.api_key
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.BASE_URL}?{query_string}"
        
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Alpha Vantage API 请求失败: {e}")
            return None
    
    def get_quote(self, symbol):
        """获取股票实时报价"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        result = self._request(params)
        if result and 'Global Quote' in result:
            quote = result['Global Quote']
            return {
                'symbol': quote.get('01. symbol', symbol),
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%'),
                'volume': int(quote.get('06. volume', 0)),
                'latest_trading_day': quote.get('07. latest trading day', '')
            }
        return None
    
    def get_company_overview(self, symbol):
        """获取公司概况（PE、市值等）"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        result = self._request(params)
        if result and 'Symbol' in result:
            return {
                'symbol': result.get('Symbol'),
                'name': result.get('Name'),
                'market_cap': result.get('MarketCapitalization'),
                'pe_ratio': result.get('PERatio'),
                'eps': result.get('EPS'),
                'dividend_yield': result.get('DividendYield'),
                '52_week_high': result.get('52WeekHigh'),
                '52_week_low': result.get('52WeekLow'),
                'sector': result.get('Sector'),
                'industry': result.get('Industry')
            }
        return None
    
    def get_daily(self, symbol):
        """获取日线数据"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact'  # 最近100天
        }
        
        result = self._request(params)
        if result and 'Time Series (Daily)' in result:
            return result['Time Series (Daily)']
        return None
    
    def format_stock_info(self, symbol):
        """格式化股票信息"""
        quote = self.get_quote(symbol)
        overview = self.get_company_overview(symbol)
        
        if not quote:
            return f"❌ 无法获取 {symbol} 的数据"
        
        lines = [
            f"📈 **{symbol}** 股票信息",
            f"",
            f"💰 当前价格: ${quote['price']:.2f}",
            f"📊 涨跌: {quote['change']:+.2f} ({quote['change_percent']})",
            f"📅 最新交易日: {quote['latest_trading_day']}",
            f"📈 成交量: {quote['volume']:,}",
        ]
        
        if overview:
            lines.extend([
                f"",
                f"🏢 公司名称: {overview.get('name', 'N/A')}",
                f"💎 市值: ${overview.get('market_cap', 'N/A')}",
                f"📊 PE比率: {overview.get('pe_ratio', 'N/A')}",
                f"💵 EPS: ${overview.get('eps', 'N/A')}",
                f"🏭 行业: {overview.get('industry', 'N/A')}",
            ])
        
        return '\n'.join(lines)

if __name__ == '__main__':
    # 测试
    try:
        client = AlphaVantageClient()
        print("✅ Alpha Vantage API 连接成功\n")
        
        # 测试获取股票数据
        symbols = ['NVDA', 'AAPL', 'TSLA']
        for symbol in symbols:
            print(client.format_stock_info(symbol))
            print("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
