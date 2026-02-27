#!/usr/bin/env node
/**
 * 语义搜索系统 - 冷记忆召回
 * 
 * 两层记忆架构：
 * - 热记忆（Hot）: MEMORY.md + memory/2026-02-20.md (~200行，每次加载)
 * - 冷记忆（Cold）: archive/ 目录 (无限容量，按需召回)
 * 
 * 使用 Voyage AI / OpenAI Embeddings 建立语义索引
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// 配置
const CONFIG = {
  // 嵌入模型选择
  // 'voyage': Voyage AI (推荐，中文好)
  // 'openai': OpenAI text-embedding-3-small
  // 'local': 本地模型 (无需API，质量较低)
  provider: process.env.EMBED_PROVIDER || 'voyage',
  
  // API Keys (从环境变量读取)
  voyageApiKey: process.env.VOYAGE_API_KEY,
  openaiApiKey: process.env.OPENAI_API_KEY,
  
  // 召回设置
  topK: 5,              // 召回 top-5 相关条目
  similarityThreshold: process.env.VOYAGE_API_KEY ? 0.65 : 0.5,  // 有API时用0.65，本地用0.5
  
  // 路径
  hotMemory: '/root/.openclaw/workspace/MEMORY.md',
  dailyMemory: '/root/.openclaw/workspace/memory',
  coldArchive: '/root/.openclaw/workspace/memory/archive',
  indexFile: '/root/.openclaw/workspace/memory/.semantic_index.json'
};

// 简单的余弦相似度计算
function cosineSimilarity(a, b) {
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// 简单的哈希嵌入（本地fallback，无需API）
function simpleEmbedding(text) {
  // 基于词频的简单向量
  const vector = new Array(128).fill(0);
  const words = text.toLowerCase().split(/\s+/);
  
  for (const word of words) {
    for (let i = 0; i < word.length; i++) {
      const char = word.charCodeAt(i);
      vector[char % 128] += 1;
    }
  }
  
  // 归一化
  const norm = Math.sqrt(vector.reduce((a, b) => a + b * b, 0));
  return vector.map(v => v / (norm || 1));
}

// 调用 Voyage AI API 获取嵌入
async function getVoyageEmbedding(text) {
  if (!CONFIG.voyageApiKey) {
    console.log('⚠️  VOYAGE_API_KEY 未设置，使用本地嵌入');
    return simpleEmbedding(text);
  }
  
  try {
    const https = require('https');
    const postData = JSON.stringify({
      input: text,
      model: 'voyage-2'  // Voyage 2 模型，性价比高
    });
    
    const options = {
      hostname: 'api.voyageai.com',
      port: 443,
      path: '/v1/embeddings',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${CONFIG.voyageApiKey}`,
        'Content-Length': Buffer.byteLength(postData)
      }
    };
    
    return new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            if (response.data && response.data[0] && response.data[0].embedding) {
              resolve(response.data[0].embedding);
            } else {
              console.log('⚠️  Voyage API 返回异常，使用本地嵌入');
              resolve(simpleEmbedding(text));
            }
          } catch (e) {
            console.log('⚠️  Voyage API 解析失败，使用本地嵌入');
            resolve(simpleEmbedding(text));
          }
        });
      });
      
      req.on('error', (e) => {
        console.log(`⚠️  Voyage API 请求失败: ${e.message}`);
        resolve(simpleEmbedding(text));
      });
      
      req.write(postData);
      req.end();
    });
  } catch (e) {
    console.log('⚠️  Voyage API 异常，使用本地嵌入');
    return simpleEmbedding(text);
  }
}

// 调用嵌入API
async function getEmbedding(text, provider = CONFIG.provider) {
  if (provider === 'voyage' && CONFIG.voyageApiKey) {
    return getVoyageEmbedding(text);
  }
  // 降级到本地嵌入
  return simpleEmbedding(text);
}

// 扫描归档目录
function scanArchive() {
  const entries = [];
  
  if (!fs.existsSync(CONFIG.coldArchive)) {
    return entries;
  }
  
  const files = fs.readdirSync(CONFIG.coldArchive);
  
  for (const file of files) {
    if (file.endsWith('.md') || file.endsWith('.log')) {
      const filePath = path.join(CONFIG.coldArchive, file);
      const content = fs.readFileSync(filePath, 'utf-8');
      
      // 解析条目
      const lines = content.split('\n');
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('- [P') && trimmed.includes('][')) {
          entries.push({
            text: trimmed,
            source: file,
            embedding: null  // 延迟计算
          });
        }
      }
    }
  }
  
  return entries;
}

// 建立索引
async function buildIndex() {
  console.log('🔨 建立语义索引...\n');
  
  const entries = scanArchive();
  console.log(`📁 扫描到 ${entries.length} 条归档记忆`);
  
  // 计算嵌入
  console.log('🧮 计算嵌入向量...');
  for (let i = 0; i < entries.length; i++) {
    entries[i].embedding = await getEmbedding(entries[i].text);
    if ((i + 1) % 10 === 0) {
      process.stdout.write(`  ${i + 1}/${entries.length}\r`);
    }
  }
  
  // 保存索引
  const index = {
    created: new Date().toISOString(),
    count: entries.length,
    entries: entries
  };
  
  fs.writeFileSync(CONFIG.indexFile, JSON.stringify(index, null, 2));
  console.log(`\n✅ 索引已保存: ${CONFIG.indexFile}`);
  console.log(`   共 ${entries.length} 条记忆`);
}

// 语义搜索
async function semanticSearch(query, topK = CONFIG.topK) {
  // 加载索引
  if (!fs.existsSync(CONFIG.indexFile)) {
    console.log('⚠️  索引不存在，先建立索引...');
    await buildIndex();
  }
  
  const index = JSON.parse(fs.readFileSync(CONFIG.indexFile, 'utf-8'));
  const queryEmbedding = await getEmbedding(query);
  
  // 计算相似度
  const results = [];
  for (const entry of index.entries) {
    const similarity = cosineSimilarity(queryEmbedding, entry.embedding);
    if (similarity >= CONFIG.similarityThreshold) {
      results.push({
        text: entry.text,
        source: entry.source,
        similarity: similarity
      });
    }
  }
  
  // 排序并返回 topK
  results.sort((a, b) => b.similarity - a.similarity);
  return results.slice(0, topK);
}

// 召回记忆（主函数）
async function recallMemory(query) {
  console.log(`\n🔍 语义搜索: "${query}"\n`);
  console.log('='.repeat(60));
  
  const startTime = Date.now();
  const results = await semanticSearch(query);
  const duration = Date.now() - startTime;
  
  if (results.length === 0) {
    console.log('❌ 未找到相关记忆\n');
    return [];
  }
  
  console.log(`✨ 召回 ${results.length} 条相关记忆 (${duration}ms)\n`);
  
  for (let i = 0; i < results.length; i++) {
    const r = results[i];
    const sim = Math.round(r.similarity * 100);
    console.log(`${i + 1}. [${sim}%] ${r.text.substring(0, 70)}${r.text.length > 70 ? '...' : ''}`);
    console.log(`   来源: ${r.source}\n`);
  }
  
  return results;
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'index' || command === 'build') {
    await buildIndex();
  } else if (command === 'search' || command === 'recall') {
    const query = args.slice(1).join(' ');
    if (!query) {
      console.error('❌ 请提供搜索关键词');
      console.error('用法: node semantic-search.js search "Dashboard布局问题"');
      process.exit(1);
    }
    await recallMemory(query);
  } else if (command === 'api') {
    // API模式：输出JSON
    const query = args.slice(1).join(' ');
    const results = await semanticSearch(query);
    console.log(JSON.stringify(results, null, 2));
  } else {
    console.log('语义搜索系统 - 冷记忆召回\n');
    console.log('用法:');
    console.log('  node semantic-search.js index          # 建立索引');
    console.log('  node semantic-search.js search "查询"   # 搜索记忆');
    console.log('  node semantic-search.js api "查询"      # JSON输出');
    console.log('\n示例:');
    console.log('  node semantic-search.js search "Twitter更新失败"');
    console.log('  node semantic-search.js search "浏览器缓存"');
  }
}

// 运行
main().catch(err => {
  console.error('❌ 错误:', err.message);
  process.exit(1);
});
