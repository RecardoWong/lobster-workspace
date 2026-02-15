#!/usr/bin/env python3
"""
智能数据库 - 替换txt文件
使用SQLite + 简单语义去重
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

class SmartDatabase:
    """智能数据库"""
    
    def __init__(self, db_path: str = "/tmp/clanker_smart.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 代币表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT UNIQUE NOT NULL,
                symbol TEXT,
                name TEXT,
                token_type TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                seen_count INTEGER DEFAULT 1,
                is_honeypot BOOLEAN DEFAULT 0,
                narrative TEXT,
                content_hash TEXT  -- 用于快速去重
            )
        ''')
        
        # 推文/内容表（用于Twitter监控）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,  -- twitter, clanker, etc.
                external_id TEXT,
                content TEXT,
                author TEXT,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP,
                content_hash TEXT UNIQUE,  -- 语义去重
                embedding TEXT  -- 预留向量字段
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_token_contract ON tokens(contract_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON contents(content_hash)')
        
        conn.commit()
        conn.close()
    
    def compute_hash(self, text: str) -> str:
        """计算内容哈希（简单语义指纹）"""
        # 简化：取前50个字符的小写+去除空格
        simplified = text.lower().replace(' ', '').replace('\n', '')[:50]
        return hashlib.md5(simplified.encode()).hexdigest()
    
    def add_token(self, contract: str, symbol: str, name: str, token_type: str, 
                  is_honeypot: bool = False, narrative: str = "") -> bool:
        """添加代币，自动去重"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在
            cursor.execute('SELECT id, seen_count FROM tokens WHERE contract_address = ?', 
                          (contract.lower(),))
            existing = cursor.fetchone()
            
            if existing:
                # 更新最后看到时间和计数
                cursor.execute('''
                    UPDATE tokens 
                    SET last_seen = CURRENT_TIMESTAMP, seen_count = seen_count + 1
                    WHERE contract_address = ?
                ''', (contract.lower(),))
                conn.commit()
                return False  # 已存在
            else:
                # 新代币
                content_hash = self.compute_hash(symbol + name + narrative)
                cursor.execute('''
                    INSERT INTO tokens (contract_address, symbol, name, token_type, 
                                       is_honeypot, narrative, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (contract.lower(), symbol, name, token_type, 
                      is_honeypot, narrative, content_hash))
                conn.commit()
                return True  # 新代币
                
        except Exception as e:
            print(f"数据库错误: {e}")
            return False
        finally:
            conn.close()
    
    def is_new_token(self, contract: str) -> bool:
        """检查是否为新代币"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM tokens WHERE contract_address = ?', 
                      (contract.lower(),))
        result = cursor.fetchone()
        
        conn.close()
        return result is None
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tokens')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tokens WHERE seen_count > 1')
        repeated = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tokens WHERE is_honeypot = 1')
        honeypots = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT symbol, seen_count FROM tokens 
            ORDER BY seen_count DESC LIMIT 5
        ''')
        hot_tokens = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_tokens': total,
            'repeated_tokens': repeated,
            'honeypot_count': honeypots,
            'hot_tokens': hot_tokens
        }
    
    def add_content(self, source: str, external_id: str, content: str, 
                    author: str, likes: int = 0) -> bool:
        """添加内容（Twitter推文等），自动去重"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            content_hash = self.compute_hash(content)
            
            # 检查是否已存在
            cursor.execute('SELECT 1 FROM contents WHERE content_hash = ?', (content_hash,))
            if cursor.fetchone():
                return False  # 已存在，去重
            
            cursor.execute('''
                INSERT INTO contents (source, external_id, content, author, 
                                     likes, created_at, content_hash)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (source, external_id, content, author, likes, content_hash))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"数据库错误: {e}")
            return False
        finally:
            conn.close()


def main():
    """测试"""
    db = SmartDatabase()
    
    # 测试添加代币
    is_new = db.add_token(
        contract="0x1234567890abcdef",
        symbol="TEST",
        name="Test Token",
        token_type="clanker_v4",
        is_honeypot=False,
        narrative="AI Agent"
    )
    print(f"新代币: {is_new}")
    
    # 查看统计
    stats = db.get_stats()
    print(f"\n统计: {stats}")


if __name__ == "__main__":
    main()
