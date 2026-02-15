#!/usr/bin/env python3
"""
🦞 Lobster Dashboard - 监控系统仪表板
自动生成HTML报告，展示所有监控任务状态
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import subprocess

class DashboardGenerator:
    """Dashboard生成器"""
    
    def __init__(self):
        self.output_dir = "/root/.openclaw/workspace/dashboard"
        self.data_file = f"{self.output_dir}/data.json"
        self.html_file = f"{self.output_dir}/index.html"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_cron_status(self) -> List[Dict]:
        """获取定时任务状态"""
        try:
            result = subprocess.run(
                ['openclaw', 'cron', 'list', '--json'],
                capture_output=True, text=True, timeout=10
            )
            data = json.loads(result.stdout)
            jobs = []
            for job in data.get('jobs', []):
                state = job.get('state', {})
                jobs.append({
                    'name': job.get('name', 'Unknown'),
                    'enabled': job.get('enabled', False),
                    'next_run': self._format_time(state.get('nextRunAtMs')),
                    'last_run': self._format_time(state.get('lastRunAtMs')),
                    'last_status': state.get('lastStatus', 'unknown'),
                    'schedule': job.get('schedule', {}).get('expr', '-')
                })
            return jobs
        except Exception as e:
            print(f"获取cron状态失败: {e}")
            return []
    
    def _format_time(self, ms: int) -> str:
        """格式化时间戳"""
        if not ms:
            return '-'
        dt = datetime.fromtimestamp(ms / 1000)
        return dt.strftime('%m-%d %H:%M')
    
    def get_latest_scan(self) -> Dict:
        """获取最新扫描结果"""
        try:
            # 读取最新的扫描报告
            files = sorted([f for f in os.listdir('/tmp') if f.startswith('xxyy_monty_')])
            if files:
                with open(f'/tmp/{files[-1]}', 'r') as f:
                    return {
                        'time': files[-1].replace('xxyy_monty_', '').replace('.txt', ''),
                        'content': f.read()[:1000]
                    }
        except Exception as e:
            pass
        return {'time': '-', 'content': '暂无数据'}
    
    def generate_html(self) -> str:
        """生成HTML Dashboard"""
        cron_jobs = self.get_cron_status()
        latest_scan = self.get_latest_scan()
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦞 Lobster Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            color: #fff;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #1e3a5f;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .time {{
            color: #888;
            font-size: 0.9em;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        .card {{
            background: #151b3d;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #1e3a5f;
        }}
        .card h2 {{
            color: #4fc3f7;
            margin-bottom: 15px;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .status {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }}
        .status.ok {{ background: #4caf50; }}
        .status.error {{ background: #f44336; }}
        .status.pending {{ background: #ff9800; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
        }}
        th, td {{
            padding: 10px 8px;
            text-align: left;
            border-bottom: 1px solid #1e3a5f;
        }}
        th {{
            color: #888;
            font-weight: 500;
        }}
        tr:hover {{
            background: #1a2342;
        }}
        .tag {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            background: #1e3a5f;
        }}
        .tag.success {{ background: #2e7d32; }}
        .tag.error {{ background: #c62828; }}
        .scan-preview {{
            background: #0d1229;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Consolas', monospace;
            font-size: 0.85em;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
            color: #a0a0a0;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #4fc3f7;
        }}
        .stat-label {{
            color: #888;
            font-size: 0.85em;
        }}
        .refresh {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #4fc3f7;
            color: #0a0e27;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }}
        .refresh:hover {{
            background: #29b6f6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦞 Lobster Dashboard</h1>
        <div class="time">更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
    
    <div class="grid">
        <!-- 定时任务状态 -->
        <div class="card">
            <h2>⏰ 定时任务状态</h2>
            <table>
                <tr>
                    <th>任务</th>
                    <th>状态</th>
                    <th>下次运行</th>
                    <th>上次状态</th>
                </tr>
'''
        
        for job in cron_jobs:
            status_class = 'ok' if job['last_status'] == 'success' else 'error' if job['last_status'] == 'error' else 'pending'
            tag_class = 'success' if job['last_status'] == 'success' else 'error' if job['last_status'] == 'error' else ''
            html += f'''
                <tr>
                    <td>{job['name']}</td>
                    <td><span class="status {status_class}"></span>{'启用' if job['enabled'] else '禁用'}</td>
                    <td>{job['next_run']}</td>
                    <td><span class="tag {tag_class}">{job['last_status']}</span></td>
                </tr>
'''
        
        html += f'''
            </table>
        </div>
        
        <!-- 监控统计 -->
        <div class="card">
            <h2>📊 监控统计</h2>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">4</div>
                    <div class="stat-label">定时任务</div>
                </div>
                <div class="stat">
                    <div class="stat-value">🧠</div>
                    <div class="stat-label">Monty AI</div>
                </div>
                <div class="stat">
                    <div class="stat-value">✅</div>
                    <div class="stat-label">运行中</div>
                </div>
            </div>
            <div style="margin-top: 20px;">
                <p>🪙 XXYY.io: 每30分钟 (MC≥$35K)</p>
                <p>🐦 TwitterAPI.io: 每8小时</p>
                <p>📊 英诺赛科: 每天09:15</p>
                <p>🌅 美股简报: 每天06:00</p>
            </div>
        </div>
        
        <!-- 最新扫描结果 -->
        <div class="card" style="grid-column: 1 / -1;">
            <h2>🪙 最新XXYY.io扫描</h2>
            <p style="color: #888; margin-bottom: 10px;">扫描时间: {latest_scan['time']}</p>
            <div class="scan-preview">{latest_scan['content']}</div>
        </div>
        
        <!-- Monty AI状态 -->
        <div class="card">
            <h2>🧠 Monty AI 状态</h2>
            <p>✅ 正常运行</p>
            <p style="margin-top: 10px; color: #888;">已集成功能:</p>
            <ul style="margin-left: 20px; color: #a0a0a0;">
                <li>Meme币分析 (0.4ms)</li>
                <li>情绪分析 (0.1ms)</li>
                <li>异常检测 (0.5ms)</li>
                <li>投资组合分析 (0.4ms)</li>
            </ul>
        </div>
        
        <!-- 快速链接 -->
        <div class="card">
            <h2>🔗 快速链接</h2>
            <p><a href="https://github.com/RecardoWong/lobster-workspace" style="color: #4fc3f7;">GitHub仓库</a></p>
            <p style="margin-top: 10px;"><a href="https://clawhub.com" style="color: #4fc3f7;">ClawHub技能市场</a></p>
            <p style="margin-top: 10px;"><a href="https://moltbook.com" style="color: #4fc3f7;">Moltbook AI社交</a></p>
        </div>
    </div>
    
    <button class="refresh" onclick="location.reload()">🔄 刷新</button>
    
    <script>
        // 自动刷新 (每60秒)
        setTimeout(() => location.reload(), 60000);
    </script>
</body>
</html>
'''
        return html
    
    def generate(self):
        """生成Dashboard"""
        html = self.generate_html()
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Dashboard已生成: {self.html_file}")
        return self.html_file


if __name__ == "__main__":
    dashboard = DashboardGenerator()
    dashboard.generate()
