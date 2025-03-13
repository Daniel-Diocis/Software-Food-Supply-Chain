import sys
import bcrypt
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import  QPropertyAnimation,QEasingCurve
from PyQt5 import QtCore, QtWidgets
from interfacciaUtente import Ui_MainWindow
from connessione_sqlite import Comunicazione

class FinestraPrincipale(QMainWindow):
    def __init__(self):
        super(FinestraPrincipale, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.database = Comunicazione()
        
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
                    self.ui.label_profilo_indirizzo.setText(utente['indirizzo'])
                    self.ui.label_profilo_telefono.setText(utente['telefono'])
                    self.ui.label_profilo_ragionesociale.setText(utente['ragione_sociale'])

                    # Riempi la pagina modProfilo
                    self.ui.editText_modProfilo_emailfield.setText(utente['email'])
                    self.ui.editText_modProfilo_indirizzofield.setText(utente['indirizzo'])
                    self.ui.editText_modProfilo_telefonofield.setText(utente['telefono'])

                    # Pulisci i field del login una volta entrato
                    self.ui.login_emailfield.setText("")
                    self.ui.login_passwordfield.setText("")
                    self.ui.login_signalError.setText("")  # Pulisce il messaggio di errore
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
        
        
if __name__ == "__main__":
     app = QApplication(sys.argv)
     my_app = FinestraPrincipale()
     my_app.show()
     sys.exit(app.exec_())