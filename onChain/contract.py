from .web3_connect import BlockchainConnector
from web3 import Web3

class MyTokenContract:
    def __init__(self, connector):
        self.connector = connector
        self.web3 = connector.get_web3()
        self.contract = connector.get_contract()
        self.account = self.web3.eth.accounts[0]

        # Leggi il numero di decimali dal contratto
        self.decimals = self.contract.functions.decimals().call()

        print(f"Contract loaded: {self.contract}")
        print(f"Account: {self.account}")
        print(f"Token decimals: {self.decimals}")

    def mint_tokens(self, address, amount):
        scaled_amount = int(float(amount) * (10 ** self.decimals))
        if scaled_amount == 0:
            raise ValueError("L'importo non può essere zero")

        try:
            print("=== MINT ===")
            print(f"👤 FROM (account firmatario): {self.account}")
            print(f"🎯 TO (beneficiario): {address}")
            print(f"💰 Amount richiesto: {amount} ({scaled_amount} con {self.decimals} decimali)")
            tx = self.contract.functions.mint(address, scaled_amount).build_transaction({
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
        scaled_amount = int(float(amount) * (10 ** self.decimals))
        if scaled_amount <= 0:
            raise ValueError("L'importo deve essere maggiore di zero")

        try:
            print("=== BURN ===")
            print(f"👤 FROM (account firmatario e bruciante): {from_address}")
            print(f"🔐 Chiave privata: {'...'+private_key[-6:]} (troncata per sicurezza)")
            print(f"🔥 Amount richiesto: {amount} ({scaled_amount} con {self.decimals} decimali)")
            tx = self.contract.functions.burn(scaled_amount).build_transaction({
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
        
    def transfer_tokens(self, from_address, private_key, to_address, amount):
        scaled_amount = int(float(amount) * (10 ** self.decimals))
        print(f"=== TRANSFER ===")
        print(f"👤 FROM (mittente): {from_address}")
        print(f"🔐 Private key presente: {'Sì' if private_key else 'No'}")
        print(f"🎯 TO (destinatario): {to_address}")
        print(f"💰 Amount: {amount} ({scaled_amount} con {self.decimals} decimali)")

        try:
            tx = self.contract.functions.transfer(to_address, scaled_amount).build_transaction({
                'from': from_address,
                'nonce': self.web3.eth.get_transaction_count(from_address),
                'gas': 2000000,
                'gasPrice': self.web3.to_wei('10', 'gwei')
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return self.web3.to_hex(tx_hash)
        except Exception as e:
            print(f"Errore nel trasferimento token: {e}")
            raise

    def get_balance(self, address):
        try:
            balance_raw = self.contract.functions.balanceOf(address).call()
            balance = balance_raw / (10 ** self.decimals)
            print(f"Saldo dell'indirizzo {address}: {balance} MTK")
            return balance
        except Exception as e:
            print(f"Errore nel recupero del saldo: {e}")
            return 0

    def get_total_supply(self):
        try:
            total = self.contract.functions.totalSupply().call()
            return total / (10 ** self.decimals)
        except Exception as e:
            print(f"Errore nel total supply: {e}")
            raise