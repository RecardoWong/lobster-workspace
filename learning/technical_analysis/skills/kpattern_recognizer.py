#!/usr/bin/env python3
"""
K线形态识别器
识别常见K线形态，判断多空信号
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class PatternType(Enum):
    """形态类型"""
    BULLISH = "看涨"
    BEARISH = "看跌"
    NEUTRAL = "中性"

@dataclass
class Candle:
    """单根K线数据"""
    open: float
    high: float
    low: float
    close: float
    volume: float = 0
    
    @property
    def body(self) -> float:
        """实体大小"""
        return abs(self.close - self.open)
    
    @property
    def upper_shadow(self) -> float:
        """上影线"""
        return self.high - max(self.open, self.close)
    
    @property
    def lower_shadow(self) -> float:
        """下影线"""
        return min(self.open, self.close) - self.low
    
    @property
    def range(self) -> float:
        """总区间"""
        return self.high - self.low
    
    @property
    def is_bullish(self) -> bool:
        """是否阳线"""
        return self.close > self.open
    
    @property
    def is_bearish(self) -> bool:
        """是否阴线"""
        return self.close < self.open


class KPatternRecognizer:
    """K线形态识别器"""
    
    def __init__(self):
        self.patterns = {
            # 单根形态
            "hammer": self._is_hammer,
            "shooting_star": self._is_shooting_star,
            "doji": self._is_doji,
            "marubozu": self._is_marubozu,
            
            # 双根形态
            "engulfing": self._is_engulfing,
            "harami": self._is_harami,
            "piercing": self._is_piercing,
            "dark_cloud": self._is_dark_cloud,
            
            # 三根形态
            "morning_star": self._is_morning_star,
            "evening_star": self._is_evening_star,
            "three_white_soldiers": self._is_three_white_soldiers,
            "three_black_crows": self._is_three_black_crows,
        }
    
    def recognize(self, candles: List[Candle]) -> List[Dict]:
        """
        识别K线形态
        
        Args:
            candles: K线列表，至少需要3根
            
        Returns:
            识别出的形态列表
        """
        if len(candles) < 2:
            return []
        
        results = []
        
        # 单根形态（最新一根）
        for pattern_name, pattern_func in self.patterns.items():
            if pattern_name in ["hammer", "shooting_star", "doji", "marubozu"]:
                result = pattern_func(candles[-1], candles[-2] if len(candles) > 1 else None)
                if result:
                    results.append(result)
            elif pattern_name in ["engulfing", "harami", "piercing", "dark_cloud"]:
                if len(candles) >= 2:
                    result = pattern_func(candles[-2], candles[-1])
                    if result:
                        results.append(result)
            else:  # 三根形态
                if len(candles) >= 3:
                    result = pattern_func(candles[-3], candles[-2], candles[-1])
                    if result:
                        results.append(result)
        
        return results
    
    # ========== 单根形态 ==========
    
    def _is_hammer(self, curr: Candle, prev: Optional[Candle]) -> Optional[Dict]:
        """锤子线 - 底部反转信号"""
        body = curr.body
        lower_shadow = curr.lower_shadow
        upper_shadow = curr.upper_shadow
        
        # 条件：下影线 > 2倍实体，上影线很短，出现在下跌趋势后
        if lower_shadow > body * 2 and upper_shadow < body * 0.5:
            return {
                "name": "锤子线",
                "type": PatternType.BULLISH.value,
                "confidence": 0.75,
                "candles": 1,
                "signal": "底部反转，关注后续确认",
                "strength": "强" if lower_shadow > body * 3 else "中"
            }
        return None
    
    def _is_shooting_star(self, curr: Candle, prev: Optional[Candle]) -> Optional[Dict]:
        """射击之星 - 顶部反转信号"""
        body = curr.body
        upper_shadow = curr.upper_shadow
        lower_shadow = curr.lower_shadow
        
        # 条件：上影线 > 2倍实体，下影线很短，出现在上涨趋势后
        if upper_shadow > body * 2 and lower_shadow < body * 0.5:
            return {
                "name": "射击之星",
                "type": PatternType.BEARISH.value,
                "confidence": 0.70,
                "candles": 1,
                "signal": "顶部反转，警惕回调",
                "strength": "强" if upper_shadow > body * 3 else "中"
            }
        return None
    
    def _is_doji(self, curr: Candle, prev: Optional[Candle]) -> Optional[Dict]:
        """十字星 - 趋势可能转折"""
        body_ratio = curr.body / curr.range if curr.range > 0 else 0
        
        # 实体很小（<5%的区间）
        if body_ratio < 0.05 and curr.range > 0:
            return {
                "name": "十字星",
                "type": PatternType.NEUTRAL.value,
                "confidence": 0.60,
                "candles": 1,
                "signal": "多空平衡，观望或等待突破",
                "strength": "长脚十字星" if curr.upper_shadow > curr.body * 2 or curr.lower_shadow > curr.body * 2 else "普通"
            }
        return None
    
    def _is_marubozu(self, curr: Candle, prev: Optional[Candle]) -> Optional[Dict]:
        """光头光脚 - 趋势强烈"""
        body_ratio = curr.body / curr.range if curr.range > 0 else 0
        
        # 几乎没有影线
        if body_ratio > 0.95:
            trend = "强势上涨" if curr.is_bullish else "强势下跌"
            return {
                "name": "光头光脚",
                "type": PatternType.BULLISH.value if curr.is_bullish else PatternType.BEARISH.value,
                "confidence": 0.80,
                "candles": 1,
                "signal": f"{trend}，趋势延续概率高",
                "strength": "强"
            }
        return None
    
    # ========== 双根形态 ==========
    
    def _is_engulfing(self, first: Candle, second: Candle) -> Optional[Dict]:
        """吞没形态 - 强烈反转信号"""
        # 看涨吞没：第一根阴线，第二根阳线，第二根实体完全包含第一根
        if first.is_bearish and second.is_bullish:
            if second.open < first.close and second.close > first.open:
                return {
                    "name": "看涨吞没",
                    "type": PatternType.BULLISH.value,
                    "confidence": 0.85,
                    "candles": 2,
                    "signal": "强烈底部反转信号",
                    "strength": "强"
                }
        
        # 看跌吞没
        if first.is_bullish and second.is_bearish:
            if second.open > first.close and second.close < first.open:
                return {
                    "name": "看跌吞没",
                    "type": PatternType.BEARISH.value,
                    "confidence": 0.85,
                    "candles": 2,
                    "signal": "强烈顶部反转信号",
                    "strength": "强"
                }
        return None
    
    def _is_harami(self, first: Candle, second: Candle) -> Optional[Dict]:
        """孕线 - 趋势可能结束"""
        # 第一根大阳线/阴线，第二根小实体完全在第一根范围内
        if first.body > second.body * 2:
            if second.high < first.high and second.low > first.low:
                trend_type = PatternType.BEARISH.value if first.is_bullish else PatternType.BULLISH.value
                signal = "上涨趋势可能结束" if first.is_bullish else "下跌趋势可能结束"
                return {
                    "name": "孕线",
                    "type": trend_type,
                    "confidence": 0.65,
                    "candles": 2,
                    "signal": signal,
                    "strength": "中"
                }
        return None
    
    def _is_piercing(self, first: Candle, second: Candle) -> Optional[Dict]:
        """刺透形态 - 底部反转"""
        # 第一根大阴线，第二根阳线开盘低于前低，收盘深入前实体50%以上
        if first.is_bearish and second.is_bullish:
            if second.open < first.low and second.close > first.open - first.body * 0.5:
                return {
                    "name": "刺透形态",
                    "type": PatternType.BULLISH.value,
                    "confidence": 0.75,
                    "candles": 2,
                    "signal": "底部反转信号",
                    "strength": "中强"
                }
        return None
    
    def _is_dark_cloud(self, first: Candle, second: Candle) -> Optional[Dict]:
        """乌云盖顶 - 顶部反转"""
        # 第一根大阳线，第二根阴线开盘高于前高，收盘深入前实体50%以上
        if first.is_bullish and second.is_bearish:
            if second.open > first.high and second.close < first.open + first.body * 0.5:
                return {
                    "name": "乌云盖顶",
                    "type": PatternType.BEARISH.value,
                    "confidence": 0.75,
                    "candles": 2,
                    "signal": "顶部反转信号",
                    "strength": "中强"
                }
        return None
    
    # ========== 三根形态 ==========
    
    def _is_morning_star(self, first: Candle, second: Candle, third: Candle) -> Optional[Dict]:
        """早晨之星 - 强烈底部反转"""
        # 第一根大阴线，第二根小实体（可跳空），第三根大阳线收盘深入第一根实体
        if first.is_bearish and third.is_bullish:
            if second.body < first.body * 0.3:  # 第二根小实体
                if third.close > first.open - first.body * 0.5:
                    return {
                        "name": "早晨之星",
                        "type": PatternType.BULLISH.value,
                        "confidence": 0.90,
                        "candles": 3,
                        "signal": "强烈底部反转，可考虑建仓",
                        "strength": "强"
                    }
        return None
    
    def _is_evening_star(self, first: Candle, second: Candle, third: Candle) -> Optional[Dict]:
        """黄昏之星 - 强烈顶部反转"""
        # 第一根大阳线，第二根小实体，第三根大阴线收盘深入第一根实体
        if first.is_bullish and third.is_bearish:
            if second.body < first.body * 0.3:
                if third.close < first.open + first.body * 0.5:
                    return {
                        "name": "黄昏之星",
                        "type": PatternType.BEARISH.value,
                        "confidence": 0.90,
                        "candles": 3,
                        "signal": "强烈顶部反转，考虑减仓",
                        "strength": "强"
                    }
        return None
    
    def _is_three_white_soldiers(self, first: Candle, second: Candle, third: Candle) -> Optional[Dict]:
        """红三兵 - 上涨趋势确认"""
        if first.is_bullish and second.is_bullish and third.is_bullish:
            # 三根阳线，依次高开，实体大致相当
            if second.open > first.open and third.open > second.open:
                if abs(first.body - second.body) < first.body * 0.3 and abs(second.body - third.body) < second.body * 0.3:
                    return {
                        "name": "红三兵",
                        "type": PatternType.BULLISH.value,
                        "confidence": 0.80,
                        "candles": 3,
                        "signal": "上涨趋势确认，可考虑追涨",
                        "strength": "强"
                    }
        return None
    
    def _is_three_black_crows(self, first: Candle, second: Candle, third: Candle) -> Optional[Dict]:
        """黑三鸦 - 下跌趋势确认"""
        if first.is_bearish and second.is_bearish and third.is_bearish:
            # 三根阴线，依次低开，实体大致相当
            if second.open < first.open and third.open < second.open:
                if abs(first.body - second.body) < first.body * 0.3 and abs(second.body - third.body) < second.body * 0.3:
                    return {
                        "name": "黑三鸦",
                        "type": PatternType.BEARISH.value,
                        "confidence": 0.80,
                        "candles": 3,
                        "signal": "下跌趋势确认，考虑止损",
                        "strength": "强"
                    }
        return None


def demo():
    """演示K线形态识别"""
    print("=" * 60)
    print("📊 K线形态识别器演示")
    print("=" * 60)
    
    recognizer = KPatternRecognizer()
    
    # 测试数据：锤子线形态
    candles_hammer = [
        Candle(open=100, high=102, low=98, close=99),   # 阴线
        Candle(open=99, high=100, low=90, close=98.5),  # 锤子线（长下影线）
    ]
    
    print("\n🔨 测试锤子线形态:")
    patterns = recognizer.recognize(candles_hammer)
    for p in patterns:
        print(f"   识别: {p['name']} ({p['type']})")
        print(f"   信号: {p['signal']}")
        print(f"   置信度: {p['confidence']}")
    
    # 测试数据：看涨吞没
    candles_engulfing = [
        Candle(open=100, high=101, low=98, close=98),   # 阴线
        Candle(open=97, high=102, low=97, close=101),   # 阳线吞没
    ]
    
    print("\n🔄 测试看涨吞没:")
    patterns = recognizer.recognize(candles_engulfing)
    for p in patterns:
        print(f"   识别: {p['name']} ({p['type']})")
        print(f"   信号: {p['signal']}")
    
    # 测试数据：早晨之星
    candles_morning_star = [
        Candle(open=105, high=106, low=100, close=100),  # 大阴线
        Candle(open=99, high=101, low=98, close=99.5),   # 小实体
        Candle(open=100, high=104, low=99, close=103),   # 大阳线
    ]
    
    print("\n⭐ 测试早晨之星:")
    patterns = recognizer.recognize(candles_morning_star)
    for p in patterns:
        print(f"   识别: {p['name']} ({p['type']})")
        print(f"   信号: {p['signal']}")
        print(f"   强度: {p['strength']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
