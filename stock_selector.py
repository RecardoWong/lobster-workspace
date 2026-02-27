#!/usr/bin/env python3
"""
六维财务评分系统 v3.2
基于投资文档：/root/.openclaw/workspace/memory/investment_strategy_v3.2.md

六维：估值(15%) + 增长(25%) + 资产(15%) + 盈利(20%) + 安全(20%) + 现金(5%)
总分100分，买入门槛：>80分且无一票否决项
"""

import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class FinancialScore:
    """六维财务评分结果"""
    symbol: str
    name: str
    total_score: float
    
    # 六维分项
    valuation_score: float      # 估值 15%
    growth_score: float         # 增长 25%
    asset_score: float          # 资产 15%
    profitability_score: float  # 盈利 20%
    safety_score: float         # 安全 20%
    cash_score: float           # 现金 5%
    
    # 原始数据
    pe: float
    peg: float  # PEG = PE / 增长
    pb: float
    roe: float
    profit_growth: float
    debt_ratio: float
    cash_flow: float
    
    recommendation: str
    risks: List[str]
    vetoes: List[str]  # 一票否决项


class FinancialSixDimensionScorer:
    """
    六维财务评分器 (v3.2)
    
    权重配置（来自v3.2文档）：
    - 增长：25%（最重要）
    - 盈利：20%
    - 安全：20%
    - 估值：15%
    - 资产：15%
    - 现金：5%
    """
    
    WEIGHTS = {
        'growth': 0.25,         # 增长
        'profitability': 0.20,  # 盈利
        'safety': 0.20,         # 安全
        'valuation': 0.15,      # 估值
        'asset': 0.15,          # 资产
        'cash': 0.05,           # 现金
    }
    
    # 一票否决红线（来自v3.2文档）
    VETO_RULES = {
        'pe': {'max': 100, 'desc': 'PE > 100'},
        'peg': {'max': 2.0, 'desc': 'PEG > 2'},
        'pb': {'max': 10, 'desc': 'PB > 10'},
        'roe': {'min': 5, 'desc': 'ROE < 5%'},
        'debt_ratio': {'max': 60, 'desc': '有息负债率 > 60%'},
        'cash_flow': {'check': 'negative_3y', 'desc': '现金流连续3年为负'},
    }
    
    def __init__(self):
        pass
    
    def get_stock_name(self, symbol: str) -> str:
        """获取股票名称"""
        try:
            df = ak.stock_zh_a_spot_em()
            name = df[df['代码'] == symbol]['名称'].values[0]
            return name
        except:
            return symbol
    
    def get_financial_data(self, symbol: str) -> Dict:
        """获取财务数据"""
        data = {
            'pe': None, 'pb': None, 'roe': None,
            'profit_growth': None, 'debt_ratio': None, 'cash_flow': None
        }
        
        try:
            # 从实时行情获取PE/PB
            df_spot = ak.stock_zh_a_spot_em()
            stock_row = df_spot[df_spot['代码'] == symbol]
            if not stock_row.empty:
                data['pe'] = stock_row['市盈率-动态'].values[0]
                data['pb'] = stock_row['市净率'].values[0]
        except:
            pass
        
        try:
            # 从财务指标获取ROE/增长率/负债率/现金流
            df_fin = ak.stock_financial_analysis_indicator(symbol=symbol)
            if not df_fin.empty:
                latest = df_fin.iloc[0]
                data['roe'] = latest.get('净资产收益率', None)
                data['profit_growth'] = latest.get('净利润增长率', None)
                data['debt_ratio'] = latest.get('资产负债率', None)
                data['cash_flow'] = latest.get('每股现金流量', None)
        except:
            pass
        
        return data
    
    def score_valuation(self, pe: float, profit_growth: float) -> Tuple[float, str, float]:
        """
        估值评分 (权重15%) - 基于PEG
        PEG = PE / 利润增长率
        标准：PEG < 1低估，1-1.5合理，>2高估（一票否决）
        """
        # 计算PEG
        if pe is None or profit_growth is None or profit_growth <= 0:
            peg = None
        else:
            peg = pe / profit_growth
        
        # 基于PEG评分（优先）
        if peg is not None:
            if peg < 1.0:
                score = 90
                desc = f"PEG低估({peg:.2f})"
            elif peg < 1.5:
                score = 75
                desc = f"PEG合理({peg:.2f})"
            elif peg < 2.0:
                score = 55
                desc = f"PEG偏高({peg:.2f})"
            else:
                score = 30
                desc = f"PEG过高({peg:.2f})-一票否决"
        else:
            # PEG无法计算时，用PE兜底
            if pe is None or pe < 0 or pe > 1000:
                score = 30
                desc = f"PE异常({pe:.0f})"
                peg = -1
            elif pe < 20:
                score = 85
                desc = f"PE低估({pe:.0f})"
                peg = -1
            elif pe < 30:
                score = 70
                desc = f"PE合理({pe:.0f})"
                peg = -1
            elif pe < 50:
                score = 55
                desc = f"PE偏高({pe:.0f})"
                peg = -1
            else:
                score = 35
                desc = f"PE过高({pe:.0f})"
                peg = -1
        
        return score, desc, peg
    
    def score_growth(self, profit_growth: float) -> Tuple[float, str]:
        """
        增长评分 (权重25%) - 基于利润增长率
        这是最重要的维度！
        """
        if profit_growth is None:
            return 40, "增长数据缺失"
        
        if profit_growth > 100:
            score = 95
            desc = f"超高增长({profit_growth:.0f}%)"
        elif profit_growth > 50:
            score = 85
            desc = f"高增长({profit_growth:.0f}%)"
        elif profit_growth > 30:
            score = 75
            desc = f"良好增长({profit_growth:.0f}%)"
        elif profit_growth > 0:
            score = 55
            desc = f"正增长({profit_growth:.0f}%)"
        else:
            score = 30
            desc = f"负增长({profit_growth:.0f}%)"
        
        return score, desc
    
    def score_asset(self, pb: float) -> Tuple[float, str]:
        """
        资产评分 (权重15%) - 基于PB
        """
        if pb is None or pb < 0:
            return 40, "PB异常-净资产为负"
        
        if pb < 2:
            score = 80
            desc = f"PB低估({pb:.1f})"
        elif pb < 4:
            score = 70
            desc = f"PB合理({pb:.1f})"
        elif pb < 8:
            score = 55
            desc = f"PB偏高({pb:.1f})"
        elif pb < 10:
            score = 35
            desc = f"PB过高({pb:.1f})-一票否决"
        else:
            score = 20
            desc = f"PB极高({pb:.1f})-一票否决"
        
        return score, desc
    
    def score_profitability(self, roe: float) -> Tuple[float, str]:
        """
        盈利评分 (权重20%) - 基于ROE
        """
        if roe is None:
            return 40, "ROE数据缺失"
        
        if roe > 20:
            score = 95
            desc = f"ROE卓越({roe:.1f}%)"
        elif roe > 15:
            score = 85
            desc = f"ROE优秀({roe:.1f}%)"
        elif roe > 10:
            score = 70
            desc = f"ROE良好({roe:.1f}%)"
        elif roe > 5:
            score = 50
            desc = f"ROE一般({roe:.1f}%)"
        else:
            score = 25
            desc = f"ROE偏低({roe:.1f}%)"
        
        return score, desc
    
    def score_safety(self, debt_ratio: float) -> Tuple[float, str]:
        """
        安全评分 (权重20%) - 基于资产负债率（有息负债更准，但用总负债替代）
        """
        if debt_ratio is None:
            return 40, "负债数据缺失"
        
        if debt_ratio < 30:
            score = 90
            desc = f"负债率低({debt_ratio:.1f}%-安全)"
        elif debt_ratio < 40:
            score = 80
            desc = f"负债率合理({debt_ratio:.1f}%)"
        elif debt_ratio < 50:
            score = 65
            desc = f"负债率中等({debt_ratio:.1f}%)"
        elif debt_ratio < 60:
            score = 45
            desc = f"负债率偏高({debt_ratio:.1f}%)"
        else:
            score = 20
            desc = f"负债率高({debt_ratio:.1f}%-一票否决)"
        
        return score, desc
    
    def score_cash(self, cash_flow: float) -> Tuple[float, str]:
        """
        现金流评分 (权重5%) - 基于每股经营现金流
        """
        if cash_flow is None:
            return 40, "现金流数据缺失"
        
        if cash_flow > 2:
            score = 90
            desc = f"现金流充沛({cash_flow:.2f})"
        elif cash_flow > 1:
            score = 75
            desc = f"现金流良好({cash_flow:.2f})"
        elif cash_flow > 0:
            score = 60
            desc = f"现金流为正({cash_flow:.2f})"
        else:
            score = 30
            desc = f"现金流为负({cash_flow:.2f})"
        
        return score, desc
    
    def check_vetoes(self, data: Dict) -> List[str]:
        """检查一票否决项"""
        vetoes = []
        
        pe = data.get('pe')
        if pe and pe > 100:
            vetoes.append(f"PE {pe:.0f} > 100")
        
        roe = data.get('roe')
        if roe and roe < 5:
            vetoes.append(f"ROE {roe:.1f}% < 5%")
        
        debt = data.get('debt_ratio')
        if debt and debt > 60:
            vetoes.append(f"负债率 {debt:.1f}% > 60%")
        
        cash = data.get('cash_flow')
        if cash and cash < 0:
            # 简化处理，实际应该检查连续3年
            vetoes.append("现金流为负")
        
        return vetoes
    
    def analyze(self, symbol: str) -> FinancialScore:
        """
        六维综合分析
        """
        print(f"\n🔍 分析 {symbol}...")
        
        # 获取数据
        name = self.get_stock_name(symbol)
        data = self.get_financial_data(symbol)
        
        print(f"   数据: PE={data['pe']}, ROE={data['roe']}, 增长={data['profit_growth']}%")
        
        # 各维度评分
        val_score, val_desc, peg = self.score_valuation(data['pe'], data['profit_growth'])
        growth_score, growth_desc = self.score_growth(data['profit_growth'])
        asset_score, asset_desc = self.score_asset(data['pb'])
        profit_score, profit_desc = self.score_profitability(data['roe'])
        safety_score, safety_desc = self.score_safety(data['debt_ratio'])
        cash_score, cash_desc = self.score_cash(data['cash_flow'])
        
        print(f"   估值: {val_score} | 增长: {growth_score} | 资产: {asset_score}")
        print(f"   盈利: {profit_score} | 安全: {safety_score} | 现金: {cash_score}")
        
        # 一票否决
        vetoes = self.check_vetoes(data)
        
        # 加权总分
        total = (
            val_score * self.WEIGHTS['valuation'] +
            growth_score * self.WEIGHTS['growth'] +
            asset_score * self.WEIGHTS['asset'] +
            profit_score * self.WEIGHTS['profitability'] +
            safety_score * self.WEIGHTS['safety'] +
            cash_score * self.WEIGHTS['cash']
        )
        
        # 投资建议
        if vetoes:
            rec = f"🚫 回避 - 一票否决: {', '.join(vetoes)}"
        elif total >= 80:
            rec = "🟢 强烈推荐 - 六维全优"
        elif total >= 70:
            rec = "🟢 推荐 - 多数维度良好"
        elif total >= 60:
            rec = "🟡 中性 - 有亮点也有风险"
        else:
            rec = "🔴 谨慎 - 多项指标偏弱"
        
        # 风险提示
        risks = []
        if data.get('pe', 0) > 50:
            risks.append("估值偏高")
        if data.get('debt_ratio', 0) > 50:
            risks.append("负债率偏高")
        if data.get('profit_growth', 0) < 0:
            risks.append("利润下滑")
        
        return FinancialScore(
            symbol=symbol, name=name, total_score=round(total, 1),
            valuation_score=val_score, growth_score=growth_score,
            asset_score=asset_score, profitability_score=profit_score,
            safety_score=safety_score, cash_score=cash_score,
            pe=data['pe'] or 0, peg=peg or -1, pb=data['pb'] or 0, roe=data['roe'] or 0,
            profit_growth=data['profit_growth'] or 0,
            debt_ratio=data['debt_ratio'] or 0, cash_flow=data['cash_flow'] or 0,
            recommendation=rec, risks=risks, vetoes=vetoes
        )
    
    def format_report(self, score: FinancialScore) -> str:
        """格式化报告"""
        lines = [
            f"\n{'='*70}",
            f"📊 {score.name} ({score.symbol}) - 六维财务评分 v3.2",
            f"{'='*70}",
            f"",
            f"🎯 综合评分: {score.total_score}/100",
            f"💡 投资建议: {score.recommendation}",
            f"",
            f"📈 六维评分 (权重):",
            f"   增长(25%):   {score.growth_score:2.0f}/100  利润增速: {score.profit_growth:.1f}%",
            f"   盈利(20%):   {score.profitability_score:2.0f}/100  ROE: {score.roe:.1f}%",
            f"   安全(20%):   {score.safety_score:2.0f}/100  负债率: {score.debt_ratio:.1f}%",
            f"   估值(15%):   {score.valuation_score:2.0f}/100  PE: {score.pe:.1f}  PEG: {score.peg:.2f}",
            f"   资产(15%):   {score.asset_score:2.0f}/100  PB: {score.pb:.1f}",
            f"   现金( 5%):   {score.cash_score:2.0f}/100  每股现金流: {score.cash_flow:.2f}",
            f"",
        ]
        
        if score.vetoes:
            lines.append(f"🚫 一票否决项:")
            for v in score.vetoes:
                lines.append(f"   • {v}")
            lines.append(f"")
        
        if score.risks:
            lines.append(f"⚠️ 风险提示:")
            for r in score.risks:
                lines.append(f"   • {r}")
            lines.append(f"")
        
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


def main():
    """演示"""
    print("=" * 70)
    print("🎯 六维财务评分系统 v3.2")
    print("增长25% | 盈利20% | 安全20% | 估值15% | 资产15% | 现金5%")
    print("买入门槛: >80分且无一票否决")
    print("=" * 70)
    
    scorer = FinancialSixDimensionScorer()
    
    # 测试股票
    test_stocks = ['000001', '300750', '600519']
    
    for symbol in test_stocks:
        score = scorer.analyze(symbol)
        print(scorer.format_report(score))
    
    print("=" * 70)
    print("✅ 六维评分完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
