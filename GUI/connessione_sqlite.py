import sqlite3

class Comunicazione():
    def __init__(self):
        self.connessione = sqlite3.connect('../database.db')
    
    def registra_utente(self, id, email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability, token):
        cursor = self.connessione.cursor()
        query = '''INSERT INTO tabella_utenti (EMAIL, PASSWORD, IVA, NOME, TIPOLOGIA, INDIRIZZO, TELEFONO, RAGIONE_SOCIALE, SUSTAINABILITY)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                
        cursor.execute(query, (email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability))
        self.connessione.commit()
        cursor.close()
        
    def get_utente_per_email(self, email):
        cursor = self.connessione.cursor()
        cursor.execute("SELECT * FROM tabella_utenti WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            # Restituisce un dizionario con i dati dell'utente
            return {
                'id': user[0],
                'email': user[1],   # Supponiamo che l'email sia la prima colonna
                'password': user[2], # La password è hashata nella seconda colonna
                'nome': user[4],
                'sustainability': user[9],
                'nft': user[10],
                'token': user[11],
                # Aggiungi altri campi se necessari
            }
        else:
            return None