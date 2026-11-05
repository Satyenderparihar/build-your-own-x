#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""blockchain_from_scratch.py: A Cryptographic Blockchain & Proof-of-Work Mining Engine built from scratch.

Implements core Blockchain & Distributed Ledger internals:
- Cryptographic SHA-256 block hashing
- Immutable block chain linkage (previous_hash pointer)
- Proof-of-Work (PoW) consensus mining algorithm (finding nonce for difficulty target)
- Genesis block generation
- Transaction ledger recording
- Chain integrity audit & tamper detection
"""

import hashlib
import json
import time

class Block:
    def __init__(self, index: int, transactions: list, previous_hash: str, nonce: int = 0, timestamp: float = None):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = timestamp or time.time()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "timestamp": self.timestamp
        }, sort_keys=True).encode("utf-8")
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, ["Genesis: Deepesh Studio Blockchain Launch"], "0" * 64, nonce=0)
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: float):
        tx = {"from": sender, "to": recipient, "amount": amount, "time": time.time()}
        self.pending_transactions.append(tx)
        return self.last_block.index + 1

    def proof_of_work(self, block: Block) -> tuple:
        target = "0" * self.difficulty
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith(target):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return block.nonce, computed_hash

    def mine_pending_transactions(self, miner_address: str):
        if not self.pending_transactions:
            return None
        # Mining reward
        self.pending_transactions.append({"from": "COINBASE", "to": miner_address, "amount": 50.0, "time": time.time()})
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.last_block.compute_hash()
        )
        nonce, final_hash = self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block, final_hash

    def validate_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            if curr.previous_hash != prev.compute_hash():
                return False
            if not curr.compute_hash().startswith("0" * self.difficulty):
                return False
        return True

def demo():
    print("=== Demonstrating Blockchain & PoW Mining From Scratch ===")
    bc = Blockchain(difficulty=3)
    print(f"Genesis Block Hash: {bc.chain[0].compute_hash()[:24]}...")
    
    # 1. Add transactions
    print("\n1. Adding transactions to memory pool:")
    bc.add_transaction("Satyender", "Editor_1", 25.5)
    bc.add_transaction("Editor_1", "Sound_Designer", 10.0)
    print(f"  Pending transactions: {len(bc.pending_transactions)}")
    
    # 2. Mine Block 1
    print("\n2. Mining Block 1 (Proof-of-Work Target: 3 leading zeros)...")
    t0 = time.time()
    block1, hash1 = bc.mine_pending_transactions(miner_address="Satyender_Mining_Node")
    dt = time.time() - t0
    print(f"  ✓ Block 1 Mined in {dt:.3f}s! Nonce: {block1.nonce}")
    print(f"  Hash: {hash1}")
    
    # 3. Add more transactions & Mine Block 2
    bc.add_transaction("Channel_Sponsor", "Satyender", 500.0)
    print("\n3. Mining Block 2...")
    block2, hash2 = bc.mine_pending_transactions(miner_address="Satyender_Mining_Node")
    print(f"  ✓ Block 2 Mined! Nonce: {block2.nonce} | Hash: {hash2}")
    
    # 4. Audit Chain Integrity
    print("\n4. Auditing Cryptographic Chain Integrity:")
    is_valid = bc.validate_chain()
    print(f"  Chain Valid: \033[32m{is_valid} (All hashes and links cryptographically verified)\033[0m")
    
    # 5. Tamper test
    print("\n5. Simulating Hacker Tampering Attack (Modifying Block 1 transaction):")
    bc.chain[1].transactions[0]["amount"] = 999999.0  # Illegal alteration
    is_valid_after_hack = bc.validate_chain()
    print(f"  Chain Valid After Tampering: \033[31m{is_valid_after_hack} (Tamper Detected & Rejected!)\033[0m")
    print("✓ Blockchain From Scratch Demo completed successfully!\n")

if __name__ == "__main__":
    demo()
