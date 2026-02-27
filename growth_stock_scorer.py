#!/usr/bin/env python3
"""
Pre-profit成长股六维评分系统
适用于：高增长、未盈利或盈利不稳定的科技公司

六维：增长(25%) + 毛利率(20%) + 市场空间(15%) + 客户质量(15%) + 技术壁垒(15%) + 现金(10%)
总分100分，买入门槛：>80分
"""

import akshare as ak
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class GrowthStockScore:
    """成长股评分结果"""
    symbol: str
    name: str
    total_score: float
    
    # 六维分项
    growth_score: float         # 增长 25%
    margin_score: float         # 毛利率 20%
    market_score: float         # 市场空间 15%
    customer_score: float       # 客户质量 15%
    moat_score: float           # 技术壁垒 15%
    cash_score: float           # 现金 10%
    
    recommendation: str
    risks: List[str]


class GrowthStockScorer:
    """
    Pre-profit成长股评分器
    
    权重配置：
    - 增长：25%（营收增速，最重要）
    - 毛利率：20%（盈利潜力，议价能力）
    - 市场空间：15%（TAM，行业天花板）
    - 客户质量：15%（大客户背书）
    - 技术壁垒：15%（护城河）
    - 现金：10%（烧钱续航能力）
    """
    
    WEIGHTS = {
        'growth': 0.25,
        'margin': 0.20,
        'market': 0.15,
        'customer': 0.15,
        'moat': 0.15,
        'cash': 0.10,
    }
    
    def __init__(self):
        # 科技股数据库（手动维护关键信息）
        self.tech_db = {
            # 新能源
            '300750': {'name': '宁德时代', 'sector': '动力电池', 'margin_trend': '稳定', 'market_space': 90, 'customers': '特斯拉/宝马/奔驰', 'moat': 85},
            '002594': {'name': '比亚迪', 'sector': '新能源汽车', 'margin_trend': '提升', 'market_space': 85, 'customers': '自有品牌', 'moat': 80},
            '601012': {'name': '隆基绿能', 'sector': '光伏', 'margin_trend': '下滑', 'market_space': 70, 'customers': '分散', 'moat': 75},
            
            # 半导体
            '688981': {'name': '中芯国际', 'sector': '晶圆代工', 'margin_trend': '提升', 'market_space': 90, 'customers': '华为/高通', 'moat': 80},
            '603501': {'name': '韦尔股份', 'sector': 'CIS芯片', 'margin_trend': '复苏', 'market_space': 75, 'customers': '小米/OPPO', 'moat': 70},
            '002371': {'name': '北方华创', 'sector': '半导体设备', 'margin_trend': '提升', 'market_space': 85, 'customers': '中芯/长江存储', 'moat': 85},
            '603986': {'name': '兆易创新', 'sector': '存储芯片', 'margin_trend': '波动', 'market_space': 80, 'customers': '华为/小米', 'moat': 75},
            
            # AI算力
            '300308': {'name': '中际旭创', 'sector': '光模块', 'margin_trend': '提升', 'market_space': 90, 'customers': '谷歌/英伟达', 'moat': 80},
            '601138': {'name': '工业富联', 'sector': 'AI服务器', 'margin_trend': '稳定', 'market_space': 85, 'customers': '苹果/英伟达', 'moat': 75},
            
            # 消费电子
            '002475': {'name': '立讯精密', 'sector': '连接器/组装', 'margin_trend': '稳定', 'market_space': 75, 'customers': '苹果', 'moat': 80},
            '002415': {'name': '海康威视', 'sector': '安防', 'margin_trend': '稳定', 'market_space': 70, 'customers': '政府/企业', 'moat': 85},
            
            # AI软件
            '002230': {'name': '科大讯飞', 'sector': 'AI语音', 'margin_trend': '低', 'market_space': 80, 'customers': '政府/教育', 'moat': 70},
        }
    
    def get_financial_data(self, symbol: str) -> Dict:
        """获取财务数据"""
        data = {'revenue_growth': None, 'gross_margin': None, 'cash': None}
        
        try:
            # 获取财务指标
            df = ak.stock_financial_analysis_indicator(symbol=symbol)
            if not df.empty:
                latest = df.iloc[0]
                data['revenue_growth'] = latest.get('营业收入增长率', None)
        except:
            pass
        
        try:
            # 从实时行情获取市值
            df_spot = ak.stock_zh_a_spot_em()
            stock_row = df_spot[df_spot['代码'] == symbol]
            if not stock_row.empty:
                data['market_cap'] = stock_row['总市值'].values[0]
        except:
            pass
        
        return data
    
    def score_growth(self, revenue_growth: float, sector: str) -> Tuple[float, str]:
        """增长评分 (25%)"""
        if revenue_growth is None:
            return 50, "增长数据缺失"
        
        # 科技股的增长标准更高
        if revenue_growth > 100:
            score = 95
            desc = f"爆发增长({revenue_growth:.0f}%)"
        elif revenue_growth > 50:
            score = 85
            desc = f"高增长({revenue_growth:.0f}%)"
        elif revenue_growth > 30:
            score = 75
            desc = f"快增长({revenue_growth:.0f}%)"
        elif revenue_growth > 0:
            score = 55
            desc = f"正增长({revenue_growth:.0f}%)"
        else:
            score = 30
            desc = f"下滑({revenue_growth:.0f}%)"
        
        return score, desc
    
    def score_margin(self, margin_trend: str) -> Tuple[float, str]:
        """毛利率评分 (20%)"""
        trends = {
            '提升': (85, "毛利率提升-规模效应显现"),
            '稳定': (70, "毛利率稳定"),
            '波动': (55, "毛利率波动"),
            '下滑': (40, "毛利率下滑-竞争加剧"),
            '低': (35, "毛利率低-商业模式问题"),
        }
        return trends.get(margin_trend, (50, "毛利率趋势未知"))
    
    def score_market(self, market_space: int) -> Tuple[float, str]:
        """市场空间评分 (15%)"""
        if market_space >= 90:
            return 90, "万亿级市场-天花板极高"
        elif market_space >= 80:
            return 80, "千亿级市场-空间广阔"
        elif market_space >= 70:
            return 65, "百亿级市场-中等空间"
        else:
            return 50, "市场有限"
    
    def score_customer(self, customers: str) -> Tuple[float, str]:
        """客户质量评分 (15%)"""
        if '英伟达' in customers or '谷歌' in customers or '苹果' in customers:
            return 90, f"顶级客户({customers})"
        elif '特斯拉' in customers or '华为' in customers:
            return 85, f"一流客户({customers})"
        elif '中芯' in customers or '小米' in customers:
            return 75, f"优质客户({customers})"
        else:
            return 60, f"普通客户({customers})"
    
    def score_moat(self, moat: int) -> Tuple[float, str]:
        """技术壁垒评分 (15%)"""
        if moat >= 85:
            return 90, "技术护城河深"
        elif moat >= 80:
            return 80, "技术领先"
        elif moat >= 75:
            return 70, "有一定壁垒"
        else:
            return 55, "壁垒一般"
    
    def score_cash(self, market_cap: float) -> Tuple[float, str]:
        """现金评分 (10%) - 简化处理，大市值通常现金充裕"""
        if market_cap > 1000e8:  # 1000亿
            return 80, "现金充裕(大市值)"
        elif market_cap > 500e8:
            return 70, "现金充足"
        elif market_cap > 100e8:
            return 60, "现金一般"
        else:
            return 45, "现金紧张"
    
    def analyze(self, symbol: str) -> GrowthStockScore:
        """成长股综合分析"""
        # 获取基本信息
        info = self.tech_db.get(symbol, {})
        name = info.get('name', symbol)
        
        # 获取财务数据
        fin_data = self.get_financial_data(symbol)
        
        # 六维评分
        growth_score, _ = self.score_growth(fin_data.get('revenue_growth', 0), info.get('sector', ''))
        margin_score, _ = self.score_margin(info.get('margin_trend', '稳定'))
        market_score, _ = self.score_market(info.get('market_space', 70))
        customer_score, _ = self.score_customer(info.get('customers', ''))
        moat_score, _ = self.score_moat(info.get('moat', 70))
        cash_score, _ = self.score_cash(fin_data.get('market_cap', 0))
        
        # 加权总分
        total = (
            growth_score * self.WEIGHTS['growth'] +
            margin_score * self.WEIGHTS['margin'] +
            market_score * self.WEIGHTS['market'] +
            customer_score * self.WEIGHTS['customer'] +
            moat_score * self.WEIGHTS['moat'] +
            cash_score * self.WEIGHTS['cash']
        )
        
        # 投资建议
        if total >= 85:
            rec = "🟢 强烈推荐 - 成长属性极佳"
        elif total >= 75:
            rec = "🟢 推荐 - 成长性良好"
        elif total >= 65:
            rec = "🟡 中性 - 有亮点但需观察"
        else:
            rec = "🔴 谨慎 - 成长逻辑存疑"
        
        # 风险提示
        risks = []
        if growth_score < 60:
            risks.append("增长放缓")
        if margin_score < 50:
            risks.append("盈利能力弱")
        if moat_score < 70:
            risks.append("竞争壁垒低")
        
        return GrowthStockScore(
            symbol=symbol, name=name, total_score=round(total, 1),
            growth_score=growth_score, margin_score=margin_score,
            market_score=market_score, customer_score=customer_score,
            moat_score=moat_score, cash_score=cash_score,
            recommendation=rec, risks=risks
        )
    
    def format_report(self, score: GrowthStockScore) -> str:
        """格式化报告"""
        lines = [
            f"\n{'='*60}",
            f"🚀 {score.name} ({score.symbol}) - 成长股评分",
            f"{'='*60}",
            f"",
            f"🎯 总分: {score.total_score}/100",
            f"💡 建议: {score.recommendation}",
            f"",
            f"📊 六维评分:",
            f"   增长(25%):   {score.growth_score:2.0f}/100",
            f"   毛利率(20%): {score.margin_score:2.0f}/100",
            f"   市场(15%):   {score.market_score:2.0f}/100",
            f"   客户(15%):   {score.customer_score:2.0f}/100",
            f"   壁垒(15%):   {score.moat_score:2.0f}/100",
            f"   现金(10%):   {score.cash_score:2.0f}/100",
            f"",
        ]
        
        if score.risks:
            lines.append(f"⚠️ 风险:")
            for r in score.risks:
                lines.append(f"   • {r}")
            lines.append(f"")
        
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


def main():
    """演示成长股评分"""
    print("=" * 70)
    print("🚀 Pre-profit成长股六维评分")
    print("增长25% | 毛利率20% | 市场15% | 客户15% | 壁垒15% | 现金10%")
    print("=" * 70)
    
    scorer = GrowthStockScorer()
    
    # 测试科技股
    tech_stocks = [
        '300750', '002594', '688981', '002371', '300308',
        '002475', '002415', '601012', '002230'
    ]
    
    results = []
    for symbol in tech_stocks:
        score = scorer.analyze(symbol)
        results.append(score)
        print(scorer.format_report(score))
    
    # 排序输出
    print("=" * 70)
    print("🏆 成长股排行榜")
    print("=" * 70 + "\n")
    
    results.sort(key=lambda x: x.total_score, reverse=True)
    for i, s in enumerate(results, 1):
        emoji = '🟢' if s.total_score >= 75 else '🟡' if s.total_score >= 65 else '⚪'
        print(f"{emoji} {i}. {s.name}: {s.total_score:.1f}分")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
