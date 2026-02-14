from web3 import Web3
import json

# BSC RPC endpoint
bsc_rpc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc_rpc))

# Wallet address
wallet_address = "0xf2BD3694E7B0505cEcC4317B3Da8F86D54d770DA"

# Check BNB balance
bnb_balance = w3.eth.get_balance(wallet_address)
bnb_balance_eth = w3.from_wei(bnb_balance, 'ether')

print(f"=== Wallet Status ===")
print(f"Address: {wallet_address}")
print(f"BNB Balance: {bnb_balance_eth:.6f} BNB")

# AGC Token contract (AgentCoin) - need to verify this
# Common pattern for BEP-20 tokens
agc_contract_address = None  # Will need to find this

print(f"\nBNB Balance Check: {'PASS' if bnb_balance_eth >= 0.01 else 'LOW - Need recharge!'}")
