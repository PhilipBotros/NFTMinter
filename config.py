import os

from dotenv import load_dotenv

load_dotenv()

NETWORK_TO_CHAIN_ID = {"ganache": 1337, "rinkeby": 4}


def load_address(network: str) -> str:
    env_key = f"ADDRESS_{network.upper()}"
    return os.getenv(env_key)


def load_private_key(network: str) -> str:
    env_key = f"PRIVATE_KEY_{network.upper()}"
    return os.getenv(env_key)

