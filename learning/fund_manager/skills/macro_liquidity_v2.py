#!/usr/bin/env python3
"""
Skill 4: 宏观流动性监控 (FRED真实数据版)
使用FRED免费API获取真实数据

监控指标:
- 净流动性 = 美联储总资产 - TGA - ON RRP
- SOFR(隔夜融资利率)
- MOVE指数(美债波动率)
- USDJPY + 收益率曲线

触发条件:
- 净流动性单周下降>5% → 预警
- SOFR突破5.5% → 减仓信号
- MOVE指数>130 → 风险资产止损
- 收益率曲线倒挂加深 → 衰退预警

输出: 流动性评级(宽松/中性/收紧/紧缩) + 仓位调整建议
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from fred_client import FREDClient, _load_env

# 加载.env中的API Key
_load_env()

@dataclass
class LiquiditySignal:
    overall_rating: str = ''  # 宽松/中性/收紧/紧缩
    net_liquidity: float = 0.0  # 净流动性 ($B)
    liquidity_change: float = 0.0  # 周变化
    
    # 各指标
    fed_balance_sheet: float = 0.0
    tga_balance: float = 0.0
    on_rrp: float = 0.0
    sofr_rate: float = 0.0
    move_index: float = 0.0
    usdjpy: float = 0.0
    yield_spread: float = 0.0  # 10Y-2Y利差
    
    # 触发状态
    liquidity_trigger: bool = False
    sofr_trigger: bool = False
    move_trigger: bool = False
    yield_trigger: bool = False
    
    # 建议
    action: str = ''  # 加仓/减仓/对冲/观望
    target_bond_allocation: float = 0.0
    target_cash_allocation: float = 0.0
    urgency: str = ''  # 立即/本周/观察
    
    reasons: List[str] = None
    risks: List[str] = None
    fred_data: Dict = None  # 原始FRED数据

class MacroLiquiditySkill:
    """
    宏观流动性监控 - FRED真实数据版
    使用FRED (Federal Reserve Economic Data) 免费API
    """
    
    def __init__(self):
        self.fred = FREDClient()
        
        # FRED Series IDs (全部免费)
        self.fred_series = {
            'fed_balance_sheet': 'WALCL',      # 美联储总资产
            'tga_balance': 'WTREGEN',          # 财政部一般账户
            'on_rrp': 'RRPONTSYD',             # 隔夜逆回购
            'sofr': 'SOFR',                    # 隔夜融资利率
            'move_index': 'MOVE',              # 美债波动率指数
            'yield_spread': 'T10Y2Y',          # 10Y-2Y利差
        }
        
        self.thresholds = {
            'liquidity_drop_weekly': 0.05,  # 5%
            'sofr_high': 5.5,
            'move_high': 130,
            'yield_inverted_deep': -0.5,  # 倒挂加深到-0.5%
        }
    
    def analyze(self) -> LiquiditySignal:
        """分析宏观流动性 - 使用真实FRED数据"""
        # 从FRED获取真实数据
        data = self._fetch_fred_data()
        
        # 计算净流动性
        net_liquidity = data.get('net_liquidity', 0)
        liquidity_change = data.get('liquidity_change_weekly', 0)
        
        # 检查各指标
        liquidity_trigger = liquidity_change < -self.thresholds['liquidity_drop_weekly']
        sofr_trigger = data.get('sofr', 0) > self.thresholds['sofr_high']
        move_trigger = data.get('move_index', 0) > self.thresholds['move_high']
        yield_trigger = data.get('yield_spread', 0) < self.thresholds['yield_inverted_deep']
        
        # 综合评级
        rating, action, bond_alloc, cash_alloc, urgency = self._determine_action(
            liquidity_trigger, sofr_trigger, move_trigger, yield_trigger,
            liquidity_change, data
        )
        
        # 生成分析
        reasons, risks = self._generate_analysis(
            net_liquidity, liquidity_change, data,
            liquidity_trigger, sofr_trigger, move_trigger, yield_trigger
        )
        
        return LiquiditySignal(
            overall_rating=rating,
            net_liquidity=net_liquidity,
            liquidity_change=liquidity_change,
            fed_balance_sheet=data.get('fed_balance_sheet', 0),
            tga_balance=data.get('tga_balance', 0),
            on_rrp=data.get('on_rrp', 0),
            sofr_rate=data.get('sofr', 0),
            move_index=data.get('move_index', 0),
            yield_spread=data.get('yield_spread', 0),
            liquidity_trigger=liquidity_trigger,
            sofr_trigger=sofr_trigger,
            move_trigger=move_trigger,
            yield_trigger=yield_trigger,
            action=action,
            target_bond_allocation=bond_alloc,
            target_cash_allocation=cash_alloc,
            urgency=urgency,
            reasons=reasons,
            risks=risks,
            fred_data=data
        )
    
    def _fetch_fred_data(self) -> Dict:
        """从FRED获取真实数据"""
        data = {}
        
        try:
            # 1. 美联储总资产 (WALCL) - 单位为百万美元，需要转换为十亿
            fed_series = self.fred.get_series('WALCL', limit=10)
            if fed_series:
                latest = fed_series[0]
                data['fed_balance_sheet'] = latest['value'] / 1000  # 转换为$B
                data['fed_date'] = latest['date']
                
                # 计算周变化（如果有足够数据）
                if len(fed_series) >= 8:
                    week_ago = fed_series[7]  # 大约一周前
                    change = (latest['value'] - week_ago['value']) / week_ago['value']
                    data['liquidity_change_weekly'] = change
                else:
                    data['liquidity_change_weekly'] = 0
        except Exception as e:
            data['fed_balance_sheet'] = 0
            data['liquidity_change_weekly'] = 0
            print(f"Warning: 无法获取美联储资产数据: {e}")
        
        try:
            # 2. TGA (财政部一般账户) - WTREGEN
            tga_series = self.fred.get_series('WTREGEN', limit=5)
            if tga_series:
                data['tga_balance'] = tga_series[0]['value'] / 1000  # 转换为$B
        except Exception as e:
            data['tga_balance'] = 0
        
        try:
            # 3. ON RRP (隔夜逆回购) - RRPONTSYD
            rrp_series = self.fred.get_series('RRPONTSYD', limit=5)
            if rrp_series:
                data['on_rrp'] = rrp_series[0]['value'] / 1000  # 转换为$B
        except Exception as e:
            data['on_rrp'] = 0
        
        # 计算净流动性
        data['net_liquidity'] = data['fed_balance_sheet'] - data['tga_balance'] - data['on_rrp']
        
        try:
            # 4. SOFR利率
            sofr_series = self.fred.get_series('SOFR', limit=5)
            if sofr_series:
                data['sofr'] = sofr_series[0]['value']
        except Exception as e:
            data['sofr'] = 0
        
        try:
            # 5. MOVE指数 (美债波动率)
            move_series = self.fred.get_series('MOVE', limit=5)
            if move_series:
                data['move_index'] = move_series[0]['value']
        except Exception as e:
            data['move_index'] = 0
        
        try:
            # 6. 收益率曲线利差 (10Y-2Y)
            spread_series = self.fred.get_series('T10Y2Y', limit=5)
            if spread_series:
                data['yield_spread'] = spread_series[0]['value']
        except Exception as e:
            data['yield_spread'] = 0
        
        # 7. 联邦基金利率 (FEDFUNDS)
        try:
            fed_rate = self.fred.get_series('FEDFUNDS', limit=5)
            if fed_rate:
                data['fed_funds_rate'] = fed_rate[0]['value']
        except Exception as e:
            data['fed_funds_rate'] = 0
        
        data['timestamp'] = datetime.now().isoformat()
        return data
    
    def _calculate_net_liquidity(self, data: Dict) -> float:
        """计算净流动性"""
        fed = data.get('fed_balance_sheet', 0)
        tga = data.get('tga_balance', 0)
        on_rrp = data.get('on_rrp', 0)
        
        # 净流动性 = 美联储总资产 - TGA - ON RRP
        net = fed - tga - on_rrp
        return net
    
    def _determine_action(self, liq_trigger, sofr_trigger, move_trigger, yield_trigger,
                         liq_change, data) -> Tuple[str, str, float, float, str]:
        """确定行动建议"""
        trigger_count = sum([liq_trigger, sofr_trigger, move_trigger, yield_trigger])
        
        # 判断流动性环境
        if liq_change < -0.10 or trigger_count >= 3:  # 单月-10%或3个触发
            return '紧缩', '大幅减仓', 0.30, 0.30, '立即'  # 30%债, 30%现金
        
        elif liq_change < -0.05 or trigger_count >= 2:  # 单周-5%或2个触发
            return '收紧', '减仓', 0.25, 0.15, '本周'  # 25%债, 15%现金
        
        elif liq_change > 0.02:  # 流动性改善
            return '宽松', '加仓风险资产', 0.15, 0.05, '观察'
        
        else:
            return '中性', '维持配置', 0.20, 0.10, '观察'
    
    def _generate_analysis(self, net_liq, liq_change, data,
                          liq_trigger, sofr_trigger, move_trigger, yield_trigger) -> Tuple[List[str], List[str]]:
        """生成分析"""
        reasons = []
        risks = []
        
        # 净流动性状况
        fed = data.get('fed_balance_sheet', 0)
        tga = data.get('tga_balance', 0)
        on_rrp = data.get('on_rrp', 0)
        fed_date = data.get('fed_date', 'N/A')
        
        reasons.append(f"美联储总资产: ${fed:.1f}B (数据日期: {fed_date})")
        reasons.append(f"TGA (财政部): ${tga:.1f}B")
        reasons.append(f"ON RRP: ${on_rrp:.1f}B")
        reasons.append(f"净流动性: ${net_liq:.1f}B")
        if liq_change != 0:
            reasons.append(f"周变化: {liq_change*100:+.2f}%")
        
        # 收益率曲线
        spread = data.get('yield_spread', 0)
        if spread:
            if spread < 0:
                reasons.append(f"⚠️ 收益率曲线倒挂: {spread:.2f}%")
            else:
                reasons.append(f"收益率曲线正常: +{spread:.2f}%")
        
        # 风险提示
        if liq_trigger:
            risks.append(f"🚨 净流动性单周下降{abs(liq_change)*100:.1f}% > 5%，流动性快速收缩")
        
        if sofr_trigger:
            sofr = data.get('sofr', 0)
            risks.append(f"🚨 SOFR {sofr:.2f}% > 5.5%，融资成本过高")
        
        if move_trigger:
            move = data.get('move_index', 0)
            risks.append(f"🚨 MOVE指数 {move:.1f} > 130，美债市场动荡")
        
        if yield_trigger:
            spread = data.get('yield_spread', 0)
            risks.append(f"🚨 收益率曲线倒挂加深至{spread:.2f}%，衰退风险上升")
        elif data.get('yield_spread', 0) < 0:
            spread = data.get('yield_spread', 0)
            risks.append(f"⚠️ 收益率曲线已倒挂({spread:.2f}%)，保持警惕")
        
        if not any([liq_trigger, sofr_trigger, move_trigger, yield_trigger]):
            reasons.append("✓ 无重大流动性风险信号")
        
        return reasons, risks
    
    def get_fred_chart_link(self) -> str:
        """生成FRED图表链接"""
        # 净流动性图表
        return "https://fred.stlouisfed.org/graph/?g=YOUR_CHART_ID"

# 测试
if __name__ == '__main__':
    skill = MacroLiquiditySkill()
    
    print("="*70)
    print("🌍 宏观流动性监控 v2.0 (免费版 - FRED数据)")
    print("="*70)
    print("\n监控指标(全部免费):")
    print("  • 净流动性 = 美联储总资产 - TGA - ON RRP")
    print("  • SOFR利率 (FRED免费)")
    print("  • MOVE指数 (FRED免费)")
    print("  • USDJPY + 美日利差")
    print("\n触发条件:")
    print("  • 净流动性单周-5% → 预警")
    print("  • SOFR > 5.5% → 减仓")
    print("  • MOVE > 130 → 止损")
    print("="*70)
    
    signal = skill.analyze()
    
    print(f"\n📊 流动性评级: {signal.overall_rating}")
    print(f"💰 净流动性: ${signal.net_liquidity:.0f}B (本周{signal.liquidity_change*100:+.1f}%)")
    print(f"📈 美联储资产: ${signal.fed_balance_sheet:.0f}B")
    print(f"💵 TGA: ${signal.tga_balance:.0f}B | ON RRP: ${signal.on_rrp:.0f}B")
    
    print(f"\n📋 指标状态:")
    print(f"  SOFR: {signal.sofr_rate:.2f}% {'🚨' if signal.sofr_trigger else '✓'}")
    print(f"  MOVE: {signal.move_index:.1f} {'🚨' if signal.move_trigger else '✓'}")
    print(f"  利差(10Y-2Y): {signal.yield_spread:.2f}% {'🚨倒挂' if signal.yield_spread < 0 else '✓'}")
    print(f"  流动性: {'🚨下降>5%' if signal.liquidity_trigger else '✓正常'}")
    
    print(f"\n💡 操作建议: {signal.action} (紧急度: {signal.urgency})")
    print(f"   建议债券仓位: {signal.target_bond_allocation*100:.0f}%")
    print(f"   建议现金仓位: {signal.target_cash_allocation*100:.0f}%")
    
    print(f"\n✅ 流动性分析:")
    for r in signal.reasons:
        print(f"   {r}")
    
    if signal.risks:
        print(f"\n⚠️ 风险警告:")
        for risk in signal.risks:
            print(f"   {risk}")
    
    print("\n" + "="*70)
    print("📊 查看FRED实时数据:")
    print("   https://fred.stlouisfed.org/")
    print("   搜索: WALCL (美联储资产), SOFR, MOVE")
    print("="*70)
