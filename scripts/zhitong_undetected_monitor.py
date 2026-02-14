#!/usr/bin/env python3
"""
智通财经监控 - 使用 patchright 绕过 401 错误
无需 API，直接抓取网页
"""
import asyncio
import json
import re
from patchright.async_api import async_playwright
from datetime import datetime

class ZhitongMonitor:
    def __init__(self):
        self.browser = None
        self.page = None
        
    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            executable_path='/opt/chromium/chrome',
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--no-sandbox',
            ]
        )
        self.page = await self.browser.new_page()
        
    async def fetch_news(self):
        """抓取智通财经新闻"""
        url = 'https://www.zhitongcaijing.com/content/recommend.html'
        print(f"正在访问: {url}")
        
        try:
            # 访问页面 - 使用更宽松的等待策略
            await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(5000)
            
            # 截图查看
            await self.page.screenshot(path='/root/.openclaw/workspace/zhitong_screenshot.png')
            print("已截图: zhitong_screenshot.png")
            
            # 获取页面内容
            content = await self.page.content()
            
            # 提取新闻标题
            news_items = []
            
            # 尝试多种选择器
            selectors = [
                '.news-list .item',
                '.article-item',
                '.news-item',
                'a[title]',
            ]
            
            for selector in selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    print(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                    for elem in elements[:10]:
                        try:
                            # 获取标题
                            title = await elem.get_attribute('title')
                            if not title:
                                text = await elem.inner_text()
                                # 清理文本
                                title = re.sub(r'\s+', ' ', text).strip()[:100]
                            
                            # 获取链接
                            href = await elem.get_attribute('href')
                            
                            # 过滤关键词
                            keywords = ['英诺赛科', '半导体', '芯片', 'AI', '算力', '存储', '港股', '美股', '英伟达', 'NVIDIA']
                            if title and any(kw in title for kw in keywords):
                                news_items.append({
                                    'title': title,
                                    'url': href if href else '',
                                    'source': '智通财经',
                                    'time': datetime.now().isoformat()
                                })
                        except:
                            continue
                    
                    if news_items:
                        break
            
            # 如果没找到，尝试从页面文本提取
            if not news_items:
                print("尝试从页面文本提取新闻...")
                text_content = await self.page.evaluate('() => document.body.innerText')
                lines = text_content.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if len(line) > 20 and len(line) < 150:
                        keywords = ['英诺赛科', '半导体', '芯片', 'AI', '算力', '存储', '港股', '美股', '英伟达']
                        if any(kw in line for kw in keywords):
                            news_items.append({
                                'title': line,
                                'url': '',
                                'source': '智通财经',
                                'time': datetime.now().isoformat()
                            })
            
            return news_items[:8]  # 返回前8条
            
        except Exception as e:
            print(f"抓取失败: {e}")
            return []
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def main():
    print(f"📊 智通财经监控启动 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    
    monitor = ZhitongMonitor()
    await monitor.start()
    
    try:
        news = await monitor.fetch_news()
        
        # 保存结果
        result_file = '/root/.openclaw/workspace/reports/zhitong_undetected_latest.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(news, f, ensure_ascii=False, indent=2)
        
        # 输出摘要
        print("\n" + "="*50)
        print(f"📰 共获取 {len(news)} 条新闻")
        print("\n新闻摘要:")
        for i, item in enumerate(news[:5]):
            print(f"\n{i+1}. {item['title'][:60]}...")
        
        print(f"\n💾 结果已保存: {result_file}")
        
    finally:
        await monitor.close()

if __name__ == '__main__':
    asyncio.run(main())
