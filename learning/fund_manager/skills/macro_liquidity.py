#!/usr/bin/env python3
"""
Skills层 - 宏观流动性监控
美联储政策 + 全球流动性 + 利率期限结构
"""

from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class MacroLiquiditySignal:
    liquidity_score: float  # 0-100，越高流动性越宽松
    fed_policy: str         # dovish/neutral/hawkish
    yield_curve_status: str # normal/flat/inverted
    global_liquidity: str   # expanding/stable/contracting
    signal: str             # RISK_ON/NEUTRAL/RISK_OFF
    interpretation: str
    timestamp: datetime

class MacroLiquiditySkill:
    """
    宏观流动性监控
    判断全球流动性环境对风险资产的影响
    """
    
    def analyze(self) -> MacroLiquiditySignal:
        """分析宏观流动性环境"""
        
        # 1. 美联储政策分析
        fed_analysis = self._analyze_fed_policy()
        
        # 2. 利率期限结构
        yield_curve = self._analyze_yield_curve()
        
        # 3. 全球流动性
        global_liquidity = self._analyze_global_liquidity()
        
        # 4. 信用利差
        credit_spreads = self._analyze_credit_spreads()
        
        # 5. 美元流动性
        dollar_liquidity = self._analyze_dollar_liquidity()
        
        # 计算综合流动性评分
        liquidity_score = self._calculate_liquidity_score(
            fed_analysis, yield_curve, global_liquidity, 
            credit_spreads, dollar_liquidity
        )
        
        # 生成交易信号
        signal, interpretation = self._generate_signal(
            liquidity_score, fed_analysis, yield_curve
        )
        
        return MacroLiquiditySignal(
            liquidity_score=liquidity_score,
            fed_policy=fed_analysis['stance'],
            yield_curve_status=yield_curve['status'],
            global_liquidity=global_liquidity['trend'],
            signal=signal,
            interpretation=interpretation,
            timestamp=datetime.now()
        )
    
    def _analyze_fed_policy(self) -> Dict:
        """分析美联储政策立场"""
        # TODO: 从FRED API获取真实数据
        data = {
            'fed_rate': 5.50,
            'rate_3m_ago': 5.50,
            'rate_6m_ago': 5.25,
            'dot_plot_median': 4.60,  # 年末预期
            'inflation_target': 2.0,
            'current_inflation': 3.1
        }
        
        # 判断政策立场
        rate_change_3m = data['fed_rate'] - data['rate_3m_ago']
        rate_change_6m = data['fed_rate'] - data['rate_6m_ago']
        
        if rate_change_3m < 0 or data['dot_plot_median'] < data['fed_rate'] - 0.5:
            stance = 'dovish'
            score = 80  # 鸽派 = 利好风险资产
        elif rate_change_6m > 0.5:
            stance = 'hawkish'
            score = 20  # 鹰派 = 利空
        else:
            stance = 'neutral'
            score = 50
        
        return {
            'stance': stance,
            'score': score,
            'current_rate': data['fed_rate'],
            'expected_year_end': data['dot_plot_median'],
            'cuts_expected': data['fed_rate'] - data['dot_plot_median']
        }
    
    def _analyze_yield_curve(self) -> Dict:
        """分析利率期限结构"""
        # TODO: 从FRED API获取真实数据
        yields = {
            '2y': 4.65,
            '10y': 4.30,
            '30y': 4.45
        }
        
        # 计算利差
        spread_10y_2y = yields['10y'] - yields['2y']
        spread_30y_10y = yields['30y'] - yields['10y']
        
        if spread_10y_2y < -0.5:
            status = 'deeply_inverted'  # 深度倒挂 = 衰退预警
            score = 10
        elif spread_10y_2y < 0:
            status = 'inverted'  # 倒挂
            score = 30
        elif spread_10y_2y < 0.5:
            status = 'flat'  # 平坦
            score = 50
        else:
            status = 'normal'  # 正常
            score = 70
        
        return {
            'status': status,
            'score': score,
            'spread_10y_2y': spread_10y_2y,
            'yields': yields
        }
    
    def _analyze_global_liquidity(self) -> Dict:
        """分析全球流动性"""
        # TODO: 从全球央行数据获取
        indicators = {
            'fed_balance_sheet': 7500000000000,  # $7.5T
            'ecb_balance_sheet': 6500000000000,  # €6.5T
            'boj_balance_sheet': 750000000000000,  # ¥750T
            'global_m2_growth': 0.02  # 2%增长
        }
        
        # 分析趋势
        m2_growth = indicators['global_m2_growth']
        
        if m2_growth > 0.05:
            trend = 'expanding'  # 扩张
            score = 80
        elif m2_growth > 0:
            trend = 'stable'  # 稳定
            score = 60
        elif m2_growth > -0.02:
            trend = 'slowing'  # 放缓
            score = 40
        else:
            trend = 'contracting'  # 收缩
            score = 20
        
        return {
            'trend': trend,
            'score': score,
            'm2_growth': m2_growth
        }
    
    def _analyze_credit_spreads(self) -> Dict:
        """分析信用利差"""
        # TODO: 从Bloomberg或FRED获取
        spreads = {
            'bbb_spread': 1.20,  # BBB级公司债利差
            'high_yield_spread': 3.50,  # 高收益债利差
            'ig_spread': 0.90   # 投资级利差
        }
        
        # 利差越窄越好
        hy_spread = spreads['high_yield_spread']
        
        if hy_spread < 3.0:
            status = 'tight'  # 利差窄 = 风险情绪好
            score = 80
        elif hy_spread < 4.0:
            status = 'normal'
            score = 60
        elif hy_spread < 5.0:
            status = 'elevated'  # 利差扩大 = 风险上升
            score = 40
        else:
            status = 'wide'  # 利差宽 = 恐慌
            score = 20
        
        return {
            'status': status,
            'score': score,
            'high_yield_spread': hy_spread
        }
    
    def _analyze_dollar_liquidity(self) -> Dict:
        """分析美元流动性"""
        # TODO: 从FRED获取
        indicators = {
            'dxy': 103.80,  # 美元指数
            'sofr_spread': 0.05,  # SOFR利差
            'repo_rates': 5.30
        }
        
        dxy = indicators['dxy']
        
        # 美元越强，新兴市场流动性越紧张
        if dxy < 100:
            score = 80  # 美元弱 = 全球流动性宽松
        elif dxy < 103:
            score = 60
        elif dxy < 106:
            score = 40
        else:
            score = 20  # 美元过强 = 流动性紧张
        
        return {
            'dxy': dxy,
            'score': score
        }
    
    def _calculate_liquidity_score(self, fed, yield_curve, global_liq, credit, dollar) -> float:
        """计算综合流动性评分"""
        weights = {
            'fed': 0.30,
            'yield_curve': 0.20,
            'global': 0.20,
            'credit': 0.15,
            'dollar': 0.15
        }
        
        score = (
            fed['score'] * weights['fed'] +
            yield_curve['score'] * weights['yield_curve'] +
            global_liq['score'] * weights['global'] +
            credit['score'] * weights['credit'] +
            dollar['score'] * weights['dollar']
        )
        
        return min(max(score, 0), 100)
    
    def _generate_signal(self, score, fed, yield_curve) -> tuple:
        """生成资产配置信号"""
        if score >= 70 and fed['stance'] in ['dovish', 'neutral']:
            signal = 'RISK_ON'
            interpretation = '流动性宽松，加仓成长股/加密货币/新兴市场'
        elif score >= 50:
            signal = 'NEUTRAL'
            interpretation = '流动性中性，维持现有配置'
        elif score >= 30:
            signal = 'CAUTION'
            interpretation = '流动性收紧，减仓风险资产，增配现金/债券'
        else:
            signal = 'RISK_OFF'
            interpretation = '流动性紧缩，大幅减仓，防御为主'
        
        # 增加收益率曲线警告
        if yield_curve['status'] in ['inverted', 'deeply_inverted']:
            interpretation += ' | ⚠️ 收益率曲线倒挂，警惕衰退风险'
        
        return signal, interpretation

# 测试
if __name__ == '__main__':
    skill = MacroLiquiditySkill()
    
    print("="*70)
    print("🌍 宏观流动性监控")
    print("="*70)
    
    signal = skill.analyze()
    
    print(f"\n📊 流动性评分: {signal.liquidity_score:.0f}/100")
    print(f"🏦 美联储立场: {signal.fed_policy}")
    print(f"📈 收益率曲线: {signal.yield_curve_status}")
    print(f"🌍 全球流动性: {signal.global_liquidity}")
    print(f"\n🎯 配置信号: {signal.signal}")
    print(f"💡 解读: {signal.interpretation}")
    
    print("\n" + "="*70)
