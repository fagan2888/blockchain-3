class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transactions = []


	def new_block(self):
		# Creates a new block and adds it to the chain