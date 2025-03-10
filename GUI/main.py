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
        
        # connessione bottoni a finestre
        self.ui.bt_welcome_accedi.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_login))
        self.ui.bt_welcome_registrati.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_register))
        self.ui.bt_accedi_registrati.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_register))
        self.ui.bt_registrati_accedi.clicked.connect(lambda: self.ui.stackedWidgetEsterno.setCurrentWidget(self.ui.page_login))
        
        
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
        
        
if __name__ == "__main__":
     app = QApplication(sys.argv)
     my_app = FinestraPrincipale()
     my_app.show()
     sys.exit(app.exec_())