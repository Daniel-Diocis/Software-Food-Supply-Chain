import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5 import QtWidgets, uic
from onChain import MyTokenContract, BlockchainConnector
from interface import Ui_MainWindow
import re  # Per validazione dell'indirizzo

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.connector = None  # Non inizializzo subito il connettore
        self.contract = None   # Lo inizializzerò dopo
        
        self.ui.connectButton.clicked.connect(self.connect_to_contract)
        self.ui.mintButton.clicked.connect(self.mint_tokens)
        self.ui.checkBalanceButton.clicked.connect(self.check_balance)
        
    def connect_to_contract(self):
        contract_address = self.ui.addressInput.text().strip()

        if not self.is_valid_address(contract_address):
            self.ui.statusLabel.setText("Errore: Indirizzo del contratto non valido.")
            return

        try:
            self.connector = BlockchainConnector(
                "http://127.0.0.1:7545",
                contract_address,
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '..', 'onChain', 'build', 'contracts', 'MyToken.json')
                )
            )

            self.contract = MyTokenContract(self.connector)
            self.ui.statusLabel.setText("Connessione al contratto riuscita!")
        except Exception as e:
            self.ui.statusLabel.setText(f"Errore nella connessione: {str(e)}")

    def mint_tokens(self):
        if not self.connector:
            self.ui.statusLabel.setText("Errore: Connettiti prima a un contratto.")
            return
        
        address = self.ui.addressInput.text().strip()
        amount_str = self.ui.amountInput.text().strip()
        
        

        #print(f"Indirizzo inserito: '{address}'")
        #print(f"Importo inserito: '{amount_str}'")
        #print(f"Tipo di amount_str: {type(amount_str)}")
        #print(f"Rappresentazione di amount_str: '{amount_str}'")

        # Validazione dell'indirizzo Ethereum
        if not self.is_valid_address(address):
            self.ui.statusLabel.setText("Errore: Indirizzo Ethereum non valido.")
            return

        # Verifica se amount_str è un numero valido prima della conversione
        #print(f"amount_str.isdigit() prima della condizione: {amount_str.isdigit()}") # AGGIUNGI QUESTA LINEA
        if not amount_str.isdigit():
            self.ui.statusLabel.setText("Errore: L'importo deve essere un numero valido.")
            print(f"Errore: '{amount_str}' non è un numero valido.")
            return

        # Convertire amount_str in un intero
        try:
            amount = int(amount_str)

            if amount <= 0:
                self.ui.statusLabel.setText("Errore: L'importo deve essere maggiore di zero.")
                return

            # Proviamo a fare la transazione con l'importo convertito
            tx_hash = self.contract.mint_tokens(address, amount)
            self.ui.statusLabel.setText(f"Transazione inviata: {tx_hash}")

        except ValueError:
            self.ui.statusLabel.setText("Errore: L'importo deve essere un numero valido.")
            print(f"Errore durante la conversione dell'importo: '{amount_str}'")
        except Exception as e:
            self.ui.statusLabel.setText(f"Errore: {str(e)}")

    def check_balance(self):
        if not self.connector:
            self.ui.balanceLabel.setText("Errore: Connettiti prima a un contratto.")
            return
        address = self.ui.addressInput.text().strip()

        if not self.is_valid_address(address):
            self.ui.balanceLabel.setText("Errore: Indirizzo Ethereum non valido.")
            return

        try:
            balance = self.contract.get_balance(address)
            self.ui.balanceLabel.setText(f"Saldo: {balance / 10**18}")
            print(f"Saldo dell'indirizzo {address}: {balance / 10**18} MTK")
        except Exception as e:
            self.ui.balanceLabel.setText(f"Errore: {str(e)}")

    def is_valid_address(self, address):
        """Verifica che l'indirizzo sia valido (inizia con 0x e ha una lunghezza di 42 caratteri)."""
        return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))

app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec()