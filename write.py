import json
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract
from web3.middleware import geth_poa_middleware
import os
from dotenv import load_dotenv

load_dotenv()


# compile your smart contract with truffle first
truffleFile = json.load(open('./build/contracts/auction.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

# web3.py instance
w3 = Web3(HTTPProvider(os.getenv('RPC_URL')))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
print(w3.isConnected())

key = os.getenv('PRIVATE_KEY')
acct = w3.eth.account.privateKeyToAccount(key)
contract_address = Web3.toChecksumAddress(os.getenv('CONTRACT_ADDRESS')) #modify
account_address = acct.address

# Instantiate and deploy contract
contract = w3.eth.contract(abi=abi, bytecode=bytecode)
# Contract instance
contract_instance = w3.eth.contract(abi=abi, address=contract_address)
# Contract instance in concise mode
# contract_instance = w3.eth.contract(abi=abi, address=contract_address, ContractFactoryClass=ConciseContract)

tx = contract_instance.functions.highestBid.buildTransaction({
    'from': acct.address,
    'nonce': w3.eth.getTransactionCount(acct.address),
    'gas': 1728712,
    'gasPrice': w3.toWei('21', 'gwei')})

#Get tx receipt to get contract address
signed_tx = w3.eth.account.signTransaction(tx, key)
#tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
print(hash.hex())