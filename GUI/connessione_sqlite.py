import sqlite3
import bcrypt


class Comunicazione():
    def __init__(self):
        self.connessione = sqlite3.connect('../database.db')
        self.utente_loggato = None  # Attributo per memorizzare l'ID dell'utente loggato
    
    
    def registra_utente(self, email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability):
        """Registra i dati del nuovo utente"""
        cursor = self.connessione.cursor()
        
        # Hash della password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        query = '''
            INSERT INTO tabella_utenti 
            (EMAIL, PASSWORD, IVA, NOME, TIPOLOGIA, INDIRIZZO, TELEFONO, RAGIONE_SOCIALE, SUSTAINABILITY)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        try:
            cursor.execute(query, (email, hashed_password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability))
            self.connessione.commit()
            print("Registrazione avvenuta con successo.")
        except sqlite3.IntegrityError:
            print("Errore: L'email risulta già registrata.")
        except sqlite3.Error as e:
            print(f"Errore durante la registrazione: {e}")
        finally:
            cursor.close()
        
    def login_utente(self, email, password):
        """Verifica le credenziali e salva l'ID dell'utente loggato."""
        cursor = self.connessione.cursor()
        
        # Recupera l'hash della password e l'ID utente
        cursor.execute("SELECT id, password FROM tabella_utenti WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user[1] if isinstance(user[1], bytes) else user[1].encode('utf-8')  # Recupero l'hash memorizzato
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                self.utente_loggato = user[0]  # Memorizza l'ID
                print(f"Login avvenuto con successo. ID utente: {self.utente_loggato}")
                return True
            else:
                print("Errore: Credenziali non valide.")
                return False
        else:
            print("Errore: Credenziali non valide.")
            return False

    def get_utente_per_id(self):
        """Recupera i dati dell'utente loggato in base al suo ID."""
        if self.utente_loggato is None:
            print("Errore: Nessun utente loggato.")
            return None

        cursor = self.connessione.cursor()
        cursor.execute("""
            SELECT id, email, password, iva, nome, tipologia, 
                indirizzo, telefono, ragione_sociale, 
                sustainability, nft, token, address
            FROM tabella_utenti 
            WHERE id = ?
        """, (self.utente_loggato,))

        user = cursor.fetchone()

        if user:
            return {
                'id': user[0],
                'email': user[1],
                'password': user[2],
                'iva': user[3],
                'nome': user[4],
                'tipologia': user[5],
                'indirizzo': user[6],
                'telefono': user[7],
                'ragione_sociale': user[8],
                'sustainability': user[9],
                'nft': user[10],
                'token': user[11],
                'address': user[12],
            }
        else:
            print("Errore: Utente non trovato.")
            return None
        
    def modifica_utente(self, vecchia_password=None, nuovo_nome=None, nuovo_indirizzo=None, nuovo_telefono=None, nuova_password=None, conferma_nuova_password=None, nuova_email=None):
        if self.utente_loggato is None:
            print("Errore: Nessun utente loggato.")
            return False

        cursor = self.connessione.cursor()
        
        # Recupera la password attuale dal database
        cursor.execute("SELECT PASSWORD FROM tabella_utenti WHERE ID = ?", (self.utente_loggato,))
        record = cursor.fetchone()

        if not record:
            print("Errore: Utente non trovato.")
            return False

        password_attuale = record[0] if isinstance(record[0], bytes) else record[0].encode('utf-8')
        
        # Verifica che la vecchia password sia corretta
        if vecchia_password and not bcrypt.checkpw(vecchia_password.encode('utf-8'), password_attuale):
            print("Errore: La vecchia password non corrisponde.")
            return False

        campi_da_modificare = []
        valori = []
        
        if nuovo_nome:
            campi_da_modificare.append("NOME = ?")
            valori.append(nuovo_nome)
        if nuovo_indirizzo:
            campi_da_modificare.append("INDIRIZZO = ?")
            valori.append(nuovo_indirizzo)
        if nuovo_telefono:
            campi_da_modificare.append("TELEFONO = ?")
            valori.append(nuovo_telefono)
        if nuova_password:
            nuova_password_hash = bcrypt.hashpw(nuova_password.encode('utf-8'), bcrypt.gensalt())
            campi_da_modificare.append("PASSWORD = ?")
            valori.append(nuova_password_hash)
        if nuova_email:
            campi_da_modificare.append("EMAIL = ?")
            valori.append(nuova_email)

        if not campi_da_modificare:
            print("Errore: Nessun campo da modificare.")
            return False

        query = f"UPDATE tabella_utenti SET {', '.join(campi_da_modificare)} WHERE ID = ?"
        valori.append(self.utente_loggato)

        try:
            cursor.execute(query, tuple(valori))
            self.connessione.commit()
            print("Modifica avvenuta con successo.")
            return True
        except sqlite3.Error as e:
            print(f"Errore durante la modifica del profilo: {e}")
            return False
        
    def aggiorna_balance(self, nuovo_balance):
        """ Aggiorna il balance dell'utente loggato """
        if self.utente_loggato is None:
            print("Errore: Nessun utente loggato.")
            return False
        cursor = self.connessione.cursor()
        try:
            cursor.execute("UPDATE tabella_utenti SET token = ? WHERE ID = ?", (nuovo_balance, self.utente_loggato))
            self.connessione.commit()
            print("Balance aggiornato con successo.")
            return True
        except sqlite3.Error as e:
            print(f"Errore durante l'aggiornamento del balance: {e}")
            return False
        
    def logout(self):
        """ Funzione per disconnettere l'utente """
        self.utente_loggato = None
        print("Logout avvenuto con successo.")
        
    def get_address(self, id):
        cursor = self.connessione.cursor()
        cursor.execute("SELECT address FROM tabella_utenti WHERE id = ?", (id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        else:
            return