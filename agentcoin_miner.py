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

# AgentCoin Mining Contract (to be updated with actual contract)
MINING_CONTRACT = None  # Will search for the correct contract

def get_web3():
    """Get Web3 connection"""
    w3 = Web3(Web3.HTTPProvider(BSC_RPC))
    if not w3.is_connected():
        logger.error("Failed to connect to BSC network")
        return None
    return w3

def check_bnb_balance(w3, address):
    """Check BNB balance"""
    try:
        balance_wei = w3.eth.get_balance(address)
        balance_bnb = w3.from_wei(balance_wei, 'ether')
        return float(balance_bnb)
    except Exception as e:
        logger.error(f"Error checking BNB balance: {e}")
        return None

def check_agc_balance(w3, address):
    """Check AGC token balance"""
    # Standard ERC20 balanceOf function signature
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
        }
    ]
    
    # AgentCoin contract address (need to find correct one)
    agc_contracts_to_try = [
        "0x0000000000000000000000000000000000000000",  # Placeholder - will be updated
    ]
    
    for contract_addr in agc_contracts_to_try:
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(contract_addr), abi=erc20_abi)
            balance = contract.functions.balanceOf(address).call()
            decimals = contract.functions.decimals().call()
            return balance / (10 ** decimals)
        except:
            continue
    
    return None

def mine_agc(w3, account):
    """Submit mining transaction"""
    try:
        # This is a placeholder - actual mining depends on AgentCoin's specific mechanism
        # Most "mining" on BSC is actually staking or interacting with a smart contract
        
        nonce = w3.eth.get_transaction_count(account.address)
        
        # Simple transaction to self (placeholder for actual mining)
        tx = {
            'nonce': nonce,
            'to': account.address,
            'value': 0,
            'gas': 21000,
            'gasPrice': w3.to_wei('5', 'gwei'),
            'chainId': 56
        }
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Mining transaction sent: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt['status'] == 1:
            logger.info(f"Transaction successful: {tx_hash.hex()}")
            return True
        else:
            logger.error(f"Transaction failed: {tx_hash.hex()}")
            return False
            
    except Exception as e:
        logger.error(f"Error in mining: {e}")
        return False

def main():
    logger.info("=" * 50)
    logger.info("AgentCoin Mining Bot Started")
    logger.info(f"Wallet: {WALLET_ADDRESS}")
    logger.info("=" * 50)
    
    w3 = get_web3()
    if not w3:
        logger.error("Cannot connect to BSC. Exiting.")
        return
    
    account = Account.from_key(PRIVATE_KEY)
    logger.info(f"Account loaded: {account.address}")
    
    # Check initial balances
    bnb_balance = check_bnb_balance(w3, account.address)
    logger.info(f"Current BNB Balance: {bnb_balance:.6f} BNB")
    
    if bnb_balance < MIN_BNB_THRESHOLD:
        logger.warning(f"⚠️ BNB balance ({bnb_balance:.6f}) is below threshold ({MIN_BNB_THRESHOLD})!")
        logger.warning("Please recharge BNB for gas fees.")
    
    agc_balance = check_agc_balance(w3, account.address)
    if agc_balance is not None:
        logger.info(f"Current AGC Balance: {agc_balance:.6f} AGC")
    else:
        logger.warning("Could not determine AGC balance - contract address may need updating")
    
    # Mining loop
    logger.info("Starting mining loop...")
    while True:
        try:
            # Re-check BNB balance periodically
            bnb_balance = check_bnb_balance(w3, account.address)
            
            if bnb_balance < MIN_BNB_THRESHOLD:
                logger.warning(f"⚠️ BNB balance ({bnb_balance:.6f}) is below threshold ({MIN_BNB_THRESHOLD})!")
                logger.warning("Waiting for BNB recharge...")
                time.sleep(300)  # Wait 5 minutes before checking again
                continue
            
            if bnb_balance < 0.001:
                logger.error("BNB balance too low for any transactions. Stopping.")
                break
            
            # Attempt mining
            logger.info("Attempting to mine AGC...")
            success = mine_agc(w3, account)
            
            if success:
                # Update AGC balance
                agc_balance = check_agc_balance(w3, account.address)
                if agc_balance is not None:
                    logger.info(f"Updated AGC Balance: {agc_balance:.6f} AGC")
            
            # Wait before next attempt
            logger.info("Waiting 60 seconds before next mining attempt...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("Mining stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
