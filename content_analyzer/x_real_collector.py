#!/usr/bin/env python3
"""
X平台真实采集器 (Playwright + Cookie)
测试Cookie并采集真实数据
"""

import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict

class XRealCollector:
    """X平台真实采集器"""
    
    def __init__(self):
        self.cookie_file = "/root/.openclaw/workspace/content_analyzer/.twitter_cookies.json"
        self.cookies = self._load_cookies()
        
    def _load_cookies(self) -> List[Dict]:
        """加载cookies"""
        with open(self.cookie_file, 'r') as f:
            return json.load(f)
    
    async def test_cookie(self) -> bool:
        """测试cookie是否有效"""
        print("🔍 测试Cookie有效性...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # 注入cookies
            await context.add_cookies(self.cookies)
            
            # 访问X主页
            page = await context.new_page()
            await page.goto("https://twitter.com/home", timeout=30000)
            
            # 检查是否登录成功
            await asyncio.sleep(3)
            
            # 检查页面元素判断登录状态
            try:
                # 如果找到时间线元素，说明登录成功
                await page.wait_for_selector("[data-testid='primaryColumn']", timeout=5000)
                print("✅ Cookie有效！登录成功")
                await browser.close()
                return True
            except:
                # 检查是否有登录按钮
                login_btn = await page.query_selector("[data-testid='loginButton']")
                if login_btn:
                    print("❌ Cookie已过期，需要重新获取")
                else:
                    print("⚠️ 状态未知，请检查")
                await browser.close()
                return False
    
    async def collect_timeline(self, max_posts: int = 50) -> List[Dict]:
        """采集时间线"""
        print(f"🕷️ 开始采集时间线 (最多{max_posts}条)...")
        
        posts = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            await context.add_cookies(self.cookies)
            
            page = await context.new_page()
            await page.goto("https://twitter.com/home", timeout=30000)
            
            # 等待页面加载
            await asyncio.sleep(5)
            
            # 滚动采集
            scroll_count = 0
            last_height = 0
            
            while len(posts) < max_posts and scroll_count < 20:
                # 提取当前可见的帖子
                articles = await page.query_selector_all("article[data-testid='tweet']")
                
                for article in articles:
                    if len(posts) >= max_posts:
                        break
                    
                    try:
                        post = await self._extract_post_data(article)
                        if post and post not in posts:
                            posts.append(post)
                            print(f"  ✓ 采集: @{post.get('author', 'unknown')}")
                    except Exception as e:
                        print(f"  ✗ 提取失败: {e}")
                
                # 滚动
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(2)
                
                # 检查是否到底
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    print("  📄 已到达底部")
                    break
                last_height = new_height
                scroll_count += 1
            
            await browser.close()
        
        print(f"\n✅ 采集完成: {len(posts)} 条帖子")
        return posts
    
    async def _extract_post_data(self, article) -> Dict:
        """提取帖子数据"""
        try:
            # 作者
            author_elem = await article.query_selector("[data-testid='User-Name'] a")
            author = await author_elem.get_attribute("href") if author_elem else ""
            author = author.replace("/", "") if author else "unknown"
            
            # 内容
            content_elem = await article.query_selector("[data-testid='tweetText']")
            content = await content_elem.inner_text() if content_elem else ""
            
            # 互动数据
            likes = await self._get_metric(article, "like")
            retweets = await self._get_metric(article, "retweet")
            replies = await self._get_metric(article, "reply")
            
            return {
                'author': author,
                'content': content,
                'likes': likes,
                'retweets': retweets,
                'replies': replies,
                'collected_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"提取错误: {e}")
            return None
    
    async def _get_metric(self, article, metric_type: str) -> int:
        """获取互动数据"""
        try:
            selector = f"[data-testid='{metric_type}']"
            elem = await article.query_selector(selector)
            if elem:
                text = await elem.inner_text()
                # 解析数字 (如 "1.2K" -> 1200)
                return self._parse_number(text)
            return 0
        except:
            return 0
    
    def _parse_number(self, text: str) -> int:
        """解析数字"""
        text = text.replace(",", "").strip()
        try:
            if "K" in text:
                return int(float(text.replace("K", "")) * 1000)
            elif "M" in text:
                return int(float(text.replace("M", "")) * 1000000)
            else:
                return int(text) if text.isdigit() else 0
        except:
            return 0
    
    def save_posts(self, posts: List[Dict]):
        """保存采集的帖子"""
        output_file = f"/root/.openclaw/workspace/content_analyzer/data/real_posts_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存: {output_file}")

async def main():
    """主函数"""
    collector = XRealCollector()
    
    print("="*70)
    print("🕷️ X平台真实采集器")
    print("="*70)
    
    # 1. 测试Cookie
    is_valid = await collector.test_cookie()
    
    if not is_valid:
        print("\n❌ Cookie无效，请重新获取")
        return
    
    # 2. 采集数据
    print("\n" + "="*70)
    posts = await collector.collect_timeline(max_posts=30)
    
    # 3. 保存
    if posts:
        collector.save_posts(posts)
        
        # 显示摘要
        print("\n📊 采集摘要:")
        print(f"   总数: {len(posts)}")
        print(f"   平均点赞: {sum(p.get('likes', 0) for p in posts) // len(posts)}")
        print(f"   平均转发: {sum(p.get('retweets', 0) for p in posts) // len(posts)}")
    
    print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
