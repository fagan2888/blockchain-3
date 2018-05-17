import hashlib
import json
import requests
from time import time
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transactions = []
		self.nodes = set()
		self.new_block(previous_hash = 1, proof = 100)

	# Create a new block and adds it to the chain
	"""
	:param proof: <int> The proof given by the Proof of Work algorithm
	:param previous_hash: (Optional) <str> Hash of previous Block
	:return: <dict> New Block
	"""
	def new_block(self, proof, previous_hash = None):
		block = {
			"index" : len(self.chain) + 1,
			"timestamp" : time(),
			"transactions" : self.current_transactions,
			"proof" : proof,
			"previous_hash" : previous_hash or self.hash(self.chain[-1])
		}
		self.chain.append(block)

		self.current_transactions = []

		return block

	# Add a new transaction to the list of transactions
	"""
	:param sender: <str> Address of the Sender
	:param recipient: <str> Address of the Recipient
	:param amount: <int> Amount
	:return: <int> The index of the Block that will hold this transaction
	""" 
	def new_transaction(self, sender, recipient, amount):
		transaction = {"sender" : sender, "recipient" : recipient, "amount" : amount}
		self.current_transactions.append(transaction)
		return self.last_block["index"] + 1

	# SHA-256 hash of a block
	"""
	:param block: <dict> Block
	:return: str
	"""
	@staticmethod
	def hash(block):
		block_string = json.dumps(block, sort_keys = True).encode()

		return hashlib.sha256(block_string).hexdigest()

	# Returns the last block in the chain
	@property
	def last_block(self):
		return self.chain[-1]

	"""
	Simple Proof of Work Algorithm:
	- Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
	- p is the previous proof, and p' is the new proof
	:param last_proof: <int>
	:return: <int>
	"""
	def proof_of_work(self, last_proof):
		proof = 0

		while self.valid_proof(last_proof, proof) is False:
			proof += 1

		return proof

	"""
	Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
	:param last_proof: <int> Previous Proof
	:param proof: <int> Current Proof
	:return: <bool> True if correct, False if not.
	"""
	@staticmethod
	def valid_proof(last_proof, proof):
		guess = (str(last_proof) + str(proof)).encode()

		#guess = proof.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"

	"""
	Add a new node to the list of nodes
	:param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
	:return: None
	"""
	def register_node(self, address):
		parsed_url = urlparse(address)

		self.nodes.add(parsed_url.netloc)


	"""
	Determine if a given blockchain is valid
	:param chain: <list> A blockchain
	:return: <bool> True if valid, False if not
	"""
	def valid_chain(self, chain):
		last_block = chain[0]

		current_index = 1

		while current_index < len(chain):
			block = chain[current_index]
			print(last_block)
			print(block)

			# Check that the hash of the block is correct
			if block["previous_hash"] != self.hash(last_block):
				return False

			# Check that the proof of work is correct:
			if not self.valid_proof(last_block["proof"], block["proof"]):
				return False


			last_block = block
			current_index += 1

		return True

	"""
	This is the consensus algorithm which resolves conflicts
	by replacing the chain with the longest one in the network.

	:return: <bool> True if our chain was replaced, False if not
	"""
	def resolve_conflicts(self):
		neighbors = self.nodes

		new_chain = None

		# Find the longest chain
		max_length = len(self.chain)


		# Check and verify the chains from all the nodes in network
		for node in neighbors:
			response = requests.get("http://" + node + "/chain")

			if response.status_code == 200:
				length = response.json()["length"]
				chain = response.json()["chain"]

				# Check if the length is longer and the chain is valid
				if length > max_length and self.valid_chain(chain):
					max_length = length
					new_chain = chain

		# Replace chain if we find a new valid longer chain
		if new_chain:
			self.chain = new_chain
			return True

		return False
