#!/usr/bin/env python3
"""
Skills层 - 美股市场情绪监控
VIX、Put/Call比率、散户情绪、机构资金流向
"""

from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SentimentSignal:
    fear_greed_index: float  # 0-100, 0=极度恐惧, 100=极度贪婪
    vix: float
    putcall_ratio: float
    retail_sentiment: str
    institutional_flow: str
    interpretation: str
    timestamp: datetime

class MarketSentimentSkill:
    """
    美股市场情绪监控
    综合多个情绪指标判断市场情绪
    """
    
    def analyze(self) -> SentimentSignal:
        """分析当前市场情绪"""
        
        # 获取各指标数据
        vix_data = self._fetch_vix()
        putcall_data = self._fetch_putcall()
        retail_data = self._fetch_retail_sentiment()
        inst_data = self._fetch_institutional_flow()
        
        # 计算恐惧贪婪指数
        fear_greed = self._calculate_fear_greed_index(
            vix_data, putcall_data, retail_data, inst_data
        )
        
        # 解读情绪
        interpretation = self._interpret_sentiment(fear_greed)
        
        return SentimentSignal(
            fear_greed_index=fear_greed,
            vix=vix_data['value'],
            putcall_ratio=putcall_data['ratio'],
            retail_sentiment=retail_data['sentiment'],
            institutional_flow=inst_data['direction'],
            interpretation=interpretation,
            timestamp=datetime.now()
        )
    
    def _fetch_vix(self) -> Dict:
        """获取VIX数据"""
        # TODO: 从Yahoo Finance API获取
        return {
            'value': 15.5,
            'change': -0.8,
            'trend': 'FALLING'  # 下降 = 恐惧缓解
        }
    
    def _fetch_putcall(self) -> Dict:
        """获取Put/Call比率"""
        # TODO: 从CBOE获取
        return {
            'ratio': 0.65,  # <1表示看涨情绪占优
            'ma_5day': 0.70,
            'extreme_reading': False
        }
    
    def _fetch_retail_sentiment(self) -> Dict:
        """获取散户情绪 (AAII调查)"""
        # TODO: 从AAII获取
        return {
            'bullish': 45,      # %
            'neutral': 30,
            'bearish': 25,
            'sentiment': 'BULLISH',  # 牛市情绪
            'bull_bear_spread': 20   # 牛市 - 熊市
        }
    
    def _fetch_institutional_flow(self) -> Dict:
        """获取机构资金流向"""
        # TODO: 从Bloomberg/EPFR获取
        return {
            'direction': 'INFLOW',  # 流入
            'weekly_flow': 15000000000,  # $15B
            'trend': 'ACCELERATING'  # 加速流入
        }
    
    def _calculate_fear_greed_index(self, vix: Dict, putcall: Dict, 
                                     retail: Dict, inst: Dict) -> float:
        """
        计算恐惧贪婪指数 (0-100)
        0 = 极度恐惧, 50 = 中性, 100 = 极度贪婪
        """
        score = 50  # 从 neutral 开始
        
        # 1. VIX (权重30%)
        vix_value = vix['value']
        if vix_value < 12:
            score += 15  # 极低VIX = 贪婪
        elif vix_value < 15:
            score += 10
        elif vix_value < 20:
            score += 5
        elif vix_value < 25:
            score -= 5
        elif vix_value < 30:
            score -= 15
        else:
            score -= 25  # 高VIX = 恐惧
        
        # 2. Put/Call比率 (权重25%)
        pcr = putcall['ratio']
        if pcr < 0.70:
            score += 12  # 低PCR = 看涨 = 贪婪
        elif pcr < 0.85:
            score += 6
        elif pcr > 1.20:
            score -= 12  # 高PCR = 看跌 = 恐惧
        elif pcr > 1.00:
            score -= 6
        
        # 3. 散户情绪 (权重25%)
        bull_spread = retail['bullish'] - retail['bearish']
        if bull_spread > 30:
            score += 12  # 极度乐观
        elif bull_spread > 15:
            score += 6
        elif bull_spread < -20:
            score -= 12  # 极度悲观
        elif bull_spread < 0:
            score -= 6
        
        # 4. 机构资金流 (权重20%)
        if inst['direction'] == 'INFLOW':
            if inst['trend'] == 'ACCELERATING':
                score += 10
            else:
                score += 5
        else:  # OUTFLOW
            score -= 10
        
        return min(max(score, 0), 100)
    
    def _interpret_sentiment(self, fear_greed: float) -> str:
        """解读情绪"""
        if fear_greed >= 80:
            return '极度贪婪 (EXTREME GREED) - 考虑减仓'
        elif fear_greed >= 65:
            return '贪婪 (GREED) - 保持谨慎'
        elif fear_greed >= 55:
            return '偏向贪婪 - 注意风险'
        elif fear_greed >= 45:
            return '中性 (NEUTRAL) - 正常操作'
        elif fear_greed >= 35:
            return '偏向恐惧 - 寻找机会'
        elif fear_greed >= 20:
            return '恐惧 (FEAR) - 考虑加仓'
        else:
            return '极度恐惧 (EXTREME FEAR) - 贪婪时刻，大胆买入'
    
    def get_contrarian_signal(self, sentiment: SentimentSignal) -> str:
        """获取逆向信号"""
        if sentiment.fear_greed_index >= 80:
            return '逆向信号: 市场过度乐观，考虑获利了结'
        elif sentiment.fear_greed_index <= 20:
            return '逆向信号: 市场极度恐慌，可能是买入良机'
        else:
            return '逆向信号: 无明显极端情绪，跟随趋势'

# 测试
if __name__ == '__main__':
    skill = MarketSentimentSkill()
    
    print("="*70)
    print("📊 美股市场情绪监控")
    print("="*70)
    
    signal = skill.analyze()
    
    print(f"\n🎯 恐惧贪婪指数: {signal.fear_greed_index:.0f}/100")
    print(f"📈 VIX: {signal.vix}")
    print(f"📊 Put/Call比率: {signal.putcall_ratio}")
    print(f"👥 散户情绪: {signal.retail_sentiment}")
    print(f"🏦 机构资金: {signal.institutional_flow}")
    
    print(f"\n💡 解读: {signal.interpretation}")
    print(f"\n🔄 {skill.get_contrarian_signal(signal)}")
    
    print("\n" + "="*70)
