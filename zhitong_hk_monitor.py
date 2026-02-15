#!/usr/bin/env python3
"""
📊 智通财经港股监控脚本
自动抓取智通财经港股实时数据
"""

import subprocess
import re
from datetime import datetime

class ZhitongHKMonitor:
    """智通财经港股监控"""
    
    def __init__(self):
        self.url = "https://www.zhitongcaijing.com/"
    
    def fetch_data(self) -> str:
        """用Agent Browser抓取数据"""
        try:
            # 打开网站
            subprocess.run(
                ['agent-browser', 'open', self.url],
                capture_output=True, text=True, timeout=30
            )
            
            # 获取港股页面
            subprocess.run(
                ['agent-browser', 'click', '@e39'],  # 点击港股栏目
                capture_output=True, text=True, timeout=15
            )
            
            # 等待加载
            subprocess.run(
                ['agent-browser', 'wait', '2000'],
                capture_output=True, text=True, timeout=10
            )
            
            # 获取页面快照
            result = subprocess.run(
                ['agent-browser', 'snapshot', '-c'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            return ""
        except Exception as e:
            return f"抓取失败: {e}"
    
    def parse_news(self, content: str) -> list:
        """解析新闻列表"""
        news_list = []
        
        # 查找新闻链接
        lines = content.split('\n')
        for line in lines:
            if 'link' in line and 'content/detail' in line:
                # 提取标题
                match = re.search(r'text:\s*"([^"]+)"', line)
                if match:
                    title = match.group(1)
                    if len(title) > 10:  # 过滤短文本
                        news_list.append(title)
        
        return news_list[:10]  # 取前10条
    
    def run(self) -> str:
        """运行监控"""
        lines = [
            "=" * 60,
            f"📊 智通财经港股快讯 | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
        ]
        
        content = self.fetch_data()
        
        if content.startswith("抓取失败"):
            lines.append(content)
        else:
            news = self.parse_news(content)
            
            if news:
                lines.append("\n🔥 最新快讯:")
                for i, title in enumerate(news[:5], 1):
                    lines.append(f"\n{i}. {title}")
            else:
                lines.append("\n暂无数据")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


if __name__ == "__main__":
    monitor = ZhitongHKMonitor()
    report = monitor.run()
    print(report)
    
    # 保存到文件
    with open(f"/tmp/zhitong_hk_{datetime.now().strftime('%H%M')}.txt", 'w', encoding='utf-8') as f:
        f.write(report)
