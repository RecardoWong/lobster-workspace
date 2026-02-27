"""
FRED API 客户端
美联储经济数据API封装
文档: https://fred.stlouisfed.org/docs/api/fred/
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# 自动加载.env文件
def _load_env():
    """从.env文件加载环境变量"""
    # 尝试多个路径
    env_paths = [
        Path(__file__).parent / ".env",  # 本地.env
        Path("/root/.openclaw/workspace/lobster-workspace/.env"),  # 主项目.env
        Path("/root/.openclaw/workspace/.env"),  # 根目录.env
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)
            break  # 只加载第一个找到的

_load_env()

class FREDClient:
    """FRED API 客户端"""
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    # 常用指标ID映射
    SERIES = {
        # 利率相关
        "fed_funds_rate": "FEDFUNDS",      # 联邦基金利率
        "treasury_10y": "DGS10",           # 10年期国债收益率
        "treasury_2y": "DGS2",             # 2年期国债收益率
        
        # 通胀相关
        "cpi": "CPIAUCSL",                 # 消费者价格指数
        "core_cpi": "CPILFESL",            # 核心CPI（不含食品和能源）
        "ppi": "PPIACO",                   # 生产者价格指数
        
        # 就业数据
        "unemployment_rate": "UNRATE",     # 失业率
        "nonfarm_payrolls": "PAYEMS",      # 非农就业人数
        
        # 经济增长
        "gdp": "GDP",                      # 国内生产总值
        "real_gdp_growth": "A191RL1Q225SBEA",  # 实际GDP增长率
        
        # 货币供应量
        "m2_money_supply": "M2SL",         # M2货币供应量
        
        # 利差（衰退指标）
        "yield_spread_10y_2y": "T10Y2Y",   # 10年期与2年期国债利差
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化FRED客户端
        
        Args:
            api_key: FRED API Key，如果不提供则从环境变量 FRED_API_KEY 读取
        """
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供FRED API Key或通过环境变量FRED_API_KEY设置")
    
    def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送API请求"""
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["api_key"] = self.api_key
        params["file_type"] = "json"
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_series(self, series_id: str, 
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   limit: int = 100) -> List[Dict]:
        """
        获取时间序列数据
        
        Args:
            series_id: 数据系列ID
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回数据点数量限制
            
        Returns:
            数据点列表，每项包含 date 和 value
        """
        params = {
            "series_id": series_id,
            "sort_order": "desc",
            "limit": limit
        }
        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date
            
        data = self._request("series/observations", params)
        
        # 转换数据格式
        observations = data.get("observations", [])
        result = []
        for obs in observations:
            value = obs.get("value")
            # FRED用"."表示缺失值
            if value and value != ".":
                result.append({
                    "date": obs["date"],
                    "value": float(value)
                })
        return result
    
    def get_series_info(self, series_id: str) -> Dict:
        """获取数据系列信息"""
        data = self._request("series", {"series_id": series_id})
        seriess = data.get("seriess", [])
        return seriess[0] if seriess else {}
    
    def get_latest(self, series_id: str) -> Optional[Dict]:
        """获取最新数据点"""
        data = self.get_series(series_id, limit=1)
        return data[0] if data else None
    
    def get_yield_curve(self, days: int = 30) -> List[Dict]:
        """
        获取收益率曲线数据（10年期 - 2年期利差）
        负值通常预示经济衰退
        """
        return self.get_series(self.SERIES["yield_spread_10y_2y"], limit=days)
    
    def get_inflation_signals(self) -> Dict:
        """
        获取通胀相关信号
        返回CPI和核心CPI的最新数据
        """
        cpi = self.get_latest(self.SERIES["cpi"])
        core_cpi = self.get_latest(self.SERIES["core_cpi"])
        
        return {
            "cpi": cpi,
            "core_cpi": core_cpi,
            "has_data": cpi is not None and core_cpi is not None
        }
    
    def get_liquidity_summary(self) -> Dict:
        """
        获取流动性摘要
        包括联邦基金利率、M2货币供应量、国债收益率
        """
        fed_rate = self.get_latest(self.SERIES["fed_funds_rate"])
        m2 = self.get_latest(self.SERIES["m2_money_supply"])
        t10y = self.get_latest(self.SERIES["treasury_10y"])
        t2y = self.get_latest(self.SERIES["treasury_2y"])
        
        spread = None
        if t10y and t2y:
            spread = round(t10y["value"] - t2y["value"], 2)
        
        return {
            "fed_funds_rate": fed_rate,
            "m2_supply": m2,
            "treasury_10y": t10y,
            "treasury_2y": t2y,
            "yield_spread": spread,
            "inverted": spread is not None and spread < 0
        }


# 便捷函数
def get_client() -> FREDClient:
    """获取默认配置的客户端实例"""
    return FREDClient()


if __name__ == "__main__":
    # 测试代码
    import json
    
    client = FREDClient()
    
    print("=" * 50)
    print("FRED API 测试")
    print("=" * 50)
    
    # 测试1: 获取最新联邦基金利率
    print("\n1. 联邦基金利率:")
    rate = client.get_latest(FREDClient.SERIES["fed_funds_rate"])
    if rate:
        print(f"   日期: {rate['date']}, 利率: {rate['value']}%")
    
    # 测试2: 获取收益率曲线
    print("\n2. 收益率曲线利差 (10Y-2Y):")
    curve = client.get_yield_curve(days=5)
    for point in curve[:3]:
        status = "⚠️ 倒挂" if point["value"] < 0 else "正常"
        print(f"   {point['date']}: {point['value']}% {status}")
    
    # 测试3: 流动性摘要
    print("\n3. 流动性摘要:")
    summary = client.get_liquidity_summary()
    print(f"   收益率曲线倒挂: {'是' if summary['inverted'] else '否'}")
    if summary["yield_spread"]:
        print(f"   利差: {summary['yield_spread']}%")
