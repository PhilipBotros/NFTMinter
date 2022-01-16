import os
from pathlib import Path
from typing import Dict, Union, Any, Tuple, List

from solcx import compile_files, install_solc
from web3.datastructures import AttributeDict
from web3 import Web3

from config import NETWORK_TO_CHAIN_ID
from helpers import get_account, get_w3_provider, get_generated_face, upload_metadata_to_ipfs


def send_transaction(w3: Web3, tx: Dict[str, Union[str, int]], private_key: str) -> AttributeDict:
    """ Given a transaction object and a private key, the transaction is signed to check if the provided private key
        matches the address in the tx, if so, return tx hash and send tx hash to the chain and wait for confirmation
    """
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def compile_contract(contract_path: Union[Path, str], solc_version: str = "0.8.0") -> Tuple[List[Dict], str]:
    install_solc(solc_version)

    compiled_contract = compile_files(contract_path,
                                     output_values=["abi", "bin"],
                                     solc_version=solc_version,
                                     import_remappings={f"@openzeppelin={os.getenv('OPENZEPPELIN')}"})
    key = list(compiled_contract.keys())[-1]
    abi = compiled_contract[key]["abi"]
    bytecode = compiled_contract[key]["bin"]
    return abi, bytecode


def build_transaction(contract: Any, address: str, chain_id: str) -> Dict[str, Union[str, int]]:
    nonce = w3.eth.getTransactionCount(address)
    tx = contract.buildTransaction(
        {"chainId": chain_id, "from": address, "nonce": nonce, "gasPrice": w3.eth.gas_price})
    return tx


def create_nft(token_id: str) -> str:
    image_url, image_metadata = get_generated_face()
    token_uri = upload_metadata_to_ipfs(image_url, image_metadata, token_id)
    return token_uri


if __name__ == "__main__":
    network_name = "rinkeby"
    abi, bytecode = compile_contract(Path("contracts/NFTMinter.sol"))

    w3 = get_w3_provider(network_name)
    chain_id = NETWORK_TO_CHAIN_ID[network_name]

    account = get_account(network_name)

    StorageContract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = build_transaction(StorageContract.constructor("AI generated humans", "AIH"), account.address, chain_id)
    tx_receipt = send_transaction(w3, tx, account.private_key)

    storage_contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
    token_id = storage_contract.functions.tokenCounter().call()
    token_uri = create_nft(token_id)
    update_tx = build_transaction(storage_contract.functions.createHuman(token_uri), account.address, chain_id)
    tx_receipt = send_transaction(w3, update_tx, account.private_key)
    print(f"View the NFT on https://testnets.opensea.io/assets/{storage_contract.address}/{token_id}")