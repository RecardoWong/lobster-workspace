#!/usr/bin/env python3
"""
Twitter OAuth 1.0a 授权脚本
运行后点击链接，授权，输入 PIN 码即可
"""

import tweepy

# 你的 Consumer Key 和 Secret
CONSUMER_KEY = "Ag90tRYlg9qNEDdNWF96FTiml"
CONSUMER_SECRET = "LUwUKwIL4WCnAaUo7kHxfOwL43NlFACV8GQMJguxEuxmRHijlO"

def main():
    print("="*70)
    print("🔐 Twitter OAuth 1.0a 授权")
    print("="*70)
    print()
    
    # 创建认证处理器
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    
    # 获取授权 URL
    try:
        redirect_url = auth.get_authorization_url()
        print("✅ 授权链接已生成！")
        print()
        print("="*70)
        print(redirect_url)
        print("="*70)
        print()
        print("📋 操作步骤：")
        print("1. 复制上面的链接到浏览器打开")
        print("2. 点击 'Authorize App'")
        print("3. 复制页面显示的 PIN 码（7位数字）")
        print("4. 回到这里，输入 PIN 码")
        print()
        
        # 获取用户输入的 PIN
        verifier = input("请输入 PIN 码: ").strip()
        
        # 获取 Access Token
        print("\n正在获取 Access Token...")
        auth.get_access_token(verifier)
        
        print()
        print("="*70)
        print("✅ 授权成功！")
        print("="*70)
        print()
        print("🔑 Access Token:")
        print(auth.access_token)
        print()
        print("🔑 Access Token Secret:")
        print(auth.access_token_secret)
        print()
        print("="*70)
        print("💾 请复制上面两行发给你的 AI 助手！")
        print("="*70)
        
        # 测试
        print("\n🧪 正在测试...")
        api = tweepy.API(auth)
        user = api.verify_credentials()
        print(f"✅ 测试通过！用户: @{user.screen_name}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("请重试，或联系 AI 助手寻求帮助")

if __name__ == "__main__":
    main()
