import sqlite3

class DatabaseConnector:
    def __init__(self):
        self.connessione = sqlite3.connect('../wallet.db')

    def get_address(self, id):
        cursor = self.connessione.cursor()
        cursor.execute("SELECT address FROM wallets WHERE id = ?", (id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        else:
            return 