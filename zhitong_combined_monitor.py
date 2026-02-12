#!/usr/bin/env python3
"""
📊 智通财经 - 全市场+半导体AI合并版
合并全市场快讯和半导体AI板块监控
"""

import subprocess
import re
from datetime import datetime

class ZhitongCombinedMonitor:
    """智通财经合并监控"""
    
    def __init__(self):
        self.url = "https://www.zhitongcaijing.com/content/recommend.html"
        # 科技关键词
        self.tech_keywords = [
            '半导体', '芯片', '中芯', '华虹', 'AI', '人工智能', '算力',
            '英伟达', 'NVIDIA', 'GPU', '大模型', '科技', '字节', '腾讯',
            '阿里', '百度', '小米', '机器人', '存储', '内存', 'HBM',
            '台积电', '三星', '海力士', '长江存储'
        ]
    
    def fetch_news(self) -> list:
        """抓取新闻"""
        all_news = []
        tech_news = []
        
        try:
            # 打开网站
            subprocess.run(
                ['agent-browser', 'open', self.url],
                capture_output=True, text=True, timeout=30
            )
            
            # 等待加载
            subprocess.run(
                ['agent-browser', 'wait', '3000'],
                capture_output=True, text=True, timeout=15
            )
            
            # 获取内容
            result = subprocess.run(
                ['agent-browser', 'snapshot', '-c'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return [], []
            
            # 解析新闻
            content = result.stdout
            lines = content.split('\n')
            
            for line in lines:
                if 'text:' in line:
                    match = re.search(r'text:\s*([^"\n]+)', line)
                    if match:
                        text = match.group(1).strip()
                        if len(text) > 20 and len(text) < 200:
                            # 检查是否科技相关
                            is_tech = any(kw in text for kw in self.tech_keywords)
                            
                            time_match = re.search(r'(\d+分钟前|\d+小时前)', line)
                            time_str = time_match.group(1) if time_match else ""
                            
                            news_item = {'text': text, 'time': time_str}
                            
                            # 科技新闻单独分类
                            if is_tech:
                                tech_news.append(news_item)
                            else:
                                all_news.append(news_item)
            
            return all_news[:5], tech_news[:5]
            
        except Exception as e:
            return [], []
    
    def run(self) -> str:
        """运行监控"""
        lines = [
            "=" * 60,
            f"📊 智通财经市场快讯 | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
        ]
        
        all_news, tech_news = self.fetch_news()
        
        # 科技板块（优先显示）
        if tech_news:
            lines.append("\n🔥 【半导体+AI板块】")
            for i, item in enumerate(tech_news, 1):
                time_str = f" [{item['time']}]" if item['time'] else ""
                lines.append(f"{i}. {item['text']}{time_str}")
        
        # 全市场
        if all_news:
            lines.append("\n📈 【全市场快讯】")
            for i, item in enumerate(all_news, 1):
                time_str = f" [{item['time']}]" if item['time'] else ""
                lines.append(f"{i}. {item['text']}{time_str}")
        
        if not tech_news and not all_news:
            lines.append("\n暂无新闻")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


if __name__ == "__main__":
    monitor = ZhitongCombinedMonitor()
    report = monitor.run()
    print(report)
    
    with open(f"/tmp/zhitong_combined_{datetime.now().strftime('%H%M')}.txt", 'w', encoding='utf-8') as f:
        f.write(report)
