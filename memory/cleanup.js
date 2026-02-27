#!/usr/bin/env node
/**
 * 记忆淘汰脚本 (Node.js 版本)
 * 
 * 用法:
 *   node cleanup.js MEMORY.md                    # 预览模式
 *   node cleanup.js MEMORY.md --apply            # 实际执行
 *   node cleanup.js MEMORY.md --archive archive.md --apply
 */

const fs = require('fs');
const path = require('path');

// 配置
const RETENTION = {
  P0: null,   // 永不淘汰
  P1: 90,     // 90天
  P2: 30      // 30天
};

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    file: null,
    archive: 'archive.md',
    apply: false,
    dryRun: true,  // 默认是预览模式
    before: null   // 参考日期
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--archive' && i + 1 < args.length) {
      result.archive = args[i + 1];
      i++;
    } else if (args[i] === '--before' && i + 1 < args.length) {
      result.before = args[i + 1];
      i++;
    } else if (args[i] === '--apply') {
      result.apply = true;
      result.dryRun = false;
    } else if (args[i] === '--dry-run') {
      result.dryRun = true;
      result.apply = false;
    } else if (!args[i].startsWith('--')) {
      result.file = args[i];
    }
  }

  return result;
}

// 解析记忆条目
function parseEntry(line) {
  const pattern = /\[(P[0-2])\]\[(\d{4}-\d{2}-\d{2})\]/;
  const match = line.match(pattern);
  
  if (match) {
    const priority = match[1];
    const dateStr = match[2];
    const date = new Date(dateStr);
    
    if (!isNaN(date.getTime())) {
      return {
        line: line,
        priority: priority,
        date: date,
        rawDate: dateStr,
        isEntry: true
      };
    }
  }
  
  return { line, isEntry: false };
}

// 判断是否过期
function isExpired(entry, referenceDate) {
  if (entry.priority === 'P0') return false;
  
  const days = RETENTION[entry.priority];
  if (days === null) return false;
  
  const age = Math.floor((referenceDate - entry.date) / (1000 * 60 * 60 * 24));
  return age > days;
}

// 主函数
async function main() {
  const args = parseArgs();
  
  if (!args.file) {
    console.error('❌ 错误: 请指定记忆文件路径');
    console.error('用法: node cleanup.js MEMORY.md [--apply] [--archive archive.md] [--before YYYY-MM-DD]');
    process.exit(1);
  }
  
  // 设置参考日期
  let referenceDate;
  if (args.before) {
    referenceDate = new Date(args.before);
    if (isNaN(referenceDate.getTime())) {
      console.error(`❌ 错误: 无效日期格式: ${args.before}`);
      console.error('日期格式应为: YYYY-MM-DD');
      process.exit(1);
    }
  } else {
    referenceDate = new Date();
  }
  
  // 安全提示
  if (args.apply) {
    console.log('⚠️  警告: 你正在执行实际淘汰操作！');
    console.log('   建议先运行预览模式检查会淘汰什么。\n');
  } else {
    console.log('🔍 预览模式 - 不会实际删除任何内容');
    console.log('   确认无误后加 --apply 执行\n');
  }
  
  console.log('🧹 记忆淘汰脚本启动 (Node.js)');
  console.log(`📅 参考日期: ${referenceDate.toISOString().split('T')[0]}`);
  console.log(`📋 规则: P0=永久, P1=90天, P2=30天`);
  console.log('='.repeat(60));
  
  // 读取文件
  let content;
  try {
    content = fs.readFileSync(args.file, 'utf-8');
  } catch (err) {
    console.error(`❌ 无法读取文件: ${args.file}`);
    console.error(err.message);
    process.exit(1);
  }
  
  const lines = content.split('\n');
  
  // 分类
  const keep = [];
  const archive = [];
  const stats = {
    total: 0,
    P0: { keep: 0, archive: 0 },
    P1: { keep: 0, archive: 0 },
    P2: { keep: 0, archive: 0 }
  };
  
  for (const line of lines) {
    const entry = parseEntry(line);
    stats.total++;
    
    if (entry.isEntry) {
      if (isExpired(entry, referenceDate)) {
        archive.push(entry);
        stats[entry.priority].archive++;
      } else {
        keep.push(entry.line);
        stats[entry.priority].keep++;
      }
    } else {
      // 非条目行保留
      keep.push(line);
    }
  }
  
  // 输出统计
  console.log(`\n📊 淘汰统计 (${path.basename(args.file)}):`);
  console.log('-'.repeat(60));
  console.log(`  原文件总行数: ${stats.total}`);
  console.log(`  P0条目: ${stats.P0.keep + stats.P0.archive} (保留 ${stats.P0.keep}, 归档 ${stats.P0.archive})`);
  console.log(`  P1条目: ${stats.P1.keep + stats.P1.archive} (保留 ${stats.P1.keep}, 归档 ${stats.P1.archive})`);
  console.log(`  P2条目: ${stats.P2.keep + stats.P2.archive} (保留 ${stats.P2.keep}, 归档 ${stats.P2.archive})`);
  console.log('-'.repeat(60));
  console.log(`  保留行数: ${keep.length}`);
  console.log(`  归档行数: ${archive.length}`);
  console.log('-'.repeat(60));
  
  // 显示归档条目
  if (archive.length > 0) {
    console.log('\n🗂️  归档条目:');
    for (const e of archive.slice(0, 5)) {
      const preview = e.line.trim().substring(0, 50) + (e.line.length > 50 ? '...' : '');
      console.log(`   [${e.priority}][${e.rawDate}]`);
      console.log(`      ${preview}`);
    }
    if (archive.length > 5) {
      console.log(`   ... 还有 ${archive.length - 5} 条`);
    }
    console.log();
  }
  
  // 执行操作
  if (args.apply) {
    try {
      // 备份原文件
      const backupPath = `${args.file}.bak`;
      fs.writeFileSync(backupPath, content);
      
      // 写回记忆文件
      fs.writeFileSync(args.file, keep.join('\n'));
      
      // 追加到归档文件
      let archiveContent = '';
      if (fs.existsSync(args.archive)) {
        archiveContent = fs.readFileSync(args.archive, 'utf-8') + '\n';
      }
      
      const timestamp = referenceDate.toISOString().split('T')[0];
      archiveContent += `\n# 归档于 ${timestamp}\n\n`;
      archiveContent += archive.map(e => e.line).join('\n');
      
      fs.writeFileSync(args.archive, archiveContent);
      
      console.log(`✅ 已更新: ${args.file}`);
      console.log(`💾 已归档: ${args.archive} (${archive.length} 条)`);
      console.log(`💾 备份: ${backupPath}`);
    } catch (err) {
      console.error(`❌ 操作失败: ${err.message}`);
      process.exit(1);
    }
  } else {
    console.log('🔍 预览模式 - 未实际执行（加 --apply 执行）\n');
  }
}

// 运行
main().catch(err => {
  console.error('❌ 脚本错误:', err);
  process.exit(1);
});
