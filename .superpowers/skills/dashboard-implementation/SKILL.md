# Dashboard 实施 Skill

## 何时触发

当用户确认设计文档并说以下话时触发：
- "开始实施"
- "去做吧"
- "开始写代码"
- "按照计划执行"

## 核心原则

**小步快跑，频繁验证**

每个任务应该在 2-5 分钟内完成，然后立即部署验证。

## 实施流程

### 1. 读取计划文档

首先读取 `plans/[feature-name]-plan.md`，确认：
- 有多少个任务？
- 每个任务的预计时间？
- 验证方式是什么？

### 2. 逐个执行任务

#### 任务格式

```
任务N: [任务名称]
文件: [文件路径]
步骤:
1. [具体步骤]
2. [具体步骤]
验证: [如何验证成功]
```

#### 执行 checklist

- [ ] 读取相关文件
- [ ] 定位插入/修改位置
- [ ] 精确编辑（不要影响其他部分）
- [ ] 保存文件
- [ ] 部署到服务器
- [ ] 验证效果
- [ ] 报告完成

### 3. 验证方式

#### HTML/CSS 变更

```bash
# 部署
deploy_dashboard.sh

# 验证服务器文件
ssh ... "grep '关键词' /var/www/html/index.html"

# 提供访问链接
http://43.160.229.161/
```

#### JavaScript 变更

```bash
# 检查浏览器控制台错误
# 验证功能正常（点击、加载等）
```

### 4. 任务完成报告

每个任务完成后报告：

```
✅ 任务N完成: [任务名称]
文件: [文件路径]
修改内容: [简要描述]
验证结果: [通过/失败]
下一步: [下一个任务名称]
```

### 5. 错误处理

如果任务失败：

1. **立即停止** - 不要继续下一个任务
2. **回滚** - 恢复上一个可用版本
3. **诊断** - 找出失败原因
4. **修复** - 重新执行当前任务
5. **验证** - 确认修复成功

## 编辑技巧

### 定位插入点

```bash
# 找到特定标记附近
grep -n '标记文本' file.html

# 查看上下文
sed -n '100,110p' file.html
```

### 安全编辑

```python
# 使用精确匹配替换
old_text = '''<div class="cards-grid">'''
new_text = '''<div class="cards-grid">\n    <!-- 新内容 -->'''

content = content.replace(old_text, new_text, 1)  # 只替换第一个
```

### 验证闭合标签

```bash
# 检查div标签数量
python3 -c "
content = open('file.html').read()
print(f'Open: {content.count(\"<div\")}')
print(f'Close: {content.count(\"</div\")}')
"
```

## 部署流程

### 标准部署

```bash
cd /root/.openclaw/workspace/lobster-workspace/dashboard

# 1. 复制文件到服务器
scp -i ~/.ssh/lobster_deploy index.html ubuntu@43.160.229.161:/home/ubuntu/

# 2. 移动到web目录
ssh -i ~/.ssh/lobster_deploy ubuntu@43.160.229.161 '
    sudo cp /home/ubuntu/index.html /var/www/html/
    sudo chown www-data:www-data /var/www/html/index.html
'

# 3. 验证
ssh ... "head -5 /var/www/html/index.html"
```

### 快速验证

```bash
# 检查关键内容是否存在
ssh ... "grep -c 'card-title' /var/www/html/index.html"
ssh ... "grep '特定文本' /var/www/html/index.html"
```

## 版本控制

### 实施前

```bash
# 创建分支或标签
git tag before-[feature-name]
git add .
git commit -m "before: 实施[功能名称]之前"
```

### 实施后

```bash
# 提交更改
git add .
git commit -m "feat: 完成[功能名称]"
git push
```

### 回滚

```bash
# 快速回滚
git checkout before-[feature-name] -- dashboard/index.html
deploy_dashboard.sh
```

## 禁止事项

❌ 不要一次修改多个任务
❌ 不要跳过验证直接下一个任务
❌ 不要让用户"刷新看看"来验证
❌ 不要在结构不确定时猜测位置
❌ 不要覆盖用户未确认的内容

## 示例对话

用户: "开始实施财经要报功能"

Agent: 
"好的，读取实施计划...

计划包含3个任务:
1. HTML结构 (5分钟)
2. CSS样式 (5分钟)  
3. 静态数据 (5分钟)

开始执行任务1: HTML结构
- 读取 dashboard/index.html
- 在cards-grid末尾添加card div
- 部署... ✅
- 验证: 服务器上找到3个card ✅

任务1完成！开始任务2: CSS样式..."

## 输出格式

每个任务结束后，用以下格式报告：

```
任务 [N/总]: [任务名称]
文件: [路径]
状态: ✅ 完成 / ❌ 失败
验证: [验证方式和结果]
耗时: [X分钟]
下一步: [下一个任务]
```
