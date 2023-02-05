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

# Instantiate and deploy contract
contract = w3.eth.contract(abi=abi, bytecode=bytecode)
# Contract instance
contract_instance = w3.eth.contract(abi=abi, address=os.getenv('CONTRACT_ADDRESS'))
# Contract instance in concise mode
#contract_instance = w3.eth.contract(abi=abi, address=contract_address, ContractFactoryClass=ConciseContract)

# Getters + Setters for web3.eth.contract object ConciseContract
#print(format(contract_instance.getGreeting()))

print('Contract value: {}'.format(contract_instance.functions.highestBid().call()))
