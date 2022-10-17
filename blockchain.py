import json
import hashlib
from urllib.parse import urlparse
import requests

from block import Block
from transaction import Transaction


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # We need an initial block
        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        block = Block(
            index=len(self.chain) + 1,
            previous_hash=previous_hash or self.hash(self.chain[-1].to_json()),
            proof=proof,
            transactions=self.current_transactions
        )
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append(Transaction(sender, recipient, amount))
        return self.last_block.index + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, difficulty=3):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            if block.previous_hash != self.hash(last_block.to_json()):
                return False

            if not self.valid_proof(last_block.proof, block.proof):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


if __name__ == '__main__':
    blockchain = Blockchain()

    transaction1 = blockchain.new_transaction('Alice', 'Bob', 10)
    transaction2 = blockchain.new_transaction('Bob', 'Alice', 5)
    transaction3 = blockchain.new_transaction('Alice', 'Bob', 2)

    proof = blockchain.proof_of_work(blockchain.last_block.proof)
    blockchain.new_block(proof)

    transaction4 = blockchain.new_transaction('Alice', 'Bob', 10)
    transaction5 = blockchain.new_transaction('Bob', 'Alice', 5)
    transaction6 = blockchain.new_transaction('Alice', 'Bob', 2)

    proof = blockchain.proof_of_work(blockchain.last_block.proof)
    blockchain.new_block(proof)

    print(blockchain.chain)
    for block in blockchain.chain:
        print(block.to_json())