#!/usr/bin/env python3
"""
Alpha Vantage API 客户端 - yfinance备用方案
免费额度: 500次/天
申请: https://www.alphavantage.co/support/#api-key
"""

import os
import requests
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class StockData:
    """股票数据结构"""
    ticker: str
    price: float
    pe: Optional[float] = None
    eps: Optional[float] = None
    market_cap: Optional[float] = None
    revenue: Optional[float] = None
    roe: Optional[float] = None
    
class AlphaVantageClient:
    """Alpha Vantage客户端"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_KEY')
        if not self.api_key:
            raise ValueError("需要提供Alpha Vantage API Key")
    
    def get_overview(self, ticker: str) -> Dict:
        """获取公司概况和财务指标"""
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': self.api_key
        }
        
        response = requests.get(self.BASE_URL, params=params, timeout=15)
        data = response.json()
        
        if 'Symbol' not in data:
            print(f"[错误] 无法获取 {ticker} 数据: {data.get('Note', 'Unknown')}")
            return {}
        
        return {
            'ticker': data.get('Symbol'),
            'name': data.get('Name'),
            'market_cap': float(data.get('MarketCapitalization', 0)) / 1e9 if data.get('MarketCapitalization') else None,  # 转为B
            'pe': float(data.get('PERatio')) if data.get('PERatio') else None,
            'eps': float(data.get('EPS')) if data.get('EPS') else None,
            'roe': float(data.get('ReturnOnEquityTTM', 0)) * 100 if data.get('ReturnOnEquityTTM') else None,
            'revenue': float(data.get('RevenueTTM', 0)) / 1e9 if data.get('RevenueTTM') else None,  # 转为B
            'gross_margin': float(data.get('GrossProfitTTM', 0)) / float(data.get('RevenueTTM', 1)) * 100 if data.get('GrossProfitTTM') and data.get('RevenueTTM') else None,
            'dividend_yield': float(data.get('DividendYield', 0)) * 100 if data.get('DividendYield') else None,
            '52_week_high': float(data.get('52WeekHigh')) if data.get('52WeekHigh') else None,
            '52_week_low': float(data.get('52WeekLow')) if data.get('52WeekLow') else None,
        }

# 测试
if __name__ == "__main__":
    import sys
    api_key = os.getenv('ALPHA_VANTAGE_KEY')
    
    if not api_key:
        print("请设置环境变量 ALPHA_VANTAGE_KEY")
        print("申请地址: https://www.alphavantage.co/support/#api-key")
        sys.exit(1)
    
    client = AlphaVantageClient(api_key)
    
    # 测试AAPL
    print("测试获取 AAPL 数据...")
    data = client.get_overview('AAPL')
    
    if data:
        print(f"\n公司: {data.get('name')}")
        print(f"市值: ${data.get('market_cap'):.1f}B" if data.get('market_cap') else "市值: N/A")
        print(f"PE: {data.get('pe')}")
        print(f"EPS: ${data.get('eps')}")
        print(f"ROE: {data.get('roe'):.1f}%" if data.get('roe') else "ROE: N/A")
    else:
        print("获取失败")
