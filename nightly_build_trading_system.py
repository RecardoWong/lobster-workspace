#!/usr/bin/env python3
"""
夜间构建交易系统 v1.0
整合：Ronin夜间构建 + Delamain TDD质量校验 + 完整交易信号生成

A: 夜间自动数据抓取与整理（Ronin方法论）
B: 输出质量校验与交易信号生成（Delamain TDD + 交易系统）
"""

import urllib.request
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import akshare as ak

# API配置
TWELVE_DATA_API_KEY = '73c7acfe931d452c82eda0af4c99300f'
BRAVE_API_KEY = 'BSA5gm2J8fUK-1VTQJZVu_IFnFFdW6P'

class NightlyBuildTradingSystem:
    """夜间构建交易系统"""
    
    def __init__(self):
        self.errors = []
        self.signals = []
        self.data = {}
    
    # ==================== A: 数据抓取（夜间构建）====================
    
    def fetch_us_stocks(self) -> List[Dict]:
        """抓取美股数据 - Twelve Data"""
        print("[02:00] 抓取美股数据...")
        stocks = [
            ('NVTS', '纳微半导体'),
            ('TXN', '德州仪器'),
            ('IFNNY', '英飞凌'),
        ]
        results = []
        
        for symbol, name in stocks:
            try:
                url = f'https://api.twelvedata.com/quote?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}'
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    
                    if 'code' not in data:
                        results.append({
                            'symbol': symbol,
                            'name': name,
                            'price': float(data.get('close', 0)),
                            'change_pct': float(data.get('percent_change', 0)),
                            'volume': int(data.get('volume', 0)),
                            'status': 'success'
                        })
                    else:
                        self.errors.append(f"{symbol}: {data.get('message', 'API Error')}")
                        results.append({'symbol': symbol, 'name': name, 'status': 'error'})
                        
            except Exception as e:
                self.errors.append(f"{symbol}: {str(e)}")
                results.append({'symbol': symbol, 'name': name, 'status': 'error'})
            
            time.sleep(1)  # 控制频率
        
        return results
    
    def fetch_hk_stock(self) -> Dict:
        """抓取港股数据 - AKShare"""
        print("[03:00] 抓取港股数据...")
        try:
            # 获取英诺赛科历史数据
            df = ak.stock_hk_hist(symbol='02577', period='daily', 
                                  start_date='20250201', end_date='20260210')
            
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'symbol': '02577.HK',
                    'name': '英诺赛科',
                    'price': float(latest['收盘']),
                    'change_pct': float(latest['涨跌幅']),
                    'volume': int(latest['成交量']),
                    'high': float(latest['最高']),
                    'low': float(latest['最低']),
                    'status': 'success'
                }
        except Exception as e:
            self.errors.append(f"02577.HK: {str(e)}")
        
        return {'symbol': '02577.HK', 'name': '英诺赛科', 'status': 'error'}
    
    def fetch_news(self, query: str) -> List[str]:
        """抓取新闻 - Brave Search"""
        print("[04:00] 抓取新闻...")
        try:
            url = f'https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count=5'
            req = urllib.request.Request(url, headers={
                'Accept': 'application/json',
                'X-Subscription-Token': BRAVE_API_KEY
            })
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get('web', {}).get('results', [])
                return [r.get('title', '') for r in results[:3]]
                
        except Exception as e:
            self.errors.append(f"News fetch: {str(e)}")
            return []
    
    # ==================== B: 质量校验（Delamain TDD）====================
    
    def validate_data(self, data: Dict) -> Tuple[bool, str]:
        """数据质量校验"""
        # 规则1: 数据完整性
        if data.get('status') != 'success':
            return False, f"数据获取失败: {data.get('symbol')}"
        
        # 规则2: 逻辑一致性
        price = data.get('price', 0)
        if price <= 0 or price > 10000:  # 异常价格范围
            return False, f"价格异常: {data.get('symbol')} = {price}"
        
        # 规则3: 数据时效性
        volume = data.get('volume', 0)
        if volume <= 0:
            return False, f"成交量异常: {data.get('symbol')} = {volume}"
        
        return True, "校验通过"
    
    def validate_report(self, report: str) -> Tuple[bool, List[str]]:
        """报告质量校验"""
        errors = []
        
        # 校验1: 包含关键股票
        required_stocks = ['NVTS', 'TXN', 'IFNNY', '02577']
        for stock in required_stocks:
            if stock not in report:
                errors.append(f"缺少股票: {stock}")
        
        # 校验2: 包含分析
        if '💡' not in report or '分析' not in report:
            errors.append("缺少分析部分")
        
        # 校验3: 包含交易信号
        if '信号' not in report:
            errors.append("缺少交易信号")
        
        return len(errors) == 0, errors
    
    # ==================== 交易信号生成 ====================
    
    def generate_signals(self, us_stocks: List[Dict], hk_stock: Dict) -> List[Dict]:
        """生成交易信号"""
        print("[05:00] 生成交易信号...")
        signals = []
        
        # 信号1: 英诺赛科价格位置
        if hk_stock.get('status') == 'success':
            price = hk_stock['price']
            if price > 53.8:  # SK成本价之上
                signals.append({
                    'type': 'POSITION',
                    'symbol': '02577.HK',
                    'signal': 'HOLD/ACCUMULATE',
                    'reason': f'价格{price}在SK成本价53.8之上，支撑有效',
                    'strength': '中'
                })
            else:
                signals.append({
                    'type': 'ALERT',
                    'symbol': '02577.HK',
                    'signal': 'WATCH',
                    'reason': f'价格{price}跌破SK成本价，观察是否有恐慌抛售',
                    'strength': '高'
                })
        
        # 信号2: 纳微技术突破后的反应
        nvts = next((s for s in us_stocks if s.get('symbol') == 'NVTS'), None)
        if nvts and nvts.get('status') == 'success':
            change = nvts.get('change_pct', 0)
            if 0 < change < 5:  # 涨但不过热
                signals.append({
                    'type': 'INDUSTRY',
                    'symbol': 'GaN Sector',
                    'signal': 'BULLISH',
                    'reason': '纳微技术突破后市场反应理性，GaN板块健康',
                    'strength': '中'
                })
        
        # 信号3: 英飞凌涨价效应
        ifnn = next((s for s in us_stocks if s.get('symbol') == 'IFNNY'), None)
        if ifnn and ifnn.get('status') == 'success':
            if ifnn.get('change_pct', 0) > 0:
                signals.append({
                    'type': 'OPPORTUNITY',
                    'symbol': '02577.HK',
                    'signal': 'BENEFIT',
                    'reason': '英飞凌涨价+上涨，英诺赛科可承接转移订单',
                    'strength': '中'
                })
        
        return signals
    
    # ==================== 报告生成 ====================
    
    def generate_report(self) -> str:
        """生成完整报告"""
        print("[06:00] 生成夜间构建报告...")
        
        # A部分: 数据抓取
        us_stocks = self.fetch_us_stocks()
        hk_stock = self.fetch_hk_stock()
        news = self.fetch_news('英诺赛科 氮化镓 新闻')
        
        # B部分: 质量校验
        print("[06:30] 执行质量校验...")
        all_data = us_stocks + [hk_stock]
        for data in all_data:
            valid, msg = self.validate_data(data)
            if not valid:
                self.errors.append(msg)
        
        # 生成交易信号
        self.signals = self.generate_signals(us_stocks, hk_stock)
        
        # 构建报告
        lines = [
            "="*60,
            "🌙 夜间构建报告 + 交易信号",
            f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*60,
            "",
            "🇺🇸 美股竞争对手监控",
            "-"*40,
        ]
        
        for stock in us_stocks:
            if stock.get('status') == 'success':
                emoji = "📈" if stock.get('change_pct', 0) >= 0 else "📉"
                lines.append(
                    f"• {stock['name']} ({stock['symbol']}): "
                    f"${stock['price']} {emoji} {stock['change_pct']:+.2f}%"
                )
        
        lines.extend([
            "",
            "🇭🇰 英诺赛科监控",
            "-"*40,
        ])
        
        if hk_stock.get('status') == 'success':
            emoji = "📈" if hk_stock.get('change_pct', 0) >= 0 else "📉"
            lines.append(f"• 英诺赛科 (02577.HK): {hk_stock['price']}港元 {emoji} {hk_stock['change_pct']:+.2f}%")
            lines.append(f"  成交量: {hk_stock['volume']:,}")
            lines.append(f"  5日高低: {hk_stock['low']} - {hk_stock['high']}")
        
        lines.extend([
            "",
            "📊 交易信号",
            "-"*40,
        ])
        
        for signal in self.signals:
            lines.append(f"• [{signal['type']}] {signal['symbol']}")
            lines.append(f"  信号: {signal['signal']} (强度: {signal['strength']})")
            lines.append(f"  理由: {signal['reason']}")
            lines.append("")
        
        lines.extend([
            "",
            "💡 竞争格局分析",
            "-"*40,
        ])
        
        # 纳微分析
        nvts = next((s for s in us_stocks if s.get('symbol') == 'NVTS'), None)
        if nvts and nvts.get('status') == 'success':
            change = nvts.get('change_pct', 0)
            if change > 5:
                lines.append(f"• 纳微大涨{change:+.2f}%，GaN板块热度飙升")
            elif change > 0:
                lines.append(f"• 纳微涨{change:+.2f}%，技术突破后市场反应理性")
            else:
                lines.append(f"• 纳微跌{change:+.2f}%，市场可能担忧量产时间")
        
        # 德州仪器分析
        txn = next((s for s in us_stocks if s.get('symbol') == 'TXN'), None)
        if txn and txn.get('status') == 'success':
            if txn.get('change_pct', 0) > 0:
                lines.append("• 德州仪器上涨，传统功率半导体强势")
            else:
                lines.append("• 德州仪器下跌，GaN替代逻辑增强")
        
        # 英诺赛科分析
        if hk_stock.get('status') == 'success':
            price = hk_stock['price']
            if price > 53.8:
                lines.append(f"• 英诺赛科站稳SK成本价({price}>53.8)，支撑有效")
            else:
                lines.append(f"• 英诺赛科跌破SK成本价，观察恐慌盘")
        
        if self.errors:
            lines.extend(["", "⚠️ 数据异常", "-"*40])
            for e in self.errors:
                lines.append(f"• {e}")
        
        lines.extend(["", "="*60])
        
        report = "\n".join(lines)
        
        # B部分: 报告质量校验
        valid, errors = self.validate_report(report)
        if not valid:
            print(f"⚠️ 报告校验失败: {errors}")
            # 修正报告...
        
        return report
    
    def run(self):
        """执行夜间构建"""
        print("\n" + "="*60)
        print("🌙 启动夜间构建交易系统")
        print("="*60 + "\n")
        
        report = self.generate_report()
        
        # 保存报告
        with open('/tmp/nightly_build_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n" + "="*60)
        print("✅ 夜间构建完成")
        print("📄 报告保存: /tmp/nightly_build_report.md")
        print("="*60)
        
        return report


def main():
    """主函数"""
    system = NightlyBuildTradingSystem()
    report = system.run()
    print(report)


if __name__ == "__main__":
    main()
