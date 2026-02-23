#!/usr/bin/env python3
"""
巨潮资讯网自动登录脚本
使用 Playwright 模拟浏览器登录
"""

from playwright.sync_api import sync_playwright
import time

def login_cninfo(username: str, password: str):
    """
    自动登录巨潮资讯网
    
    Args:
        username: 用户名/手机号
        password: 密码
        
    Returns:
        Cookie 字符串
    """
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("🌐 访问登录页面...")
            page.goto("https://uc.cninfo.com.cn/login")
            
            # 等待页面加载
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            
            # 截图查看当前状态
            page.screenshot(path="/tmp/cninfo_login_1.png")
            print("📸 已截图: /tmp/cninfo_login_1.png")
            
            # 检查是否有验证码
            print("🔍 检查页面元素...")
            
            # 查找用户名输入框
            username_selectors = [
                'input[name="username"]',
                'input[name="login"]',
                'input[placeholder*="用户名"]',
                'input[placeholder*="手机"]',
                '#username',
                '#login'
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        username_input = selector
                        print(f"   ✅ 找到用户名输入框: {selector}")
                        break
                except:
                    continue
            
            if not username_input:
                print("   ❌ 未找到用户名输入框")
                # 输出页面HTML帮助调试
                html = page.content()
                with open("/tmp/cninfo_page.html", "w") as f:
                    f.write(html[:5000])
                print("   📝 已保存页面HTML: /tmp/cninfo_page.html")
                return None
            
            # 输入用户名
            print("📝 输入用户名...")
            page.fill(username_input, username)
            
            # 查找密码输入框
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '#password'
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        password_input = selector
                        print(f"   ✅ 找到密码输入框: {selector}")
                        break
                except:
                    continue
            
            if password_input:
                print("📝 输入密码...")
                page.fill(password_input, password)
            else:
                print("   ⚠️ 未找到密码输入框，可能在下一步")
            
            # 检查验证码
            print("🔍 检查验证码...")
            captcha_selectors = [
                'img[alt*="验证码"]',
                '.captcha',
                '#captcha',
                'img[src*="captcha"]'
            ]
            
            has_captcha = False
            for selector in captcha_selectors:
                try:
                    if page.locator(selector).count() > 0 and page.locator(selector).is_visible():
                        has_captcha = True
                        print(f"   ⚠️ 发现验证码元素: {selector}")
                        page.screenshot(path="/tmp/cninfo_captcha.png")
                        print("   📸 验证码截图: /tmp/cninfo_captcha.png")
                        break
                except:
                    continue
            
            if has_captcha:
                print("\n⚠️ 需要验证码！")
                print("请告诉我验证码图片中的文字")
                return None
            
            # 点击登录按钮
            print("🖱️ 点击登录...")
            login_button_selectors = [
                'button[type="submit"]',
                '.login-btn',
                '#login-btn',
                'button:has-text("登录")'
            ]
            
            for selector in login_button_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector)
                        print(f"   ✅ 点击登录按钮: {selector}")
                        break
                except:
                    continue
            
            # 等待登录完成
            time.sleep(3)
            
            # 检查是否登录成功
            if "login" not in page.url and "uc.cninfo" not in page.url:
                print("✅ 登录成功!")
                print(f"   当前URL: {page.url}")
                
                # 获取 Cookie
                cookies = context.cookies()
                cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                
                print("\n🍪 Cookie 获取成功!")
                print(f"   长度: {len(cookie_str)} 字符")
                
                return cookie_str
            else:
                print("❌ 登录可能失败")
                page.screenshot(path="/tmp/cninfo_login_failed.png")
                print("   📸 失败截图: /tmp/cninfo_login_failed.png")
                return None
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            page.screenshot(path="/tmp/cninfo_error.png")
            return None
            
        finally:
            browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🔐 巨潮资讯网自动登录")
    print("=" * 60)
    
    # 这里需要填入你的账号密码
    USERNAME = "your_username"  # 替换为你的用户名
    PASSWORD = "your_password"  # 替换为你的密码
    
    if USERNAME == "your_username":
        print("\n⚠️ 请先编辑脚本，填入你的账号密码!")
        print("修改第 156-157 行的 USERNAME 和 PASSWORD")
        exit(1)
    
    cookie = login_cninfo(USERNAME, PASSWORD)
    
    if cookie:
        print("\n" + "=" * 60)
        print("✅ 登录成功!")
        print("\n请保存以下 Cookie 到 .env 文件:")
        print(f"\nCNINFO_COOKIE={cookie[:200]}...")
        print("\n" + "=" * 60)
    else:
        print("\n❌ 登录失败")
