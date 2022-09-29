import time


class Block:
    def __init__(self, index, previous_hash, proof, transactions):
        self.index = index
        self.previous_hash = previous_hash
        self.proof = proof
        self.transactions = transactions
        self.timestamp = time.time()

    def to_json(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'proof': self.proof,
            'transactions': [t.to_json() for t in self.transactions],
            'timestamp': self.timestamp
        }

    def get_json_transactions(self):
        return [t.to_json() for t in self.transactions]
