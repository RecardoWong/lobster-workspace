# Dashboard 代码档案

**创建时间**: 2026-02-15  
**服务器**: 43.160.229.161 (新加坡)  
**访问地址**: http://43.160.229.161/  

---

## 📁 文件结构

```
dashboard/
├── index.html              # 主仪表板 (PC端) - 当前线上版本
├── index_v2.html           # 改进版 (三标签页导航) ⭐ 新版本
├── mobile.html             # 移动端适配版
├── twitter.html            # Twitter 监控页面
├── hello_dashboard.html    # 第一课：最简单的Dashboard
├── lesson1.html            # 基础教学版
├── lesson2.html            # 进阶教学版
├── deploy.sh               # Bash 部署脚本
├── deploy.py               # Python 部署脚本
├── DEPLOY.md               # 部署配置指南
└── README.md               # 本文件
```

---

## 🎨 设计规范

### 颜色主题
- 主背景: `#f5f7fa` (浅灰)
- 卡片背景: `#ffffff` (白色)
- 主色: `#3b82f6` (蓝色)
- 辅助色: `#8b5cf6` (紫色)
- 上涨: `#16a34a` (绿色)
- 下跌: `#dc2626` (红色)
- 文字: `#1a1a1a` (深黑)
- 次要文字: `#6b7280` (灰色)

### 布局
- 侧边栏: 280px 固定宽度
- 主内容区: 自适应
- 卡片圆角: 12px
- 卡片阴影: `0 1px 3px rgba(0,0,0,0.1)`

---

## 📄 各文件说明

### 1. index.html (主仪表板)
- 功能: 投资监控总览
- 布局: 左侧边栏 + 右侧主内容
- 模块: 股价监控、财经要闻、Twitter动态、系统状态

### 2. index_v2.html (改进版) ⭐
- 功能: 三标签页导航 (总览/投资分析/投资报告)
- 新增: 技术面分析、基本面分析、多空对比、研报摘要
- 状态: 待部署到服务器

### 3. mobile.html (移动端)
- 功能: iPhone 适配版
- 特点: iOS 风格，毛玻璃效果

### 4. twitter.html (Twitter监控)
- 功能: 展示 Twitter 监控内容
- 布局: 卡片式推文展示
- 特点: 包含中文翻译

---

## 🚀 部署说明

### 当前部署状态
- **问题**: SSH 免密登录未配置，自动部署需要密码
- **解决方案**: 配置 SSH 密钥或使用密码登录

### 手动部署步骤
```bash
# 1. 登录服务器
ssh ubuntu@43.160.229.161

# 2. 进入 Web 目录
cd /var/www/html

# 3. 备份当前版本
cp index.html index.html.backup

# 4. 上传新文件（在本地执行）
scp /root/.openclaw/workspace/memory/dashboard/index_v2.html ubuntu@43.160.229.161:/var/www/html/

# 5. 或者替换为新版
ssh ubuntu@43.160.229.161 "sudo cp /var/www/html/index_v2.html /var/www/html/index.html"
```

### 自动部署配置
详见 `DEPLOY.md` 文件，包含：
- SSH 免密登录配置
- Git 自动部署 (Webhook)
- Cron 定时同步
- Python 自动部署脚本

---

## 🔧 技术栈

- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **样式**: 纯 CSS，无框架
- **响应式**: 支持 PC + Mobile
- **动画**: CSS transitions + keyframes

---

## 📝 更新日志

### 2026-02-15
- ✅ 创建 index_v2.html (三标签页版本)
- ✅ 添加 deploy.sh 和 deploy.py 部署脚本
- ✅ 添加 DEPLOY.md 部署配置指南
- ⏳ 待配置 SSH 免密登录实现自动部署

---

*最后更新: 2026-02-15*
