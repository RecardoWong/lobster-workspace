#!/usr/bin/env python3
"""
FRED API接入器
获取美联储宏观经济数据
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class FREDClient:
    """FRED API客户端"""
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._load_api_key()
        
    def _load_api_key(self) -> str:
        """从文件加载API Key"""
        try:
            with open('/root/.openclaw/workspace/.fred_api_key', 'r') as f:
                return f.read().strip()
        except:
            return None
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """发起API请求"""
        if not self.api_key:
            print("❌ 未配置FRED API Key")
            return None
        
        params['api_key'] = self.api_key
        params['file_type'] = 'json'
        
        try:
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API请求失败: {e}")
            return None
    
    def get_series_data(self, series_id: str, limit: int = 10) -> Optional[Dict]:
        """获取时间序列数据"""
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        params = {
            'series_id': series_id,
            'observation_start': start_date.strftime('%Y-%m-%d'),
            'observation_end': end_date.strftime('%Y-%m-%d'),
            'limit': limit
        }
        
        return self._make_request('series/observations', params)
    
    def get_latest_value(self, series_id: str) -> Optional[float]:
        """获取最新值"""
        data = self.get_series_data(series_id, limit=1)
        if data and 'observations' in data and len(data['observations']) > 0:
            try:
                return float(data['observations'][0]['value'])
            except:
                return None
        return None
    
    def get_fed_data(self) -> Dict:
        """获取美联储核心数据"""
        # 关键指标系列ID
        series = {
            'fed_balance_sheet': 'WALCL',      # 美联储总资产
            'tga_balance': 'WTREGEN',          # 财政部一般账户
            'on_rrp': 'RRPONTSYD',             # 隔夜逆回购
            'fed_rate': 'DFF',                 # 联邦基金利率
            'sofr': 'SOFR',                    # 隔夜融资利率
            'treasury_10y': 'DGS10',           # 10年美债收益率
            'treasury_2y': 'DGS2',             # 2年美债收益率
            'cpi': 'CPIAUCSL',                 # CPI
            'unemployment': 'UNRATE',          # 失业率
            'nfp': 'PAYEMS',                   # 非农就业
        }
        
        result = {}
        print("📊 正在获取FRED数据...")
        
        for name, series_id in series.items():
            value = self.get_latest_value(series_id)
            result[name] = value
            if value:
                print(f"  ✅ {name}: {value}")
            else:
                print(f"  ⚠️ {name}: 获取失败")
        
        return result
    
    def get_mock_data(self) -> Dict:
        """获取模拟数据 (API未配置时使用)"""
        return {
            'fed_balance_sheet': 7500.0,      # $7.5T
            'tga_balance': 700.0,             # $700B
            'on_rrp': 500.0,                  # $500B
            'fed_rate': 5.33,                 # 5.33%
            'sofr': 5.35,                     # 5.35%
            'treasury_10y': 4.30,             # 4.30%
            'treasury_2y': 4.65,              # 4.65%
            'cpi': 3.1,                       # 3.1%
            'unemployment': 3.7,              # 3.7%
            'nfp': 353000.0,                  # +353k
            'is_mock': True
        }

def setup_fred_api():
    """设置FRED API Key向导"""
    print("="*70)
    print("🔧 FRED API Key设置向导")
    print("="*70)
    print()
    print("FRED提供免费的美国经济数据API")
    print()
    print("申请步骤:")
    print("1. 访问 https://fred.stlouisfed.org/")
    print("2. 点击右上角 'My Account' → 'API Keys'")
    print("3. 点击 'Request API Key'")
    print("4. 填写简单信息，立即获得Key")
    print()
    print("或者直接把Key发给我，我会保存到:")
    print("  /root/.openclaw/workspace/.fred_api_key")
    print()
    print("="*70)

if __name__ == '__main__':
    client = FREDClient()
    
    if not client.api_key:
        setup_fred_api()
        print("\n⚠️ 未检测到API Key，使用模拟数据演示...")
        data = client.get_mock_data()
    else:
        data = client.get_fed_data()
    
    print("\n📊 美联储核心数据:")
    print("-"*70)
    
    # 净流动性
    net_liquidity = data.get('fed_balance_sheet', 0) - data.get('tga_balance', 0) - data.get('on_rrp', 0)
    print(f"💰 净流动性: ${net_liquidity:.0f}B")
    print(f"   (美联储资产${data.get('fed_balance_sheet', 0):.0f}B - TGA${data.get('tga_balance', 0):.0f}B - ON RRP${data.get('on_rrp', 0):.0f}B)")
    
    print(f"\n📈 利率环境:")
    print(f"   联邦基金利率: {data.get('fed_rate', 0):.2f}%")
    print(f"   SOFR: {data.get('sofr', 0):.2f}%")
    print(f"   10年美债: {data.get('treasury_10y', 0):.2f}%")
    print(f"   2年美债: {data.get('treasury_2y', 0):.2f}%")
    
    print(f"\n🎯 经济数据:")
    print(f"   CPI: {data.get('cpi', 0):.1f}%")
    print(f"   失业率: {data.get('unemployment', 0):.1f}%")
    print(f"   非农就业: +{data.get('nfp', 0):.0f}k")
    
    if data.get('is_mock'):
        print("\n⚠️  当前使用模拟数据")
        print("    配置真实API Key后自动获取实时数据")
    else:
        print("\n✅ 数据来源: FRED API (实时)")
    
    print("="*70)
