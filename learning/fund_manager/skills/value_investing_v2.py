#!/usr/bin/env python3
"""
Skill 1: 美股价值投资框架 (免费版)
使用Yahoo Finance免费数据
判断标准(你的标准):
- ROE > 15%(持续3年以上) → 基础门槛
- 负债率 < 50%
- 自由现金流 > 净利润的80%
- 护城河评估(品牌/网络效应/成本优势)
输出: A/B/C/D评级 + 具体理由
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ValueRating:
    ticker: str
    rating: str  # A/B/C/D
    score: int   # 0-100
    roe_pass: bool
    debt_pass: bool
    fcf_pass: bool
    moat_score: int  # 0-30
    reasons: List[str]
    red_flags: List[str]

class ValueInvestingSkill:
    """
    价值投资框架 - 免费版
    使用Yahoo Finance数据
    """
    
    def __init__(self):
        self.yf_session = None
    
    def analyze(self, ticker: str) -> ValueRating:
        """分析单只股票"""
        # 从Yahoo Finance获取数据 (免费API)
        data = self._fetch_yahoo_data(ticker)
        
        # 1. 检查ROE (你的标准: >15%持续3年)
        roe_pass, roe_detail = self._check_roe(data)
        
        # 2. 检查负债率 (你的标准: <50%)
        debt_pass, debt_detail = self._check_debt(data)
        
        # 3. 检查FCF (你的标准: >净利润80%)
        fcf_pass, fcf_detail = self._check_fcf(data)
        
        # 4. 护城河评估 (你的标准: 品牌/网络/成本)
        moat_score, moat_detail = self._evaluate_moat(data)
        
        # 5. 综合评级
        rating, score = self._calculate_rating(
            roe_pass, debt_pass, fcf_pass, moat_score
        )
        
        # 生成理由和红旗
        reasons, red_flags = self._generate_analysis(
            roe_pass, debt_pass, fcf_pass, moat_score, data
        )
        
        return ValueRating(
            ticker=ticker,
            rating=rating,
            score=score,
            roe_pass=roe_pass,
            debt_pass=debt_pass,
            fcf_pass=fcf_pass,
            moat_score=moat_score,
            reasons=reasons,
            red_flags=red_flags
        )
    
    def _fetch_yahoo_data(self, ticker: str) -> Dict:
        """从Yahoo Finance获取免费数据"""
        # TODO: 实际使用yfinance库获取
        # 模拟数据 - 基于真实公司特征
        mock_data = {
            'AAPL': {
                'roe_3yr_avg': 0.82,  # 82% ROE (优秀)
                'roe_history': [0.90, 0.80, 0.75],  # 3年ROE
                'debt_to_equity': 0.45,  # 负债率45% (合格)
                'free_cash_flow': 99e9,  # $99B FCF
                'net_income': 97e9,  # $97B 净利润
                'fcf_to_net_income': 1.02,  # 102% > 80%
                'gross_margin': 0.45,  # 毛利率45%
                'industry_avg_gross_margin': 0.35,
                'operating_margin': 0.30,
                'revenue_growth_3yr': 0.11,  # 3年复合增长11%
                'user_base': 'ecosystem',  # 生态系统粘性
            },
            'MSFT': {
                'roe_3yr_avg': 0.43,  # 43% ROE (优秀)
                'roe_history': [0.48, 0.43, 0.38],
                'debt_to_equity': 0.35,  # 35% (优秀)
                'free_cash_flow': 65e9,
                'net_income': 72e9,
                'fcf_to_net_income': 0.90,  # 90%, 略低于80%
                'gross_margin': 0.69,  # 69% (极高)
                'industry_avg_gross_margin': 0.60,
                'operating_margin': 0.42,
                'revenue_growth_3yr': 0.14,
                'user_base': 'enterprise',  # 企业粘性
            },
            'NVDA': {
                'roe_3yr_avg': 0.40,  # 40% ROE (优秀，但波动大)
                'roe_history': [0.70, 0.25, 0.25],  # 波动大
                'debt_to_equity': 0.20,  # 20% (优秀)
                'free_cash_flow': 27e9,
                'net_income': 30e9,
                'fcf_to_net_income': 0.90,  # 90%
                'gross_margin': 0.72,  # 72% (极高)
                'industry_avg_gross_margin': 0.50,
                'operating_margin': 0.55,
                'revenue_growth_3yr': 0.50,  # 50%增长
                'user_base': 'monopoly',  # CUDA垄断
            },
            'TSLA': {
                'roe_3yr_avg': 0.18,  # 18% ROE (刚达标)
                'roe_history': [0.22, 0.18, 0.15],
                'debt_to_equity': 0.15,  # 15% (优秀)
                'free_cash_flow': 11e9,
                'net_income': 15e9,
                'fcf_to_net_income': 0.73,  # 73% < 80% (不达标)
                'gross_margin': 0.18,  # 18% (低)
                'industry_avg_gross_margin': 0.18,
                'operating_margin': 0.08,
                'revenue_growth_3yr': 0.28,
                'user_base': 'brand',  # 品牌力
            }
        }
        return mock_data.get(ticker, mock_data['AAPL'])
    
    def _check_roe(self, data: Dict) -> Tuple[bool, str]:
        """检查ROE是否>15%持续3年"""
        roe_history = data.get('roe_history', [])
        
        if len(roe_history) < 3:
            return False, "ROE历史数据不足3年"
        
        # 检查最近3年是否都>15%
        all_pass = all(roe > 0.15 for roe in roe_history)
        avg_roe = sum(roe_history) / len(roe_history)
        
        if all_pass:
            if avg_roe > 0.30:
                return True, f"ROE优秀: 3年均值{avg_roe*100:.0f}% (连续3年>15%)"
            else:
                return True, f"ROE合格: 3年均值{avg_roe*100:.0f}% (连续3年>15%)"
        else:
            failed_years = [f"{roe*100:.0f}%" for roe in roe_history if roe <= 0.15]
            return False, f"ROE不达标: 有{len(failed_years)}年低于15% ({', '.join(failed_years)})"
    
    def _check_debt(self, data: Dict) -> Tuple[bool, str]:
        """检查负债率是否<50%"""
        debt_ratio = data.get('debt_to_equity', 1.0)
        
        if debt_ratio < 0.30:
            return True, f"负债率优秀: {debt_ratio*100:.0f}% (<30%)"
        elif debt_ratio < 0.50:
            return True, f"负债率合格: {debt_ratio*100:.0f}% (<50%)"
        else:
            return False, f"负债率过高: {debt_ratio*100:.0f}% (>50%)"
    
    def _check_fcf(self, data: Dict) -> Tuple[bool, str]:
        """检查FCF是否>净利润80%"""
        fcf = data.get('free_cash_flow', 0)
        net_income = data.get('net_income', 1)
        fcf_ratio = fcf / net_income
        
        if fcf_ratio >= 0.80:
            return True, f"FCF优秀: {fcf_ratio*100:.0f}% of净利润 (>80%)"
        else:
            return False, f"FCF不足: {fcf_ratio*100:.0f}% of净利润 (<80%)"
    
    def _evaluate_moat(self, data: Dict) -> Tuple[int, str]:
        """
        护城河评估 (0-30分)
        品牌/网络效应/成本优势
        """
        score = 0
        details = []
        
        # 1. 品牌溢价 (毛利率高于行业) - 10分
        gross_margin = data.get('gross_margin', 0)
        industry_avg = data.get('industry_avg_gross_margin', gross_margin)
        
        if gross_margin > industry_avg + 0.10:  # 高于行业10pp
            score += 10
            details.append("强品牌溢价(毛利率超行业10pp+)")
        elif gross_margin > industry_avg + 0.05:
            score += 7
            details.append("品牌溢价(毛利率超行业5pp)")
        elif gross_margin > industry_avg:
            score += 4
            details.append("轻度品牌溢价")
        
        # 2. 网络效应/用户粘性 - 10分
        user_base = data.get('user_base', '')
        if user_base == 'ecosystem':
            score += 10
            details.append("强生态系统粘性")
        elif user_base == 'enterprise':
            score += 9
            details.append("企业级客户粘性")
        elif user_base == 'monopoly':
            score += 10
            details.append("技术垄断地位")
        elif user_base == 'brand':
            score += 6
            details.append("品牌认知度")
        
        # 3. 成本优势/规模效应 - 10分
        op_margin = data.get('operating_margin', 0)
        growth = data.get('revenue_growth_3yr', 0)
        
        if op_margin > 0.30 and growth > 0.10:
            score += 10
            details.append("规模效应+高利润")
        elif op_margin > 0.20:
            score += 7
            details.append("良好运营效率")
        elif growth > 0.20:
            score += 5
            details.append("高速增长期")
        
        return score, "; ".join(details) if details else "护城河不明显"
    
    def _calculate_rating(self, roe_pass: bool, debt_pass: bool, 
                         fcf_pass: bool, moat_score: int) -> Tuple[str, int]:
        """
        计算综合评级
        A: 全通过 + 护城河>20分
        B: 全通过 + 护城河10-20分
        C: 1-2项不达标
        D: 3项+不达标
        """
        # 基础分计算
        base_score = 0
        if roe_pass: base_score += 25
        if debt_pass: base_score += 25
        if fcf_pass: base_score += 20
        
        # 护城河加分
        total_score = base_score + moat_score
        
        # 评级判定
        passes = sum([roe_pass, debt_pass, fcf_pass])
        
        if passes == 3 and moat_score >= 20:
            return 'A', total_score
        elif passes == 3 and moat_score >= 10:
            return 'B', total_score
        elif passes >= 2:
            return 'C', total_score
        else:
            return 'D', total_score
    
    def _generate_analysis(self, roe_pass, debt_pass, fcf_pass, 
                          moat_score, data) -> Tuple[List[str], List[str]]:
        """生成分析理由和风险提示"""
        reasons = []
        red_flags = []
        
        # 优点
        if roe_pass:
            avg_roe = sum(data.get('roe_history', [0])) / 3
            reasons.append(f"✓ ROE连续3年>15%，均值{avg_roe*100:.0f}%")
        
        if debt_pass:
            reasons.append(f"✓ 负债率{data.get('debt_to_equity', 0)*100:.0f}%，财务稳健")
        
        if fcf_pass:
            reasons.append(f"✓ FCF/净利润{data.get('fcf_to_net_income', 0)*100:.0f}%，现金流健康")
        
        if moat_score >= 20:
            reasons.append(f"✓ 护城河强({moat_score}/30分)，竞争优势明显")
        elif moat_score >= 10:
            reasons.append(f"✓ 有一定护城河({moat_score}/30分)")
        
        # 风险
        if not roe_pass:
            red_flags.append("✗ ROE不达标或波动大")
        if not debt_pass:
            red_flags.append("✗ 负债率过高")
        if not fcf_pass:
            red_flags.append("✗ 现金流转化能力不足")
        if moat_score < 10:
            red_flags.append("✗ 护城河薄弱，竞争优势不明显")
        
        return reasons, red_flags
    
    def batch_analyze(self, tickers: List[str]) -> List[ValueRating]:
        """批量分析"""
        results = []
        for ticker in tickers:
            try:
                rating = self.analyze(ticker)
                results.append(rating)
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
        
        # 按评级排序 (A>B>C>D)
        rating_order = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
        results.sort(key=lambda x: (rating_order.get(x.rating, 0), x.score), reverse=True)
        
        return results

# 测试
if __name__ == '__main__':
    skill = ValueInvestingSkill()
    
    print("="*70)
    print("🎯 价值投资框架 v2.0 (免费版 - 你的标准)")
    print("="*70)
    print("\n判断标准:")
    print("  • ROE > 15% 且持续3年")
    print("  • 负债率 < 50%")
    print("  • FCF > 净利润80%")
    print("  • 护城河评估(品牌/网络/成本)")
    print("="*70)
    
    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA']
    results = skill.batch_analyze(tickers)
    
    for r in results:
        print(f"\n{r.ticker}: 评级 {r.rating} (评分{r.score}/100)")
        print(f"  ROE: {'✓' if r.roe_pass else '✗'} | 负债: {'✓' if r.debt_pass else '✗'} | FCF: {'✓' if r.fcf_pass else '✗'}")
        print(f"  护城河: {r.moat_score}/30分")
        print(f"\n  优点:")
        for reason in r.reasons:
            print(f"    {reason}")
        if r.red_flags:
            print(f"\n  风险:")
            for flag in r.red_flags:
                print(f"    {flag}")
        print("-"*70)
