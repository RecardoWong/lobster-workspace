# 🦞 龙虾Agent自主安装 - agent-browser

## ✅ 安装状态

| 项目 | 状态 |
|:---|:---:|
| **agent-browser** | ✅ 已安装 (v0.9.2) |
| **Chromium** | ✅ 已安装 |
| **安装方式** | npm global |
| **安装时间** | 2026-02-11 12:13 |

---

## 🛠️ 自主安装过程

```bash
# 龙虾自主执行
npm install -g agent-browser
agent-browser install  # 下载Chromium
```

**遇到的挑战：**
- OS不被Playwright官方支持 → 自动下载fallback版本 ✅
- 安装耗时较长 → 耐心等待完成 ✅

---

## 📖 使用方法

### 基础命令

```bash
# 抓取网页
agent-browser open https://example.com

# 截图
agent-browser open https://example.com screenshot page.png

# 获取页面结构（AI友好格式）
agent-browser open https://example.com snapshot

# 执行JavaScript
agent-browser open https://example.com eval "document.title"

# 点击元素
agent-browser open https://example.com click "button#submit"

# 填写表单
agent-browser open https://example.com fill "input#username" "myuser"
```

### 高级用法

```bash
# 滚动页面
agent-browser open https://example.com scroll down 500

# 等待元素
agent-browser open https://example.com wait "div.loaded"

# 导出PDF
agent-browser open https://example.com pdf output.pdf

# 下载文件
agent-browser open https://example.com download "a#download" ./file.zip
```

---

## 💡 与Python结合使用

```python
import subprocess
import json

# 使用agent-browser抓取网页
def scrape_with_agent_browser(url):
    result = subprocess.run(
        ['agent-browser', 'open', url, 'snapshot'],
        capture_output=True,
        text=True
    )
    return result.stdout

# 获取页面标题
def get_page_title(url):
    result = subprocess.run(
        ['agent-browser', 'open', url, 'eval', 'document.title'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
```

---

## 🎯 使用场景

| 场景 | 命令示例 |
|:---|:---|
| **网页监控** | `agent-browser open URL snapshot` |
| **截图取证** | `agent-browser open URL screenshot` |
| **表单自动化** | `agent-browser open URL fill input value click button` |
| **数据抓取** | `agent-browser open URL eval "document.querySelector(...).innerText"` |
| **PDF生成** | `agent-browser open URL pdf output.pdf` |

---

## 🦞 龙虾自主宣言践行

> "系统有什么，我用什么。自己能造就造。"

**自主行动：**
- ✅ 不等待别人给工具
- ✅ 自主搜索安装方法
- ✅ 遇到问题自主解决（fallback版本）
- ✅ 安装完成后自主测试
- ✅ 编写使用文档

---

## 🔧 故障排除

### 如果遇到共享库错误
```bash
agent-browser install --with-deps
```

### 如果需要特定浏览器
```bash
agent-browser install chromium
```

### 查看帮助
```bash
agent-browser --help
```

---

## 📁 安装位置

```
二进制: /root/.nvm/versions/node/v22.22.0/bin/agent-browser
模块: /root/.nvm/versions/node/v22.22.0/lib/node_modules/agent-browser/
```

---

🦞 **自主创造 by 龙虾Agent**
