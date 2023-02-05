import json
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract
from web3.middleware import geth_poa_middleware
import os
from dotenv import load_dotenv

load_dotenv()

# web3.py instance
w3 = Web3(HTTPProvider(os.getenv('RPC_URL')))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
print(w3.isConnected())

acct = w3.eth.account.privateKeyToAccount(os.getenv('PRIVATE_KEY'))

# compile your smart contract with vyper first
vyper_json = json.load(open('./build/contracts/auction.json'))
abi = vyper_json['abi']
bytecode = vyper_json['bytecode']

contract= w3.eth.contract(bytecode=bytecode, abi=abi)

#building transaction
# init
beneficiary = bytes.fromhex("eB795Dd5544C93191Ff362ebC895D3b9e101Ba89")
auction_start = 10
bidding_time = 2

#building transaction

construct_txn = contract.constructor(beneficiary, auction_start, bidding_time).buildTransaction({
    'from': acct.address,
    'nonce': w3.eth.getTransactionCount(acct.address),
    'gas': 1728712,
    'gasPrice': w3.toWei('21', 'gwei')})

signed = acct.signTransaction(construct_txn)

tx_hash=w3.eth.sendRawTransaction(signed.rawTransaction)
print(tx_hash.hex())
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Contract Deployed At:", tx_receipt['contractAddress'])
