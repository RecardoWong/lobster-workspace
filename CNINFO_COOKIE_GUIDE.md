# 巨潮资讯网 Cookie 配置指南

## 注册后操作步骤

### 1. 登录巨潮资讯网
- 访问: https://www.cninfo.com.cn/
- 点击右上角"登录"
- 输入账号密码登录

### 2. 获取 Cookie
登录后，按 F12 打开开发者工具:

```
1. 按 F12 打开开发者工具
2. 点击 Network (网络) 标签
3. 刷新页面
4. 找到任意请求，点击 Headers
5. 复制 Request Headers 中的 Cookie 字段
```

### 3. 保存 Cookie
将获取的 Cookie 保存到 `.env` 文件:

```bash
# 编辑 .env 文件
nano /root/.openclaw/workspace/lobster-workspace/.env
```

添加:
```
# 巨潮资讯网 Cookie
CNINFO_COOKIE=你的cookie字符串
```

### 4. 我可以抓取的数据

有了 Cookie 后，我可以抓取:

| 数据类型 | API 端点 | 用途 |
|---------|---------|------|
| **个股公告** | /new/hisAnnouncement/query | 定期报告、重大事项 |
| **重大事项** | category_zj_szsh | 股权激励、增发、重组 |
| **监管函件** | category_jgcs_szsh | 问询函、监管措施 |
| **股权质押** | category_gqzy_szsh | 风险预警 |
| **增减持** | category_zjc_szsh | 股东增减持 |
| **互动易** | /new/information/topSearch/query | 投资者问答 |

### 5. 学习指标体系

这些数据可以建立以下学习指标:

```
📊 个股F10学习框架
├── 基本面
│   ├── 公司简介
│   ├── 主营业务
│   └── 行业地位
├── 财务指标
│   ├── ROE/毛利率
│   ├── 营收/利润增速
│   └── 现金流
├── 重大事项 (巨潮)
│   ├── 股权激励 ⭐
│   ├── 增发发行 ⭐
│   ├── 重大合同 ⭐
│   ├── 资产重组 ⭐
│   └── 关联交易
├── 风险信号 (巨潮)
│   ├── 股权质押 ⭐
│   ├── 监管问询函 ⭐
│   └── 股东减持 ⭐
└── 市场情绪
    ├── 互动易热度
    └── 机构调研
```

## Cookie 有效期

- 通常有效期: 7-30天
- 过期后需要重新获取
- 可以设置定时提醒更新

## 安全提醒

⚠️ Cookie 包含登录凭证，请勿:
- 提交到 git
- 分享给他人
- 在公共环境暴露

建议:
```bash
# 确保 .env 在 .gitignore 中
echo ".env" >> /root/.openclaw/workspace/lobster-workspace/.gitignore
```

---

注册完成后告诉我，我来配置抓取脚本！
