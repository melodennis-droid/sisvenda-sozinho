import sqlite3

def get_connection():
    conn = sqlite3.connect('sisvenda.db')
    return conn

def criar_tabelas():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    preco REAL,
                    estoque INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY,
                    nome TEXT)''')
    
    conn.commit()
    conn.close()

criar_tabelas()