from blockchain import Blockchain
from textwrap import dedent
from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-","")

blockchain = Blockchain()

@app.route("/mine", methods = ["GET"])
def mine():
	# run the proof of work to get the next proof
	last_block = blockchain.last_block
	last_proof = last_block["proof"]
	proof = blockchain.proof_of_work(last_proof)

	# Must receive a reward for finding the proof
	# The sender is 0 to signify that this node has mined a new coin.
	blockchain.new_transaction(sender = "0", recipient = node_identifier, amount = 1)

	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, previous_hash)

	response = {
		"message" : "New Block forged",
		"index" : block["index"],
		"transactions" : block["transactions"],
		"proof" : block["proof"],
		"previous_hash" : block["previous_hash"]
	}

	return jsonify(response), 200

@app.route("/transactions/new", methods = ["POST"])
def new_transaction():
	values = request.get_json()

	required = ["sender", "recipient", "amount"]
	if not all(k in values for k in required):
		return "Missing values", 400

	index = blockchain.new_transaction(values["sender"], values["recipient"], values["amount"])

	response = {
		"message" : "Transaction will be added to block {index}"
	}
	return jsonify(response), 201

@app.route("/chain", methods = ["GET"])
def full_chain():
	response = {
		"chain" : blockchain.chain,
		"length" : len(blockchain.chain)
	}

	return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port=5005)