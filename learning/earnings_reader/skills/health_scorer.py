#!/usr/bin/env python3
"""
财报健康度评分系统
5维评分模型 + 异常预警
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class HealthRating(Enum):
    """健康度评级"""
    A = "A"  # 优秀 (85-100分)
    B = "B"  # 良好 (70-84分)
    C = "C"  # 一般 (60-69分)
    D = "D"  # 较差 (<60分)


@dataclass
class HealthScore:
    """健康度评分结果"""
    total_score: float  # 总分 (0-100)
    rating: str  # A/B/C/D
    
    # 5维评分
    growth_score: float  # 成长性 (30%)
    profitability_score: float  # 盈利能力 (25%)
    efficiency_score: float  # 运营效率 (20%)
    safety_score: float  # 财务安全 (15%)
    valuation_score: float  # 估值水平 (10%)
    
    # 异常预警
    warnings: List[str]  # 异常信号列表
    positives: List[str]  # 积极信号列表
    
    # 一句话总结
    summary: str = ""


class HealthScorer:
    """财报健康度评分器"""
    
    # 权重配置
    WEIGHTS = {
        'growth': 0.30,
        'profitability': 0.25,
        'efficiency': 0.20,
        'safety': 0.15,
        'valuation': 0.10
    }
    
    def __init__(self):
        pass
    
    def score(self, data: Dict) -> HealthScore:
        """
        对财报数据进行5维评分
        
        Args:
            data: 财报数据字典，包含:
                - revenue, revenue_growth
                - net_profit, net_profit_growth
                - gross_margin, net_margin, roe, roa
                - operating_cash_flow, free_cash_flow
                - pe, pb, ps
                - debt_ratio, current_ratio
                - total_assets, equity
                
        Returns:
            HealthScore对象
        """
        warnings = []
        positives = []
        
        # 1. 成长性评分 (30%)
        growth_score = self._score_growth(data, warnings, positives)
        
        # 2. 盈利能力评分 (25%)
        profitability_score = self._score_profitability(data, warnings, positives)
        
        # 3. 运营效率评分 (20%)
        efficiency_score = self._score_efficiency(data, warnings, positives)
        
        # 4. 财务安全评分 (15%)
        safety_score = self._score_safety(data, warnings, positives)
        
        # 5. 估值评分 (10%)
        valuation_score = self._score_valuation(data, warnings, positives)
        
        # 计算总分
        total_score = (
            growth_score * self.WEIGHTS['growth'] +
            profitability_score * self.WEIGHTS['profitability'] +
            efficiency_score * self.WEIGHTS['efficiency'] +
            safety_score * self.WEIGHTS['safety'] +
            valuation_score * self.WEIGHTS['valuation']
        )
        
        # 确定评级
        rating = self._get_rating(total_score)
        
        # 生成一句话总结
        summary = self._generate_summary(total_score, rating, warnings, positives)
        
        return HealthScore(
            total_score=round(total_score, 1),
            rating=rating,
            growth_score=round(growth_score, 1),
            profitability_score=round(profitability_score, 1),
            efficiency_score=round(efficiency_score, 1),
            safety_score=round(safety_score, 1),
            valuation_score=round(valuation_score, 1),
            warnings=warnings,
            positives=positives,
            summary=summary
        )
    
    def _score_growth(self, data: Dict, warnings: List, positives: List) -> float:
        """成长性评分 (0-100)"""
        score = 50  # 基础分
        
        revenue_growth = data.get('revenue_growth')
        profit_growth = data.get('net_profit_growth') or data.get('profit_growth')
        
        if revenue_growth is not None:
            if revenue_growth > 30:
                score += 25
                positives.append(f"营收高增长: +{revenue_growth:.1f}%")
            elif revenue_growth > 15:
                score += 15
                positives.append(f"营收稳健增长: +{revenue_growth:.1f}%")
            elif revenue_growth > 0:
                score += 5
            else:
                score -= 20
                warnings.append(f"营收下滑: {revenue_growth:.1f}%")
        
        if profit_growth is not None:
            if profit_growth > 30:
                score += 25
                positives.append(f"净利润高增长: +{profit_growth:.1f}%")
            elif profit_growth > 15:
                score += 15
            elif profit_growth > 0:
                score += 5
            else:
                score -= 15
                warnings.append(f"净利润下滑: {profit_growth:.1f}%")
        
        # 营收增长但利润下滑的风险信号
        if revenue_growth and revenue_growth > 0 and profit_growth and profit_growth < 0:
            warnings.append("⚠️ 增收不增利: 营收增长但利润下滑")
            score -= 10
        
        return max(0, min(100, score))
    
    def _score_profitability(self, data: Dict, warnings: List, positives: List) -> float:
        """盈利能力评分 (0-100)"""
        score = 50
        
        gross_margin = data.get('gross_margin')
        net_margin = data.get('net_margin')
        roe = data.get('roe')
        roa = data.get('roa')
        
        # 毛利率
        if gross_margin is not None:
            if gross_margin > 50:
                score += 15
                positives.append(f"高毛利率: {gross_margin:.1f}%")
            elif gross_margin > 30:
                score += 10
            elif gross_margin < 15:
                score -= 10
                warnings.append(f"低毛利率: {gross_margin:.1f}%")
        
        # 净利率
        if net_margin is not None:
            if net_margin > 20:
                score += 15
            elif net_margin > 10:
                score += 10
            elif net_margin < 5:
                score -= 10
                if net_margin < 0:
                    warnings.append(f"净亏损: {net_margin:.1f}%")
        
        # ROE
        if roe is not None:
            if roe > 20:
                score += 20
                positives.append(f"优秀ROE: {roe:.1f}%")
            elif roe > 15:
                score += 15
            elif roe > 10:
                score += 10
            elif roe < 5:
                score -= 10
        
        return max(0, min(100, score))
    
    def _score_efficiency(self, data: Dict, warnings: List, positives: List) -> float:
        """运营效率评分 (0-100)"""
        score = 50
        
        operating_cash_flow = data.get('operating_cash_flow')
        net_profit = data.get('net_profit')
        
        # 经营现金流 vs 净利润
        if operating_cash_flow is not None and net_profit is not None:
            if net_profit > 0:
                cash_to_profit_ratio = operating_cash_flow / net_profit
                if cash_to_profit_ratio > 1.0:
                    score += 20
                    positives.append("经营现金流覆盖净利润，盈利质量高")
                elif cash_to_profit_ratio > 0.8:
                    score += 10
                elif cash_to_profit_ratio < 0.5:
                    score -= 15
                    warnings.append("⚠️ 经营现金流远低于净利润，盈利质量存疑")
            elif operating_cash_flow > 0 and net_profit < 0:
                # 亏损但现金流为正（可能是非现金亏损）
                positives.append("经营现金流为正，亏损主要是非现金项目")
                score += 10
        
        # 自由现金流
        free_cash_flow = data.get('free_cash_flow')
        if free_cash_flow is not None:
            if free_cash_flow > 0:
                score += 10
                positives.append("自由现金流为正")
            else:
                warnings.append("自由现金流为负")
        
        return max(0, min(100, score))
    
    def _score_safety(self, data: Dict, warnings: List, positives: List) -> float:
        """财务安全评分 (0-100)"""
        score = 50
        
        debt_ratio = data.get('debt_ratio')
        current_ratio = data.get('current_ratio')
        total_cash = data.get('total_cash')
        total_debt = data.get('total_debt')
        
        # 资产负债率
        if debt_ratio is not None:
            if debt_ratio < 40:
                score += 20
                positives.append(f"低负债率: {debt_ratio:.1f}%")
            elif debt_ratio < 60:
                score += 10
            elif debt_ratio > 70:
                score -= 15
                warnings.append(f"高负债率: {debt_ratio:.1f}%")
            elif debt_ratio > 80:
                score -= 25
                warnings.append(f"⚠️ 极高负债率: {debt_ratio:.1f}%，财务风险高")
        
        # 流动比率
        if current_ratio is not None:
            if current_ratio > 2:
                score += 15
            elif current_ratio > 1.5:
                score += 10
            elif current_ratio < 1:
                score -= 15
                warnings.append("流动比率<1，短期偿债能力弱")
        
        # 现金vs债务
        if total_cash is not None and total_debt is not None:
            if total_debt > 0:
                cash_debt_ratio = total_cash / total_debt
                if cash_debt_ratio > 0.5:
                    score += 10
                elif cash_debt_ratio < 0.1:
                    warnings.append("现金储备不足，债务压力大")
        
        return max(0, min(100, score))
    
    def _score_valuation(self, data: Dict, warnings: List, positives: List) -> float:
        """估值评分 (0-100) - 估值越低分数越高"""
        score = 50
        
        pe = data.get('pe')
        pb = data.get('pb')
        
        # PE估值
        if pe is not None and pe > 0:
            if pe < 15:
                score += 25
                positives.append(f"低PE估值: {pe:.1f}")
            elif pe < 25:
                score += 15
            elif pe < 40:
                score += 5
            elif pe > 50:
                score -= 10
                warnings.append(f"高PE估值: {pe:.1f}，可能存在泡沫")
            elif pe > 100:
                score -= 20
                warnings.append(f"极高PE估值: {pe:.1f}")
        
        # PB估值
        if pb is not None and pb > 0:
            if pb < 1.5:
                score += 15
            elif pb < 3:
                score += 5
            elif pb > 5:
                score -= 10
        
        return max(0, min(100, score))
    
    def _get_rating(self, score: float) -> str:
        """根据分数确定评级"""
        if score >= 85:
            return HealthRating.A.value
        elif score >= 70:
            return HealthRating.B.value
        elif score >= 60:
            return HealthRating.C.value
        else:
            return HealthRating.D.value
    
    def _generate_summary(self, score: float, rating: str, warnings: List, positives: List) -> str:
        """生成一句话总结"""
        if rating == HealthRating.A.value:
            return "财务表现优秀，核心指标健康，值得重点关注"
        elif rating == HealthRating.B.value:
            return "财务表现良好，整体稳健，可考虑配置"
        elif rating == HealthRating.C.value:
            return "财务表现一般，存在部分风险点，需进一步分析"
        else:
            return "财务表现较差，存在明显风险，建议回避"


# 测试运行
if __name__ == "__main__":
    scorer = HealthScorer()
    
    # 测试数据 - 模拟一家公司的财报
    test_data = {
        'revenue': 100.5,
        'revenue_growth': 25.5,
        'net_profit': 15.2,
        'net_profit_growth': 30.0,
        'eps': 2.5,
        'gross_margin': 45.0,
        'net_margin': 15.1,
        'roe': 18.5,
        'operating_cash_flow': 18.0,
        'free_cash_flow': 12.0,
        'debt_ratio': 35.0,
        'current_ratio': 2.1,
        'pe': 22.0,
        'pb': 3.5
    }
    
    result = scorer.score(test_data)
    
    print("="*50)
    print(f"📊 健康度评分: {result.rating} ({result.total_score}分)")
    print("="*50)
    print(f"成长性: {result.growth_score}/100 (权重30%)")
    print(f"盈利能力: {result.profitability_score}/100 (权重25%)")
    print(f"运营效率: {result.efficiency_score}/100 (权重20%)")
    print(f"财务安全: {result.safety_score}/100 (权重15%)")
    print(f"估值水平: {result.valuation_score}/100 (权重10%)")
    print()
    print("✅ 积极信号:")
    for p in result.positives:
        print(f"  • {p}")
    print()
    print("⚠️ 风险信号:")
    for w in result.warnings:
        print(f"  • {w}")
    print()
    print(f"💡 总结: {result.summary}")
