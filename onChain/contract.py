from .web3_connect import BlockchainConnector
from web3 import Web3

class MyTokenContract:
    def __init__(self, connector):
        self.connector = connector
        self.web3 = connector.get_web3()
        self.contract = connector.get_contract()
        self.account = self.web3.eth.accounts[1]  # Account predefinito per le transazioni
        print(f"Contract loaded: {self.contract}")
        print(f"Account: {self.account}")

    def mint_tokens(self, address, amount):
        amount = int(amount) * 10**18  # Assicurati che sia un numero intero
        if amount == 0:
            raise ValueError("L'importo non può essere zero")

        try:
            print(f"Address: {address}")
            print(f"Amount: {amount}")
            # Costruisce la transazione da inviare alla blockchain,
            # chiamando la funzione mint di MyToken.sol
            tx = self.contract.functions.mint(address, amount).build_transaction({
                'from': self.account, # L'account che invia la transazione
                'nonce': self.web3.eth.get_transaction_count(self.account), # Il numero di transazioni inviate da quell'account
                'gas': 2000000, # Il limite massimo di gas
                'gasPrice': self.web3.to_wei('10', 'gwei') # Il prezzo per unità di gas
            })
            #print(f"Transaction to mint tokens: {tx}")
            
            # Firma della transazione
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key='0xf42a54c01d431762de0c0fecceba036f5776571c58ded16039edaead9280c29d')
            #print(f"Signed transaction: {signed_tx}")
            
            # Invio della transazione firmata direttamente alla rete Ethereum
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            #print(f"Transaction Hash: {tx_hash}")
            return self.web3.to_hex(tx_hash)
        except Exception as e:
            print(f"Error minting tokens: {e}")
            raise

    def get_balance(self, address):
        try:
            balance = self.contract.functions.balanceOf(address).call()
            return balance
        except Exception as e:
            print(f"Errore nel recupero del saldo: {str(e)}")
            return 0

    def get_total_supply(self):
        try:
            total_supply = self.contract.functions.totalSupply().call()
            print(f"Total supply: {total_supply}")
            return total_supply
        except Exception as e:
            print(f"Error getting total supply: {e}")
            raise