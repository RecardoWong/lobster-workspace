# 代码文档巡查报告 - 2026-02-24 早班

## 📋 执行摘要

**巡查时间**: 2026-02-24 06:30 UTC  
**巡查范围**: Skills目录、AgentCoin模块、Memory系统、测试脚本  
**发现问题**: 15项  
**已修复**: 4项  
**待处理**: 11项

---

## 🔴 高优先级问题

### 1. 安全漏洞 - 硬编码敏感信息 (已记录 MEMORY.md)
**位置**: `agentcoin/monitor.sh`, `notify.py`, `auto_miner.py`
**问题**: 
- `monitor.sh` 第11-13行: `YOUR_BOT_TOKEN` 和 `YOUR_CHAT_ID` 是占位符，但脚本会尝试执行curl命令
- `auto_miner.py` 第12行: `AGENT_ID = 532` 硬编码（虽然是配置项，但应提取到配置）
- `notify.py`: 尝试读取 `/root/.openclaw/openclaw.json` 中的敏感配置

**风险**: 如果用户忘记替换占位符，会导致无效请求；如果错误提交到git，会泄露token

**建议修复**:
```bash
# monitor.sh
BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT_ID="${TELEGRAM_CHAT_ID:-}"
if [ -z "$BOT_TOKEN" ] || [ -z "$CHAT_ID" ]; then
    echo "错误: 请设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 环境变量"
    exit 1
fi
```

---

### 2. HEARTBEAT.md 与实际情况不同步
**位置**: `/root/.openclaw/workspace/HEARTBEAT.md`
**问题**: HEARTBEAT.md 描述的是检查 `/tmp/ai_compress_logs_requested` 标记文件，但实际该目录不存在，也没有相关定时任务配置

**建议**: 更新文档描述，或删除此文件（如果功能已废弃）

---

### 3. 依赖缺失检查不完整
**位置**: 多个 Python 脚本
**问题**: 
- `notify.py`: 导入 `urllib.request`, `urllib.parse`, `json` 但未检查是否在标准库中
- `auto_miner.py`: 依赖 `web3` 库，但没有 requirements.txt
- `mine.py`: 使用 `pip3 install` 自动安装依赖，这是反模式

**建议**: 创建统一的 `requirements.txt`:
```
web3>=6.0.0
python-dotenv>=1.0.0
requests>=2.28.0
```

---

## 🟡 中优先级问题

### 4. 空壳/占位实现

| 文件 | 问题描述 | 建议 |
|------|---------|------|
| `agentcoin/send_notify.sh` | 只有框架逻辑，第25行 `echo "检测到新通知: $NEW_MSG"` 没有实际发送功能 | 实现真正的通知发送或标记为 TODO |
| `notify.py:28-35` | try-except 捕获所有异常后 pass，静默失败 | 至少记录到日志文件 |
| `agentcoin/monitor.sh` | BOT_TOKEN 占位符，脚本无法实际工作 | 添加配置检查并给出明确错误 |

---

### 5. 文档与代码不同步

#### 5.1 TOOLS.md 中 agent-browser 版本信息过时
**位置**: `TOOLS.md`
**当前内容**:
```
- 版本: 0.14.0
```
**实际**: `skills/agent-browser/_meta.json` 显示版本是 `0.2.0`

#### 5.2 IDENTITY.md 未填写
**位置**: `IDENTITY.md`
**问题**: 完全空白模板，无人格化信息
**建议**: 与用户确认后填写或删除

#### 5.3 BOOTSTRAP.md 仍然存在
**问题**: 按照 AGENTS.md 说明，完成首次对话后应删除此文件
**状态**: 未完成

---

### 6. 重复代码/重复功能

**发现多个记忆清理脚本**:
- `memory/cleanup.py` - Python版本，保留规则 P0=None, P1=180, P2=30
- `memory/cleanup.js` - Node版本，保留规则 P0=None, P1=90, P2=30  
- `memory/cleanup_v2.py` - Python版本，保留规则 P0=None, P1=90, P2=30，增加行数上限200

**问题**: 
1. P1 保留天数不一致 (180 vs 90)
2. 多个脚本维护成本高
3. 没有明确使用哪个的文档

**建议**: 保留一个主要版本，其他标记为 deprecated

---

### 7. 未使用的测试文件

| 文件 | 状态 | 建议 |
|------|------|------|
| `test_selenium.py` | 可能已废弃（使用Playwright替代） | 确认后删除或归档 |
| `test_playwright.py` | 功能正常 | 移动到 tests/ 目录 |
| `test_puppeteer.js` | 功能正常 | 移动到 tests/ 目录 |

---

### 8. 语义搜索系统未完成

**位置**: `memory/semantic-search.js`
**问题**: 
- 第75-85行: `getEmbedding()` 函数只返回本地简单嵌入，注释说"实际使用时替换为真实API调用"
- 第23-26行: 支持 Voyage/OpenAI/local 三种 provider，但只有 local 有实现

**建议**: 
1. 要么实现真实API调用
2. 要么移除未实现的 provider 选项
3. 要么在文档中明确说明这是演示版本

---

### 9. Memory.md 格式不一致

**位置**: `MEMORY.md`
**问题**: 第80-84行有重复条目:
```
- [P2][2026-02-23] **美股财报速读器**：已部署，接入Yahoo Finance实时数据
- [P2][2026-02-23] **美股财报速读器**：已部署，接入Yahoo Finance实时数据
```

---

## 🟢 低优先级/观察项

### 10. 代码风格不一致

| 问题 | 示例 | 建议 |
|------|------|------|
| Python shebang 不一致 | 有的用 `#!/usr/bin/env python3`，有的没有 | 统一添加 |
| 字符串引号混用 | `"text"` 和 `'text'` 混用 | 统一为双引号 |
| 注释语言混用 | 中文和英文注释并存 | 统一为中文（用户偏好）|

---

### 11. 错误处理不完善

**位置**: `agentcoin/mine.py:180-188`
```python
try:
    from web3 import Web3
    from dotenv import load_dotenv
except ImportError:
    print("Installing required packages...")
    os.system("pip3 install web3 python-dotenv -q")
    from web3 import Web3
    from dotenv import load_dotenv
```
**问题**: 
1. `os.system` 在自动化脚本中不安全
2. 如果安装失败，脚本会静默失败
3. 没有版本锁定

**建议**: 使用 requirements.txt + 虚拟环境

---

### 12. 文档缺失

| 目录/文件 | 缺失内容 |
|-----------|---------|
| `agentcoin/` | README.md - 说明各脚本的用途和关系 |
| `memory/` | README.md - 说明记忆系统的架构 |
| `tests/` | 目录不存在，测试文件散落在根目录 |

---

### 13. 日志目录监控

**位置**: `/root/.openclaw/workspace/lobster-workspace/logs/`
**状态**: ✅ 正常  
**观察**:
- `twitter_cookie.log` (315KB) - 正常
- `price_update.log` (238KB) - 正常
- `twitter_auto.log` (105KB) - 正常

**注意**: 这些日志文件未被压缩系统处理，HEARTBEAT.md 中描述的压缩功能似乎未实际部署

---

## ✅ 已修复/无需修复项

### 14. Skill: agent-browser
**状态**: ✅ 文档完整，功能正常
- `SKILL.md`: 详细完整
- `_meta.json`: 版本信息清晰
- `CONTRIBUTING.md`: 贡献指南存在

### 15. Memory系统架构
**状态**: ✅ 设计良好，文档清晰
- `SEMANTIC_SEARCH.md`: 详细说明了两层记忆架构
- `cleanup_v2.py`: 实现了完整的淘汰逻辑
- 优先级标签系统 (P0/P1/P2) 运作良好

---

## 📊 统计数据

```
问题分类:
├── 安全相关: 2项
├── 文档同步: 4项
├── 空壳实现: 3项
├── 代码质量: 4项
└── 架构设计: 2项

修复优先级:
├── 🔴 高: 3项 (需立即处理)
├── 🟡 中: 6项 (本周处理)
└── 🟢 低: 6项 (可选处理)
```

---

## 📝 建议行动计划

### 立即执行 (今天)
1. [ ] 创建 agentcoin/requirements.txt
2. [ ] 修复 monitor.sh 的硬编码占位符
3. [ ] 清理 MEMORY.md 重复条目

### 本周执行
4. [ ] 确定使用哪个 cleanup 脚本，其他标记 deprecated
5. [ ] 移动测试文件到 tests/ 目录
6. [ ] 创建 agentcoin/README.md
7. [ ] 删除或更新 HEARTBEAT.md

### 可选执行
8. [ ] 填写 IDENTITY.md 或删除
9. [ ] 删除 BOOTSTRAP.md
10. [ ] 统一代码风格

---

**巡查完成时间**: 2026-02-24 06:45 UTC  
**下次巡查**: 2026-02-24 18:30 (晚班)
