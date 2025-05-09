import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QTextEdit
from supply_chain_contract import SupplyChainNFT
import json

class TestNFTApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test SupplyChain NFT")
        self.resize(500, 400)

        # Load ABI
        with open("build/contracts/SupplyChainNFT.json") as f:
            abi = json.load(f)["abi"]

        self.contract = SupplyChainNFT(
            "http://127.0.0.1:7545",
            "0xdFe96997D15b4478bcC3ABdbc3B6806fc93aC98f",
            abi
        )

        # UI Elements
        layout = QVBoxLayout()

        self.label_info = QLabel("Info:")
        layout.addWidget(self.label_info)

        self.input_address = QLineEdit()
        self.input_address.setPlaceholderText("Indirizzo destinatario...")
        layout.addWidget(self.input_address)

        self.input_tokenuri = QLineEdit()
        self.input_tokenuri.setPlaceholderText("Token URI (es: metadata IPFS)")
        layout.addWidget(self.input_tokenuri)

        self.btn_mint = QPushButton("Mint NFT")
        self.btn_mint.clicked.connect(self.mint_nft)
        layout.addWidget(self.btn_mint)
        
        self.input_from_address = QLineEdit()
        self.input_from_address.setPlaceholderText("Indirizzo mittente...")
        layout.addWidget(self.input_from_address)

        self.input_private_key = QLineEdit()
        self.input_private_key.setPlaceholderText("Chiave privata del mittente...")
        layout.addWidget(self.input_private_key)

        self.input_transfer_to = QLineEdit()
        self.input_transfer_to.setPlaceholderText("Trasferisci a (address)")
        layout.addWidget(self.input_transfer_to)

        self.input_tokenid = QLineEdit()
        self.input_tokenid.setPlaceholderText("Token ID")
        layout.addWidget(self.input_tokenid)

        self.btn_transfer = QPushButton("Trasferisci NFT")
        self.btn_transfer.clicked.connect(self.transfer_nft)
        layout.addWidget(self.btn_transfer)

        self.btn_history = QPushButton("Mostra Storico")
        self.btn_history.clicked.connect(self.show_history)
        layout.addWidget(self.btn_history)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def mint_nft(self):
        address = self.input_address.text().strip()
        token_uri = self.input_tokenuri.text().strip()
        if address and token_uri:
            tx_hash, token_id = self.contract.mint_product_nft(address, token_uri)
            self.text_output.append(f"Mintato! TX: {tx_hash}\nToken ID: {token_id}")
            
    def transfer_nft(self):
        from_address = self.input_from_address.text().strip()
        private_key = self.input_private_key.text().strip()
        to_address = self.input_transfer_to.text().strip()
        token_id = int(self.input_tokenid.text().strip())

        if from_address and private_key and to_address and token_id >= 0:
            tx_hash = self.contract.transfer_product_nft(from_address, to_address, token_id, private_key)
            self.text_output.append(f"Trasferito! TX: {tx_hash}")

    def show_history(self):
        token_id = int(self.input_tokenid.text().strip())
        history = self.contract.get_ownership_history(token_id)
        self.text_output.append(f"Storico: {history}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestNFTApp()
    window.show()
    sys.exit(app.exec_())