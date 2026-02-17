#!/usr/bin/env python3
"""
Twitter Cookie 登录监控
使用 Selenium + Cookie 登录 Twitter，抓取推文
"""

import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display

# Twitter Cookie
AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN', '5da5c73c3286e0c825c5a337eb60ffaf93f2620c')
CT0 = os.getenv('TWITTER_CT0', 'bb867bfa8ae5a410dec9e6537f8aa4f183c43b65c641f9b293a171e8eb8b1b9df359891c89b0e181f4c21bb6e292f422075b77ac3f51a0915fc5e82e2c69c9c5100c14355137082faa36804f10f18ebd')

# 监控账号
MONITOR_ACCOUNTS = {
    'elonmusk': 'Elon Musk',
    'jdhasoptions': 'jdhasoptions',
    'xiaomucrypto': 'xiaomucrypto', 
    'aistocksavvy': 'AI Stock Savvy'
}

def setup_driver():
    """配置 Chrome 浏览器"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 使用系统 Chrome
    chrome_options.binary_location = '/opt/chrome/chrome'
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def login_with_cookie(driver):
    """使用 Cookie 登录 Twitter"""
    try:
        # 先访问 Twitter 域名
        driver.get('https://x.com')
        time.sleep(2)
        
        # 添加 cookie
        driver.add_cookie({
            'name': 'auth_token',
            'value': AUTH_TOKEN,
            'domain': '.x.com',
            'path': '/',
            'secure': True
        })
        
        driver.add_cookie({
            'name': 'ct0',
            'value': CT0,
            'domain': '.x.com', 
            'path': '/',
            'secure': True
        })
        
        # 刷新页面应用 cookie
        driver.get('https://x.com/home')
        time.sleep(3)
        
        # 检查是否登录成功
        if 'home' in driver.current_url or 'Home' in driver.title:
            print('✅ Cookie 登录成功!')
            return True
        else:
            print(f'⚠️  登录状态: {driver.current_url}')
            return False
            
    except Exception as e:
        print(f'❌ 登录失败: {str(e)[:100]}')
        return False

def fetch_tweets(driver, username):
    """抓取用户推文"""
    try:
        url = f'https://x.com/{username}'
        driver.get(url)
        time.sleep(5)  # 等待页面加载
        
        # 查找推文元素
        tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
        
        results = []
        for tweet in tweets[:3]:  # 只取前3条
            try:
                # 提取推文文本
                text_elem = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                text = text_elem.text if text_elem else '无文本'
                
                # 提取时间
                time_elem = tweet.find_element(By.TAG_NAME, 'time')
                time_str = time_elem.get_attribute('datetime') if time_elem else ''
                
                results.append({
                    'text': text[:200],
                    'time': time_str,
                    'fetched_at': datetime.now().isoformat()
                })
            except:
                continue
        
        return results
        
    except Exception as e:
        print(f'❌ 抓取失败 @{username}: {str(e)[:100]}')
        return []

def main():
    """主函数"""
    print(f"🐦 Twitter Cookie 监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 启动虚拟显示器
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    print("✅ 虚拟显示器已启动")
    
    driver = None
    try:
        # 设置浏览器
        print("🚀 启动 Chrome...")
        driver = setup_driver()
        
        # 使用 Cookie 登录
        if login_with_cookie(driver):
            # 抓取每个账号的推文
            for username, name in MONITOR_ACCOUNTS.items():
                print(f"\n📱 抓取 @{username}...")
                tweets = fetch_tweets(driver, username)
                
                if tweets:
                    print(f"✅ 获取到 {len(tweets)} 条推文")
                    for i, tweet in enumerate(tweets, 1):
                        print(f"   {i}. {tweet['text'][:80]}...")
                else:
                    print(f"⚠️  未获取到推文")
                
                time.sleep(2)  # 避免请求过快
        else:
            print('❌ 登录失败，跳过抓取')
            
    except Exception as e:
        print(f'❌ 运行错误: {str(e)[:200]}')
        
    finally:
        if driver:
            driver.quit()
        display.stop()
        print("\n✅ 浏览器已关闭")
        print("=" * 60)

if __name__ == '__main__':
    main()
