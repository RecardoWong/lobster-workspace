#!/usr/bin/env python3
"""
AgentCoin Mining Script
Mine AGC tokens by solving problems on Base mainnet
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Optional

try:
    from web3 import Web3
    from dotenv import load_dotenv
except ImportError:
    print("Installing required packages...")
    os.system("pip3 install web3 python-dotenv -q")
    from web3 import Web3
    from dotenv import load_dotenv

load_dotenv()

# Contract addresses (Base mainnet)
AGENT_REGISTRY_ADDRESS = os.getenv("AGENT_REGISTRY_ADDRESS", "0x5A899d52C9450a06808182FdB1D1e4e23AdFe04D")
PROBLEM_MANAGER_ADDRESS = os.getenv("PROBLEM_MANAGER_ADDRESS", "0x7D563ae2881D2fC72f5f4c66334c079B4Cc051c6")
REWARD_DISTRIBUTOR_ADDRESS = os.getenv("REWARD_DISTRIBUTOR_ADDRESS", "0x31AF6C3C703aa5b2538F05B7bC1D632351b099a1")
RPC_URL = os.getenv("AGC_RPC_URL", "https://mainnet.base.org")

# Minimal ABIs
AGENT_REGISTRY_ABI = [
    {"inputs": [{"internalType": "address", "name": "", "type": "address"}], "name": "agents", "outputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}, {"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "bool", "name": "isActive", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "_agent", "type": "address"}], "name": "getAgentId", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "registerAgent", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]

PROBLEM_MANAGER_ABI = [
    {"inputs": [], "name": "currentProblemId", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "problems", "outputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}, {"internalType": "string", "name": "template", "type": "string"}, {"internalType": "uint256", "name": "deadline", "type": "uint256"}, {"internalType": "bool", "name": "isActive", "type": "bool"}, {"internalType": "bool", "name": "isSettled", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "_problemId", "type": "uint256"}, {"internalType": "int256", "name": "_answer", "type": "int256"}], "name": "submitAnswer", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]

REWARD_DISTRIBUTOR_ABI = [
    {"inputs": [{"internalType": "address", "name": "_agent", "type": "address"}], "name": "getClaimableRewards", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "claimRewards", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]


class AgentCoinMiner:
    def __init__(self, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to {RPC_URL}")
        
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address
        
        self.agent_registry = self.w3.eth.contract(
            address=Web3.to_checksum_address(AGENT_REGISTRY_ADDRESS),
            abi=AGENT_REGISTRY_ABI
        )
        self.problem_manager = self.w3.eth.contract(
            address=Web3.to_checksum_address(PROBLEM_MANAGER_ADDRESS),
            abi=PROBLEM_MANAGER_ABI
        )
        self.reward_distributor = self.w3.eth.contract(
            address=Web3.to_checksum_address(REWARD_DISTRIBUTOR_ADDRESS),
            abi=REWARD_DISTRIBUTOR_ABI
        )
    
    def get_agent_id(self) -> Optional[int]:
        """Get agent ID for the current wallet"""
        try:
            agent_id = self.agent_registry.functions.getAgentId(self.address).call()
            return agent_id if agent_id > 0 else None
        except Exception as e:
            print(f"Error getting agent ID: {e}")
            return None
    
    def register_agent(self) -> str:
        """Register agent on-chain"""
        try:
            tx = self.agent_registry.functions.registerAgent().build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
            })
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return tx_hash.hex()
        except Exception as e:
            return f"Error: {e}"
    
    def get_current_problem(self) -> Optional[dict]:
        """Fetch current problem from API"""
        import urllib.request
        try:
            req = urllib.request.Request(
                "https://api.agentcoin.site/api/problem/current",
                headers={"User-Agent": "AgentCoin-Miner/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"Error fetching problem: {e}")
            return None
    
    def get_onchain_problem(self) -> Optional[dict]:
        """Get current problem from blockchain"""
        try:
            problem_id = self.problem_manager.functions.currentProblemId().call()
            if problem_id == 0:
                return None
            problem = self.problem_manager.functions.problems(problem_id).call()
            return {
                "id": problem[0],
                "template": problem[1],
                "deadline": problem[2],
                "is_active": problem[3],
                "is_settled": problem[4]
            }
        except Exception as e:
            print(f"Error reading on-chain problem: {e}")
            return None
    
    def submit_answer(self, problem_id: int, answer: int) -> str:
        """Submit answer on-chain"""
        try:
            tx = self.problem_manager.functions.submitAnswer(problem_id, answer).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
            })
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return tx_hash.hex()
        except Exception as e:
            return f"Error: {e}"
    
    def get_claimable_rewards(self) -> int:
        """Get claimable AGC rewards"""
        try:
            return self.reward_distributor.functions.getClaimableRewards(self.address).call()
        except Exception as e:
            print(f"Error getting rewards: {e}")
            return 0
    
    def claim_rewards(self) -> str:
        """Claim rewards"""
        try:
            tx = self.reward_distributor.functions.claimRewards().build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
            })
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return tx_hash.hex()
        except Exception as e:
            return f"Error: {e}"
    
    def status(self):
        """Show miner status"""
        print(f"\n{'='*50}")
        print(f"🤖 AgentCoin Miner Status")
        print(f"{'='*50}")
        print(f"Wallet: {self.address}")
        print(f"Balance: {self.w3.from_wei(self.w3.eth.get_balance(self.address), 'ether'):.6f} ETH")
        
        agent_id = self.get_agent_id()
        if agent_id:
            print(f"Agent ID: {agent_id}")
            print(f"Status: ✅ Registered")
        else:
            print(f"Agent ID: Not registered")
            print(f"Status: ❌ Need to register on-chain")
        
        rewards = self.get_claimable_rewards()
        print(f"Claimable Rewards: {self.w3.from_wei(rewards, 'ether')} AGC")
        
        problem = self.get_current_problem()
        if problem:
            print(f"\n📋 Current Problem (API):")
            print(f"  ID: {problem.get('problem_id', 'N/A')}")
            print(f"  Active: {problem.get('is_active', False)}")
            print(f"  Deadline: {problem.get('answer_deadline', 'N/A')}")
        
        onchain = self.get_onchain_problem()
        if onchain:
            print(f"\n⛓️  Current Problem (On-chain):")
            print(f"  ID: {onchain['id']}")
            print(f"  Active: {onchain['is_active']}")
            print(f"  Settled: {onchain['is_settled']}")
        
        print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description="AgentCoin Mining Tool")
    parser.add_argument("command", choices=["status", "register", "submit", "claim", "solve"], help="Command to run")
    parser.add_argument("--problem-id", type=int, help="Problem ID for submit")
    parser.add_argument("--answer", type=int, help="Answer for submit")
    parser.add_argument("--private-key", help="Private key (or set AGC_PRIVATE_KEY env var)")
    
    args = parser.parse_args()
    
    private_key = args.private_key or os.getenv("AGC_PRIVATE_KEY")
    if not private_key:
        print("❌ Error: Private key required. Set AGC_PRIVATE_KEY env var or use --private-key")
        sys.exit(1)
    
    miner = AgentCoinMiner(private_key)
    
    if args.command == "status":
        miner.status()
    elif args.command == "register":
        tx_hash = miner.register_agent()
        print(f"✅ Registration transaction: {tx_hash}")
    elif args.command == "submit":
        if args.problem_id is None or args.answer is None:
            print("❌ Error: --problem-id and --answer required for submit")
            sys.exit(1)
        tx_hash = miner.submit_answer(args.problem_id, args.answer)
        print(f"✅ Transaction sent: {tx_hash}")
    elif args.command == "claim":
        tx_hash = miner.claim_rewards()
        print(f"✅ Claim transaction: {tx_hash}")
    elif args.command == "solve":
        # Auto-solve and submit
        problem = miner.get_current_problem()
        if not problem or not problem.get('is_active'):
            print("❌ No active problem")
            sys.exit(1)
        
        agent_id = miner.get_agent_id()
        if not agent_id:
            print("❌ Agent not registered. Please register first.")
            sys.exit(1)
        
        template = problem.get('template_text', '')
        personalized = template.replace('{AGENT_ID}', str(agent_id))
        
        print(f"Problem: {personalized}")
        print(f"I need to solve this. Call me with the answer to submit.")


if __name__ == "__main__":
    main()
