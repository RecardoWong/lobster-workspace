# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### Agent Browser (已配置)

- 版本: 0.2.0 (meta.json) / CLI 0.14.0
- 路径: `/root/.nvm/versions/node/v22.22.0/bin/agent-browser`
- Chromium: 已安装 (fallback build for ubuntu24.04-x64)
- 守护进程: 自动运行

**常用命令:**
```bash
agent-browser open <url>          # 打开网页
agent-browser snapshot -i         # 获取可交互元素
agent-browser click @e1           # 点击元素
agent-browser fill @e2 "text"     # 填充输入框
agent-browser get text @e1        # 获取元素文本
agent-browser close               # 关闭浏览器
```

**示例工作流:**
```bash
agent-browser open https://example.com
agent-browser snapshot -i         # 查看页面元素
agent-browser click @e1           # 点击链接
agent-browser get text @e2        # 获取文本内容
agent-browser close
```

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
