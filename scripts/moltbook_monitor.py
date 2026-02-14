#!/usr/bin/env python3
"""
Moltbook 实时监控脚本
使用 Playwright 抓取热门帖子
"""

from playwright.sync_api import sync_playwright
import json
import os
from datetime import datetime

def fetch_moltbook_hot():
    """抓取 Moltbook 热门帖子"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://www.moltbook.com', wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            # 获取帖子列表
            posts_data = page.evaluate('''() => {
                const posts = [];
                const postElements = document.querySelectorAll('article, [class*="post"], .post-card');
                
                postElements.forEach((el, index) => {
                    if (index < 10) {
                        const titleEl = el.querySelector('h1, h2, h3, .title, [class*="title"]');
                        const authorEl = el.querySelector('[class*="author"], .username');
                        const contentEl = el.querySelector('p, .content, [class*="content"]');
                        const timeEl = el.querySelector('time, [class*="time"], [class*="date"]');
                        const linkEl = el.querySelector('a');
                        
                        posts.push({
                            title: titleEl?.innerText?.substring(0, 100) || 'N/A',
                            author: authorEl?.innerText || 'Unknown',
                            content: contentEl?.innerText?.substring(0, 200) || 'N/A',
                            time: timeEl?.innerText || 'N/A',
                            link: linkEl?.href || 'N/A'
                        });
                    }
                });
                
                return posts;
            }''')
            
            browser.close()
            return posts_data
            
    except Exception as e:
        return [{'error': str(e)}]

def main():
    posts = fetch_moltbook_hot()
    
    if posts and len(posts) > 0 and 'error' not in posts[0]:
        print(f"Moltbook 热门帖子 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
        print("=" * 60)
        for i, post in enumerate(posts[:5], 1):
            print(f"\n{i}. {post['title']}")
            print(f"   作者: {post['author']}")
            print(f"   时间: {post['time']}")
            if post['content'] and post['content'] != 'N/A':
                print(f"   内容: {post['content'][:150]}...")
            if post['link'] and post['link'] != 'N/A':
                print(f"   链接: {post['link']}")
        print("\n" + "=" * 60)
    else:
        error_msg = posts[0].get('error', 'Unknown error') if posts else 'No data'
        print(f"获取失败: {error_msg}")

if __name__ == '__main__':
    main()
