# Dashboard 布局调试 Skill

## 何时触发

当出现以下情况时触发：
- "这个卡片怎么跑到下面去了"
- "三栏怎么变成两栏了"
- "右边是空白的"
- "布局乱了"
- "响应式不工作"

## 核心原则

**永远不要让用户反复刷新来测试布局！**

每次修改后：
1. 部署到服务器
2. 提供截图验证步骤
3. 明确告诉用户预期效果

## 诊断流程

### 1. 检查当前状态（2分钟）

```bash
# 检查服务器上的HTML结构
ssh ... "grep -c 'class=\"card\"' /var/www/html/index.html"
ssh ... "grep -A 2 'cards-grid' /var/www/html/index.html"
```

确认：
- 有多少个卡片？
- 卡片是否嵌套？
- CSS grid设置是什么？

### 2. 识别问题类型

| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 卡片跑到下一行 | 响应式断点触发 | 调整 `@media (max-width: Xpx)` |
| 卡片缺失 | HTML结构损坏/未闭合 | 恢复git版本或重新添加 |
| 卡片嵌套 | div标签未正确闭合 | 检查闭合标签数量 |
| 宽度不均 | grid-template-columns设置 | 调整 fr 比例或固定像素 |
| 内容溢出 | 没有max-height/overflow | 添加限制和滚动条 |

### 3. 修复策略

#### 方案A: 调整响应式断点（推荐先尝试）

```css
/* 默认3栏 */
.cards-grid {
    grid-template-columns: repeat(3, 1fr);
}

/* 大屏保持3栏 */
@media (max-width: 1600px) {  /* 从1400改为1600 */
    .cards-grid { 
        grid-template-columns: repeat(2, 1fr); 
    }
}
```

#### 方案B: 固定宽度布局

```css
.cards-grid {
    display: grid;
    grid-template-columns: 280px 1fr 1fr;  /* 固定+弹性 */
    gap: 16px;
}
```

#### 方案C: Flexbox强制不换行

```css
.cards-grid {
    display: flex;
    flex-wrap: nowrap;  /* 强制一行 */
    gap: 16px;
}
.card {
    flex: 1 1 0;  /* 等分宽度 */
    min-width: 0; /* 允许压缩 */
}
```

### 4. 验证清单

每次修复后必须验证：
- [ ] 服务器上HTML结构正确（卡片数量、嵌套关系）
- [ ] CSS grid设置生效
- [ ] 三栏并排显示（截图验证）
- [ ] 2栏断点正确触发
- [ ] 1栏移动端正确触发

### 5. 常见布局模板

#### 模板1: 标准三栏（当前使用）

```html
<div class="cards-grid">
    <div class="card">...</div>  <!-- 左 -->
    <div class="card">...</div>  <!-- 中 -->
    <div class="card">...</div>  <!-- 右 -->
</div>
```

#### 模板2: 左窄右宽

```css
.cards-grid {
    grid-template-columns: 0.8fr 1.1fr 1.1fr;
}
```

#### 模板3: 固定+弹性混合

```css
.cards-grid {
    grid-template-columns: 300px 1fr 1fr;
}
```

## 禁止事项

❌ 不要反复尝试不同的布局方案让用户测试
❌ 不要修改后不立即部署验证
❌ 不要忽略响应式断点的影响
❌ 不要在没有检查服务器HTML的情况下猜测问题

## 快速诊断命令

```bash
# 1. 检查卡片数量
grep -c 'class="card"' /var/www/html/index.html

# 2. 检查卡片标题
grep 'card-title' /var/www/html/index.html | grep -v 'font-size'

# 3. 检查CSS设置
grep -A 3 'cards-grid {' /var/www/html/index.html

# 4. 检查响应式断点
grep '@media' /var/www/html/index.html
```

## 成功案例记录

### 问题: 财经要报跑到下面
**原因**: 响应式断点1200px过低，用户屏幕触发2栏
**解决**: 改为1600px，同时缩小左侧栏宽度
**验证**: 截图确认三栏并排

### 问题: Twitter卡片嵌套在上游供应商里
**原因**: div标签未闭合
**解决**: 恢复v4.1版本重新添加
**验证**: 检查服务器上3个独立的card div
