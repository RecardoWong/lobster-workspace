#!/usr/bin/env python3
"""
🦞 英诺赛科供应商监控脚本 - Monty 异常检测版
监控上游公司股价和动态，自动识别异常波动
"""

import json
import urllib.request
from datetime import datetime
import os
from monty_analyzer import detect_anomalies, MontyAnalyzer

class InnoscienceSupplierMonitor:
    """英诺赛科供应商监控"""
    
    def __init__(self):
        self.suppliers = {
            'a_share': {
                '600703': {'name': '三安光电', 'business': 'GaN衬底/外延'},
                '002371': {'name': '北方华创', 'business': 'MOCVD设备'},
                '688012': {'name': '中微公司', 'business': 'MOCVD设备'},
                '688396': {'name': '华润微', 'business': '功率半导体'},
                '600460': {'name': '士兰微', 'business': 'Si基GaN'},
                '300346': {'name': '南大光电', 'business': '特气MO源'},
                '300487': {'name': '蓝晓科技', 'business': '离子交换树脂(镓提取)'},
                '601600': {'name': '中国铝业', 'business': '铝材+金属镓(GaN原材料)'},
            },
            'hk': {
                '0981': {'name': '中芯国际', 'business': '晶圆代工'},
                '1347': {'name': '华虹半导体', 'business': '特色工艺代工'},
                '02600': {'name': '中国铝业(H)', 'business': '铝材+金属镓'},
            },
            'us': {
                'AMAT': {'name': 'Applied Materials', 'business': 'MOCVD设备'},
                'LRCX': {'name': 'Lam Research', 'business': '刻蚀设备'},
            }
        }
        self.report_file = "/tmp/supplier_report_innoscience.txt"
    
    def get_a_share_price(self, code):
        """获取A股价格（使用AKShare）"""
        try:
            import akshare as ak
            stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
            stock_info = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == code]
            if not stock_info.empty:
                return {
                    'price': stock_info['最新价'].values[0],
                    'change': stock_info['涨跌幅'].values[0],
                    'volume': stock_info['成交额'].values[0]
                }
        except Exception as e:
            return {'error': str(e)}
        return None
    
    def get_hk_price(self, code):
        """获取港股价格（使用AKShare）"""
        try:
            import akshare as ak
            # 港股实时行情
            stock_hk_ggt_components_em_df = ak.stock_hk_ggt_components_em()
            stock_info = stock_hk_ggt_components_em_df[stock_hk_ggt_components_em_df['代码'] == code]
            if not stock_info.empty:
                return {
                    'price': stock_info['最新价'].values[0],
                    'change': stock_info['涨跌幅'].values[0],
                }
        except Exception as e:
            return {'error': str(e)}
        return None
    
    def monty_analyze_suppliers(self) -> dict:
        """使用 Monty 分析供应商异常波动"""
        # 收集股价变动数据
        price_changes = []
        
        for code, info in self.suppliers['a_share'].items():
            price_data = self.get_a_share_price(code)
            if price_data and 'error' not in price_data:
                price_changes.append({
                    'name': info['name'],
                    'change_pct': price_data.get('change', 0) / 100  # 转为小数
                })
        
        if not price_changes:
            return {}
        
        # 调用 Monty 异常检测
        result = detect_anomalies(price_changes, threshold=0.03)  # 3%阈值
        return result.get('result', {}) if result.get('success') else {}
    
    def generate_report(self):
        """生成供应商监控报告"""
        now = datetime.now()
        
        lines = [
            "=" * 60,
            "🏭 英诺赛科供应商监控报告",
            f"📅 {now.strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            ""
        ]
        
        # Monty 异常检测
        monty_result = self.monty_analyze_suppliers()
        if monty_result and monty_result.get('anomalies'):
            lines.append("🤖 Monty AI 异常检测")
            lines.append("-" * 60)
            lines.append(f"⚠️ 发现 {monty_result.get('anomaly_count', 0)} 家异常波动供应商:")
            for anomaly in monty_result.get('anomalies', []):
                emoji = "📈" if anomaly['change_pct'] > 0 else "📉"
                lines.append(f"   {emoji} {anomaly['name']}: {anomaly['direction']} ({anomaly['change_pct']*100:+.2f}%)")
            lines.append("")
        
        # A股供应商
        lines.append("🇨🇳 A股核心供应商")
        lines.append("-" * 60)
        
        for code, info in self.suppliers['a_share'].items():
            price_data = self.get_a_share_price(code)
            if price_data and 'error' not in price_data:
                change_emoji = "📈" if price_data.get('change', 0) > 0 else "📉"
                lines.append(f"{change_emoji} {info['name']} ({code})")
                lines.append(f"   业务: {info['business']}")
                lines.append(f"   价格: ¥{price_data.get('price', 'N/A')} ({price_data.get('change', 0):+.2f}%)")
                lines.append("")
            else:
                lines.append(f"⏳ {info['name']} ({code}) - 数据获取中")
                lines.append("")
        
        # 未上市供应商（特殊显示）
        lines.append("🏭 未上市核心供应商")
        lines.append("-" * 60)
        lines.append(f"🔥 三门峡铝业 (未上市)")
        lines.append(f"   业务: 粗镓(全国#2,>20%)-东方希望/锦江集团")
        lines.append(f"   地位: 隐形冠军，英诺镓供应链源头")
        lines.append(f"   监控: 产能扩张、关联方动态")
        lines.append("")
        lines.append(f"💎 先导稀材 (未上市)")
        lines.append(f"   业务: 金属镓(150吨产能，一期80吨)")
        lines.append(f"   地位: 英诺供应商，与九龙万博合作")
        lines.append(f"   监控: 产能释放、出口管制影响")
        lines.append("")
        
        # 港股供应商
        lines.append("🇭🇰 港股供应商")
        lines.append("-" * 60)
        
        for code, info in self.suppliers['hk'].items():
            price_data = self.get_hk_price(code)
            if price_data and 'error' not in price_data:
                change_emoji = "📈" if price_data.get('change', 0) > 0 else "📉"
                lines.append(f"{change_emoji} {info['name']} ({code})")
                lines.append(f"   业务: {info['business']}")
                lines.append(f"   价格: HK${price_data.get('price', 'N/A')} ({price_data.get('change', 0):+.2f}%)")
                lines.append("")
            else:
                lines.append(f"⏳ {info['name']} ({code}) - 数据获取中")
                lines.append("")
        
        # 镓供应链重点提示
        lines.append("🔑 镓供应链核心（GaN原材料）")
        lines.append("-" * 60)
        lines.append("三门峡铝业(粗镓 #2, >20%) → 精炼厂 → 中国铝业(金属镓 #1, 23.5%) → 英诺赛科")
        lines.append("⚠️ 两家合计控制全国 40%+ 镓产能！")
        lines.append("")
        lines.append("🔬 技术层：蓝晓科技(300487) = 镓提取技术龙头")
        lines.append("   离子交换树脂吸附效率: 60-70% → 90%+ (2025-2026突破)")
        lines.append("   高选择性、抗污染大孔树脂 = 产量+20-30%")
        lines.append("   技术突破 → 英诺原材料供应更安全！")
        lines.append("")
        lines.append("🏭 其他关键供应商")
        lines.append("   先导稀材(未上市) = 金属镓供应商(150吨产能)")
        lines.append("   南大光电(300346) = MO源/三甲基镓(GaN外延核心)")
        lines.append("")
        
        # 监控要点
        lines.append("🔍 今日监控要点")
        lines.append("-" * 60)
        lines.append("□ 北方华创 - 设备订单/交付进度")
        lines.append("□ 三安光电 - 外延片价格/产能")
        lines.append("□ 中国铝业 - 铝价/金属镓产量/订单")
        lines.append("□ 三门峡铝业 - 粗镓产能/东方希望/锦江动态")
        lines.append("□ 蓝晓科技 - **吸附效率突破/镓提取技术升级**")
        lines.append("□ 先导稀材 - **产能释放/出口管制动态**")
        lines.append("□ 南大光电 - MO源供应/价格")
        lines.append("□ 中芯/华虹 - GaN代工进展")
        lines.append("□ 出口管制 - **2026年11月关键节点/政策变化**")
        lines.append("□ 行业动态 - 8英寸产线建设")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append("🦞 自主监控 by 龙虾Agent")
        
        return "\n".join(lines)
    
    def save_and_print(self):
        """保存并打印报告"""
        report = self.generate_report()
        
        # 保存
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n💾 报告已保存: {self.report_file}")
        return report


def main():
    """主函数"""
    monitor = InnoscienceSupplierMonitor()
    monitor.save_and_print()


if __name__ == "__main__":
    main()
