from web3 import Web3
import json

# Questa classe gestisce la connessione a una blockchain Ethereum (tramite Ganache)
class BlockchainConnector:
    def __init__(self, provider_url, contract_address, abi_path):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        
        # Qui si verifica se la connessione alla blockchain è avvenuta correttamente
        if self.web3.is_connected():
            print("Connected to Ethereum")
        else:
            print("Not connected to Ethereum")

        if not self.web3.is_connected():
            raise ConnectionError("Errore nella connessione a Ganache")
        
        # Il metodo json.load() carica il contenuto del file e il campo ['abi'] estrae la parte che definisce l’interfaccia del contratto
        with open(abi_path, 'r') as abi_file:
            contract_abi = json.load(abi_file)['abi']
            
        # Qui viene creato un oggetto contratto (contract) che rappresenta lo smart contract Ethereum con cui si vuole interagire
        self.contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)

    def get_web3(self):
        return self.web3

    def get_contract(self):
        return self.contract

    def mint_tokens(self, recipient_address, amount, from_address):
        try:
            print(f"Tentativo di minting: {recipient_address}, {amount}, {from_address}")
            
            tx = self.contract.functions.mint(
                recipient_address, amount
            ).transact({'from': from_address})
            
            print(f"Transazione inviata: {tx}")

            receipt = self.web3.eth.waitForTransactionReceipt(tx)
            print(f"Minting completato! Ricevuta della transazione: {receipt}")

        except Exception as e:
            print(f"Errore durante il minting: {e}")