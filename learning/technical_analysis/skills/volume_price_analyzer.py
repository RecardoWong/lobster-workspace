#!/usr/bin/env python3
"""
量价关系分析器
分析成交量与价格的关系，识别量价背离、放量突破等信号
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class VolumeSignal(Enum):
    """量价信号类型"""
    VOLUME_PRICE_RISE = "量价齐升"
    VOLUME_PRICE_FALL = "量价齐跌"
    DIVERGENCE_TOP = "顶背离"
    DIVERGENCE_BOTTOM = "底背离"
    VOLUME_SHRINK_PULLBACK = "缩量回调"
    VOLUME_SURGE_BREAKOUT = "放量突破"
    VOLUME_STALL = "放量滞涨"
    VOLUME_DRY_UP = "量能枯竭"

@dataclass
class PriceVolumeData:
    """价格成交量数据"""
    price: float
    volume: float
    high: float = 0
    low: float = 0
    open: float = 0

class VolumePriceAnalyzer:
    """量价关系分析器"""
    
    def __init__(self, lookback_period: int = 20):
        self.lookback_period = lookback_period
    
    def analyze(self, data: List[PriceVolumeData]) -> Dict:
        """分析量价关系"""
        if len(data) < self.lookback_period:
            return {"error": f"数据不足，至少需要{self.lookback_period}条数据"}
        
        prices = [d.price for d in data]
        volumes = [d.volume for d in data]
        
        # 计算均量
        vol_ma = sum(volumes[-self.lookback_period:]) / self.lookback_period
        
        result = {
            "current_price": prices[-1],
            "current_volume": volumes[-1],
            "volume_ma": vol_ma,
            "signals": [],
            "trend_strength": 0,
            "recommendation": ""
        }
        
        # 检测信号
        divergence = self._detect_divergence(prices, volumes)
        if divergence:
            result["signals"].append(divergence)
        
        alignment = self._detect_price_volume_alignment(prices, volumes)
        if alignment:
            result["signals"].append(alignment)
        
        volume_anomaly = self._detect_volume_anomaly(prices, volumes, vol_ma)
        if volume_anomaly:
            result["signals"].append(volume_anomaly)
        
        result["trend_strength"] = self._calculate_trend_strength(prices, volumes)
        result["recommendation"] = self._generate_recommendation(result)
        
        return result
    
    def _detect_divergence(self, prices: List[float], volumes: List[float]) -> Optional[Dict]:
        """检测量价背离"""
        if len(prices) < 10:
            return None
        
        recent_prices = prices[-10:]
        recent_volumes = volumes[-10:]
        
        price_high_idx = recent_prices.index(max(recent_prices))
        price_low_idx = recent_prices.index(min(recent_prices))
        
        # 顶背离
        if price_high_idx >= 7:
            recent_vol_max = max(recent_volumes[-5:])
            earlier_vol_max = max(recent_volumes[:5])
            avg_early_price = sum(recent_prices[:-3]) / len(recent_prices[:-3])
            
            if recent_prices[-1] > avg_early_price * 1.05:
                if recent_vol_max < earlier_vol_max * 0.8:
                    return {
                        "type": VolumeSignal.DIVERGENCE_TOP.value,
                        "description": "价格创新高，成交量萎缩",
                        "signal": "警惕回调风险",
                        "confidence": 0.75,
                        "urgency": "高"
                    }
        
        # 底背离
        if price_low_idx >= 7:
            recent_vol_min = min(recent_volumes[-5:])
            earlier_vol_min = min(recent_volumes[:5])
            avg_early_price = sum(recent_prices[:-3]) / len(recent_prices[:-3])
            
            if recent_prices[-1] < avg_early_price * 0.95:
                if recent_vol_min > earlier_vol_min * 1.2:
                    return {
                        "type": VolumeSignal.DIVERGENCE_BOTTOM.value,
                        "description": "价格创新低，成交量未跟跌",
                        "signal": "可能见底，关注反弹",
                        "confidence": 0.70,
                        "urgency": "中"
                    }
        
        return None
    
    def _detect_price_volume_alignment(self, prices: List[float], volumes: List[float]) -> Optional[Dict]:
        """检测量价配合"""
        recent_prices = prices[-5:]
        recent_volumes = volumes[-5:]
        
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        vol_avg_earlier = sum(recent_volumes[:-1]) / len(recent_volumes[:-1])
        volume_change = (recent_volumes[-1] - vol_avg_earlier) / vol_avg_earlier if vol_avg_earlier > 0 else 0
        
        # 量价齐升
        if price_change > 0.03 and volume_change > 0.2:
            return {
                "type": VolumeSignal.VOLUME_PRICE_RISE.value,
                "description": f"价格上涨{price_change*100:.1f}%，成交量放大{volume_change*100:.1f}%",
                "signal": "健康上涨，可持股",
                "confidence": 0.80,
                "urgency": "低"
            }
        
        # 量价齐跌
        if price_change < -0.03 and volume_change > 0.3:
            return {
                "type": VolumeSignal.VOLUME_PRICE_FALL.value,
                "description": f"价格下跌{abs(price_change)*100:.1f}%，成交量放大",
                "signal": "恐慌抛售，可能超跌反弹",
                "confidence": 0.70,
                "urgency": "高"
            }
        
        # 缩量回调
        if price_change < -0.02 and volume_change < -0.2:
            return {
                "type": VolumeSignal.VOLUME_SHRINK_PULLBACK.value,
                "description": f"价格回调{abs(price_change)*100:.1f}%，成交量萎缩",
                "signal": "缩量洗盘，关注企稳",
                "confidence": 0.65,
                "urgency": "中"
            }
        
        return None
    
    def _detect_volume_anomaly(self, prices: List[float], volumes: List[float], vol_ma: float) -> Optional[Dict]:
        """检测量能异常"""
        current_vol = volumes[-1]
        current_price = prices[-1]
        prev_price = prices[-2]
        
        vol_ratio = current_vol / vol_ma if vol_ma > 0 else 1
        price_change = (current_price - prev_price) / prev_price
        
        # 放量滞涨
        if vol_ratio > 2.0 and abs(price_change) < 0.01:
            return {
                "type": VolumeSignal.VOLUME_STALL.value,
                "description": f"成交量放大{vol_ratio:.1f}倍，价格几乎不变",
                "signal": "放量滞涨，主力出货嫌疑",
                "confidence": 0.80,
                "urgency": "高"
            }
        
        # 放量突破
        if vol_ratio > 1.5 and price_change > 0.03:
            return {
                "type": VolumeSignal.VOLUME_SURGE_BREAKOUT.value,
                "description": f"成交量放大{vol_ratio:.1f}倍，价格上涨{price_change*100:.1f}%",
                "signal": "放量突破，趋势可能加速",
                "confidence": 0.85,
                "urgency": "中"
            }
        
        # 量能枯竭
        if vol_ratio < 0.5:
            return {
                "type": VolumeSignal.VOLUME_DRY_UP.value,
                "description": f"成交量仅为均量{vol_ratio*100:.0f}%",
                "signal": "量能枯竭，变盘在即",
                "confidence": 0.60,
                "urgency": "中"
            }
        
        return None
    
    def _calculate_trend_strength(self, prices: List[float], volumes: List[float]) -> float:
        """计算趋势强度"""
        if len(prices) < 10:
            return 50
        
        price_change = (prices[-1] - prices[-10]) / prices[-10]
        
        recent_vol = sum(volumes[-5:]) / 5
        earlier_vol = sum(volumes[-10:-5]) / 5
        vol_ratio = recent_vol / earlier_vol if earlier_vol > 0 else 1
        
        if price_change > 0 and vol_ratio > 1:
            strength = min(50 + price_change * 500 + (vol_ratio - 1) * 20, 95)
        elif price_change < 0 and vol_ratio > 1:
            strength = max(50 + price_change * 500 - (vol_ratio - 1) * 20, 5)
        else:
            strength = 50 + price_change * 300
        
        return max(0, min(100, strength))
    
    def _generate_recommendation(self, result: Dict) -> str:
        """生成操作建议"""
        signals = result.get("signals", [])
        
        for signal in signals:
            signal_type = signal.get("type", "")
            
            if signal_type == VolumeSignal.DIVERGENCE_TOP.value:
                return "⚠️ 顶背离，考虑减仓"
            elif signal_type == VolumeSignal.VOLUME_STALL.value:
                return "⚠️ 放量滞涨，警惕出货"
            elif signal_type == VolumeSignal.DIVERGENCE_BOTTOM.value:
                return "💡 底背离，关注买入机会"
            elif signal_type == VolumeSignal.VOLUME_SURGE_BREAKOUT.value:
                return "🚀 放量突破，可追涨"
            elif signal_type == VolumeSignal.VOLUME_PRICE_RISE.value:
                return "✅ 量价齐升，持股"
            elif signal_type == VolumeSignal.VOLUME_SHRINK_PULLBACK.value:
                return "💡 缩量回调，关注低吸"
        
        strength = result.get("trend_strength", 50)
        if strength > 70:
            return "💪 趋势较强，顺势操作"
        elif strength < 30:
            return "⚠️ 趋势较弱，谨慎观望"
        else:
            return "➡️ 趋势中性，等待信号"
    
    def format_report(self, result: Dict) -> str:
        """格式化输出报告"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        lines = [
            "📊 量价关系分析报告",
            "=" * 50,
            ""
        ]
        
        lines.append(f"💰 当前价格: ${result['current_price']:.2f}")
        lines.append(f"📈 当前成交量: {result['current_volume']:,.0f}")
        lines.append(f"📊 均量({self.lookback_period}日): {result['volume_ma']:,.0f}")
        
        vol_ratio = result['current_volume'] / result['volume_ma'] if result['volume_ma'] > 0 else 1
        emoji = "🟢" if vol_ratio > 1.2 else "🔴" if vol_ratio < 0.8 else "⚪"
        lines.append(f"{emoji} 量能比: {vol_ratio:.2f}x")
        lines.append("")
        
        strength = result['trend_strength']
        strength_bar = "█" * int(strength / 10) + "░" * (10 - int(strength / 10))
        lines.append(f"💪 趋势强度: [{strength_bar}] {strength:.0f}/100")
        lines.append("")
        
        if result['signals']:
            lines.append("🔔 量价信号:")
            for signal in result['signals']:
                urgency_emoji = "🚨" if signal.get('urgency') == '高' else "⚠️" if signal.get('urgency') == '中' else "💡"
                lines.append(f"   {urgency_emoji} {signal['type']}")
                lines.append(f"      {signal['description']}")
                lines.append(f"      信号: {signal['signal']}")
                lines.append("")
        
        lines.append(f"💡 操作建议: {result['recommendation']}")
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)


def demo():
    """演示量价分析"""
    print("=" * 60)
    print("📊 量价关系分析器演示")
    print("=" * 60)
    
    analyzer = VolumePriceAnalyzer()
    
    import random
    random.seed(42)
    data = []
    base_price = 100
    base_vol = 1000000
    
    for i in range(30):
        if i >= 25:
            vol = base_vol * (2.0 + random.random())
            price_change = random.gauss(2, 1)
        else:
            vol = base_vol * (0.8 + random.random() * 0.4)
            price_change = random.gauss(0, 1)
        
        price = max(base_price + price_change, 50)
        data.append(PriceVolumeData(
            price=price,
            volume=vol,
            high=price * 1.02,
            low=price * 0.98,
            open=price - price_change * 0.5
        ))
        base_price = price
    
    result = analyzer.analyze(data)
    print(analyzer.format_report(result))


if __name__ == "__main__":
    demo()
