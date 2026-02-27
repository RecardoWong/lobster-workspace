#!/usr/bin/env python3
"""
浏览器自动化测试脚本 - Selenium + Xvfb
"""

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# 启动虚拟显示器
display = Display(visible=0, size=(1920, 1080))
display.start()
print("✅ Xvfb 虚拟显示器已启动")

try:
    # 配置 Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 使用系统安装的 Chrome
    chrome_options.binary_location = '/opt/chrome/chrome'
    
    # 启动浏览器
    driver = webdriver.Chrome(options=chrome_options)
    print("✅ Chrome 浏览器已启动")
    
    # 访问网站
    driver.get('https://agentcoin.site')
    print(f"✅ 已加载页面: {driver.title}")
    
    # 截图
    driver.save_screenshot('/tmp/selenium_test.png')
    print("✅ 截图已保存: /tmp/selenium_test.png")
    
    # 获取页面源码
    html = driver.page_source[:500]
    print(f"📄 页面源码预览: {html}...")
    
    driver.quit()
    print("✅ 浏览器已关闭")
    
finally:
    display.stop()
    print("✅ 虚拟显示器已停止")
