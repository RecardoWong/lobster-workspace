#!/usr/bin/env python3
"""
浏览器自动化测试脚本 - Playwright
"""

from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu']
        )
        print("✅ Playwright 浏览器已启动")
        
        # 创建页面
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # 访问网站
        page.goto('https://agentcoin.site')
        print(f"✅ 已加载页面: {page.title()}")
        
        # 截图
        page.screenshot(path='/tmp/playwright_test.png')
        print("✅ 截图已保存: /tmp/playwright_test.png")
        
        # 获取内容
        content = page.content()[:500]
        print(f"📄 页面内容预览: {content}...")
        
        browser.close()
        print("✅ 浏览器已关闭")

if __name__ == '__main__':
    main()
