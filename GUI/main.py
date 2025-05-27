import sys
import json
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import bcrypt
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import  QPropertyAnimation,QEasingCurve, Qt
from PyQt5 import QtCore, QtWidgets
from functools import partial
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
            
        self.needed_tokens = 0

        # Connessione dei bottoni alle funzioni
        self.ui.mintButton.clicked.connect(self.mint_tokens)
        self.ui.burnButton.clicked.connect(self.burn_tokens)
        self.ui.transferButton.clicked.connect(self.transfer_tokens)
        
        self.ui.btn_mint.clicked.connect(self.mint_nft)
        self.ui.btn_transfer.clicked.connect(self.transfer_nft)
        self.ui.btn_history.clicked.connect(self.show_history)
        self.ui.mintNFT_mintNFTbutton.clicked.connect(self.crea_json_nft)
        self.ui.azioniNormali_eseguiButton.clicked.connect(self.esegui_azioneNormale)
        self.ui.azioniCompensative_mintingButton.clicked.connect(self.esegui_azioneCompensativa)
        self.ui.transferNFT_btnTransfer.clicked.connect(self.transferNFT)
        self.ui.azioniNormali_helpButton.clicked.connect(self.help_tokens)
        
        self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_welcome)
        
        
        # connessione bottoni a funzioni
        self.ui.bt_registrati_registrati.clicked.connect(self.registra_utente)
        self.ui.bt_accedi_accedi.clicked.connect(self.login_utente)
        self.ui.bt_logout.clicked.connect(self.effettua_logout)
        self.ui.bt_modProfilo_salva.clicked.connect(self.modifica_profilo)
        
        self.ui.azioniNormali_azioneComboBox.currentIndexChanged.connect(self.aggiorna_dettagli_azione)
        self.ui.azioniNormali_trasformaInTokenButton.clicked.connect(self.calcola_token)
        
        # connessione bottoni alle pagine
        self.ui.bt_welcome_accedi.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_login))
        self.ui.bt_welcome_registrati.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_register))
        self.ui.bt_accedi_registrati.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_register))
        self.ui.bt_registrati_accedi.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_login))
        self.ui.bt_home.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_home))
        self.ui.bt_profilo.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_profilo))
        self.ui.bt_profilo_modifica.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_modProfilo))
        self.ui.bt_azioniNormali.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_azioniNormali))
        self.ui.bt_azioniCompensative.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_azioniCompensative))
        self.ui.bt_transazioni.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_transazioni))
        self.ui.bt_NFT.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_NFT))
        self.ui.pushButton.clicked.connect(lambda: self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_mintNFT))
    
    def carica_combo_azioni(self):
        azioni = self.database.carica_azioni_nella_combobox()
        self.ui.azioniNormali_azioneComboBox.clear()
        for azione in azioni:
            self.ui.azioniNormali_azioneComboBox.addItem(azione[0])
            
    def aggiorna_dettagli_azione(self):
        # Ottieni il nome dell'azione selezionata nella ComboBox
        azione = self.ui.azioniNormali_azioneComboBox.currentText()
        
        # Recupera l'unità di riferimento dal DB
        info = self.database.get_info_azione(azione)
        
        # Aggiorna la label con l'unità, se esiste
        if info:
            self.ui.azioniNormali_unitaDiMisuraLabel.setText(info["unita_di_riferimento"])
            self.ui.azioniNormali_riferimentoPraticoLabel.setText(info["riferimento"])
        else:
            self.ui.azioniNormali_unitaDiMisuraLabel.setText("N/A")
            self.ui.azioniNormali_riferimentoPraticoLabel.setText("N/A")
    
    def popola_combobox_NFT(self):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        address = self.database.get_address(id)
        
        print(">>> Inizio popolamento comboBox nft")

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        print(f"Percorso base calcolato: {base_dir}")

        nft_dir = os.path.join(base_dir, "nft_metadata")
        print(f"Percorso completo nft: {nft_dir}")

        if not os.path.exists(nft_dir):
            print(f"⚠️  Cartella nft_metadata NON trovata in: {nft_dir}")
            return

        print(f"✅ Cartella nft trovata")

        estensioni_nft = ('.json')
        nft = []

        for f in os.listdir(nft_dir):
            if f.lower().endswith('.json'):
                path = os.path.join(nft_dir, f)
                try:
                    with open(path, 'r') as file:
                        data = json.load(file)
                        owner = data.get("owner", "").lower()
                        usable = data.get("usable", False)
                        
                        if owner == address.lower() and usable is True:
                            nft.append(f)
                            print(f"➕ Aggiunto (owner match e usable): {f}")
                        else:
                            print(f"❌ Escluso: owner ≠ address o usable ≠ true → {f}")
                except Exception as e:
                    print(f"⚠️ Errore nel parsing del file {f}: {e}")
            else:
                print(f"❌ Ignorato (non JSON): {f}")

        if not nft:
            print("⚠️  Nessun NFT valido trovato nella cartella nft_metadata.")
        else:
            print(f"🎉 NFT validi trovati: {nft}")

        self.ui.azioniNormali_NFTcomboBox.clear()
        self.ui.azioniNormali_NFTcomboBox.addItems(nft)
        print(f"✅ Caricate {len(nft)} nft nella comboBox.")
        print(">>> Fine popolamento comboBox nft")
    
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
        
    def popola_combobox_certificazioni(self):
        print(">>> Inizio popolamento comboBox certificazioni")

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        print(f"Percorso base calcolato: {base_dir}")

        certifications_dir = os.path.join(base_dir, "assets/certifications")
        print(f"Percorso completo certifications: {certifications_dir}")

        if not os.path.exists(certifications_dir):
            print(f"⚠️  Cartella certifications NON trovata in: {certifications_dir}")
            return

        print(f"✅ Cartella certifications trovata")

        estensioni_certificazioni = ('.png', '.jpg', '.jpeg', '.gif')
        certificazioni = []

        for f in os.listdir(certifications_dir):
            print(f"Esaminando file: {f}")
            if f.lower().endswith(estensioni_certificazioni):
                certificazioni.append(f)
                print(f"➕ Aggiunto: {f}")
            else:
                print(f"❌ Ignorato (non certificazione): {f}")

        if not certificazioni:
            print("⚠️  Nessuna certificazione valida trovata nella cartella assets.")
        else:
            print(f"🎉 Certificazioni trovate: {certificazioni}")

        self.ui.mintNFT_certificationcomboBox.clear()
        self.ui.mintNFT_certificationcomboBox.addItems(certificazioni)
        print(f"✅ Caricate {len(certificazioni)} certificazioni nella comboBox.")
        print(">>> Fine popolamento comboBox certificazioni")
    
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
                        token_id = int(data.get("token_id"))
                        usable = data.get("usable", False)

                        try:
                            onchain_owner = self.nft_contract.contract.functions.ownerOf(token_id).call()
                        except Exception as e:
                            print(f"⚠️ Token {token_id} non valido o già bruciato: {e}")
                            continue

                        if onchain_owner.lower() == address.lower() and usable:
                            # (prosegui con costruzione dell'NFT visuale)
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
                            transfer_button.clicked.connect(
                                partial(self.handle_transfer_click, data, data.get('token_id'))
                            )
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
        
    def handle_transfer_click(self, json_data, token_id):
        # Mostra la pagina di trasferimento
        self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_transferNFT)
        
        # Costruisci il percorso assoluto dell’immagine se serve
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        img_path = os.path.join(base_dir, json_data.get('image'))

        # Carica e imposta l’immagine
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.ui.transferNFT_image.setPixmap(pixmap.scaledToWidth(200))  # o .scaled(width, height)
        else:
            print("❌ Immagine non trovata o non valida:", img_path)
        self.ui.transferNFT_name.setText(json_data.get('name'))
        
        # Salva temporaneamente i dati per uso futuro
        self.selected_nft_data = json_data
        self.selected_token_id = token_id
    
    def registra_utente(self):
        email = self.ui.register_emailfield.text().strip()
        password = self.ui.register_passwordfield.text().strip()
        address = self.ui.register_addressfield.text().strip()
        iva = self.ui.register_ivafield.text().strip()
        nome = self.ui.register_nomefield.text().strip()
        tipologia = self.ui.register_tipologiacomboBox.currentText().strip()
        indirizzo = self.ui.register_indirizzofield.text().strip()
        telefono = self.ui.register_telefonofield.text().strip()
        ragioneSociale = self.ui.register_ragionesocialefield.text().strip()
        sustainability = self.ui.register_sustainabilitydoubleSpinBox.value()
        token = 0  # Inizializza i token a 0
        SOGLIA_CO2 = {
            "Farmer and Fisher": 25,
            "Manufacturer": 100,
            "Packer": 20,
            "Storage": 40,
            "Waste": 15,
            "Carrier": 80,
            "Retailer": 50,
            "Food and Beverage Hospitality": 35,
            "Client": 10
        }
        
        if sustainability >= SOGLIA_CO2[tipologia]:
            self.ui.register_signalError.setText("Emissioni troppo alte per {tipologia}: {sustainability} >= {SOGLIA_CO2[tipologia]}. Registrazione negata.")
            print(f"Emissioni troppo alte per {tipologia}: {sustainability} >= {SOGLIA_CO2[tipologia]}")
            return
        token = (SOGLIA_CO2[tipologia] - sustainability)/SOGLIA_CO2[tipologia]*100  # Calcola i token in base alla sostenibilità
        print(f"Token calcolati: {token} per {tipologia} con sostenibilità {sustainability}")
        # Controllo che nessun campo sia vuoto
        if not all([email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability, address]): # Controllo che nessun campo sia vuoto
            self.ui.register_signalError.setText('Ci sono degli spazi vuoti')
            return

        # Chiamata alla funzione nel database
        try:
            # Registrazione dell'utente
            self.database.registra_utente(email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability, address)
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
                    self.mint_tokens(token) # Mint dei token appena registrato

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
                    self.ui.azioniNormali_helpButton.hide()  # Nascondi il pulsante di aiuto per le azioni normali

                    # Passa alla pagina home o alla pagina successiva
                    self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_dashboard)
                    self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_home)
                    self.ui.label_welcome.setText("Welcome back, ")
                    self.ui.label_home_name.setText(utente['nome'])
                    nft_count = self.conta_nft_posseduti()
                    self.ui.label_home_nft.setText(str(nft_count))

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
                    
                    self.carica_combo_azioni()  # Popola la comboBox delle azioni
                    self.popola_combobox_NFT()  # Popola la comboBox degli NFT
                    self.popola_combobox_immagini()  # Popola la comboBox delle immagini
                    self.popola_combobox_certificazioni()  # Popola la comboBox delle certificazioni
                    self.popola_nft_widget()  # Popola la pagina NFT con gli NFT dell'utente
                    self.popola_utenti_who_need()  # Popola la pagina utenti che hanno bisogno di token
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
    
    def calcola_token(self):
        """
        Calcola i token da mintare (+) o burnare (-)
        :param nome_azione: nome dell’azione scelta
        :param quantita: quantità dell’attività svolta (es. 2.5 tonnellate)
        :param emissioni_registrate_totali: emissioni effettive totali CO2e generate
        :return: dizionario con info e token
        """
        nome_azione = self.ui.azioniNormali_azioneComboBox.currentText()
        quantita = self.ui.azioniNormali_quantitaDoubleSpinBox.value()
        emissioni_registrate_totali = self.ui.azioniNormali_CO2emessaDoubleSpinBox.value()
        
        info = self.database.get_info_azione(nome_azione)
        if not info:
            raise ValueError("Azione non trovata nel database.")

        # Emissione media per unità operativa
        unita_di_misura = info["unita_di_riferimento"]  # es. "ton", "kg", "km"
        emissione_media_unitaria = float(info["emissioni_medie"])
        riferimento = info["riferimento"]  # es. "1 ton", "100 kg", "100 km"
        
        # Calcolo emissioni attese in base alla quantità
        emissioni_attese_totali = emissione_media_unitaria * quantita

        # Differenza = risparmio o eccesso
        delta = round(emissioni_attese_totali - emissioni_registrate_totali, 2)
        token = abs(delta)  # Token da mintare o burnare
        # Determina se mintare o burnare
        if delta > 0:
            azione_token = "mint"
        elif delta < 0:
            azione_token = "burn"
        else:
            azione_token = "neutro"
            
        self.ui.azioniNormali_trasformazioneInTokenLabel.setText(f"Token da {azione_token}: {token}")
        self.ui.azioniNormali_TxHashLabel.setText(f"Azione: {nome_azione}\nQuantità: {quantita} {unita_di_misura}\nEmissioni attese: {emissioni_attese_totali} CO2e\nEmissioni registrate: {emissioni_registrate_totali} CO2e\nDelta: {delta} CO2e\nToken da {azione_token}: {token}")
    
    def esegui_azioneNormale(self):
        nft = self.ui.azioniNormali_NFTcomboBox.currentText().strip()
        nome_azione = self.ui.azioniNormali_azioneComboBox.currentText()
        quantita = self.ui.azioniNormali_quantitaDoubleSpinBox.value()
        emissioni_registrate_totali = self.ui.azioniNormali_CO2emessaDoubleSpinBox.value()
        
        info = self.database.get_info_azione(nome_azione)
        if not info:
            raise ValueError("Azione non trovata nel database.")

        # Emissione media per unità operativa
        unita_di_misura = info["unita_di_riferimento"]  # es. "ton", "kg", "km"
        emissione_media_unitaria = float(info["emissioni_medie"])
        riferimento = info["riferimento"]  # es. "1 ton", "100 kg", "100 km"
        
        # Calcolo emissioni attese in base alla quantità
        emissioni_attese_totali = emissione_media_unitaria * quantita

        # Differenza = risparmio o eccesso
        delta = round(emissioni_attese_totali - emissioni_registrate_totali, 2)
        token = abs(delta)  # Token da mintare o burnare
        # Determina se mintare o burnare
        if delta > 0:
            azione_token = "mint"
            self.mint_tokens(token)
            self.ui.azioniNormali_TxHashLabel.setText(f"Token mintati: {token}")
            self.aggiorna_risparmio_co2_nft(nft, token, "mint")
        elif delta < 0:
            azione_token = "burn"
            self.burn_tokens(token)
        else:
            azione_token = "neutro"
            self.ui.azioniNormali_TxHashLabel.setText("Nessuna azione necessaria: emissioni attese e registrate coincidono.")
            
    def esegui_azioneCompensativa(self):
        token = self.ui.azioniCompensative_CO2doubleSpinBox.value()
        self.mint_tokens(token)
        self.ui.azioniCompensative_mintingLabel.setText(f"Token mintati: {token}")
    
    def mint_tokens(self, token):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        # amount_str = self.ui.amountInput.text().strip()
        amount = token
        address = self.database.get_address(id)

        # Validazione dell'indirizzo Ethereum
        if not self.is_valid_address(address):
            self.ui.mintingLabel.setText("Errore: Indirizzo Ethereum non valido.")
            return

        # Prova a convertire direttamente in float
        try:
            # Sostituisce la virgola con il punto, per compatibilità internazionale
            # amount_str = amount_str.replace(',', '.')
            # amount = round(float(amount_str), 2)

            if amount <= 0:
                self.ui.mintingLabel.setText("Errore: L'importo deve essere maggiore di zero.")
                return

            tx_hash = self.contract.mint_tokens(address, amount)
            #self.ui.mintingLabel.setText(f"Transazione inviata: {tx_hash}")
            #self.ui.burningLabel.setText(f"")
            print(f"Mintati {amount} token per {address}")
            self.check_balance()

        except ValueError:
            self.ui.mintingLabel.setText("Errore: L'importo deve essere un numero valido.")
            print(f"Errore durante la conversione dell'importo: '{token}'")
        except Exception as e:
            self.ui.mintingLabel.setText(f"Errore: {str(e)}")
            
    def burn_tokens(self, token):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        # amount_str = self.ui.amountInput.text().strip()
        amount = token
        nft = self.ui.azioniNormali_NFTcomboBox.currentText().strip()
        address = self.database.get_address(id)

        if not self.is_valid_address(address):
            self.ui.burningLabel.setText("Errore: Indirizzo Ethereum non valido.")
            return

        try:
            # Sostituisce la virgola con punto e arrotonda a 2 decimali
            # amount = round(float(amount_str.replace(',', '.')), 2)

            if amount <= 0:
                self.ui.burningLabel.setText("Errore: L'importo deve essere maggiore di zero.")
                return

            # Per fare il burn usiamo un valore negativo
            burn_amount = -amount
            tx_hash = self.contract.mint_tokens(address, burn_amount)

            #self.ui.burningLabel.setText(f"🔥 Token bruciati! TX hash: {tx_hash}")
            #self.ui.mintingLabel.setText("")
            self.check_balance()
            self.ui.azioniNormali_TxHashLabel.setText(f"Token bruciati: {token}")
            self.aggiorna_risparmio_co2_nft(nft, token, "burn")

        except ValueError:
            self.ui.azioniNormali_TxHashLabel.setText("Errore: L'importo deve essere un numero valido.")
            #self.ui.burningLabel.setText("Errore: L'importo deve essere un numero valido.")
            print(f"Errore durante la conversione dell'importo: '{token}'")
        except Exception as e:
            #self.ui.burningLabel.setText(f"Errore durante il burn: {str(e)}")
            balance = self.contract.get_balance(address)
            needed_tokens = round(abs(balance - token), 2)
            self.needed_tokens = needed_tokens  # salva il valore
            
            self.ui.azioniNormali_TxHashLabel.setText(f"Errore durante il burn: non hai abbastanza token.\nTi mancano {needed_tokens} token.\nPuoi richiedere aiuto cliccando sul pulsante di aiuto.")
            self.ui.azioniNormali_helpButton.show()  # Mostra il pulsante di aiuto se il burn fallisce
            
    def help_tokens(self):
        '''Funzione che si attiva quando l'utente non ha token e clicca su "Aiuto"'''
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        current_need = float(utente['need_token'])

        # Confronto robusto per evitare problemi con i float
        if abs(self.needed_tokens - current_need) > 0.001:
            aggiornato = self.database.help_token(id, self.needed_tokens)
            if aggiornato:
                self.ui.azioniNormali_TxHashLabel.setText(f"Aiuto richiesto! Saranno richiesti {self.needed_tokens:.2f} token.")
            else:
                self.ui.azioniNormali_TxHashLabel.setText("Errore nella richiesta di aiuto.")
        else:
            self.ui.azioniNormali_TxHashLabel.setText(f"Hai già richiesto aiuto. Ti servono {current_need:.2f} token.")
            
    def popola_utenti_who_need(self):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        utenti = self.database.get_needed_users(id)
        self.ui.transaction_recipientComboBox.clear()
        for u in utenti:
            print(f"{u['id']} - {u['nome']} - {u['address']} richiede {u['need_token']} token")
            self.ui.transaction_recipientComboBox.addItem(f"{u['id']} - {u['nome']} - {u['address']} - ({u['need_token']} token)")
        
    def transfer_tokens(self):
        utente = self.database.get_utente_per_id()
        id_from = str(utente['id']).strip()

        testo_combo = self.ui.transaction_recipientComboBox.currentText().strip()
        amount_str = self.ui.transaction_amountInput.text().strip()
        private_key = self.ui.transaction_privateKeyInput.text().strip()

        # ⚠️ Controllo che tutti i campi siano compilati
        if not testo_combo or not amount_str or not private_key:
            self.ui.transferLabel.setText("Errore: Compila tutti i campi obbligatori.")
            return

        try:
            id_to = testo_combo.split(" - ")[0].strip()
            match = re.search(r"\(([\d.]+)\s+token\)", testo_combo)
            needed_token = float(match.group(1)) if match else 0.0

            address_from = self.database.get_address(id_from)
            address_to = self.database.get_address(id_to)

            if not self.is_valid_address(address_from) or not self.is_valid_address(address_to):
                self.ui.transferLabel.setText("Errore: Uno degli indirizzi Ethereum non è valido.")
                return

            amount = round(float(amount_str.replace(",", ".")), 2)
            if amount < needed_token:
                self.ui.transferLabel.setText(
                    f"Errore: Devi trasferire almeno {needed_token:.2f} token."
                )
                return

            tx_hash = self.contract.transfer_tokens(address_from, private_key, address_to, amount)
            self.check_balance()
            self.database.reset_need_token(id_to)
            self.popola_utenti_who_need()
            self.ui.transferLabel.setText(f"✅ Token inviati! TX hash: {tx_hash}")

        except ValueError:
            self.ui.transferLabel.setText("Errore: L'importo inserito non è valido.")
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
            self.ui.azioniNormali_balanceLabel.setText(f"Saldo Token: {balance}")
            self.ui.azioniCompensative_balanceLabel.setText(f"Saldo Token: {balance}")
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
            nft_count = self.conta_nft_posseduti()
            self.ui.label_home_nft.setText(str(nft_count))

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
        certificazione = self.ui.mintNFT_certificationcomboBox.currentText().strip()
        quantita = self.ui.mintNFT_quantityfield.text().strip()
        data_raccolta = self.ui.mintNFT_harvestdate.date().toString("yyyy-MM-dd")
        data_scadenza = self.ui.mintNFT_expirydate.date().toString("yyyy-MM-dd")
        saldo_co2 = 0  # Placeholder per il saldo CO2, se necessario
        utlizzabile = True

        if not nome or not immagine:
            print("Nome o immagine mancanti, impossibile creare JSON.")
            return

        json_data = {
            "name": nome,
            "description": descrizione,
            "image": f"assets/{immagine}",
            "origin": origine,
            "producer": produttore,
            "certification": f"assets/certifications/{certificazione}",
            "quantity": quantita,
            "harvest_date": data_raccolta,
            "expiry_date": data_scadenza,
            "owner": address,
            "risparmio_co2": saldo_co2,
            "usable": utlizzabile
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
        self.popola_combobox_NFT()  # Popola la comboBox degli NFT
        nft_count = self.conta_nft_posseduti()
        self.ui.label_home_nft.setText(str(nft_count))
        self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_NFT)
        
        # Pulisce i campi dopo la creazione
        self.ui.mintNFT_namefield.clear()
        self.ui.mintNFT_descriptionfield.clear()
        self.ui.mintNFT_imagecomboBox.setCurrentIndex(0)
        self.ui.mintNFT_originfield.clear()
        self.ui.mintNFT_producerfield.clear()
        self.ui.mintNFT_certificationcomboBox.setCurrentIndex(0)
        self.ui.mintNFT_quantityfield.clear()
        self.ui.mintNFT_harvestdate.setDate(QtCore.QDate.currentDate())
        self.ui.mintNFT_expirydate.setDate(QtCore.QDate.currentDate())
        
    def aggiorna_risparmio_co2_nft(self, json_filename, delta_token, operazione):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        path = os.path.join(base_dir, "nft_metadata", json_filename)

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            saldo_attuale = float(data.get("risparmio_co2", 0))

            if operazione == "mint":
                saldo_attuale += delta_token
            elif operazione == "burn":
                saldo_attuale -= delta_token

            data["risparmio_co2"] = round(saldo_attuale, 2)

            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✅ risparmio_co2 aggiornato per {json_filename}: {data['risparmio_co2']}")

        except Exception as e:
            print(f"❌ Errore aggiornando risparmio_co2 per {json_filename}: {e}")
        
    def transferNFT(self, token_id):
        utente = self.database.get_utente_per_id()
        id_from = str(utente['id']).strip()
        from_address = self.database.get_address(id_from)
        
        id_to = self.ui.transferNFT_inputTransferTo.text().strip()
        to_address = self.database.get_address(id_to)
        
        private_key = self.ui.transferNFT_inputPrivateKey.text().strip()
        token_id = int(self.selected_token_id)

        if from_address and private_key and to_address and token_id >= 0:
            tx_hash = self.nft_contract.transfer_product_nft(from_address, to_address, token_id, private_key)
            # self.ui.text_output.append(f"Trasferito! TX: {tx_hash}")
            print(f"Trasferito NFT con ID {token_id} da {from_address} a {to_address}. TX: {tx_hash}")

            # 🔁 Aggiorna il campo owner nel file JSON
            self.aggiorna_owner_json_nft(token_id, to_address)

            # 🔁 Ricarica interfaccia
            self.popola_nft_widget()
            self.popola_combobox_NFT()  # Popola la comboBox degli NFT
            
            nft_count = self.conta_nft_posseduti()
            self.ui.label_home_nft.setText(str(nft_count))
        
    def aggiorna_owner_json_nft(self, token_id, nuovo_owner):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        metadata_dir = os.path.join(base_dir, "nft_metadata")
        

        for f in os.listdir(metadata_dir):
            if f.endswith('.json'):
                path = os.path.join(metadata_dir, f)
                try:
                    with open(path, 'r') as file:
                        data = json.load(file)
                        if int(data.get("token_id", -1)) == token_id:
                            data["owner"] = nuovo_owner
                            
                            history = self.nft_contract.get_ownership_history(token_id)
                            data["ownership_history"] = history
                            
                            # Salva il JSON aggiornato
                            with open(path, 'w') as out:
                                json.dump(data, out, indent=2)
                            
                            print(f"✅ Owner e history aggiornati in {f} → {nuovo_owner}")
                            return
                        
                except Exception as e:
                    print(f"⚠️ Errore nel file {f}: {e}")

        print(f"❌ Nessun file JSON trovato per token_id {token_id}")
        
    def conta_nft_posseduti(self):
        utente = self.database.get_utente_per_id()
        id = str(utente['id']).strip()
        address = self.database.get_address(id).lower()

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        metadata_dir = os.path.join(base_dir, "nft_metadata")

        count = 0

        if not os.path.exists(metadata_dir):
            print("❌ Cartella nft_metadata non trovata.")
            return 0

        for f in os.listdir(metadata_dir):
            if f.endswith('.json'):
                path = os.path.join(metadata_dir, f)
                try:
                    with open(path, 'r') as file:
                        data = json.load(file)
                        if data.get("owner", "").lower() == address:
                            count += 1
                except Exception as e:
                    print(f"⚠️ Errore leggendo {f}: {e}")
                    continue

        return count
        
if __name__ == "__main__":
     app = QApplication(sys.argv)
     my_app = FinestraPrincipale()
     my_app.show()
     sys.exit(app.exec_())