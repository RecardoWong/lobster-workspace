from web3 import Web3
import datetime

# BSC RPC endpoint
bsc_rpc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc_rpc))

# Wallet address
wallet_address = "0xf2BD3694E7B0505cEcC4317B3Da8F86D54d770DA"

# AGC Token contract address (from the mining script)
agc_contract = "0x09D1A98772225b4b11c36607926dca916C436Fe3"

# Standard ERC20 ABI for balanceOf
erc20_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

# Get BNB balance
bnb_balance = w3.eth.get_balance(wallet_address)
bnb_balance_eth = float(w3.from_wei(bnb_balance, 'ether'))

print(f"=== AgentCoin Mining Status ===")
print(f"📅 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"\n💼 Wallet: {wallet_address}")
print(f"🔷 BNB Balance: {bnb_balance_eth:.6f} BNB")

if bnb_balance_eth < 0.01:
    print(f"⚠️  ALERT: BNB余额低于0.01！需要充值！")
else:
    print(f"✅ BNB余额充足 (可挖约 {int(bnb_balance_eth / 0.005)} 次)")

# Get AGC balance
try:
    token_contract = w3.eth.contract(address=agc_contract, abi=erc20_abi)
    agc_balance = token_contract.functions.balanceOf(wallet_address).call()
    decimals = token_contract.functions.decimals().call()
    symbol = token_contract.functions.symbol().call()
    agc_formatted = agc_balance / (10 ** decimals)
    print(f"🪙 {symbol} Balance: {agc_formatted:,.2f} {symbol}")
except Exception as e:
    print(f"❌ 无法获取AGC余额: {e}")

print(f"\n=== Mining Process ===")
