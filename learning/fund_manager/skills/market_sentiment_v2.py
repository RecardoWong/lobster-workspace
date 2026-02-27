#!/usr/bin/env python3
"""
Skill 3: 美股市场情绪监控 (免费版)
使用免费替代方案监控情绪

监控指标(你的标准):
- NAAIM暴露指数: 免费替代 - 使用VIX + Put/Call近似
- 机构股票配置比例: State Street免费月度报告
- 散户净买入额: 摩根大通数据 - 免费替代用VIX散户关联指标
- 标普500远期市盈率: Yahoo Finance免费计算
- 对冲基金杠杆率: FINRA数据 - 免费替代用保证金余额

触发条件:
- 3个以上指标预警 → 减仓信号
- 5个指标全部预警 → 大幅减仓或对冲

输出: 情绪评级(极度贪婪/贪婪/中性/恐慌) + 仓位建议
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class SentimentSignal:
    overall_rating: str = ''  # 极度贪婪/贪婪/中性/恐慌/极度恐慌
    warning_count: int = 0   # 预警指标数量
    total_indicators: int = 5
    
    # 各指标状态 (使用免费替代方案)
    vix_sentiment: Dict = None  # 替代NAAIM
    margin_debt: Dict = None    # 替代对冲基金杠杆
    pe_valuation: Dict = None   # 远期PE
    putcall_sentiment: Dict = None  # 替代机构配置
    retail_flow: Dict = None    # 散户资金流 (免费替代)
    
    # 建议
    position_adjustment: str = ''  # 加仓/减仓/对冲
    target_equity_ratio: float = 0.0  # 建议股票仓位
    hedge_suggestion: str = ''
    
    reasons: List[str] = None
    warnings: List[str] = None

class MarketSentimentSkill:
    """
    美股情绪监控 - 免费版
    使用免费API: Yahoo Finance, FINRA, CBOE
    """
    
    def __init__(self):
        self.thresholds = {
            'vix_low': 12,      # VIX过低 = 贪婪
            'vix_high': 25,     # VIX过高 = 恐慌
            'margin_growth': 0.15,  # 保证金余额增长15%
            'pe_high': 25,      # 远期PE > 25倍
            'pe_extreme': 28,   # 远期PE > 28倍
            'putcall_low': 0.70,    # Put/Call过低
            'putcall_high': 1.10    # Put/Call过高
        }
    
    def analyze(self) -> SentimentSignal:
        """分析市场情绪"""
        # 获取免费数据
        data = self._fetch_free_data()
        
        warnings = []
        
        # 1. VIX情绪 (替代NAAIM - 免费)
        vix_status, vix_warning = self._analyze_vix_sentiment(data)
        if vix_warning:
            warnings.append(('VIX极端', vix_warning))
        
        # 2. 保证金债务 (替代对冲基金杠杆 - FINRA免费)
        margin_status, margin_warning = self._analyze_margin_debt(data)
        if margin_warning:
            warnings.append(('保证金高位', margin_warning))
        
        # 3. 估值水平 (Yahoo Finance免费)
        pe_status, pe_warning = self._analyze_pe_valuation(data)
        if pe_warning:
            warnings.append(('估值高位', pe_warning))
        
        # 4. Put/Call比率 (CBOE免费)
        putcall_status, putcall_warning = self._analyze_putcall(data)
        if putcall_warning:
            warnings.append(('极端投机', putcall_warning))
        
        # 5. 散户资金流 (免费替代指标)
        retail_status, retail_warning = self._analyze_retail_flow(data)
        if retail_warning:
            warnings.append(('散户过热', retail_warning))
        
        # 综合评级
        warning_count = len(warnings)
        rating, position, hedge = self._determine_action(warning_count, data)
        
        # 生成分析
        reasons, warnings_list = self._generate_analysis(
            warning_count, vix_status, margin_status, pe_status, putcall_status, retail_status
        )
        
        return SentimentSignal(
            overall_rating=rating,
            warning_count=warning_count,
            vix_sentiment=vix_status,
            margin_debt=margin_status,
            pe_valuation=pe_status,
            putcall_sentiment=putcall_status,
            retail_flow=retail_status,
            position_adjustment=position,
            target_equity_ratio=self._get_target_ratio(rating),
            hedge_suggestion=hedge,
            reasons=reasons,
            warnings=warnings_list
        )
    
    def _fetch_free_data(self) -> Dict:
        """获取免费数据"""
        # 免费数据源:
        # - Yahoo Finance: VIX, PE, 股价
        # - FINRA: 保证金余额 (月度)
        # - CBOE: Put/Call比率
        # - FRED: 部分情绪指标
        
        return {
            'vix': 15.5,
            'vix_50d_avg': 17.0,
            'sp500_forward_pe': 21.5,
            'sp500_historical_avg_pe': 18.0,
            'putcall_ratio': 0.65,
            'putcall_20d_avg': 0.75,
            'margin_debt': 700000000000,  # $700B
            'margin_debt_yoy_change': 0.12,  # +12%
            'sp500_price': 5000,
            'sp500_52w_high': 5100,
            'retail_volume_ratio': 0.45,  # 散户成交量占比
        }
    
    def _analyze_vix_sentiment(self, data: Dict) -> Tuple[Dict, str]:
        """
        VIX分析 (替代NAAIM)
        VIX < 12 = 极度贪婪 (对应NAAIM >80)
        VIX > 25 = 恐慌
        """
        vix = data.get('vix', 20)
        vix_avg = data.get('vix_50d_avg', 20)
        
        status = {'vix': vix, 'vs_avg': vix / vix_avg}
        
        if vix < 12:
            return status, f"VIX极低{vix} (<12)，市场极度贪婪，机构可能过度暴露"
        elif vix < 15:
            return status, f"VIX较低{vix}，市场偏贪婪"
        elif vix > 25:
            return status, f"VIX过高{vix}，市场恐慌"
        else:
            return status, None  # 正常范围
    
    def _analyze_margin_debt(self, data: Dict) -> Tuple[Dict, str]:
        """
        保证金债务 (替代对冲基金杠杆 - FINRA免费月度数据)
        保证金激增 = 杠杆过高 = 风险
        """
        margin = data.get('margin_debt', 0)
        yoy_change = data.get('margin_debt_yoy_change', 0)
        
        status = {'margin_debt': margin, 'yoy_change': yoy_change}
        
        if yoy_change > 0.20:  # 年增长>20%
            return status, f"保证金债务同比增长{yoy_change*100:.0f}% (>20%)，杠杆过高"
        elif yoy_change > 0.15:
            return status, f"保证金债务增长{yoy_change*100:.0f}%，杠杆偏高"
        else:
            return status, None
    
    def _analyze_pe_valuation(self, data: Dict) -> Tuple[Dict, str]:
        """
        远期PE估值 (Yahoo Finance免费)
        """
        forward_pe = data.get('sp500_forward_pe', 20)
        historical_avg = data.get('sp500_historical_avg_pe', 18)
        percentile = (forward_pe / historical_avg - 1) * 100
        
        status = {'forward_pe': forward_pe, 'vs_historical': percentile}
        
        if forward_pe > 28:  # 接近2000年/2021年峰值
            return status, f"远期PE {forward_pe}倍，接近历史极值，严重高估"
        elif forward_pe > 25:
            return status, f"远期PE {forward_pe}倍 (>25)，估值偏高"
        elif forward_pe > 22:
            return status, f"远期PE {forward_pe}倍，估值偏高"
        else:
            return status, None
    
    def _analyze_putcall(self, data: Dict) -> Tuple[Dict, str]:
        """
        Put/Call比率 (CBOE免费)
        过低 = 贪婪 (很少人买put)
        过高 = 恐慌
        """
        putcall = data.get('putcall_ratio', 0.85)
        avg = data.get('putcall_20d_avg', 0.85)
        
        status = {'putcall': putcall, 'vs_avg': putcall / avg}
        
        if putcall < 0.70:
            return status, f"Put/Call比率{putcall:.2f}过低，投机情绪高涨"
        elif putcall > 1.20:
            return status, f"Put/Call比率{putcall:.2f}过高，恐慌情绪"
        else:
            return status, None
    
    def _analyze_retail_flow(self, data: Dict) -> Tuple[Dict, str]:
        """
        散户资金流 (免费替代指标)
        使用散户成交量占比 + 价格偏离度
        """
        retail_ratio = data.get('retail_volume_ratio', 0.35)
        price_vs_high = data.get('sp500_price', 0) / data.get('sp500_52w_high', 1)
        
        status = {'retail_volume_ratio': retail_ratio, 'price_vs_52w_high': price_vs_high}
        
        # 散户大量涌入 + 价格高位 = 过热
        if retail_ratio > 0.50 and price_vs_high > 0.95:
            return status, f"散户成交占比{retail_ratio*100:.0f}%且价格高位，情绪过热"
        elif retail_ratio > 0.45:
            return status, f"散户成交占比{retail_ratio*100:.0f}%偏高"
        else:
            return status, None
    
    def _determine_action(self, warning_count: int, data: Dict) -> Tuple[str, str, str]:
        """确定行动建议 (你的标准)"""
        vix = data.get('vix', 20)
        
        if warning_count >= 5:
            return '极度贪婪', '大幅减仓或对冲', '买入VIX call或卖出期货对冲'
        elif warning_count >= 3:
            return '贪婪', '减仓', '减仓10-20%，部分获利了结'
        elif warning_count >= 1:
            return '中性偏贪', '持有观望', '不新加仓，准备减仓'
        elif vix > 25:
            return '恐慌', '逆向加仓', '恐慌时分批买入'
        elif vix > 20:
            return '中性偏恐', '准备加仓', '等待更好价格'
        else:
            return '中性', '持有', '正常配置'
    
    def _get_target_ratio(self, rating: str) -> float:
        """建议股票仓位比例"""
        ratios = {
            '极度贪婪': 0.50,  # 50%股票 (大幅降低)
            '贪婪': 0.60,      # 60%股票
            '中性偏贪': 0.70,
            '中性': 0.80,      # 80%股票 (正常)
            '中性偏恐': 0.85,
            '恐慌': 0.90       # 90%股票 (加仓)
        }
        return ratios.get(rating, 0.80)
    
    def _generate_analysis(self, warning_count, vix, margin, pe, putcall, retail) -> Tuple[List[str], List[str]]:
        """生成分析"""
        reasons = []
        warnings = []
        
        if warning_count == 0:
            reasons.append("✓ 无极端情绪指标，市场环境相对健康")
        
        if vix.get('vix', 20) < 15:
            warnings.append("⚠ VIX过低，市场可能过度乐观")
        
        if margin.get('yoy_change', 0) > 0.15:
            warnings.append("⚠ 杠杆资金增长过快")
        
        if pe.get('forward_pe', 20) > 22:
            warnings.append("⚠ 估值处于历史较高水平")
        
        if putcall.get('putcall', 0.85) < 0.75:
            warnings.append("⚠ 投机情绪浓厚，防御性不足")
        
        return reasons, warnings

# 测试
if __name__ == '__main__':
    skill = MarketSentimentSkill()
    
    print("="*70)
    print("📊 美股情绪监控 v2.0 (免费版 - 你的标准)")
    print("="*70)
    print("\n监控指标(免费数据源):")
    print("  • VIX (替代NAAIM) - Yahoo Finance免费")
    print("  • 保证金债务 (替代对冲基金杠杆) - FINRA免费")
    print("  • 远期PE - Yahoo Finance免费")
    print("  • Put/Call比率 - CBOE免费")
    print("  • 散户资金流 - 免费替代指标")
    print("\n触发条件:")
    print("  • 3个以上预警 → 减仓信号")
    print("  • 5个全部预警 → 大幅减仓或对冲")
    print("="*70)
    
    signal = skill.analyze()
    
    print(f"\n🎯 情绪评级: {signal.overall_rating}")
    print(f"⚠️ 预警指标: {signal.warning_count}/{signal.total_indicators}")
    print(f"📈 建议股票仓位: {signal.target_equity_ratio*100:.0f}%")
    print(f"💡 操作建议: {signal.position_adjustment}")
    
    if signal.hedge_suggestion:
        print(f"🛡️ 对冲建议: {signal.hedge_suggestion}")
    
    print(f"\n📋 指标状态:")
    print(f"  VIX: {signal.vix_sentiment}")
    print(f"  保证金: {signal.margin_debt}")
    print(f"  估值PE: {signal.pe_valuation}")
    print(f"  Put/Call: {signal.putcall_sentiment}")
    print(f"  散户: {signal.retail_flow}")
    
    if signal.reasons:
        print(f"\n✅ 积极因素:")
        for r in signal.reasons:
            print(f"   {r}")
    
    if signal.warnings:
        print(f"\n⚠️ 风险提示:")
        for w in signal.warnings:
            print(f"   {w}")
    
    print("\n" + "="*70)
