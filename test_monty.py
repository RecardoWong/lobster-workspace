#!/usr/bin/env python3
"""
🧪 Pydantic Monty 测试脚本
演示如何用 Monty 安全执行 AI 生成的代码
"""

import pydantic_monty
import time

# 示例1: 简单计算
def test_basic():
    print("=" * 50)
    print("测试1: 简单计算")
    print("=" * 50)
    
    code = """
x = a + b
x * 2
"""
    
    m = pydantic_monty.Monty(code, inputs=['a', 'b'])
    result = m.run(inputs={'a': 21, 'b': 21})
    
    print(f"代码: {code.strip()}")
    print(f"输入: a=21, b=21")
    print(f"输出: {result}")  # 应该是 84
    print()

# 示例2: 分析 Meme 币数据（模拟）
def test_meme_analysis():
    print("=" * 50)
    print("测试2: Meme币数据分析")
    print("=" * 50)
    
    code = """
# 计算平均 holder 数
total = sum(token['holders'] for token in tokens)
avg = total / len(tokens)

# 找出 holder 最多的币 (不用 max() key)
max_holders = 0
max_symbol = ''
for t in tokens:
    if t['holders'] > max_holders:
        max_holders = t['holders']
        max_symbol = t['symbol']

# 统计叙事类型
narratives = {}
for t in tokens:
    nar = t.get('narrative', '其他')
    narratives[nar] = narratives.get(nar, 0) + 1

{
    'avg_holders': avg,
    'hottest_token': max_symbol,
    'hottest_holders': max_holders,
    'narrative_counts': narratives,
}
"""
    
    # 模拟代币数据
    tokens = [
        {'symbol': 'CMP', 'holders': 245, 'narrative': '敏感/争议'},
        {'symbol': 'INU', 'holders': 206, 'narrative': '动物+金融'},
        {'symbol': 'DIGLETT', 'holders': 181, 'narrative': '游戏/动漫'},
        {'symbol': 'POPE', 'holders': 174, 'narrative': '宗教/信仰'},
        {'symbol': 'CLAIRE', 'holders': 102, 'narrative': 'AI科技'},
    ]
    
    m = pydantic_monty.Monty(code, inputs=['tokens'])
    
    start = time.time()
    result = m.run(inputs={'tokens': tokens})
    elapsed = (time.time() - start) * 1000
    
    print(f"代码: 分析 {len(tokens)} 个代币")
    print(f"执行时间: {elapsed:.3f} ms")
    print(f"结果:")
    print(f"  - 平均 holders: {result['avg_holders']:.1f}")
    print(f"  - 最热门: {result['hottest_token']} ({result['hottest_holders']} holders)")
    print(f"  - 叙事分布: {result['narrative_counts']}")
    print()

# 示例3: 外部函数调用（模拟 LLM 调用）
def test_external_function():
    print("=" * 50)
    print("测试3: 外部函数调用")
    print("=" * 50)
    
    code = """
# 调用外部函数获取数据
price = get_price(symbol)
double = price * 2

# 条件判断
if double > 100:
    result = f'{symbol} 翻倍后超过100: {double}'
else:
    result = f'{symbol} 翻倍后: {double}'

result
"""
    
    # 定义外部函数
    def get_price(symbol: str) -> float:
        prices = {'BTC': 50000, 'ETH': 3000, 'SOL': 100}
        return prices.get(symbol, 0)
    
    m = pydantic_monty.Monty(
        code,
        inputs=['symbol'],
        external_functions=['get_price']
    )
    
    start = time.time()
    result = m.run(
        inputs={'symbol': 'SOL'},
        external_functions={'get_price': get_price}
    )
    elapsed = (time.time() - start) * 1000
    
    print(f"代码: 查询价格并翻倍")
    print(f"执行时间: {elapsed:.3f} ms")
    print(f"结果: {result}")
    print()

# 示例4: 序列化状态（暂停和恢复）
def test_serialization():
    print("=" * 50)
    print("测试4: 序列化状态（暂停/恢复）")
    print("=" * 50)
    
    code = """
step1 = x * 2
# 这里会暂停，等待外部数据
step2 = fetch_data(step1)
step2 + 10
"""
    
    def fetch_data(val: int) -> int:
        # 模拟 API 调用
        return val + 100
    
    m = pydantic_monty.Monty(
        code,
        inputs=['x'],
        external_functions=['fetch_data']
    )
    
    # 开始执行 - 会在 fetch_data 处暂停
    progress = m.start(inputs={'x': 5})
    
    print(f"状态类型: {type(progress).__name__}")
    print(f"暂停在函数: {progress.function_name}")
    print(f"参数: {progress.args}")
    
    # 执行 fetch_data
    return_val = fetch_data(*progress.args)
    print(f"fetch_data 返回: {return_val}")
    
    # 序列化测试（在恢复之前）
    state = progress.dump()
    print(f"状态序列化大小: {len(state)} bytes")
    
    # 恢复执行
    result = progress.resume(return_value=return_val)
    print(f"最终结果: {result.output}")
    print()

# 示例5: 性能对比
def test_performance():
    print("=" * 50)
    print("测试5: 性能对比 (Monty vs Python exec)")
    print("=" * 50)
    
    code = """
result = 0
for i in range(1000):
    result += i
result
"""
    
    # Monty 执行
    m = pydantic_monty.Monty(code)
    
    start = time.time()
    for _ in range(100):
        m.run()
    monty_time = (time.time() - start) * 1000 / 100
    
    # Python exec 执行
    start = time.time()
    for _ in range(100):
        exec(code)
    python_time = (time.time() - start) * 1000 / 100
    
    print(f"代码: 1+2+...+999")
    print(f"Monty 平均: {monty_time:.3f} ms")
    print(f"Python exec 平均: {python_time:.3f} ms")
    print(f"比例: Monty 是 Python 的 {monty_time/python_time:.2f}x")
    print()

# 示例6: 安全测试（尝试做危险操作）
def test_security():
    print("=" * 50)
    print("测试6: 安全测试（尝试危险操作）")
    print("=" * 50)
    
    # 尝试读取文件（应该失败）
    code = """
open('/etc/passwd').read()
"""
    
    try:
        m = pydantic_monty.Monty(code)
        result = m.run()
        print(f"❌ 安全测试失败: {result}")
    except Exception as e:
        print(f"✅ 安全测试通过: 无法读取文件")
        print(f"   错误: {type(e).__name__}")
    
    print()

if __name__ == "__main__":
    print("🚀 Pydantic Monty 测试开始\n")
    
    test_basic()
    test_meme_analysis()
    test_external_function()
    test_serialization()
    test_performance()
    test_security()
    
    print("=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)
