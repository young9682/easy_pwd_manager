import sqlite3

DB_FILE = "passwords.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS password_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credential_id INTEGER NOT NULL,
            password TEXT NOT NULL,
            length INTEGER,
            has_uppercase INTEGER,
            has_lowercase INTEGER,
            has_numbers INTEGER,
            has_symbols INTEGER,
            strength_score INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (credential_id) REFERENCES credentials(id) ON DELETE CASCADE
        )
    ''')

    c.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()

def add_credential(name, username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO credentials (name, username) VALUES (?, ?)', (name, username))
    cred_id = c.lastrowid
    conn.commit()
    conn.close()
    return cred_id

def add_password_analysis(cred_id, password, length, upper, lower, num, sym, score):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO password_analysis
            (credential_id, password, length, has_uppercase, has_lowercase,
             has_numbers, has_symbols, strength_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cred_id, password, length, upper, lower, num, sym, score))
    conn.commit()
    conn.close()

def get_all_credentials():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT c.id, c.name, c.username,
               p.password, p.length, p.strength_score, c.created_at
        FROM credentials c
        LEFT JOIN password_analysis p ON c.id = p.credential_id
        WHERE p.id = (SELECT MAX(id) FROM password_analysis WHERE credential_id = c.id)
        ORDER BY c.created_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_password_history(cred_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT password, length, strength_score, created_at
        FROM password_analysis
        WHERE credential_id = ?
        ORDER BY created_at DESC
    ''', (cred_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_credential(cred_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("DELETE FROM credentials WHERE id = ?", (cred_id,))
    conn.commit()
    conn.close()
