import sqlite3

class DatabaseConnector:
    def __init__(self, wallet):
        self.db_file = wallet

    def connect(self):
        return sqlite3.connect(self.db_file)

    def get_balance(self, address):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM wallets WHERE address = ?", (address,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return 0

    def update_balance(self, address, new_balance):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE wallets SET balance = ? WHERE address = ?", (new_balance, address))
        conn.commit()
        conn.close()