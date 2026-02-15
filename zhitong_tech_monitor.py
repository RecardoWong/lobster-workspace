#!/usr/bin/env python3
"""
📊 智通财经 - 半导体+AI板块监控
专门抓取半导体、人工智能相关新闻
"""

import subprocess
import re
from datetime import datetime

class ZhitongTechMonitor:
    """智通财经科技板块监控"""
    
    def __init__(self):
        self.url = "https://www.zhitongcaijing.com/content/recommend.html"
        # 关键词：半导体+AI
        self.keywords = [
            '半导体', '芯片', '中芯', '华虹', 'AI', '人工智能', '算力', 
            '英伟达', 'NVIDIA', 'GPU', '大模型', 'ChatGPT', 'OpenAI',
            '科技', '字节', '腾讯', '阿里', '百度', '小米', '机器人',
            '存储', '内存', 'HBM', '先进封装', '光刻', '刻蚀',
            '台积电', '三星', '海力士', '美光', '长江存储', '长鑫存储'
        ]
    
    def fetch_news(self) -> list:
        """抓取新闻"""
        news_list = []
        
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
                return []
            
            # 解析新闻
            content = result.stdout
            lines = content.split('\n')
            
            for line in lines:
                if 'text:' in line:
                    # 提取文本
                    match = re.search(r'text:\s*([^"\n]+)', line)
                    if match:
                        text = match.group(1).strip()
                        # 检查是否包含关键词
                        if any(kw in text for kw in self.keywords) and len(text) > 15:
                            # 提取时间（如果有）
                            time_match = re.search(r'(\d+分钟前|\d+小时前|\d+天前)', line)
                            time_str = time_match.group(1) if time_match else ""
                            news_list.append({
                                'text': text,
                                'time': time_str
                            })
            
            return news_list[:8]  # 取前8条
            
        except Exception as e:
            return []
    
    def run(self) -> str:
        """运行监控"""
        lines = [
            "=" * 60,
            f"📊 半导体+AI板块快讯 | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
        ]
        
        news = self.fetch_news()
        
        if not news:
            lines.append("\n暂无相关新闻")
        else:
            lines.append(f"\n🔥 找到 {len(news)} 条相关新闻：\n")
            for i, item in enumerate(news, 1):
                time_str = f" [{item['time']}]" if item['time'] else ""
                lines.append(f"{i}. {item['text']}{time_str}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


if __name__ == "__main__":
    monitor = ZhitongTechMonitor()
    report = monitor.run()
    print(report)
    
    # 保存
    with open(f"/tmp/zhitong_tech_{datetime.now().strftime('%H%M')}.txt", 'w', encoding='utf-8') as f:
        f.write(report)
