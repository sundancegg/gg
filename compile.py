import vyper
import os, json
from pathlib import Path

contract_name = "auction"
json_output_file = "build/contracts/auction.json"
vy_contract = "contracts/auction.vy"

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