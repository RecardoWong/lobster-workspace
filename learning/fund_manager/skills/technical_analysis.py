#!/usr/bin/env python3
"""
Skills层 - 技术分析
趋势识别、支撑阻力、形态检测
"""

from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class TrendType(Enum):
    STRONG_UPTREND = "STRONG_UPTREND"
    UPTREND = "UPTREND"
    SIDEWAYS = "SIDEWAYS"
    DOWNTREND = "DOWNTREND"
    STRONG_DOWNTREND = "STRONG_DOWNTREND"

class PatternType(Enum):
    BREAKOUT = "BREAKOUT"           # 突破
    BREAKDOWN = "BREAKDOWN"         # 跌破
    GOLDEN_CROSS = "GOLDEN_CROSS"   # 金叉
    DEATH_CROSS = "DEATH_CROSS"     # 死叉
    SUPPORT_BOUNCE = "SUPPORT_BOUNCE"  # 支撑反弹
    RESISTANCE_REJECT = "RESISTANCE_REJECT"  # 阻力回落
    NONE = "NONE"

@dataclass
class TechnicalSignal:
    ticker: str
    trend: TrendType
    pattern: PatternType
    support_levels: List[float]
    resistance_levels: List[float]
    rsi: float
    macd_signal: str
    volume_trend: str
    risk_reward_ratio: float
    entry_price: float
    stop_loss: float
    take_profit: float
    signal_strength: str  # strong/medium/weak
    recommendation: str

class TechnicalAnalysisSkill:
    """
    技术分析器
    自动识别趋势、支撑阻力、交易形态
    """
    
    def analyze(self, ticker: str) -> TechnicalSignal:
        """技术分析主函数"""
        # 获取价格数据
        data = self._fetch_price_data(ticker)
        
        # 计算均线
        sma_20 = self._calculate_sma(data['prices'], 20)
        sma_50 = self._calculate_sma(data['prices'], 50)
        sma_200 = self._calculate_sma(data['prices'], 200)
        
        # 判断趋势
        trend = self._identify_trend(data['current_price'], sma_20, sma_50, sma_200)
        
        # 识别形态
        pattern = self._identify_pattern(data, sma_20, sma_50)
        
        # 计算支撑阻力
        supports, resistances = self._calculate_support_resistance(data['prices'])
        
        # 技术指标
        rsi = self._calculate_rsi(data['prices'])
        macd_signal = self._calculate_macd(data['prices'])
        volume_trend = self._analyze_volume(data['volumes'])
        
        # 计算入场点
        entry, stop_loss, take_profit, rr_ratio = self._calculate_entry_exit(
            data['current_price'], trend, supports, resistances, pattern
        )
        
        # 信号强度
        strength = self._calculate_signal_strength(
            trend, pattern, rsi, macd_signal, volume_trend
        )
        
        # 生成建议
        recommendation = self._generate_recommendation(
            trend, pattern, strength, rr_ratio
        )
        
        return TechnicalSignal(
            ticker=ticker,
            trend=trend,
            pattern=pattern,
            support_levels=supports,
            resistance_levels=resistances,
            rsi=rsi,
            macd_signal=macd_signal,
            volume_trend=volume_trend,
            risk_reward_ratio=rr_ratio,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            signal_strength=strength,
            recommendation=recommendation
        )
    
    def _fetch_price_data(self, ticker: str) -> Dict:
        """获取价格数据"""
        # TODO: 从Yahoo Finance API获取
        import random
        base_price = {'AAPL': 185, 'MSFT': 420, 'NVDA': 700, 'TSLA': 195}.get(ticker, 100)
        
        # 生成模拟价格序列 (最近60天)
        prices = [base_price * (0.9 + i * 0.003 + random.uniform(-0.02, 0.02)) for i in range(60)]
        volumes = [random.randint(40000000, 60000000) for _ in range(60)]
        
        return {
            'ticker': ticker,
            'current_price': prices[-1],
            'prices': prices,
            'volumes': volumes
        }
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """计算简单移动平均线"""
        if len(prices) < period:
            return prices[-1]
        return sum(prices[-period:]) / period
    
    def _identify_trend(self, price: float, sma20: float, sma50: float, sma200: float) -> TrendType:
        """识别趋势"""
        # 多头排列检查
        if price > sma20 > sma50 > sma200:
            return TrendType.STRONG_UPTREND
        elif price > sma20 > sma50:
            return TrendType.UPTREND
        
        # 空头排列检查
        elif price < sma20 < sma50 < sma200:
            return TrendType.STRONG_DOWNTREND
        elif price < sma20 < sma50:
            return TrendType.DOWNTREND
        
        else:
            return TrendType.SIDEWAYS
    
    def _identify_pattern(self, data: Dict, sma20: float, sma50: float) -> PatternType:
        """识别技术形态"""
        prices = data['prices']
        current = data['current_price']
        
        # 检查均线交叉 (简化版)
        prev_sma20 = self._calculate_sma(prices[:-1], 20)
        prev_sma50 = self._calculate_sma(prices[:-1], 50)
        
        # 金叉
        if prev_sma20 < prev_sma50 and sma20 > sma50:
            return PatternType.GOLDEN_CROSS
        
        # 死叉
        if prev_sma20 > prev_sma50 and sma20 < sma50:
            return PatternType.DEATH_CROSS
        
        # 突破前高
        recent_high = max(prices[-20:])
        if current > recent_high * 0.98 and current > sma20:
            return PatternType.BREAKOUT
        
        # 跌破前低
        recent_low = min(prices[-20:])
        if current < recent_low * 1.02 and current < sma20:
            return PatternType.BREAKDOWN
        
        return PatternType.NONE
    
    def _calculate_support_resistance(self, prices: List[float]) -> Tuple[List[float], List[float]]:
        """计算支撑阻力水平"""
        # 简化版：使用近期高低点
        recent_prices = prices[-30:]  # 最近30天
        
        # 找局部低点作为支撑
        supports = []
        for i in range(1, len(recent_prices) - 1):
            if recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i+1]:
                supports.append(recent_prices[i])
        
        # 找局部高点作为阻力
        resistances = []
        for i in range(1, len(recent_prices) - 1):
            if recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i+1]:
                resistances.append(recent_prices[i])
        
        # 取最近的2-3个水平
        supports = sorted(supports)[-3:] if supports else [prices[-1] * 0.95]
        resistances = sorted(resistances)[:3] if resistances else [prices[-1] * 1.05]
        
        return supports, resistances
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, period + 1):
            change = prices[-i] - prices[-i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> str:
        """计算MACD信号"""
        # 简化版
        ema12 = self._calculate_sma(prices[-12:], 12)
        ema26 = self._calculate_sma(prices[-26:], 26)
        macd_line = ema12 - ema26
        
        # 信号线 (9日EMA of MACD)
        # 简化：用近期MACD均值
        signal_line = macd_line * 0.9  # 近似
        
        if macd_line > signal_line and macd_line > 0:
            return "BULLISH"  # 强势
        elif macd_line > signal_line:
            return "IMPROVING"  # 改善中
        elif macd_line < signal_line and macd_line < 0:
            return "BEARISH"  # 弱势
        else:
            return "WEAKENING"  # 走弱中
    
    def _analyze_volume(self, volumes: List[float]) -> str:
        """分析成交量趋势"""
        recent_vol = sum(volumes[-5:]) / 5
        avg_vol = sum(volumes[-20:]) / 20
        
        if recent_vol > avg_vol * 1.3:
            return "EXPANDING"  # 放量
        elif recent_vol > avg_vol * 1.1:
            return "ABOVE_AVERAGE"  # 高于平均
        elif recent_vol < avg_vol * 0.7:
            return "CONTRACTING"  # 缩量
        else:
            return "NORMAL"  # 正常
    
    def _calculate_entry_exit(self, price: float, trend: TrendType, 
                               supports: List[float], resistances: List[float],
                               pattern: PatternType) -> Tuple[float, float, float, float]:
        """计算入场点、止损、止盈"""
        
        # 根据趋势确定入场点
        if trend in [TrendType.STRONG_UPTREND, TrendType.UPTREND]:
            entry = price
            stop_loss = max(supports[-1], price * 0.95)  # 支撑或-5%
            take_profit = resistances[0] if resistances else price * 1.10
        elif trend in [TrendType.DOWNTREND, TrendType.STRONG_DOWNTREND]:
            entry = price  # 等待反弹或做空
            stop_loss = min(resistances[0], price * 1.05) if resistances else price * 1.05
            take_profit = supports[-1] if supports else price * 0.90
        else:
            entry = price
            stop_loss = price * 0.97
            take_profit = price * 1.05
        
        # 计算盈亏比
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        return entry, stop_loss, take_profit, rr_ratio
    
    def _calculate_signal_strength(self, trend, pattern, rsi, macd, volume) -> str:
        """计算信号强度"""
        score = 0
        
        # 趋势分数
        if trend == TrendType.STRONG_UPTREND: score += 3
        elif trend == TrendType.UPTREND: score += 2
        elif trend == TrendType.SIDEWAYS: score += 1
        else: score -= 2
        
        # 形态分数
        if pattern == PatternType.GOLDEN_CROSS: score += 2
        elif pattern == PatternType.BREAKOUT: score += 2
        elif pattern == PatternType.DEATH_CROSS: score -= 2
        
        # RSI分数
        if 40 < rsi < 60: score += 1
        elif rsi < 30: score += 1  # 超卖反弹
        elif rsi > 70: score -= 1
        
        # MACD分数
        if macd == "BULLISH": score += 1
        elif macd == "BEARISH": score -= 1
        
        # 成交量分数
        if volume == "EXPANDING": score += 1
        
        if score >= 5: return "STRONG"
        elif score >= 3: return "MEDIUM"
        else: return "WEAK"
    
    def _generate_recommendation(self, trend, pattern, strength, rr_ratio) -> str:
        """生成交易建议"""
        if trend in [TrendType.STRONG_UPTREND, TrendType.UPTREND]:
            if pattern in [PatternType.GOLDEN_CROSS, PatternType.BREAKOUT]:
                if strength == "STRONG" and rr_ratio >= 2:
                    return "🟢 强烈买入 - 趋势向上+突破确认，盈亏比优秀"
                else:
                    return "🟢 买入 - 趋势向上，顺势操作"
            else:
                return "🟡 观望 - 趋势向上但无明确入场点，等待回调或突破"
        
        elif trend == TrendType.SIDEWAYS:
            return "🟡 观望 - 震荡行情，等待方向选择"
        
        else:
            if pattern in [PatternType.DEATH_CROSS, PatternType.BREAKDOWN]:
                return "🔴 卖出/观望 - 趋势向下+破位，规避风险"
            else:
                return "🟡 观望 - 趋势向下，等待企稳信号"

# 测试
if __name__ == '__main__':
    skill = TechnicalAnalysisSkill()
    
    print("="*70)
    print("📈 技术分析")
    print("="*70)
    
    tickers = ['AAPL', 'NVDA', 'TSLA']
    
    for ticker in tickers:
        signal = skill.analyze(ticker)
        print(f"\n📊 {signal.ticker}")
        print(f"趋势: {signal.trend.value}")
        print(f"形态: {signal.pattern.value}")
        print(f"RSI: {signal.rsi:.1f}")
        print(f"MACD: {signal.macd_signal}")
        print(f"成交量: {signal.volume_trend}")
        print(f"支撑位: ${signal.support_levels[-1]:.2f}")
        print(f"阻力位: ${signal.resistance_levels[0]:.2f}")
        print(f"入场: ${signal.entry_price:.2f}")
        print(f"止损: ${signal.stop_loss:.2f}")
        print(f"止盈: ${signal.take_profit:.2f}")
        print(f"盈亏比: {signal.risk_reward_ratio:.1f}:1")
        print(f"信号强度: {signal.signal_strength}")
        print(f"建议: {signal.recommendation}")
        print("-"*70)
    
    print("\n" + "="*70)
