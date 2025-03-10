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
        
        # Hash della password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        
        # Chiamata alla funzione nel database
        try:
            self.database.registra_utente(None, email, password_hash, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability, 0)
            self.ui.register_signalError.setText('Registrazione avvenuta con successo!')

            # Cambio di pagina alla home
            self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_dashboard)
            self.ui.stackedWidgetInterno.setCurrentWidget(self.ui.page_home)
            
            utente = self.database.get_utente_per_email(email)  # Supponiamo che questa funzione esista nel tuo DB
            self.utente_loggato = utente
            
            self.ui.label_welcome.setText("Welcome, ")
            self.ui.label_home_name.setText(utente['nome'])
            self.ui.label_home_nft.setText(str(utente['nft']))
            self.ui.label_home_token.setText(str(utente['token']))
            self.ui.label_home_sustainability.setText(str(utente['sustainability']))
            
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

        except Exception as e:
            self.ui.register_signalError.setText(f'Errore: {e}')
            

    def login_utente(self):
        email = self.ui.login_emailfield.text().strip()
        password = self.ui.login_passwordfield.text().strip()

        # Controllo che nessun campo sia vuoto
        if not all([email, password]):
            self.ui.login_signalError.setText('Email o password non inseriti correttamente')
            return

        # Recupera l'utente dal database usando l'email
        try:
            utente = self.database.get_utente_per_email(email)  # Supponiamo che questa funzione esista nel tuo DB

            if utente is None:
                self.ui.login_signalError.setText('Utente non trovato')
                return

            # Confronta la password inserita con quella hashata nel database
            if bcrypt.checkpw(password.encode('utf-8'), utente['password']):
                self.utente_loggato = utente
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
                self.ui.label_profilo_password.setText("●●●●●●")
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
                self.ui.login_signalError.setText("")

            else:
                self.ui.login_signalError.setText('Password errata')

        except Exception as e:
            self.ui.login_signalError.setText(f'Errore: {e}')
            
    def effettua_logout(self):
        # Cancella i dati dell'utente autenticato
        self.utente_loggato = None  

        # Pulisce eventuali label con i dati utente
        self.ui.label_home_name.setText("")
        self.ui.label_home_nft.setText("")
        self.ui.label_home_token.setText("")
        self.ui.label_home_sustainability.setText("")

        # Torna alla schermata di login
        self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_welcome)
        
    def modifica_profilo(self):
        utente = self.utente_loggato
        email = self.ui.editText_modProfilo_emailfield.text().strip()
        indirizzo = self.ui.editText_modProfilo_indirizzofield.text().strip()
        telefono = self.ui.editText_modProfilo_telefonofield.text().strip()
        vecchiaPassword = self.ui.editText_modProfilo_vecchiaPasswordfield.text().strip()
        nuovaPassword = self.ui.editText_modProfilo_nuovaPasswordfield.text().strip()
        
        # Controllo se la vecchia password corrisponde
        if not bcrypt.checkpw(vecchiaPassword.encode('utf-8'), utente['password']):
            self.ui.modProfilo_signalError.setText("La vecchia password non corrisponde")
            return
        
        # Se viene inserita una nuova password, la criptiamo
        nuova_password_hash = bcrypt.hashpw(nuovaPassword.encode('utf-8'), bcrypt.gensalt()) if nuovaPassword else None

        # Aggiornamento nel database
        aggiornato = self.database.modifica_utente(
            email=email,
            nuovo_indirizzo=indirizzo,
            nuovo_telefono=telefono,
            nuova_password=nuova_password_hash
        )

        if aggiornato:
            self.ui.modProfilo_signalError.setText("Profilo aggiornato con successo")
        else:
            self.ui.modProfilo_signalError.setText("Errore durante l'aggiornamento del profilo")
        
        
if __name__ == "__main__":
     app = QApplication(sys.argv)
     my_app = FinestraPrincipale()
     my_app.show()
     sys.exit(app.exec_())