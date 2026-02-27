#!/usr/bin/env python3
"""
均线系统分析器
计算多条均线，识别多头排列/空头排列
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class MATrend(Enum):
    """均线趋势"""
    GOLDEN_CROSS = "金叉"
    DEAD_CROSS = "死叉"
    BULLISH_ARRAY = "多头排列"
    BEARISH_ARRAY = "空头排列"
    CONVERGENCE = "均线粘合"
    DIVERGENCE = "均线发散"

@dataclass
class MAConfig:
    """均线配置"""
    period: int
    name: str
    
# 标准均线配置
DEFAULT_MA_PERIODS = [
    MAConfig(5, "MA5"),    # 周线
    MAConfig(10, "MA10"),  # 两周线
    MAConfig(20, "MA20"),  # 月线
    MAConfig(60, "MA60"),  # 季线
    MAConfig(120, "MA120"), # 半年线
    MAConfig(250, "MA250"), # 年线
]

class MASystemAnalyzer:
    """均线系统分析器"""
    
    def __init__(self, ma_periods: List[int] = None):
        """
        初始化
        
        Args:
            ma_periods: 均线周期列表，默认[5, 10, 20, 60, 120, 250]
        """
        self.ma_periods = ma_periods or [5, 10, 20, 60, 120, 250]
        self.ma_names = {5: "MA5", 10: "MA10", 20: "MA20", 
                        60: "MA60", 120: "MA120", 250: "MA250"}
    
    def calculate_ma(self, prices: List[float], period: int) -> List[float]:
        """
        计算简单移动平均线(SMA)
        """
        if len(prices) < period:
            return [None] * len(prices)
        
        ma = [None] * (period - 1)
        for i in range(period - 1, len(prices)):
            ma.append(sum(prices[i - period + 1:i + 1]) / period)
        return ma
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """
        计算指数移动平均线(EMA)
        
        Args:
            prices: 价格列表
            period: 周期
        """
        if len(prices) < period:
            return [None] * len(prices)
        
        multiplier = 2 / (period + 1)
        ema = [None] * (period - 1)
        
        # 第一个EMA用SMA
        ema.append(sum(prices[:period]) / period)
        
        for i in range(period, len(prices)):
            ema.append((prices[i] - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def analyze(self, prices: List[float], current_price: float = None) -> Dict:
        """
        分析均线系统
        
        Args:
            prices: 历史价格列表（收盘价）
            current_price: 当前价格（可选）
            
        Returns:
            分析结果字典
        """
        if len(prices) < max(self.ma_periods):
            return {"error": "数据不足，无法计算所有均线"}
        
        # 计算所有均线
        mas = {}
        for period in self.ma_periods:
            ma_values = self.calculate_ma(prices, period)
            mas[period] = ma_values
        
        # 获取最新均线值
        latest_ma = {}
        for period in self.ma_periods:
            valid_values = [v for v in mas[period] if v is not None]
            if valid_values:
                latest_ma[period] = valid_values[-1]
        
        # 分析结果
        result = {
            "current_price": current_price or prices[-1],
            "ma_values": latest_ma,
            "signals": [],
            "trend": "",
            "support_resistance": {},
            "recommendation": ""
        }
        
        # 1. 检测金叉/死叉
        result["signals"].extend(self._detect_crosses(latest_ma))
        
        # 2. 检测多头排列/空头排列
        array_result = self._detect_array(latest_ma)
        if array_result:
            result["signals"].append(array_result)
            result["trend"] = array_result["type"]
        
        # 3. 检测均线粘合/发散
        convergence_result = self._detect_convergence(latest_ma)
        if convergence_result:
            result["signals"].append(convergence_result)
        
        # 4. 找支撑和阻力位
        result["support_resistance"] = self._find_support_resistance(latest_ma, result["current_price"])
        
        # 5. 生成操作建议
        result["recommendation"] = self._generate_recommendation(result)
        
        return result
    
    def _detect_crosses(self, latest_ma: Dict[int, float]) -> List[Dict]:
        """检测金叉/死叉"""
        signals = []
        
        # 常用交叉对
        cross_pairs = [
            (5, 10, "短期"),
            (5, 20, "中期"),
            (10, 20, "中短期"),
            (20, 60, "中长期"),
            (50, 200, "长期")  # 金叉/死叉经典组合
        ]
        
        for short, long, term in cross_pairs:
            if short in latest_ma and long in latest_ma:
                # 这里需要历史数据判断交叉，简化处理
                if latest_ma[short] > latest_ma[long]:
                    # 可能金叉后
                    if short == 5 and long == 20:
                        signals.append({
                            "type": MATrend.GOLDEN_CROSS.value,
                            "term": term,
                            "pair": f"MA{short}/MA{long}",
                            "signal": "买入",
                            "strength": "强" if short == 5 and long == 20 else "中"
                        })
                else:
                    if short == 5 and long == 20:
                        signals.append({
                            "type": MATrend.DEAD_CROSS.value,
                            "term": term,
                            "pair": f"MA{short}/MA{long}",
                            "signal": "卖出",
                            "strength": "强" if short == 5 and long == 20 else "中"
                        })
        
        return signals
    
    def _detect_array(self, latest_ma: Dict[int, float]) -> Optional[Dict]:
        """检测多头排列/空头排列"""
        # 检查MA5 > MA10 > MA20（多头排列）
        if all(p in latest_ma for p in [5, 10, 20]):
            if latest_ma[5] > latest_ma[10] > latest_ma[20]:
                return {
                    "type": MATrend.BULLISH_ARRAY.value,
                    "description": "MA5 > MA10 > MA20",
                    "signal": "上涨趋势，持股待涨",
                    "confidence": 0.80
                }
            elif latest_ma[5] < latest_ma[10] < latest_ma[20]:
                return {
                    "type": MATrend.BEARISH_ARRAY.value,
                    "description": "MA5 < MA10 < MA20",
                    "signal": "下跌趋势，观望或减仓",
                    "confidence": 0.80
                }
        return None
    
    def _detect_convergence(self, latest_ma: Dict[int, float]) -> Optional[Dict]:
        """检测均线粘合/发散"""
        if all(p in latest_ma for p in [5, 10, 20]):
            values = [latest_ma[5], latest_ma[10], latest_ma[20]]
            max_diff = max(values) - min(values)
            avg = sum(values) / len(values)
            
            # 粘合：最大差 < 1%
            if max_diff / avg < 0.01:
                return {
                    "type": MATrend.CONVERGENCE.value,
                    "description": "短期均线粘合",
                    "signal": "变盘信号，等待突破",
                    "confidence": 0.70
                }
            # 发散：最大差 > 5%
            elif max_diff / avg > 0.05:
                return {
                    "type": MATrend.DIVERGENCE.value,
                    "description": "短期均线发散",
                    "signal": "趋势强劲，顺势操作",
                    "confidence": 0.75
                }
        return None
    
    def _find_support_resistance(self, latest_ma: Dict[int, float], current_price: float) -> Dict:
        """找支撑和阻力位"""
        sr = {"support": [], "resistance": []}
        
        # 价格在均线上方，均线是支撑
        # 价格在均线下方，均线是阻力
        for period in [20, 60, 120]:
            if period in latest_ma:
                ma_value = latest_ma[period]
                if current_price > ma_value:
                    sr["support"].append({
                        "level": ma_value,
                        "name": f"MA{period}",
                        "distance_pct": (current_price - ma_value) / current_price * 100
                    })
                else:
                    sr["resistance"].append({
                        "level": ma_value,
                        "name": f"MA{period}",
                        "distance_pct": (ma_value - current_price) / current_price * 100
                    })
        
        # 按距离排序
        sr["support"].sort(key=lambda x: x["distance_pct"])
        sr["resistance"].sort(key=lambda x: x["distance_pct"])
        
        return sr
    
    def _generate_recommendation(self, result: Dict) -> str:
        """生成操作建议"""
        signals = result.get("signals", [])
        trend = result.get("trend", "")
        
        # 综合判断
        if any(s["type"] == MATrend.BULLISH_ARRAY.value for s in signals):
            return "多头排列，建议持股或逢低买入"
        elif any(s["type"] == MATrend.BEARISH_ARRAY.value for s in signals):
            return "空头排列，建议观望或减仓"
        elif any(s["type"] == MATrend.GOLDEN_CROSS.value for s in signals):
            return "金叉信号，关注买入机会"
        elif any(s["type"] == MATrend.DEAD_CROSS.value for s in signals):
            return "死叉信号，注意风险"
        elif any(s["type"] == MATrend.CONVERGENCE.value for s in signals):
            return "均线粘合，等待方向明确"
        else:
            return "趋势不明，观望为主"
    
    def format_report(self, result: Dict) -> str:
        """格式化输出报告"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        lines = [
            "📈 均线系统分析报告",
            "=" * 50,
            ""
        ]
        
        # 当前价格和均线
        lines.append(f"💰 当前价格: ${result['current_price']:.2f}")
        lines.append("")
        lines.append("📊 均线数值:")
        for period in sorted(result['ma_values'].keys()):
            name = self.ma_names.get(period, f"MA{period}")
            value = result['ma_values'][period]
            # 计算偏离度
            deviation = (result['current_price'] - value) / value * 100
            emoji = "🟢" if deviation > 0 else "🔴"
            lines.append(f"   {emoji} {name}: ${value:.2f} ({deviation:+.2f}%)")
        
        # 信号
        if result['signals']:
            lines.append("")
            lines.append("🔔 技术信号:")
            for signal in result['signals']:
                lines.append(f"   • {signal.get('type', '未知')}")
                if 'description' in signal:
                    lines.append(f"     {signal['description']}")
                if 'signal' in signal:
                    lines.append(f"     💡 {signal['signal']}")
        
        # 支撑阻力
        sr = result.get('support_resistance', {})
        if sr.get('support') or sr.get('resistance'):
            lines.append("")
            lines.append("🎯 支撑/阻力:")
            if sr.get('support'):
                lines.append("   支撑位:")
                for s in sr['support'][:2]:
                    lines.append(f"     • {s['name']}: ${s['level']:.2f} (距离{s['distance_pct']:.1f}%)")
            if sr.get('resistance'):
                lines.append("   阻力位:")
                for r in sr['resistance'][:2]:
                    lines.append(f"     • {r['name']}: ${r['level']:.2f} (距离{r['distance_pct']:.1f}%)")
        
        # 建议
        lines.append("")
        lines.append(f"💡 操作建议: {result['recommendation']}")
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)


def demo():
    """演示均线系统分析"""
    print("=" * 60)
    print("📈 均线系统分析器演示")
    print("=" * 60)
    
    analyzer = MASystemAnalyzer()
    
    # 生成模拟价格数据（上涨趋势）
    import random
    random.seed(42)
    base_price = 100
    prices = [base_price]
    for i in range(1, 300):
        change = random.gauss(0.05, 1.5)  # 轻微上涨趋势
        prices.append(max(prices[-1] + change, 50))  # 确保不跌太多
    
    # 分析
    result = analyzer.analyze(prices)
    report = analyzer.format_report(result)
    print(report)


if __name__ == "__main__":
    demo()
