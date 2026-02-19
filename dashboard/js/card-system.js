/**
 * Dashboard Card System - 独立卡片框架
 * 
 * 使用说明:
 * 1. 复制 CARD_TEMPLATE 到 cards-grid 中
 * 2. 修改 data-card-id 为唯一标识
 * 3. 填充你的内容
 * 4. 添加对应的 CSS（在 style 标签中）
 * 5. 添加对应的 JS（在 script 标签中）
 */

// ==================== 卡片模板 ====================
const CARD_TEMPLATE = `
<!-- 卡片: [你的卡片名称] -->
<div class="card" data-card-id="[unique-id]">
    <div class="card-header">
        <div class="card-title">[图标] [标题]</div>
        <span class="card-subtitle">[副标题]</span>
    </div>
    <div class="card-body" id="[body-id]">
        <!-- 你的内容在这里 -->
    </div>
</div>
`;

// ==================== 卡片注册系统 ====================
class CardRegistry {
    constructor() {
        this.cards = new Map();
    }
    
    // 注册一个新卡片
    register(cardId, config) {
        this.cards.set(cardId, {
            id: cardId,
            title: config.title,
            render: config.render,
            update: config.update,
            interval: config.interval || null
        });
        
        // 如果有定时更新，启动定时器
        if (config.interval) {
            setInterval(() => {
                this.update(cardId);
            }, config.interval);
        }
    }
    
    // 渲染指定卡片
    render(cardId) {
        const card = this.cards.get(cardId);
        if (card && card.render) {
            card.render();
        }
    }
    
    // 更新指定卡片
    async update(cardId) {
        const card = this.cards.get(cardId);
        if (card && card.update) {
            try {
                await card.update();
                console.log(`✅ [${card.title}] 更新成功`);
            } catch (e) {
                console.error(`❌ [${card.title}] 更新失败:`, e);
            }
        }
    }
    
    // 更新所有卡片
    async updateAll() {
        for (const [id] of this.cards) {
            await this.update(id);
        }
    }
}

// 全局卡片注册表
const dashboardCards = new CardRegistry();

// ==================== 示例: 财经要报卡片 ====================
// 这是第三个卡片的完整实现示例

const FINANCE_BULLETIN_CONFIG = {
    id: 'finance-bulletin',
    title: '📊 财经要报',
    subtitle: 'AI·数据中心·GaN',
    interval: 1800000, // 30分钟更新一次
    
    // 渲染函数 - 初始化时调用
    render() {
        const container = document.querySelector('[data-card-id="finance-bulletin"] .card-body');
        if (!container) return;
        
        container.innerHTML = `
            <div class="bulletin-list" id="bulletinList">
                <!-- 动态内容 -->
            </div>
        `;
        
        // 初始加载数据
        this.update();
    },
    
    // 更新函数 - 定时调用
    async update() {
        const list = document.getElementById('bulletinList');
        if (!list) return;
        
        // 示例数据 - 可以替换为API调用
        const data = [
            {
                tag: 'AI数据中心',
                tagColor: '#8b5cf6',
                time: '刚刚',
                title: '英伟达Blackwell GPU产能紧张，AI数据中心订单排到2026年',
                source: '行业动态'
            },
            {
                tag: 'GaN需求',
                tagColor: '#ec4899',
                time: '1小时前',
                title: '微软投资$80亿建AI数据中心，GaN功率器件需求大增',
                source: '华尔街见闻'
            }
        ];
        
        list.innerHTML = data.map(item => `
            <div class="bulletin-item" style="border-left-color: ${item.tagColor}; background: linear-gradient(135deg, ${item.tagColor}10, ${item.tagColor}05);">
                <div class="bulletin-header">
                    <span class="bulletin-tag" style="color: ${item.tagColor}; background: ${item.tagColor}15;">${item.tag}</span>
                    <span class="bulletin-time">${item.time}</span>
                </div>
                <div class="bulletin-title">${item.title}</div>
                <div class="bulletin-source">来源: ${item.source}</div>
            </div>
        `).join('');
    }
};

// 注册财经要报卡片
dashboardCards.register('finance-bulletin', FINANCE_BULLETIN_CONFIG);

// ==================== 使用示例 ====================

/*
// 1. 在HTML中添加卡片容器
<div class="cards-grid">
    <!-- 已有的上游供应商卡片 -->
    <div class="card" data-card-id="suppliers">...</div>
    
    <!-- 已有的Twitter卡片 -->
    <div class="card" data-card-id="twitter">...</div>
    
    <!-- 新的第三个卡片 - 复制CARD_TEMPLATE -->
    <div class="card" data-card-id="finance-bulletin">
        <div class="card-header">
            <div class="card-title">📊 财经要报</div>
            <span class="card-subtitle">AI·数据中心·GaN</span>
        </div>
        <div class="card-body" id="financeBulletinBody">
            <!-- 内容由JS动态填充 -->
        </div>
    </div>
</div>

// 2. 添加对应的CSS（在style标签中）
.bulletin-item {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 12px;
    border-left: 3px solid;
}
.bulletin-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}
.bulletin-tag {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
}
.bulletin-time {
    font-size: 11px;
    color: #9ca3af;
}
.bulletin-title {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a1a;
    line-height: 1.5;
}
.bulletin-source {
    font-size: 11px;
    color: #6b7280;
    margin-top: 4px;
}

// 3. 初始化时渲染
window.addEventListener('DOMContentLoaded', () => {
    dashboardCards.render('finance-bulletin');
});

// 4. 手动更新
// dashboardCards.update('finance-bulletin');

// 5. 更新所有卡片
// dashboardCards.updateAll();
*/

// ==================== 导出 ====================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CardRegistry, dashboardCards, CARD_TEMPLATE };
}
