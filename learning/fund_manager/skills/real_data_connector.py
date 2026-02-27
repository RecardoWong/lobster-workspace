#!/usr/bin/env python3
"""
真实数据连接器
从各数据源获取实时数据
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

class RealDataConnector:
    """真实数据连接器"""
    
    def __init__(self):
        pass
    
    def get_stock_quote(self, symbol: str, market: str = "hk") -> dict:
        """
        获取股票实时行情
        使用腾讯财经API
        """
        try:
            # 腾讯财经API
            if market == "hk":
                # 港股: hk02577
                url = f"https://qt.gtimg.cn/q=hk{symbol}"
            elif market == "us":
                # 美股: usNVDA
                url = f"https://qt.gtimg.cn/q=us{symbol}"
            else:
                # A股
                url = f"https://qt.gtimg.cn/q={symbol}"
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('gbk')
                
            # 解析数据
            # 格式: v_hk02577="1~英诺赛科~02577~...";
            if '~' in data:
                parts = data.split('~')
                if len(parts) > 45:
                    try:
                        # 处理可能的小数或空值
                        volume_str = parts[6].replace(',', '')
                        volume = int(float(volume_str)) if volume_str and volume_str != '' else 0
                        
                        return {
                            "symbol": symbol,
                            "name": parts[1],
                            "price": float(parts[3]) if parts[3] else 0,
                            "change": float(parts[4]) if parts[4] else 0,
                            "change_pct": float(parts[5]) if parts[5] else 0,
                            "volume": volume,
                            "market_cap": parts[45] if len(parts) > 45 else None,
                            "update_time": datetime.now().isoformat()
                        }
                    except (ValueError, IndexError) as e:
                        return {"error": f"解析错误: {e}", "raw_preview": data[:300]}
            
            return {"error": "无法解析数据", "raw": data[:200]}
            
        except Exception as e:
            return {"error": str(e), "symbol": symbol}
    
    def get_crypto_quote(self, symbol: str = "BTC") -> dict:
        """
        获取加密货币行情
        使用币安API
        """
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            return {
                "symbol": symbol,
                "price": float(data['lastPrice']),
                "change": float(data['priceChange']),
                "change_pct": float(data['priceChangePercent']),
                "volume": float(data['volume']),
                "high_24h": float(data['highPrice']),
                "low_24h": float(data['lowPrice']),
                "update_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "symbol": symbol}
    
    def get_index_quote(self, index_code: str) -> dict:
        """
        获取指数行情
        使用腾讯财经API
        """
        try:
            # 指数代码映射
            index_map = {
                "nasdaq": "us.IXIC",      # 纳斯达克
                "sp500": "us.SP500",      # 标普500
                "hsi": "hkHSI",           # 恒生指数
                "hscei": "hkHSCEI",       # 恒生国企
                "hstech": "hkHSTECH",     # 恒生科技
                "shcomp": "sh000001",     # 上证指数
                "szcomp": "sz399001",     # 深证成指
            }
            
            code = index_map.get(index_code, index_code)
            url = f"https://qt.gtimg.cn/q={code}"
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('gbk')
                
            # 解析
            if '~' in data:
                parts = data.split('~')
                if len(parts) > 5:
                    try:
                        return {
                            "index": index_code,
                            "name": parts[1],
                            "price": float(parts[2]) if parts[2] else 0,
                            "change": float(parts[3]) if parts[3] else 0,
                            "change_pct": float(parts[4]) if parts[4] else 0,
                            "update_time": datetime.now().isoformat()
                        }
                    except (ValueError, IndexError) as e:
                        return {"error": f"解析错误: {e}", "raw_preview": data[:300]}
            
            return {"error": "无法解析数据", "raw": data[:200]}
            
        except Exception as e:
            return {"error": str(e), "index": index_code}
    
    def get_fred_data(self, series_id: str, api_key: str = None) -> dict:
        """
        获取FRED宏观数据
        需要FRED API Key
        """
        # 检查是否有API Key
        api_key = api_key or self._get_fred_api_key()
        
        if not api_key:
            return {"error": "FRED API Key未配置", "note": "请从 https://fred.stlouisfed.org/docs/api/api_key.html 申请"}
        
        try:
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&limit=1&sort_order=desc"
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                
            if 'observations' in data and len(data['observations']) > 0:
                latest = data['observations'][0]
                return {
                    "series_id": series_id,
                    "date": latest['date'],
                    "value": float(latest['value']) if latest['value'] != '.' else None,
                    "update_time": datetime.now().isoformat()
                }
            
            return {"error": "无数据", "series_id": series_id}
            
        except Exception as e:
            return {"error": str(e), "series_id": series_id}
    
    def _get_fred_api_key(self) -> str:
        """从环境变量获取FRED API Key"""
        import os
        return os.environ.get('FRED_API_KEY', None)
    
    def get_market_overview(self) -> dict:
        """获取市场概览"""
        overview = {
            "update_time": datetime.now().isoformat(),
            "stocks": {},
            "indices": {},
            "crypto": {}
        }
        
        # 港股 - 英诺赛科
        overview["stocks"]["02577.HK"] = self.get_stock_quote("02577", "hk")
        
        # 美股指数
        overview["indices"]["nasdaq"] = self.get_index_quote("nasdaq")
        overview["indices"]["sp500"] = self.get_index_quote("sp500")
        
        # 港股指数
        overview["indices"]["hsi"] = self.get_index_quote("hsi")
        overview["indices"]["hstech"] = self.get_index_quote("hstech")
        
        # 加密货币
        overview["crypto"]["BTC"] = self.get_crypto_quote("BTC")
        overview["crypto"]["ETH"] = self.get_crypto_quote("ETH")
        
        return overview


def main():
    """测试数据连接器"""
    connector = RealDataConnector()
    
    print("=" * 60)
    print("🔌 真实数据连接器测试")
    print("=" * 60)
    
    # 测试港股
    print("\n📈 港股 - 英诺赛科(02577):")
    hk_stock = connector.get_stock_quote("02577", "hk")
    print(json.dumps(hk_stock, ensure_ascii=False, indent=2))
    
    # 测试美股指数
    print("\n📊 纳斯达克指数:")
    nasdaq = connector.get_index_quote("nasdaq")
    print(json.dumps(nasdaq, ensure_ascii=False, indent=2))
    
    # 测试加密货币
    print("\n₿ 比特币:")
    btc = connector.get_crypto_quote("BTC")
    print(json.dumps(btc, ensure_ascii=False, indent=2))
    
    # 测试FRED数据
    print("\n🏦 FRED数据 (联邦基金利率):")
    fred = connector.get_fred_data("DFF")
    print(json.dumps(fred, ensure_ascii=False, indent=2))
    
    # 保存市场概览
    print("\n💾 保存市场概览...")
    overview = connector.get_market_overview()
    
    import os
    output_dir = "/root/.openclaw/workspace/learning/fund_manager/data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = f"{output_dir}/market_overview_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(overview, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存: {output_path}")


if __name__ == "__main__":
    main()
