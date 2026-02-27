#!/usr/bin/env node
/**
 * AI 日志压缩脚本
 * 调用 OpenClaw Agent 进行智能日志分析
 * 
 * 用法：
 *   node ai-log-compress.js logs/xxx.log    # AI 分析并输出精华
 *   node ai-log-compress.js --apply         # 执行压缩
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const DAYS_TO_KEEP = 7;
const MEMORY_FILE = '/root/.openclaw/workspace/memory/2026-02-20.md';
const ARCHIVE_DIR = '/root/.openclaw/workspace/lobster-workspace/logs/archive';

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

// 检查文件年龄
function isOldLog(filePath) {
  try {
    const stats = fs.statSync(filePath);
    const ageDays = (Date.now() - stats.mtime.getTime()) / (1000 * 60 * 60 * 24);
    return ageDays > DAYS_TO_KEEP;
  } catch (e) {
    return false;
  }
}

// 发送消息给 AI 并获取回复（通过 sessions_send）
async function askAI(prompt) {
  return new Promise((resolve, reject) => {
    // 构建 OpenClaw 命令
    const cmd = 'openclaw';
    const args = ['sessions_send', 'agent:main:main', prompt];
    
    console.log('   🤖 调用 AI 分析中...');
    
    const child = spawn(cmd, args, {
      encoding: 'utf-8',
      timeout: 60000
    });
    
    let output = '';
    let error = '';
    
    child.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    child.on('close', (code) => {
      if (code !== 0 && code !== null) {
        reject(new Error(`Command failed: ${error}`));
      } else {
        resolve(output.trim());
      }
    });
    
    child.on('error', (err) => {
      reject(err);
    });
  });
}

// 主函数
async function main() {
  const args = parseArgs();
  
  if (!args.file) {
    console.error('❌ 错误: 请指定日志文件路径');
    console.error('用法: node ai-log-compress.js logs/xxx.log [--apply]');
    process.exit(1);
  }
  
  const filePath = path.resolve(args.file);
  
  if (!fs.existsSync(filePath)) {
    console.error(`❌ 文件不存在: ${filePath}`);
    process.exit(1);
  }
  
  // 检查年龄
  if (!isOldLog(filePath)) {
    const stats = fs.statSync(filePath);
    const ageDays = Math.floor((Date.now() - stats.mtime.getTime()) / (1000 * 60 * 60 * 24));
    console.log(`⏭️  跳过: ${path.basename(filePath)} (${ageDays}天 < ${DAYS_TO_KEEP}天)`);
    return;
  }
  
  // 读取日志
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').length;
  const fileName = path.basename(filePath);
  const timestamp = new Date().toISOString().split('T')[0];
  
  console.log('\n📦 AI 日志压缩');
  console.log('='.repeat(60));
  console.log(`📄 文件: ${fileName}`);
  console.log(`📊 原行数: ${lines}`);
  console.log(`📅 年龄: >${DAYS_TO_KEEP}天`);
  console.log('-'.repeat(60));
  
  // 准备 prompt
  const logSample = content.substring(0, 3000); // 前3000字符
  
  const prompt = `请分析以下日志文件，提取关键信息生成记忆条目。

**文件**: ${fileName}
**日期**: ${timestamp}
**原始行数**: ${lines}

**任务**:
1. 从日志中提取有价值的信息：错误、完成的功能、关键决策、重要发现
2. 忽略：常规输出、调试信息、重复的时间戳
3. 生成不超过15条记忆条目
4. 每条格式: - [P1或P2][${timestamp}] 一句话总结
   - P1: 错误、关键问题、重要决策
   - P2: 完成的功能、一般信息

**日志内容**:
\`\`\`
${logSample}
${content.length > 3000 ? '\n... (日志截断，共 ' + content.length + ' 字符)' : ''}
\`\`\`

请直接输出记忆条目，每行一条：
- [P2][${timestamp}] xxxx
- [P1][${timestamp}] xxxx

只输出记忆条目，不要有其他内容。`;

  // 调用 AI
  let essence = [];
  try {
    const response = await askAI(prompt);
    // 解析 AI 返回的记忆条目
    essence = response.split('\n')
      .map(line => line.trim())
      .filter(line => line.startsWith('- [P') && line.includes(']['));
    
    if (essence.length === 0) {
      throw new Error('AI 未返回有效的记忆条目');
    }
  } catch (e) {
    console.log(`   ⚠️  AI 分析失败: ${e.message}`);
    console.log('   跳过此文件');
    return;
  }
  
  console.log(`✨ 提取精华: ${essence.length} 条`);
  console.log(`📉 压缩比: 1:${Math.floor(lines / essence.length)}`);
  
  // 显示精华
  console.log('\n📝 AI 提取的精华:');
  for (const line of essence.slice(0, 10)) {
    console.log(`   ${line.substring(0, 80)}${line.length > 80 ? '...' : ''}`);
  }
  if (essence.length > 10) {
    console.log(`   ... 还有 ${essence.length - 10} 条`);
  }
  
  // 执行操作
  if (args.apply) {
    console.log('\n💾 正在执行...');
    
    // 确保归档目录
    if (!fs.existsSync(ARCHIVE_DIR)) {
      fs.mkdirSync(ARCHIVE_DIR, { recursive: true });
    }
    
    // 追加到记忆文件
    const memoryContent = fs.existsSync(MEMORY_FILE) 
      ? fs.readFileSync(MEMORY_FILE, 'utf-8') 
      : '';
    
    const essenceBlock = [
      '',
      `## 日志精华 - ${fileName} (${timestamp})`,
      ''
    ].concat(essence).concat(['']);
    
    fs.writeFileSync(MEMORY_FILE, memoryContent + essenceBlock.join('\n'));
    console.log(`✅ 已追加到: ${MEMORY_FILE}`);
    
    // 归档原文
    const archiveName = `${fileName}.${timestamp}.bak`;
    const archivePath = path.join(ARCHIVE_DIR, archiveName);
    fs.renameSync(filePath, archivePath);
    console.log(`✅ 已归档到: ${archivePath}`);
    
    console.log('\n✨ AI 压缩完成！');
  } else {
    console.log('\n🔍 预览模式 - 未实际执行（加 --apply 执行）');
  }
}

// 运行
main().catch(err => {
  console.error('❌ 错误:', err.message);
  process.exit(1);
});
