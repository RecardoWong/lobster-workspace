#!/usr/bin/env python3
"""
Skills层 - 比特币抄底模型
基于链上数据的BTC底部检测
"""

import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class BTCBottomSignal:
    bottom_probability: float  # 0-100
    signal_strength: str       # STRONG/MODERATE/WEAK
    accumulation_plan: Dict
    risk_level: str
    indicators: Dict
    timestamp: datetime

class BTCBottomSkill:
    """
    比特币抄底模型
    基于链上数据判断BTC是否接近底部
    """
    
    def __init__(self):
        self.thresholds = {
            'mvrv_z_score': -0.5,      # MVRV Z-Score < -0.5 = 超卖
            'nupl': 0.0,                # NUPL < 0 = 市场亏损
            'pi_cycle': 100000,         # Pi周期指标
            'miner_outflow': 1.5,       # 矿工流出量倍数
            'exchange_outflow': 50000,  # 交易所流出量 (BTC)
            'lth_sopr': 0.98            # 长期持有者SOPR
        }
    
    def analyze(self) -> BTCBottomSignal:
        """
        分析比特币底部信号
        """
        # 获取链上数据
        data = self._fetch_onchain_data()
        
        # 计算各个指标
        indicators = {
            'mvrv_z_score': self._analyze_mvrv(data),
            'nupl': self._analyze_nupl(data),
            'pi_cycle': self._analyze_pi_cycle(data),
            'miner_behavior': self._analyze_miners(data),
            'exchange_flow': self._analyze_exchange_flow(data),
            'lth_behavior': self._analyze_long_term_holders(data)
        }
        
        # 计算底部概率
        bottom_prob = self._calculate_bottom_probability(indicators)
        
        # 信号强度
        strength = self._determine_strength(bottom_prob, indicators)
        
        # 分批建仓计划
        accumulation = self._generate_accumulation_plan(bottom_prob)
        
        # 风险等级
        risk = self._assess_risk(indicators)
        
        return BTCBottomSignal(
            bottom_probability=bottom_prob,
            signal_strength=strength,
            accumulation_plan=accumulation,
            risk_level=risk,
            indicators=indicators,
            timestamp=datetime.now()
        )
    
    def _fetch_onchain_data(self) -> Dict:
        """获取链上数据"""
        # TODO: 接入Glassnode/Chainalysis API
        # 模拟数据
        return {
            'mvrv_z_score': -0.8,           # 负值表示低估
            'nupl': -0.05,                   # 负值表示市场亏损
            'pi_cycle_top': 120000,          # Pi周期顶部指标
            'pi_cycle_bottom': 25000,        # Pi周期底部指标
            'current_price': 51000,
            'miner_outflow': 1.8,            # 倍数
            'exchange_inflow': 20000,        # BTC
            'exchange_outflow': 55000,       # BTC
            'lth_sopr': 0.97,                # <1表示亏损卖出
            'lth_supply_percent': 0.78       # 78%由长期持有者持有
        }
    
    def _analyze_mvrv(self, data: Dict) -> Dict:
        """
        MVRV Z-Score分析
        判断市场价值与实现价值的偏离程度
        """
        z_score = data.get('mvrv_z_score', 0)
        
        if z_score < -0.5:
            status = 'OVERSOLD'
            score = 100
        elif z_score < 0:
            status = 'UNDERVALUED'
            score = 75
        elif z_score < 3:
            status = 'FAIR'
            score = 50
        else:
            status = 'OVERVALUED'
            score = 0
        
        return {
            'value': z_score,
            'status': status,
            'score': score,
            'interpretation': f'MVRV Z-Score: {z_score:.2f} ({status})'
        }
    
    def _analyze_nupl(self, data: Dict) -> Dict:
        """
        NUPL分析 (Net Unrealized Profit/Loss)
        判断市场整体盈亏状态
        """
        nupl = data.get('nupl', 0)
        
        if nupl < -0.1:
            status = 'CAPITULATION'
            score = 100
        elif nupl < 0:
            status = 'LOSSES'
            score = 80
        elif nupl < 0.25:
            status = 'HOPE'
            score = 50
        elif nupl < 0.5:
            status = 'OPTIMISM'
            score = 25
        else:
            status = 'EUPHORIA'
            score = 0
        
        return {
            'value': nupl,
            'status': status,
            'score': score,
            'interpretation': f'NUPL: {nupl*100:.1f}% ({status})'
        }
    
    def _analyze_pi_cycle(self, data: Dict) -> Dict:
        """
        Pi周期分析
        预测周期顶部和底部
        """
        price = data.get('current_price', 0)
        pi_top = data.get('pi_cycle_top', 100000)
        pi_bottom = data.get('pi_cycle_bottom', 30000)
        
        # 计算距离底部的距离
        if price < pi_bottom * 1.2:
            status = 'NEAR_BOTTOM'
            score = 100
        elif price < pi_bottom * 1.5:
            status = 'APPROACHING_BOTTOM'
            score = 75
        elif price > pi_top * 0.8:
            status = 'NEAR_TOP'
            score = 0
        else:
            status = 'MID_CYCLE'
            score = 50
        
        return {
            'price': price,
            'pi_top': pi_top,
            'pi_bottom': pi_bottom,
            'status': status,
            'score': score,
            'interpretation': f'Pi周期: {status} (价格${price:,.0f})'
        }
    
    def _analyze_miners(self, data: Dict) -> Dict:
        """
        矿工行为分析
        矿工投降通常是底部信号
        """
        outflow = data.get('miner_outflow', 1.0)
        
        if outflow > 2.0:
            status = 'CAPITULATION'
            score = 100  # 矿工投降 = 买入信号
        elif outflow > 1.5:
            status = 'STRESS'
            score = 75
        elif outflow > 1.0:
            status = 'ELEVATED'
            score = 50
        else:
            status = 'NORMAL'
            score = 25
        
        return {
            'outflow_multiple': outflow,
            'status': status,
            'score': score,
            'interpretation': f'矿工流出: {outflow:.1f}x ({status})'
        }
    
    def _analyze_exchange_flow(self, data: Dict) -> Dict:
        """
        交易所资金流向
        流出 = 买入持有 = 看涨
        """
        inflow = data.get('exchange_inflow', 0)
        outflow = data.get('exchange_outflow', 0)
        net_flow = outflow - inflow
        
        if net_flow > 50000:
            status = 'STRONG_OUTFLOW'
            score = 100
        elif net_flow > 20000:
            status = 'MODERATE_OUTFLOW'
            score = 75
        elif net_flow > 0:
            status = 'SLIGHT_OUTFLOW'
            score = 50
        else:
            status = 'INFLOW'
            score = 25
        
        return {
            'net_flow': net_flow,
            'status': status,
            'score': score,
            'interpretation': f'交易所净流: {net_flow:,.0f} BTC ({status})'
        }
    
    def _analyze_long_term_holders(self, data: Dict) -> Dict:
        """
        长期持有者行为
        LTH在亏损时卖出 = 投降信号
        """
        sopr = data.get('lth_sopr', 1.0)
        supply_pct = data.get('lth_supply_percent', 0.7)
        
        if sopr < 0.95:
            status = 'CAPITULATION'
            score = 100
        elif sopr < 1.0:
            status = 'LOSSES'
            score = 75
        elif supply_pct > 0.75:
            status = 'ACCUMULATING'
            score = 50
        else:
            status = 'DISTRIBUTING'
            score = 25
        
        return {
            'sopr': sopr,
            'supply_percent': supply_pct,
            'status': status,
            'score': score,
            'interpretation': f'LTH SOPR: {sopr:.2f}, 供应占比: {supply_pct*100:.0f}% ({status})'
        }
    
    def _calculate_bottom_probability(self, indicators: Dict) -> float:
        """计算综合底部概率"""
        scores = [
            indicators['mvrv_z_score']['score'] * 0.25,
            indicators['nupl']['score'] * 0.25,
            indicators['pi_cycle']['score'] * 0.15,
            indicators['miner_behavior']['score'] * 0.15,
            indicators['exchange_flow']['score'] * 0.10,
            indicators['lth_behavior']['score'] * 0.10
        ]
        
        return min(sum(scores), 100)
    
    def _determine_strength(self, prob: float, indicators: Dict) -> str:
        """确定信号强度"""
        if prob >= 80:
            return 'STRONG'
        elif prob >= 60:
            return 'MODERATE'
        elif prob >= 40:
            return 'WEAK'
        else:
            return 'NONE'
    
    def _generate_accumulation_plan(self, prob: float) -> Dict:
        """生成分批建仓计划"""
        if prob >= 80:
            return {
                'strategy': 'AGGRESSIVE_DCA',
                'total_allocation': 0.30,  # 30%资金
                'num_tranches': 5,
                'tranche_size': 0.06,      # 每次6%
                'frequency': 'every_3_days',
                'stop_loss': -0.20,
                'take_profit': 0.50
            }
        elif prob >= 60:
            return {
                'strategy': 'MODERATE_DCA',
                'total_allocation': 0.20,
                'num_tranches': 4,
                'tranche_size': 0.05,
                'frequency': 'weekly',
                'stop_loss': -0.15,
                'take_profit': 0.40
            }
        elif prob >= 40:
            return {
                'strategy': 'CONSERVATIVE_DCA',
                'total_allocation': 0.10,
                'num_tranches': 3,
                'tranche_size': 0.033,
                'frequency': 'bi_weekly',
                'stop_loss': -0.10,
                'take_profit': 0.30
            }
        else:
            return {
                'strategy': 'WAIT',
                'total_allocation': 0,
                'message': '等待更好的入场时机'
            }
    
    def _assess_risk(self, indicators: Dict) -> str:
        """评估风险等级"""
        # 计算风险分数 (越高越危险)
        risk_score = 0
        
        # MVRV过高
        if indicators['mvrv_z_score']['value'] > 3:
            risk_score += 30
        
        # NUPL过高
        if indicators['nupl']['value'] > 0.5:
            risk_score += 30
        
        # 矿工流出正常 (不再投降)
        if indicators['miner_behavior']['outflow_multiple'] < 1.0:
            risk_score += 20
        
        # 交易所流入
        if indicators['exchange_flow']['net_flow'] < 0:
            risk_score += 20
        
        if risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'

# 测试
if __name__ == '__main__':
    skill = BTCBottomSkill()
    
    print("="*70)
    print("₿ 比特币抄底模型")
    print("="*70)
    
    signal = skill.analyze()
    
    print(f"\n📊 底部概率: {signal.bottom_probability:.1f}%")
    print(f"📈 信号强度: {signal.signal_strength}")
    print(f"⚠️ 风险等级: {signal.risk_level}")
    
    print("\n📋 指标详情:")
    for name, data in signal.indicators.items():
        print(f"  • {data['interpretation']}")
    
    print(f"\n💰 建仓计划:")
    plan = signal.accumulation_plan
    if plan.get('total_allocation', 0) > 0:
        print(f"  策略: {plan['strategy']}")
        print(f"  总仓位: {plan['total_allocation']*100:.0f}%")
        print(f"  分批: {plan['num_tranches']}次")
        print(f"  每批: {plan['tranche_size']*100:.1f}%")
        print(f"  频率: {plan['frequency']}")
        print(f"  止损: {plan['stop_loss']*100:.0f}%")
        print(f"  止盈: {plan['take_profit']*100:.0f}%")
    else:
        print(f"  {plan.get('message', '观望')}")
    
    print("\n" + "="*70)
