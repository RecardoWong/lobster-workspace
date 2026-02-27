#!/usr/bin/env node
/**
 * 日志压缩脚本
 * 
 * 策略：
 * - 7天内日志：原样保留
 * - 超过7天：提取精华 → 追加到记忆文件 → 原文归档
 * - 压缩比：10:1 ~ 20:1（几百行 → 十几条精华）
 * 
 * 用法：
 *   node log-compress.js logs/dashboard.log          # 预览
 *   node log-compress.js logs/dashboard.log --apply  # 执行
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DAYS_TO_KEEP = 7;           // 保留天数
const COMPRESS_TARGET = 20;       // 压缩后不超过20行精华
const MEMORY_FILE = 'MEMORY.md';  // 记忆文件
const ARCHIVE_DIR = 'logs/archive'; // 归档目录

// 解析参数
function parseArgs() {
  const args = process.argv.slice(2);
  const result = { file: null, apply: false };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--apply') {
      result.apply = true;
    } else if (!args[i].startsWith('--')) {
      result.file = args[i];
    }
  }
  
  return result;
}

// 判断文件是否超过7天
function isOldLog(filePath) {
  const stats = fs.statSync(filePath);
  const ageDays = (Date.now() - stats.mtime.getTime()) / (1000 * 60 * 60 * 24);
  return ageDays > DAYS_TO_KEEP;
}

// 简单提取精华（基于规则）
function extractEssence(content) {
  const lines = content.split('\n').filter(l => l.trim());
  const essence = [];
  
  // 提取包含关键信息的行
  const patterns = [
    /error|fail|失败|错误/i,
    /success|完成|✅|部署成功/i,
    /警告|⚠️|warning/i,
    /关键|核心|重要|教训/i,
    /新增|修复|完成|更新/i
  ];
  
  for (const line of lines) {
    for (const pattern of patterns) {
      if (pattern.test(line) && line.length < 200) {
        // 去重
        if (!essence.includes(line.trim())) {
          essence.push(line.trim());
        }
        break;
      }
    }
  }
  
  // 如果太多，只保留最新的
  if (essence.length > COMPRESS_TARGET) {
    return essence.slice(-COMPRESS_TARGET);
  }
  
  return essence;
}

// AI提取精华（通过OpenClaw命令行）
async function extractWithAI(content, fileName) {
  // 构建prompt
  const prompt = `请从以下日志中提取关键信息，总结为不超过${COMPRESS_TARGET}条记忆条目。
每条格式：- [P1或P2][${new Date().toISOString().split('T')[0]}] 一句话总结

只提取有价值的信息：错误、完成的功能、关键决策、重要发现。
忽略常规输出、调试信息、时间戳。

日志文件：${fileName}

日志内容（前5000字符）：
${content.substring(0, 5000)}

请直接输出记忆条目，每条一行：`;

  try {
    // 尝试调用OpenClaw提取
    // 注意：这里假设可以通过某种方式调用AI，实际可能需要调整
    const result = execSync(`echo "${prompt.replace(/"/g, '\\"')}" | openclaw ask --quick`, {
      encoding: 'utf-8',
      timeout: 30000
    });
    return result.trim().split('\n').filter(l => l.startsWith('- ['));
  } catch (e) {
    console.log('   ⚠️  AI提取失败，使用规则提取');
    return extractEssence(content).map(line => {
      const priority = /error|fail|错误|失败/i.test(line) ? 'P1' : 'P2';
      return `- [${priority}][${new Date().toISOString().split('T')[0]}] ${line.substring(0, 100)}`;
    });
  }
}

// 主函数
async function main() {
  const args = parseArgs();
  
  if (!args.file) {
    console.error('❌ 错误: 请指定日志文件路径');
    console.error('用法: node log-compress.js logs/xxx.log [--apply]');
    process.exit(1);
  }
  
  const filePath = path.resolve(args.file);
  
  if (!fs.existsSync(filePath)) {
    console.error(`❌ 文件不存在: ${filePath}`);
    process.exit(1);
  }
  
  // 检查是否超过7天
  if (!isOldLog(filePath)) {
    const stats = fs.statSync(filePath);
    const ageDays = Math.floor((Date.now() - stats.mtime.getTime()) / (1000 * 60 * 60 * 24));
    console.log(`⏭️  跳过: ${path.basename(filePath)} (${ageDays}天 < ${DAYS_TO_KEEP}天)`);
    return;
  }
  
  // 读取日志内容
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').length;
  
  console.log('\n📦 日志压缩');
  console.log('='.repeat(60));
  console.log(`📄 文件: ${path.basename(filePath)}`);
  console.log(`📊 原行数: ${lines}`);
  console.log(`📅 年龄: >${DAYS_TO_KEEP}天`);
  console.log('-'.repeat(60));
  
  // 提取精华
  console.log('🧠 提取精华...');
  const essence = extractEssence(content);
  
  console.log(`✨ 精华条目: ${essence.length} 条`);
  console.log(`📉 压缩比: 1:${Math.floor(lines / essence.length)}`);
  
  if (essence.length === 0) {
    console.log('⚠️  未找到有价值的信息，跳过');
    return;
  }
  
  // 显示精华
  console.log('\n📝 提取的精华:');
  for (const line of essence.slice(0, 10)) {
    console.log(`   ${line.substring(0, 80)}${line.length > 80 ? '...' : ''}`);
  }
  if (essence.length > 10) {
    console.log(`   ... 还有 ${essence.length - 10} 条`);
  }
  
  // 执行操作
  if (args.apply) {
    console.log('\n💾 正在执行...');
    
    // 确保归档目录存在
    if (!fs.existsSync(ARCHIVE_DIR)) {
      fs.mkdirSync(ARCHIVE_DIR, { recursive: true });
    }
    
    // 将精华追加到记忆文件
    const memoryPath = path.join(process.cwd(), MEMORY_FILE);
    const timestamp = new Date().toISOString().split('T')[0];
    
    let memoryContent = '';
    if (fs.existsSync(memoryPath)) {
      memoryContent = fs.readFileSync(memoryPath, 'utf-8');
    }
    
    // 添加日志精华区块
    const essenceBlock = [
      '',
      `## 日志精华 - ${path.basename(filePath)} (${timestamp})`,
      ''
    ];
    
    for (const line of essence) {
      // 添加优先级标签
      const priority = /error|fail|错误|失败|critical/i.test(line) ? 'P1' : 'P2';
      essenceBlock.push(`- [${priority}][${timestamp}] ${line.substring(0, 150)}`);
    }
    
    essenceBlock.push('');
    
    fs.writeFileSync(memoryPath, memoryContent + essenceBlock.join('\n'));
    console.log(`✅ 已追加到: ${MEMORY_FILE}`);
    
    // 移动原文到归档目录
    const archiveName = `${path.basename(filePath)}.${timestamp}.bak`;
    const archivePath = path.join(ARCHIVE_DIR, archiveName);
    fs.renameSync(filePath, archivePath);
    console.log(`✅ 已归档到: ${archivePath}`);
    
    console.log('\n✨ 压缩完成！');
  } else {
    console.log('\n🔍 预览模式 - 未实际执行（加 --apply 执行）');
  }
}

// 运行
main().catch(err => {
  console.error('❌ 错误:', err.message);
  process.exit(1);
});
