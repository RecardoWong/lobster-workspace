#!/usr/bin/env python3
"""简单缓存系统 - 减少重复查询"""
import json
import time
from pathlib import Path

class SimpleCache:
    def __init__(self, cache_dir='/root/.openclaw/workspace/cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
        
    def get(self, key, ttl=300):
        """获取缓存，ttl=秒"""
        # 先查内存
        if key in self.memory_cache:
            data, ts = self.memory_cache[key]
            if time.time() - ts < ttl:
                return data
        
        # 再查文件
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                if time.time() - data.get('_ts', 0) < ttl:
                    return data.get('value')
        return None
    
    def set(self, key, value):
        """设置缓存"""
        # 内存缓存
        self.memory_cache[key] = (value, time.time())
        
        # 文件缓存
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump({'value': value, '_ts': time.time()}, f)

# 全局缓存实例
cache = SimpleCache()
