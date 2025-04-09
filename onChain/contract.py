from .web3_connect import BlockchainConnector
from web3 import Web3

class MyTokenContract:
    def __init__(self, connector):
        self.connector = connector
        self.web3 = connector.get_web3()
        self.contract = connector.get_contract()
        self.account = self.web3.eth.accounts[0]
        print(f"Contract loaded: {self.contract}")
        print(f"Account: {self.account}")

    def mint_tokens(self, address, amount):
        amount = int(amount) * 10**18
        if amount == 0:
            raise ValueError("L'importo non può essere zero")

        try:
            print(f"Address: {address}")
            print(f"Amount: {amount}")
            tx = self.contract.functions.mint(address, amount).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
                'gas': 2000000,
                'gasPrice': self.web3.to_wei('10', 'gwei')
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key='0xbfa8471445678988529d065e2d7f4dec55a6180beffc2a4310ef1bc0db0fe754')
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return self.web3.to_hex(tx_hash)
        except Exception as e:
            print(f"Error minting tokens: {e}")
            raise

    def burn_tokens(self, amount):
        amount = int(amount) * 10**18
        if amount <= 0:
            raise ValueError("L'importo deve essere maggiore di zero")

        try:
            print(f"Burning {amount} token da {self.account}")
            tx = self.contract.functions.burn(amount).build_transaction({
                'from': self.account,
                'nonce': self.web3.eth.get_transaction_count(self.account),
                'gas': 2000000,
                'gasPrice': self.web3.to_wei('10', 'gwei')
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key='0xbfa8471445678988529d065e2d7f4dec55a6180beffc2a4310ef1bc0db0fe754')
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return self.web3.to_hex(tx_hash)
        except Exception as e:
            print(f"Errore nel burn: {e}")
            raise

    def get_balance(self, address):
        try:
            print(f"Chiamando balanceOf per l'indirizzo: {address}")
            balance = self.contract.functions.balanceOf(address).call()
            print(f"Saldo di {address} nella funzione contract: {balance}")
            return balance
        except Exception as e:
            print(f"Errore nel recupero del saldo per l'indirizzo {address}: {str(e)}")
            return 0

    def get_total_supply(self):
        try:
            total_supply = self.contract.functions.totalSupply().call()
            print(f"Total supply: {total_supply}")
            return total_supply
        except Exception as e:
            print(f"Error getting total supply: {e}")
            raise