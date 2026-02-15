import os
import time
import json
import logging
from datetime import datetime
from web3 import Web3
from eth_account import Account

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agentcoin_mining.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
PRIVATE_KEY = "0x4a8d58943a9695cbb5d85fd94066d10fc52806c56c9dd17cf5b0499019452cf6"
WALLET_ADDRESS = "0xf2BD3694E7B0505cEcC4317B3Da8F86D54d770DA"
BSC_RPC = "https://bsc-dataseed.binance.org/"
MIN_BNB_THRESHOLD = 0.01

# Contract addresses
MINING_CONTRACT = "0x09D1A98772225b4b11c36607926dca916C436Fe3"
AGC_TOKEN = "0x72Af2068Cc5430388CD7653767A22d74134866Ea"

# Contract ABIs
MINING_ABI = [
    {'inputs': [], 'name': 'agentCoin', 'outputs': [{'internalType': 'contract IERC20', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [{'internalType': 'address', 'name': 'wallet', 'type': 'address'}], 'name': 'canMine', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [{'internalType': 'address', 'name': 'wallet', 'type': 'address'}], 'name': 'activated', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [{'internalType': 'address', 'name': 'wallet', 'type': 'address'}], 'name': 'cooldownRemaining', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'miningEnabled', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'TOKENS_PER_MINE', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'MINE_PRICE', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'totalMined', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'},
]

ERC20_ABI = [
    {'constant': True, 'inputs': [{'name': '_owner', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'name': 'balance', 'type': 'uint256'}], 'type': 'function'},
    {'constant': True, 'inputs': [], 'name': 'decimals', 'outputs': [{'name': '', 'type': 'uint8'}], 'type': 'function'},
    {'constant': True, 'inputs': [], 'name': 'symbol', 'outputs': [{'name': '', 'type': 'string'}], 'type': 'function'},
]

def get_web3():
    """Get Web3 connection"""
    w3 = Web3(Web3.HTTPProvider(BSC_RPC))
    if not w3.is_connected():
        logger.error("Failed to connect to BSC network")
        return None
    return w3

def check_balances(w3, wallet_address):
    """Check BNB and AGC balances"""
    results = {}
    
    # Check BNB balance
    try:
        balance_wei = w3.eth.get_balance(wallet_address)
        results['bnb'] = float(w3.from_wei(balance_wei, 'ether'))
    except Exception as e:
        logger.error(f"Error checking BNB balance: {e}")
        results['bnb'] = None
    
    # Check AGC balance
    try:
        agc_contract = w3.eth.contract(address=AGC_TOKEN, abi=ERC20_ABI)
        balance = agc_contract.functions.balanceOf(wallet_address).call()
        decimals = agc_contract.functions.decimals().call()
        results['agc'] = balance / (10 ** decimals)
    except Exception as e:
        logger.error(f"Error checking AGC balance: {e}")
        results['agc'] = None
    
    return results

def check_mining_status(w3, wallet_address):
    """Check mining contract status"""
    results = {}
    
    try:
        mining_contract = w3.eth.contract(address=MINING_CONTRACT, abi=MINING_ABI)
        
        results['activated'] = mining_contract.functions.activated(wallet_address).call()
        results['can_mine'] = mining_contract.functions.canMine(wallet_address).call()
        results['cooldown_remaining'] = mining_contract.functions.cooldownRemaining(wallet_address).call()
        results['mining_enabled'] = mining_contract.functions.miningEnabled().call()
        
        tokens_per_mine = mining_contract.functions.TOKENS_PER_MINE().call()
        results['tokens_per_mine'] = tokens_per_mine / (10 ** 18)
        
        mine_price = mining_contract.functions.MINE_PRICE().call()
        results['mine_price'] = float(w3.from_wei(mine_price, 'ether'))
        
        total_mined = mining_contract.functions.totalMined().call()
        results['total_mined'] = total_mined / (10 ** 18)
        
    except Exception as e:
        logger.error(f"Error checking mining status: {e}")
        results = {'error': str(e)}
    
    return results

def print_status_report(balances, mining_status):
    """Print formatted status report"""
    print("\n" + "=" * 60)
    print("🪙 AGENTCOIN MINING STATUS REPORT")
    print("=" * 60)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"👛 Wallet: {WALLET_ADDRESS}")
    print("-" * 60)
    
    # Balance Section
    print("💰 BALANCES:")
    if balances.get('bnb') is not None:
        bnb_status = "✅" if balances['bnb'] >= MIN_BNB_THRESHOLD else "⚠️ LOW"
        print(f"   BNB: {balances['bnb']:.6f} BNB {bnb_status}")
        if balances['bnb'] < MIN_BNB_THRESHOLD:
            print(f"   ⚠️  WARNING: BNB balance below {MIN_BNB_THRESHOLD} threshold!")
            print(f"   💡 Action needed: Recharge BNB for gas fees")
    else:
        print("   BNB: Error fetching balance")
    
    if balances.get('agc') is not None:
        print(f"   AGC: {balances['agc']:,.2f} AGC")
    else:
        print("   AGC: Error fetching balance")
    
    print("-" * 60)
    
    # Mining Status Section
    print("⛏️  MINING STATUS:")
    if 'error' not in mining_status:
        print(f"   Wallet Activated: {'✅ Yes' if mining_status.get('activated') else '❌ No'}")
        print(f"   Mining Enabled: {'✅ Yes' if mining_status.get('mining_enabled') else '❌ No'}")
        print(f"   Can Mine Now: {'✅ Yes' if mining_status.get('can_mine') else '❌ No'}")
        
        cooldown = mining_status.get('cooldown_remaining', 0)
        if cooldown > 0:
            mins, secs = divmod(cooldown, 60)
            print(f"   Cooldown: ⏱️  {mins}m {secs}s remaining")
        
        print(f"   Reward per Mine: {mining_status.get('tokens_per_mine', 0):,.0f} AGC")
        print(f"   Cost per Mine: {mining_status.get('mine_price', 0):.4f} BNB")
        print(f"   Total Network Mined: {mining_status.get('total_mined', 0):,.0f} AGC")
        
        # Estimated mines remaining
        if balances.get('bnb') and mining_status.get('mine_price'):
            mines_remaining = int(balances['bnb'] / mining_status['mine_price'])
            print(f"   Estimated Mines Left: ~{mines_remaining}")
    else:
        print(f"   Error: {mining_status.get('error')}")
    
    print("=" * 60)

def main():
    logger.info("=" * 60)
    logger.info("AgentCoin Mining Monitor Started")
    logger.info(f"Wallet: {WALLET_ADDRESS}")
    logger.info(f"Mining Contract: {MINING_CONTRACT}")
    logger.info(f"AGC Token: {AGC_TOKEN}")
    logger.info("=" * 60)
    
    w3 = get_web3()
    if not w3:
        logger.error("Cannot connect to BSC. Exiting.")
        return
    
    # Single status check (for cron job)
    logger.info("Checking status...")
    balances = check_balances(w3, WALLET_ADDRESS)
    mining_status = check_mining_status(w3, WALLET_ADDRESS)
    print_status_report(balances, mining_status)
    
    # Save status to JSON for external use
    status_data = {
        'timestamp': datetime.now().isoformat(),
        'wallet': WALLET_ADDRESS,
        'balances': balances,
        'mining_status': mining_status
    }
    
    with open('mining_status.json', 'w') as f:
        json.dump(status_data, f, indent=2)
    
    logger.info("Status saved to mining_status.json")
    
    # Check for low BNB alert
    if balances.get('bnb') is not None and balances['bnb'] < MIN_BNB_THRESHOLD:
        logger.warning(f"⚠️ ALERT: BNB balance ({balances['bnb']:.6f}) below threshold ({MIN_BNB_THRESHOLD})")
        print(f"\n🚨 ALERT: BNB balance is low! Please recharge.")
        return 1  # Exit with error code for alerting
    
    return 0

if __name__ == "__main__":
    exit(main())
