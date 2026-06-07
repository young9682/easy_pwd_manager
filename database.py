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
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS password_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credential_id INTEGER NOT NULL,
            length INTEGER,
            has_uppercase INTEGER,
            has_lowercase INTEGER,
            has_numbers INTEGER,
            has_symbols INTEGER,
            strength_score INTEGER,
            FOREIGN KEY (credential_id) REFERENCES credentials(id) ON DELETE CASCADE
        )
    ''')

    c.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()

def add_password(name, username, password, length, upper, lower, num, sym, score):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO credentials (name, username, password)
        VALUES (?, ?, ?)
    ''', (name, username, password))
    cred_id = c.lastrowid
    c.execute('''
        INSERT INTO password_analysis (credential_id, length, has_uppercase,
                                       has_lowercase, has_numbers, has_symbols,
                                       strength_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (cred_id, length, upper, lower, num, sym, score))
    conn.commit()
    conn.close()

def get_all_passwords():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT c.id, c.name, c.username, c.password,
               p.length, p.strength_score, c.created_at
        FROM credentials c
        LEFT JOIN password_analysis p ON c.id = p.credential_id
        ORDER BY c.created_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def delete_password(pid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("DELETE FROM credentials WHERE id = ?", (pid,))
    conn.commit()
    conn.close()
