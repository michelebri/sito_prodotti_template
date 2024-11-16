import sqlite3
import json
import bcrypt


class DatabaseManager:
    def __init__(self, path):
        self.path = path
        self.create_table()
        self.populate_database()
        self.special_token = "REGISTER_TOKEN"


    def create_connection(self):
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create_table(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                Email TEXT PRIMARY KEY,
                Username TEXT,
                Password TEXT,
                Logged BOOLEAN DEFAULT 0
            );''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Fornitore (
                    Pivafornitore TEXT PRIMARY KEY,
                    Nome TEXT,
                    Citta TEXT
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Cliente (
                    Pivacliente TEXT PRIMARY KEY,
                    Nome TEXT,
                    Citta TEXT
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Fornitura (
                    Codicefornitura TEXT PRIMARY KEY,
                    Idcliente TEXT,
                    Idfornitore TEXT,
                    FOREIGN KEY (Idcliente) REFERENCES Cliente(Pivacliente),
                    FOREIGN KEY (Idfornitore) REFERENCES Fornitore(Pivafornitore)
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Prodotto (
                    Barcode TEXT PRIMARY KEY,
                    Nome TEXT,
                    Peso TEXT,
                    Categoria TEXT,
                    Prezzo REAL,
                    Idfornitura TEXT,
                    FOREIGN KEY (Idfornitura) REFERENCES Fornitura(Codicefornitura)
                );
            ''')

            print("Tabelle create correttamente.")
        except sqlite3.Error as e:
            print("Errore nella creazione delle tabelle:", e)
        finally:
            conn.commit()
            conn.close()

    def populate_database(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            with open('data.json', 'r') as json_file:
                data = json.load(json_file)

            fornitori = data['fornitori']
            clienti = data['clienti']
            forniture = data['forniture']
            prodotti = data['prodotti']

            cursor.executemany('INSERT INTO Fornitore (Pivafornitore, Nome, Citta) VALUES (?, ?, ?)', fornitori)
            cursor.executemany('INSERT INTO Cliente (Pivacliente, Nome, Citta) VALUES (?, ?, ?)', clienti)
            cursor.executemany('INSERT INTO Fornitura (Codicefornitura, Idcliente, Idfornitore) VALUES (?, ?, ?)', forniture)
            cursor.executemany('INSERT INTO Prodotto (Barcode, Nome, Peso, Categoria, Prezzo, Idfornitura) VALUES (?, ?, ?, ?, ?, ?)', prodotti)
            conn.commit()
            print("Dati inseriti correttamente.")
        except sqlite3.Error as e:
            print("Errore nell'inserimento dei dati:", e)
        except FileNotFoundError as e:
            print("File data.json non trovato:", e)
        except json.JSONDecodeError as e:
            print("Errore nel parsing del file JSON:", e)
        finally:
            conn.close()

    def insert_user(self, email, username ="", password="", logged=""):
        if username == "":
            username = None
        if password == "":
            password = None
        else:
            bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(bytes, salt)
        if logged == "":
            logged = False
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (Email, Username, Password, Logged) VALUES (?, ?, ?, ?)", (email, username,password, logged))
        conn.commit()
        conn.close()
    
    def update_user(self, email, username, password):
        conn = self.create_connection()
        cursor = conn.cursor()
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(bytes, salt)
        user = self.get_user(email)
        if user is None:
            return "utente non esistente"
        #se username di user è diverso da None allora vuol dire che l'utente ha inserito un username
        if user[1] is not None:
            return "utente già registrato"
        #I have user with only email i want to find the user and modify the None values

        cursor.execute("UPDATE Users SET Username = ?, Password = ? WHERE Email = ?", (username, password, email))
        conn.commit()

    
    def get_user(self, email):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def remove_user(self, username):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE Username = ?", (username,))
        conn.commit()
        conn.close()
    
    def check_access(self, username, password):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user is None:
            return False
        else:
            user_password = user[2]
            bytes = password.encode('utf-8')
            return bcrypt.checkpw(bytes, user_password)
    
    def check_if_user_can_added(self, email):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user is None
    
    def get_prodotti(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Prodotto")
        prodotti = cursor.fetchall()
        conn.close()
        return prodotti
    
    def get_prodotto(self, barcode):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Prodotto WHERE Barcode = ?", (barcode,))
        prodotto = cursor.fetchone()
        conn.close()
        return prodotto