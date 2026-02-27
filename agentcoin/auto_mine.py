#!/usr/bin/env python3
"""
AgentCoin Auto-Miner - Continuous submission mode
"""

import os
import sys
import json
import time
import urllib.request
from web3 import Web3

AGENT_ID = 532
PRIVATE_KEY = os.getenv('AGC_PRIVATE_KEY')
RPC_URL = os.getenv('AGC_RPC_URL', 'https://mainnet.base.org')
PROBLEM_MANAGER = '0x7D563ae2881D2fC72f5f4c66334c079B4Cc051c6'

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address

print(f"🤖 AgentCoin Auto-Miner")
print(f"Agent ID: {AGENT_ID}")
print(f"Wallet: {address}")
print(f"Balance: {w3.from_wei(w3.eth.get_balance(address), 'ether'):.6f} ETH")
print("=" * 60)

def get_problem():
    try:
        req = urllib.request.Request(
            'https://api.agentcoin.site/api/problem/current',
            headers={'User-Agent': 'AgentCoin-Miner/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return None

def solve_problem_140():
    """Solve problem #140"""
    N = (AGENT_ID % 1000) + 1000  # = 1532
    S = 0
    for k in range(1, N + 1):
        v_k = (k**2 + AGENT_ID) % (k + 5)
        S += v_k
    multiplier = (AGENT_ID % 17) + 1  # = 6
    modulus = N + 23  # = 1555
    return (S * multiplier) % modulus

def submit_answer(problem_id, answer):
    """Submit answer to contract"""
    try:
        abi = [{"inputs": [{"internalType": "uint256", "name": "problemId", "type": "uint256"}, {"internalType": "int256", "name": "answer", "type": "int256"}], "name": "submitAnswer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
        contract = w3.eth.contract(address=w3.to_checksum_address(PROBLEM_MANAGER), abi=abi)
        
        tx = contract.functions.submitAnswer(problem_id, answer).build_transaction({
            'from': address,
            'nonce': w3.eth.get_transaction_count(address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return tx_hash.hex()
    except Exception as e:
        return f"Error: {e}"

last_problem_id = None
submission_count = 0

while True:
    try:
        problem = get_problem()
        if not problem:
            time.sleep(10)
            continue
        
        pid = problem.get('problem_id')
        is_active = problem.get('is_active', False)
        
        # New problem detected
        if pid != last_problem_id:
            print(f"\n{'='*60}")
            print(f"🎯 NEW PROBLEM #{pid}!")
            print(f"Template: {problem.get('template_text', '')[:80]}...")
            print(f"Deadline: {problem.get('answer_deadline')}")
            last_problem_id = pid
            submission_count = 0
            
            # Try to solve and submit
            if pid == 140:
                answer = solve_problem_140()
                print(f"Calculated answer: {answer}")
                
                # Submit multiple times for this problem
                for attempt in range(5):  # Try 5 times per problem
                    tx_hash = submit_answer(pid, answer)
                    if not tx_hash.startswith("Error"):
                        submission_count += 1
                        print(f"  ✅ Submission #{submission_count}: {tx_hash[:30]}...")
                    else:
                        print(f"  ❌ Attempt {attempt+1} failed: {tx_hash[:50]}")
                    time.sleep(5)  # Wait between submissions
        else:
            # Same problem, periodic status
            if submission_count > 0:
                print(f"\r⏳ Problem #{pid} | Submissions: {submission_count} | Waiting...", end='', flush=True)
            else:
                # Try to submit if we haven't yet
                if is_active and pid == 140:
                    answer = solve_problem_140()
                    tx_hash = submit_answer(pid, answer)
                    if not tx_hash.startswith("Error"):
                        submission_count += 1
                        print(f"\n✅ Auto-submission #{submission_count}: {tx_hash[:30]}...")
        
        time.sleep(15)  # Check every 15 seconds
        
    except KeyboardInterrupt:
        print(f"\n\nStopped. Total submissions: {submission_count}")
        break
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        time.sleep(10)
