import sqlite3

class Comunicazione():
    def __init__(self):
        self.connessione = sqlite3.connect('../database.db')
    
    def registra_utente(self, email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability):
        cursor = self.connessione.cursor()
        query = '''INSERT INTO tabella_utenti (EMAIL, PASSWORD, IVA, NOME, TIPOLOGIA, INDIRIZZO, TELEFONO, RAGIONE_SOCIALE, SUSTAINABILITY)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                
        cursor.execute(query, (email, password, iva, nome, tipologia, indirizzo, telefono, ragioneSociale, sustainability))
        self.connessione.commit()
        cursor.close()
        
    def get_utente_per_email(self, email):
        cursor = self.connessione.cursor()
        cursor.execute("""
            SELECT id, email, password, iva, nome, tipologia, 
                indirizzo, telefono, ragione_sociale, 
                sustainability, nft, token
            FROM tabella_utenti 
            WHERE email = ?
        """, (email,))
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
            }
        else:
            return None
        
    def modifica_utente(self, email, nuovo_nome=None, nuovo_indirizzo=None, nuovo_telefono=None, nuova_password=None):
        cursor = self.connessione.cursor()
        
        # Creazione dinamica della query in base ai campi forniti
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
            campi_da_modificare.append("PASSWORD = ?")
            valori.append(nuova_password)
        
        # Se non ci sono campi da aggiornare, esci
        if not campi_da_modificare:
            return False

        query = f"UPDATE tabella_utenti SET {', '.join(campi_da_modificare)} WHERE EMAIL = ?"
        valori.append(email)

        try:
            cursor.execute(query, tuple(valori))
            self.connessione.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print(f"Errore durante la modifica dell'utente: {e}")
            return False