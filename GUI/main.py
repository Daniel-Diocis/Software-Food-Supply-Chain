import sys
import json
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import bcrypt
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import  QPropertyAnimation,QEasingCurve, Qt
from PyQt5 import QtCore, QtWidgets
from interfacciaUtente import Ui_MainWindow
from connessione_sqlite import Comunicazione
from onChain import MyTokenContract, BlockchainConnector, SupplyChainNFT
from connessione2_sqlite import DatabaseConnector
import re  # Per validazione dell'indirizzo
import assets
class FinestraPrincipale(QMainWindow):
    def __init__(self):
        super(FinestraPrincipale, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.database = Comunicazione()
        
        self.connector = None  # Non inizializzo subito il connettore per gestire eventuali errori
        contract_address = "0xAF87fa6a2DF3501d77c0F8F05195d4f4b50aA897"  # Indirizzo del contratto creato (CREATED CONTRACT ADDRESS di quando sia crea il contratto)
        try:
            self.connector = BlockchainConnector(
                "http://127.0.0.1:7545",
                contract_address,
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '..', 'onChain', 'build', 'contracts', 'MyToken.json')
                )
            )

            self.contract = MyTokenContract(self.connector)
            print(f"Connessione al contratto riuscita!")
        except Exception as e:
            print(f"Errore nella connessione: {str(e)}")
            
        # Inizializzazione del contratto NFT SupplyChain
        try:
            with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'onChain', 'build', 'contracts', 'SupplyChainNFT.json'))) as f:
                abi = json.load(f)["abi"]

            self.nft_contract = SupplyChainNFT(
                "http://127.0.0.1:7545",
                "0xdFe96997D15b4478bcC3ABdbc3B6806fc93aC98f",  # indirizzo contratto NFT
                abi
            )
            print(f" | Contratto NFT ok")
        except Exception as e:
            print(f" | NFT errore: {str(e)}")

        # Connessione dei bottoni alle funzioni
        self.ui.mintButton.clicked.connect(self.mint_tokens)
        self.ui.burnButton.clicked.connect(self.burn_tokens)
        self.ui.transferButton.clicked.connect(self.transfer_tokens)
        
        self.ui.btn_mint.clicked.connect(self.mint_nft)
        self.ui.btn_transfer.clicked.connect(self.transfer_nft)
        self.ui.btn_history.clicked.connect(self.show_history)
        self.ui.mintNFT_mintNFTbutton.clicked.connect(self.crea_json_nft)
        
        self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_welcome)
        
        
        # connessione bottoni a funzioni
        self.ui.bt_registrati_registrati.clicked.connect(self.registra_utente)
        self.ui.bt_accedi_accedi.clicked.connect(self.login_utente)
        self.ui.bt_logout.clicked.connect(self.effettua_logout)
        self.ui.bt_modProfilo_salva.clicked.connect(self.modifica_profilo)
        
        # connessione bottoni alle pagine
        self.ui.bt_welcome_accedi.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_login))
        self.ui.bt_welcome_registrati.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_register))
        self.ui.bt_accedi_registrati.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_register))
        self.ui.bt_registrati_accedi.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_login))
        self.ui.bt_home.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_home))
        self.ui.bt_profilo.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_profilo))
        self.ui.bt_profilo_modifica.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_modProfilo))
        self.ui.bt_azioni.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_azioni))
        self.ui.bt_transazioni.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_transazioni))
        self.ui.bt_statistiche.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_NFT))
        self.ui.pushButton.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_mintNFT))
    
    def popola_combobox_immagini(self):
        print(">>> Inizio popolamento comboBox immagini")

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        print(f"Percorso base calcolato: {base_dir}")

        assets_dir = os.path.join(base_dir, "assets")
        print(f"Percorso completo assets: {assets_dir}")

        if not os.path.exists(assets_dir):
            print(f"⚠️  Cartella assets NON trovata in: {assets_dir}")
            return

        print(f"✅ Cartella assets trovata")

        estensioni_immagini = ('.png', '.jpg', '.jpeg', '.gif')
        immagini = []

        for f in os.listdir(assets_dir):
            print(f"Esaminando file: {f}")
            if f.lower().endswith(estensioni_immagini):
                immagini.append(f)
                print(f"➕ Aggiunto: {f}")
            else:
                print(f"❌ Ignorato (non immagine): {f}")

        if not immagini:
            print("⚠️  Nessuna immagine valida trovata nella cartella assets.")
        else:
            print(f"🎉 Immagini trovate: {immagini}")

        self.ui.mintNFT_imagecomboBox.clear()
        self.ui.mintNFT_imagecomboBox.addItems(immagini)
        print(f"✅ Caricate {len(immagini)} immagini nella comboBox.")
        print(">>> Fine popolamento comboBox immagini")
    
    def popola_nft_widget(self):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        address = self.database.get_address(id)

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        metadata_dir = os.path.join(base_dir, "nft_metadata")

        if not os.path.exists(metadata_dir):
            print("❌ Cartella nft_metadata non trovata.")
            return

        layout = QVBoxLayout()
        count = 0


        for filename in os.listdir(metadata_dir):
            if filename.endswith('.json'):
                path = os.path.join(metadata_dir, filename)
                with open(path, 'r') as f:
                    try:
                        data = json.load(f)
                        if data.get("owner", "").lower() == address.lower():
                            # === Crea layout orizzontale per ogni NFT ===
                            hbox = QHBoxLayout()

                            # Carica immagine NFT
                            img_path = os.path.join(base_dir, data.get('image'))
                            pixmap = QPixmap(img_path)
                            img_label = QLabel()
                            img_label.setPixmap(pixmap.scaledToWidth(100))  # ridimensiona immagine
                            hbox.addWidget(img_label)

                            # Info testuali
                            text_label = QLabel(
                                f"<b>{data.get('name')}</b>\n"
                                f"📍 Origine: {data.get('origin')}\n"
                                f"📦 Quantità: {data.get('quantity')}"
                            )
                            text_label.setStyleSheet("color: white; padding-left: 10px;")
                            hbox.addWidget(text_label)
                            
                            # Bottone per trasferimento NFT
                            transfer_button = QPushButton("Trasferisci")
                            transfer_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
                            transfer_button.clicked.connect(lambda _, token_id=data.get('token_id'): self.transfer_nft(token_id))
                            hbox.addWidget(transfer_button)

                            # Container per la riga
                            row = QWidget()
                            row.setLayout(hbox)
                            row.setStyleSheet("border: 1px solid gray; padding: 5px;")
                            layout.addWidget(row)

                            count += 1
                    except json.JSONDecodeError:
                        print(f"⚠️ Errore di parsing in: {filename}")

        if count == 0:
            layout.addWidget(QLabel("Nessun NFT trovato per questo utente."))

        container = QWidget()
        container.setLayout(layout)
        self.ui.scrollArea.setWidget(container)
    
    def registra_utente(self):
        email = self.ui.register_emailfield.text().strip()
        password = self.ui.register_passwordfield.text().strip()
        iva = self.ui.register_ivafield.text().strip()
        nome = self.ui.register_nomefield.text().strip()
        tipologia = self.ui.register_tipologiacomboBox.currentText().strip()
        indirizzo = self.ui.register_indirizzofield.text().strip()
        telefono = self.ui.register_telefonofield.text().strip()
        ragioneSociale = self.ui.register_ragionesocialefield.text().strip()
        sustainability = self.ui.register_sustainabilitydoubleSpinBox.value()
        
        # Controllo che nessun campo sia vuoto
        if not all([email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability]):
            self.ui.register_signalError.setText('Ci sono degli spazi vuoti')
            return

        # Chiamata alla funzione nel database
        try:
            # Registrazione dell'utente
            self.database.registra_utente(email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability)
            self.ui.register_signalError.setText('Registrazione avvenuta con successo!')

            # Login automatico dopo la registrazione
            if self.database.login_utente(email, password):
                self.ui.register_signalError.setText('Login avvenuto con successo!')

                # Recupera i dati dell'utente loggato dal database
                utente = self.database.get_utente_per_id()  # Usa la funzione per ottenere i dettagli dell'utente loggato

                if utente:  # Verifica che l'utente esista
                    self.ui.label_welcome.setText("Welcome, ")
                    self.ui.label_home_name.setText(utente['nome'])
                    self.ui.label_home_nft.setText(str(utente['nft']))
                    self.ui.label_home_token.setText(str(utente['token']))
                    self.ui.label_home_sustainability.setText(str(utente['sustainability']))

                # Cambio di pagina alla home
                self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_dashboard)
                self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_home)

                # Pulisci i campi del form di registrazione
                self.ui.register_emailfield.setText("")
                self.ui.register_passwordfield.setText("")
                self.ui.register_confirmpasswordfield.setText("")
                self.ui.register_ivafield.setText("")
                self.ui.register_nomefield.setText("")
                self.ui.register_tipologiacomboBox.setCurrentIndex(0)
                self.ui.register_indirizzofield.setText("")
                self.ui.register_telefonofield.setText("")
                self.ui.register_ragionesocialefield.setText("")
                self.ui.register_sustainabilitydoubleSpinBox.setValue(0)
                self.ui.register_signalError.setText("")
                
                # Riempi la pagina profilo
                self.ui.label_profilo_email.setText(utente['email'])
                self.ui.label_profilo_password.setText("●●●●●●")  # Non mostriamo la password
                self.ui.label_profilo_iva.setText(utente['iva'])
                self.ui.label_profilo_nome.setText(utente['nome'])
                self.ui.label_profilo_tipologia.setText(utente['tipologia'])
                self.ui.label_profilo_indirizzo.setText(utente['indirizzo'])
                self.ui.label_profilo_telefono.setText(utente['telefono'])
                self.ui.label_profilo_ragionesociale.setText(utente['ragione_sociale'])

                # Riempi la pagina modProfilo
                self.ui.editText_modProfilo_emailfield.setText(utente['email'])
                self.ui.editText_modProfilo_indirizzofield.setText(utente['indirizzo'])
                self.ui.editText_modProfilo_telefonofield.setText(utente['telefono'])
                
            else:
                self.ui.register_signalError.setText('Errore: Login non riuscito.')

        except Exception as e:
            self.ui.register_signalError.setText(f'Errore: {e}')

    def login_utente(self):
        email = self.ui.login_emailfield.text().strip()
        password = self.ui.login_passwordfield.text().strip()

        # Controllo che nessun campo sia vuoto
        if not all([email, password]):
            self.ui.login_signalError.setText('Email o password non inseriti correttamente')
            return

        
        try:
            # Verifica che le credenziali siano corrette
            if self.database.login_utente(email, password):  # Funzione per verificare le credenziali
                # Recupera l'ID dell'utente loggato da connessione_sqlite
                utente = self.database.get_utente_per_id()  # Recupera i dati dell'utente tramite l'ID
                if utente:
                    # Aggiorna la UI con i dati dell'utente
                    self.ui.login_signalError.setText('Login avvenuto con successo!')

                    # Passa alla pagina home o alla pagina successiva
                    self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_dashboard)
                    self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_home)
                    self.ui.label_welcome.setText("Welcome back, ")
                    self.ui.label_home_name.setText(utente['nome'])
                    self.ui.label_home_nft.setText(str(utente['nft']))
                    self.ui.label_home_token.setText(str(utente['token']))
                    self.ui.label_home_sustainability.setText(str(utente['sustainability']))

                    # Riempi la pagina profilo
                    self.ui.label_profilo_email.setText(utente['email'])
                    self.ui.label_profilo_password.setText("●●●●●●")  # Non mostriamo la password
                    self.ui.label_profilo_iva.setText(utente['iva'])
                    self.ui.label_profilo_nome.setText(utente['nome'])
                    self.ui.label_profilo_tipologia.setText(utente['tipologia'])
                    self.ui.label_profilo_indirizzo.setText(utente['indirizzo'])
                    self.ui.label_profilo_telefono.setText(utente['telefono'])
                    self.ui.label_profilo_ragionesociale.setText(utente['ragione_sociale'])
                    self.check_balance()  # Aggiorna il saldo all'accesso

                    # Riempi la pagina modProfilo
                    self.ui.editText_modProfilo_emailfield.setText(utente['email'])
                    self.ui.editText_modProfilo_indirizzofield.setText(utente['indirizzo'])
                    self.ui.editText_modProfilo_telefonofield.setText(utente['telefono'])

                    # Pulisci i field del login una volta entrato
                    self.ui.login_emailfield.setText("")
                    self.ui.login_passwordfield.setText("")
                    self.ui.login_signalError.setText("")  # Pulisce il messaggio di errore
                    
                    self.popola_combobox_immagini()  # Popola la comboBox delle immagini
                    self.popola_nft_widget()  # Popola la pagina NFT con gli NFT dell'utente
                else:
                    self.ui.login_signalError.setText("Errore: Impossibile recuperare i dati dell'utente.")
            else:
                # Se il login non ha avuto successo
                self.ui.login_signalError.setText('Errore: Credenziali non valide.')

        except Exception as e:
            self.ui.login_signalError.setText(f'Errore: {e}')
            
    def effettua_logout(self):
        # Chiama il metodo logout dal database senza assegnarlo a 'utente'
        self.database.logout()  # Chiamata alla funzione logout() per resettare lo stato dell'utente

        # Pulisce eventuali label con i dati utente
        self.ui.label_home_name.setText("")
        self.ui.label_home_nft.setText("")
        self.ui.label_home_token.setText("")
        self.ui.label_home_sustainability.setText("")

        # Torna alla schermata di login
        self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_welcome)
        
    def modifica_profilo(self):
        nuova_email = self.ui.editText_modProfilo_emailfield.text().strip()
        nuovo_indirizzo = self.ui.editText_modProfilo_indirizzofield.text().strip()
        nuovo_telefono = self.ui.editText_modProfilo_telefonofield.text().strip()
        vecchia_password = self.ui.editText_modProfilo_vecchiaPasswordfield.text().strip()
        nuova_password = self.ui.editText_modProfilo_nuovaPasswordfield.text().strip()
        conferma_nuova_password = self.ui.editText_modProfilo_confermaNuovaPasswordfield.text().strip()

        # Controllo che la nuova password coincida con la conferma
        if nuova_password and nuova_password != conferma_nuova_password:
            self.ui.modProfilo_signalError.setText("Le nuove password non coincidono.")
            return

        aggiornato = self.database.modifica_utente(
            vecchia_password=vecchia_password,
            nuovo_nome=None,
            nuovo_indirizzo=nuovo_indirizzo,
            nuovo_telefono=nuovo_telefono,
            nuova_password=nuova_password if nuova_password else None,
            nuova_email=nuova_email
        )

        if aggiornato:
            self.ui.modProfilo_signalError.setText("Profilo aggiornato con successo")
            self.ui.editText_modProfilo_emailfield.setText(nuova_email)
            self.ui.editText_modProfilo_indirizzofield.setText(nuovo_indirizzo)
            self.ui.editText_modProfilo_telefonofield.setText(nuovo_telefono)
            self.ui.editText_modProfilo_vecchiaPasswordfield.setText("")
            self.ui.editText_modProfilo_nuovaPasswordfield.setText("")
            self.ui.editText_modProfilo_confermaNuovaPasswordfield.setText("")
        else:
            self.ui.modProfilo_signalError.setText("Errore durante l'aggiornamento del profilo")
            
    def mint_tokens(self):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        amount_str = self.ui.amountInput.text().strip()
        
        address = self.database.get_address(id)

        # Validazione dell'indirizzo Ethereum
        if not self.is_valid_address(address):
            self.ui.mintingLabel.setText("Errore: Indirizzo Ethereum non valido.")
            return

        # Prova a convertire direttamente in float
        try:
            # Sostituisce la virgola con il punto, per compatibilità internazionale
            amount_str = amount_str.replace(',', '.')
            amount = round(float(amount_str), 2)

            if amount <= 0:
                self.ui.mintingLabel.setText("Errore: L'importo deve essere maggiore di zero.")
                return

            tx_hash = self.contract.mint_tokens(address, amount)
            self.ui.mintingLabel.setText(f"Transazione inviata: {tx_hash}")
            self.ui.burningLabel.setText(f"")
            self.check_balance()

        except ValueError:
            self.ui.mintingLabel.setText("Errore: L'importo deve essere un numero valido.")
            print(f"Errore durante la conversione dell'importo: '{amount_str}'")
        except Exception as e:
            self.ui.mintingLabel.setText(f"Errore: {str(e)}")
            
    def burn_tokens(self):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        amount_str = self.ui.amountInput.text().strip()

        address = self.database.get_address(id)

        if not self.is_valid_address(address):
            self.ui.burningLabel.setText("Errore: Indirizzo Ethereum non valido.")
            return

        try:
            # Sostituisce la virgola con punto e arrotonda a 2 decimali
            amount = round(float(amount_str.replace(',', '.')), 2)

            if amount <= 0:
                self.ui.burningLabel.setText("Errore: L'importo deve essere maggiore di zero.")
                return

            # Per fare il burn usiamo un valore negativo
            burn_amount = -amount
            tx_hash = self.contract.mint_tokens(address, burn_amount)

            self.ui.burningLabel.setText(f"🔥 Token bruciati! TX hash: {tx_hash}")
            self.ui.mintingLabel.setText("")
            self.check_balance()
            print(f"Bruciati {amount} token per {address}")

        except ValueError:
            self.ui.burningLabel.setText("Errore: L'importo deve essere un numero valido.")
            print(f"Errore durante la conversione dell'importo: '{amount_str}'")
        except Exception as e:
            self.ui.burningLabel.setText(f"Errore durante il burn: {str(e)}")
            
    def transfer_tokens(self):
        utente = self.database.get_utente_per_id()
        id_from = str(utente['id']).strip()
        id_to = self.ui.transaction_recipientInput.text().strip()
        amount_str = self.ui.transaction_amountInput.text().strip()

        address_from = self.database.get_address(id_from)
        address_to = self.database.get_address(id_to)

        if not self.is_valid_address(address_from) or not self.is_valid_address(address_to):
            self.ui.transferLabel.setText("Errore: Uno degli indirizzi Ethereum non è valido.")
            return

        try:
            # Converte virgole in punti e arrotonda a due cifre
            amount = round(float(amount_str.replace(',', '.')), 2)

            if amount <= 0:
                self.ui.transferLabel.setText("Errore: L'importo deve essere maggiore di zero.")
                return

            tx_hash = self.contract.transfer_tokens(address_to, amount)
            self.check_balance()
            self.ui.transferLabel.setText(f"✅ Token inviati! TX hash: {tx_hash}")

        except ValueError:
            self.ui.transferLabel.setText("Errore: L'importo deve essere un numero valido.")
            print(f"Errore durante la conversione dell'importo: '{amount_str}'")
        except Exception as e:
            self.ui.transferLabel.setText(f"Errore nel trasferimento: {str(e)}")

    def check_balance(self):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        
        address = self.database.get_address(id)

        if not self.is_valid_address(address):
            self.ui.balanceLabel.setText("Errore: Indirizzo Ethereum non valido.")
            return

        try:
            balance = self.contract.get_balance(address)
            self.ui.balanceLabel.setText(f"Saldo Token: {balance}")
            self.ui.label_home_token.setText(f"{balance}")
            self.ui.transaction_addressLabel.setText(f"Saldo Token: {balance}")
            print(f"Saldo dell'indirizzo {address}: {balance} MTK")
        except Exception as e:
            self.ui.balanceLabel.setText(f"Errore: {str(e)}")

    def is_valid_address(self, address):
        """Verifica che l'indirizzo sia valido (inizia con 0x e ha una lunghezza di 42 caratteri)."""
        return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))
    
    def mint_nft(self, path_file):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        address = self.database.get_address(id)
        token_uri = path_file
        if address and token_uri:
            tx_hash, token_id = self.nft_contract.mint_product_nft(address, token_uri)
            self.ui.text_output.append(f"Mintato! TX: {tx_hash}\nToken ID: {token_id}")
            print(f"Mintato NFT con ID {token_id} per l'indirizzo {address}. TX: {tx_hash}")
            
    def transfer_nft(self):
        from_address = self.ui.input_from_address.text().strip()
        private_key = self.ui.input_private_key.text().strip()
        to_address = self.ui.input_transfer_to.text().strip()
        token_id = int(self.ui.input_tokenid.text().strip())

        if from_address and private_key and to_address and token_id >= 0:
            tx_hash = self.nft_contract.transfer_product_nft(from_address, to_address, token_id, private_key)
            self.ui.text_output.append(f"Trasferito! TX: {tx_hash}")

    def show_history(self):
        token_id = int(self.ui.input_tokenid.text().strip())
        history = self.nft_contract.get_ownership_history(token_id)
        self.ui.text_output.append(f"Storico: {history}")

    def crea_json_nft(self):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        address = self.database.get_address(id)
        
        nome = self.ui.mintNFT_namefield.text().strip()
        descrizione = self.ui.mintNFT_descriptionfield.toPlainText().strip()
        immagine = self.ui.mintNFT_imagecomboBox.currentText().strip()
        origine = self.ui.mintNFT_originfield.text().strip()
        produttore = self.ui.mintNFT_producerfield.text().strip()
        certificazione = self.ui.mintNFT_certificationfield.text().strip()
        sostenibilita = self.ui.mintNFT_sustainabilityspinBox.value()
        quantita = self.ui.mintNFT_quantityfield.text().strip()
        data_raccolta = self.ui.mintNFT_harvestdate.date().toString("yyyy-MM-dd")
        data_scadenza = self.ui.mintNFT_expirydate.date().toString("yyyy-MM-dd")

        if not nome or not immagine:
            print("Nome o immagine mancanti, impossibile creare JSON.")
            return

        json_data = {
            "name": nome,
            "description": descrizione,
            "image": f"assets/{immagine}",
            "origin": origine,
            "producer": produttore,
            "certification": certificazione,
            "sustainability_score": sostenibilita,
            "quantity": quantita,
            "harvest_date": data_raccolta,
            "expiry_date": data_scadenza,
            "owner": address
        }

        # Percorso cartella nft_metadata
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        metadata_dir = os.path.join(base_dir, "nft_metadata")
        os.makedirs(metadata_dir, exist_ok=True)

        nome_file = f"{nome.replace(' ', '_')}_{data_raccolta}.json"
        path_file = os.path.join(metadata_dir, nome_file)

        # Scrivi il JSON temporaneo
        with open(path_file, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"✅ JSON NFT creato in: {path_file}")

        # 🔥 MINT e AGGIORNA JSON con tokenId e ownershipHistory
        tx_hash, token_id = self.nft_contract.mint_product_nft(address, path_file)
        print(f"✅ Mintato NFT con ID {token_id} per {address}. TX: {tx_hash}")

        # 📜 Ottieni lo storico dei possessori
        history = self.nft_contract.get_ownership_history(token_id)

        # 🔁 Riapri il JSON, aggiorna e risalva
        with open(path_file, 'r') as f:
            updated_data = json.load(f)

        updated_data["token_id"] = token_id
        updated_data["ownership_history"] = history

        with open(path_file, 'w') as f:
            json.dump(updated_data, f, indent=2)

        # Log/GUI
        self.ui.text_output.append(f"✅ NFT registrato!\nToken ID: {token_id}\nTX Hash: {tx_hash}")
        self.popola_nft_widget()  # Popola la pagina NFT con gli NFT dell'utente
        self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_NFT)
        
        # Pulisce i campi dopo la creazione
        self.ui.mintNFT_namefield.clear()
        self.ui.mintNFT_descriptionfield.clear()
        self.ui.mintNFT_imagecomboBox.setCurrentIndex(0)
        self.ui.mintNFT_originfield.clear()
        self.ui.mintNFT_producerfield.clear()
        self.ui.mintNFT_certificationfield.clear()
        self.ui.mintNFT_sustainabilityspinBox.setValue(0)
        self.ui.mintNFT_quantityfield.clear()
        self.ui.mintNFT_harvestdate.setDate(QtCore.QDate.currentDate())
        self.ui.mintNFT_expirydate.setDate(QtCore.QDate.currentDate())
        
if __name__ == "__main__":
     app = QApplication(sys.argv)
     my_app = FinestraPrincipale()
     my_app.show()
     sys.exit(app.exec_())