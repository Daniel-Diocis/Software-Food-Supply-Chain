from web3 import Web3

class SupplyChainNFT:
    def __init__(self, provider_url, contract_address, abi):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
        self.account = self.web3.eth.accounts[0]  # Usa il primo account per ora

    def mint_product_nft(self, to_address, token_uri):
        tx = self.contract.functions.mintProductNFT(to_address, token_uri).build_transaction({
            'from': self.account,
            'nonce': self.web3.eth.get_transaction_count(self.account),
            'gas': 3000000,
            'gasPrice': self.web3.to_wei('20', 'gwei')
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key="0xbfa8471445678988529d065e2d7f4dec55a6180beffc2a4310ef1bc0db0fe754")
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

        # Prende il tokenId dal log dell'evento Transfer
        event = receipt['logs'][0]
        token_id = int(event['topics'][3].hex(), 16)  # standard: topic[3] = tokenId

        return self.web3.to_hex(tx_hash), token_id

    def transfer_product_nft(self, from_address, to_address, token_id, private_key):
        tx = self.contract.functions.transferProductNFT(from_address, to_address, token_id).build_transaction({
            'from': from_address,
            'nonce': self.web3.eth.get_transaction_count(from_address),
            'gas': 3000000,
            'gasPrice': self.web3.to_wei('20', 'gwei')
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return self.web3.to_hex(tx_hash)

    def get_ownership_history(self, token_id):
        return self.contract.functions.getOwnershipHistory(token_id).call()