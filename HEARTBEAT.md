# HEARTBEAT.md - 定时检查任务

## 检查 AI 日志压缩请求
- 检查 `/tmp/ai_compress_logs_requested` 标记文件
- 如果存在，执行日志压缩任务
- 压缩完成后删除标记文件

## 日志压缩任务
1. 扫描 `/root/.openclaw/workspace/lobster-workspace/logs/*.log`
2. 找出超过7天的日志文件
3. 逐个分析内容，提取精华
4. 生成记忆条目（格式: - [Px][日期] 内容）
5. 追加到 `memory/2026-02-20.md`
6. 移动原文到 `logs/archive/`
7. 创建 `.compressed` 标记
