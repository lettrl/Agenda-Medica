import os
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "agenda.db"))
SEED_USERNAME = os.getenv("SEED_USERNAME", "admin")
SEED_EMAIL = os.getenv("SEED_EMAIL", "admin@teste.com")
SEED_PASSWORD = os.getenv("SEED_PASSWORD", "123456")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL
        )
    """)

    cur.execute('SELECT id FROM usuarios WHERE username = ?', (SEED_USERNAME,))
    if cur.fetchone() is None:
        cur.execute('INSERT INTO usuarios (username, email, senha_hash) VALUES (?, ?, ?)',
                    (SEED_USERNAME, SEED_EMAIL, generate_password_hash(SEED_PASSWORD)))
        print(f"[seed]Usuário de teste '{SEED_USERNAME}' criado com sucesso.")
    else:
        print(f"[seed] Usuário de teste '{SEED_USERNAME}' já existe.")

    conn.commit()

    if __name__ == "__main__":
        init_db()