import nacl.signing
import nacl.encoding
import json
import base64
import requests

# 密钥信息
public_key_b64 = "I63i+Wh945AS7G1XXjFtkFYdYVoFTYu2MuW1Z/GuFhs="
secret_key_b64 = "qNOatVx1pCaFAJp8BL9FVMCcng2GER7PKlg+GJrs97MjreL5aH3jkBLsbVdeMW2QVh1hWgVNi7Yy5bVn8a4WGw=="

# 解码密钥
public_key = base64.b64decode(public_key_b64)
secret_key_full = base64.b64decode(secret_key_b64)

# Ed25519: 前32字节是seed，后32字节是公钥
seed = secret_key_full[:32]

# 创建签名密钥对象
signing_key = nacl.signing.SigningKey(seed)

# 尝试选择 "The Hunter's Arrow" 谜题 (id: 52)
transaction = {
    "type": "pick",
    "huntId": 52,
    "publicKey": public_key_b64,
    "timestamp": int(__import__('time').time() * 1000)
}

# 将交易转为JSON并编码
message = json.dumps(transaction, separators=(',', ':'))
message_bytes = message.encode('utf-8')

# 签名
signature = signing_key.sign(message_bytes)
signature_b64 = base64.b64encode(signature.signature).decode('utf-8')

print("=" * 60)
print("尝试选择「猎人之箭」谜题")
print("=" * 60)
print(f"\n交易内容: {message}")
print(f"\n签名: {signature_b64}")

# 发送请求
url = "https://botcoin.farm/api/hunts/pick"
payload = {
    "transaction": transaction,
    "signature": signature_b64
}

print(f"\n发送请求到: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

print(f"\n状态码: {response.status_code}")
print(f"响应: {response.text}")

# 保存结果
result = {
    "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
    "action": "pick_hunt",
    "hunt_id": 52,
    "hunt_name": "The Hunter's Arrow",
    "transaction": transaction,
    "signature": signature_b64,
    "status_code": response.status_code,
    "response": response.json() if response.status_code == 200 else response.text
}

with open("botcoin_hunt_result.json", "w") as f:
    json.dump(result, f, indent=2)

print("\n结果已保存到 botcoin_hunt_result.json")
