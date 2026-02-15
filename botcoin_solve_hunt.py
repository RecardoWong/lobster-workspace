import nacl.signing
import nacl.encoding
import json
import base64
import requests
import sys

# 密钥信息
public_key_b64 = "I63i+Wh945AS7G1XXjFtkFYdYVoFTYu2MuW1Z/GuFhs="
secret_key_b64 = "qNOatVx1pCaFAJp8BL9FVMCcng2GER7PKlg+GJrs97MjreL5aH3jkBLsbVdeMW2QVh1hWgVNi7Yy5bVn8a4WGw=="

# 解码密钥
public_key = base64.b64decode(public_key_b64)
secret_key_full = base64.b64decode(secret_key_b64)
seed = secret_key_full[:32]
signing_key = nacl.signing.SigningKey(seed)

# 获取答案参数
answer = sys.argv[1] if len(sys.argv) > 1 else "183"

# 构造解答交易
transaction = {
    "type": "solve",
    "huntId": 52,
    "answer": answer,
    "publicKey": public_key_b64,
    "timestamp": int(__import__('time').time() * 1000)
}

# 签名
message = json.dumps(transaction, separators=(',', ':'))
message_bytes = message.encode('utf-8')
signature = signing_key.sign(message_bytes)
signature_b64 = base64.b64encode(signature.signature).decode('utf-8')

print("=" * 60)
print(f"尝试解答「猎人之箭」谜题")
print(f"答案: {answer}")
print("=" * 60)

# 发送请求
url = "https://botcoin.farm/api/hunts/solve"
payload = {
    "transaction": transaction,
    "signature": signature_b64
}

print(f"\n发送请求到: {url}")

response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

print(f"\n状态码: {response.status_code}")
print(f"响应: {response.text}")

# 保存结果
result = {
    "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
    "action": "solve_hunt",
    "hunt_id": 52,
    "hunt_name": "The Hunter's Arrow",
    "answer": answer,
    "status_code": response.status_code,
    "response": response.json() if response.status_code == 200 else response.text
}

with open(f"botcoin_solve_result_{answer}.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"\n结果已保存到 botcoin_solve_result_{answer}.json")

# 检查是否成功
try:
    resp_json = response.json()
    if resp_json.get("correct"):
        print("\n✅ 答案正确！")
    else:
        print(f"\n❌ 答案错误")
        if "hint" in resp_json:
            print(f"提示: {resp_json['hint']}")
except:
    pass
