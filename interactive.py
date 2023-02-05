#!/usr/local/bin/python3

import vyper
import os, json
from pathlib import Path
import fileinput
import argparse
import json
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

load_dotenv()
build_dir = f"./build/contracts/"
contract_dir = f"./contracts/"

w3 = Web3(HTTPProvider(os.getenv('RPC_URL')))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
acct = w3.eth.account.privateKeyToAccount(os.getenv('PRIVATE_KEY'))
assert(w3.isConnected())

def load_contract(contract_name):
    # compile your smart contract first
    json_abi = json.load(open(f"{build_dir}{contract_name}.json"))
    abi = json_abi['abi']
    bytecode = json_abi['bytecode']

    # Instantiate and deploy contract
    return abi, bytecode


def read_contract_var(w3, contract_name, contract_func):
    # Contract instance
    abi, _ = load_contract(contract_name)
    contract_instance = w3.eth.contract(
        abi=abi, address=os.getenv(f"CONTRACT_ADDRESS_{contract_name.upper()}"))
    func = getattr(contract_instance.functions, contract_func)
    contract_value = func().call()
    return contract_value


def write_contract_var(w3, contract_name, contract_func, contract_params):
    abi, _ = load_contract(contract_name)
    contract_instance = w3.eth.contract(
        abi=abi, address=os.getenv(f"CONTRACT_ADDRESS_{contract_name.upper()}"))

    func = getattr(contract_instance.functions, contract_func)
    # TODO fix this tx 
    tx = func(contract_params).buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')})

    #Get tx receipt to get contract address
    signed_tx = w3.eth.account.signTransaction(tx, os.getenv('PRIVATE_KEY'))
    #tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(hash)

    return tx_receipt



def update_env_file(env_key, env_value):
    for line in fileinput.input(".env", inplace=True):
        if env_key in line:
            print(f"{env_key}={env_value}", end='')
        else:
            print(line, end='')


# Defaults to writing the contract addrs
parser = argparse.ArgumentParser(description='Interact with GG contracts')
parser.add_argument('-c', '--compile', type=str, help="Contract name to compile")
parser.add_argument('-d', '--deploy', type=str, help="Contract name to deploy")
parser.add_argument('-r', '--read', type=str, help="Contract to read from")
parser.add_argument('-w', '--write', type=str, help="Contract to write to")
parser.add_argument('-f', '--func', type=str) 
parser.add_argument('-i', '--input', type=str, help="function input") 
args = parser.parse_args()


# COMPILE
if args.compile:
    contract_name = args.compile
    json_output_file = f"{build_dir}{contract_name}.json"
    vy_contract = f"{contract_dir}{contract_name}.vy"

    with open(vy_contract, 'r') as f:
        content = f.read()

    current_directory = os.curdir
    smart_contract = {}
    smart_contract[current_directory] = content

    format = ['abi', 'bytecode']
    compiled_code = vyper.compile_codes(smart_contract, format, 'dict')

    smart_contract_json = {
        'contractName': contract_name,
        'abi': compiled_code[current_directory]['abi'],
        'bytecode': compiled_code[current_directory]['bytecode']
    }

    vy_json = Path(json_output_file)
    vy_json.parent.mkdir(exist_ok=True, parents=True)
    vy_json = open(json_output_file, 'w+')
    json.dump(smart_contract_json, vy_json, indent=2)
    vy_json.close()
    print(f"Compiled:\n{json_output_file}")


# DEPLOY
if args.deploy:
    contract_name = args.deploy

    # compile your smart contract with vyper first
    vyper_json = json.load(open(f'{build_dir}{contract_name}.json'))
    abi = vyper_json['abi']
    bytecode = vyper_json['bytecode']

    contract= w3.eth.contract(bytecode=bytecode, abi=abi)
    
    init_vars = []
    if contract_name == 'temple':
        #building transaction init
        _GoddessGuild = acct.address
        _TempleName = "Sundance Temple"
        _TempleDivision = 1
        _TempleMaster =  acct.address
        _BaseRate = 2000
        init_vars = [_GoddessGuild, _TempleName, _TempleDivision, _TempleMaster, _BaseRate]

    construct_txn = contract.constructor(*init_vars).buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')})

    signed = acct.signTransaction(construct_txn)

    tx_hash=w3.eth.sendRawTransaction(signed.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    update_env_file(f"CONTRACT_ADDRESS_{contract_name.upper()}",tx_receipt['contractAddress'])
    print(f"Contract Deployed At:\n{tx_receipt['contractAddress']}")


# READ/WRITE
if args.read: 
    print(read_contract_var(w3, args.read, args.func))

if args.write:
    print(write_contract_var(w3, args.write, args.func, args.input))
