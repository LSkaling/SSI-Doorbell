import sqlite3

DB_FILE = "doorbellrings.db"

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    with conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT UNIQUE NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            invoked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
        )
        ''')
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_FILE)

def get_or_create_client_id(conn, client_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clients WHERE client_id = ?", (client_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO clients (client_id) VALUES (?)", (client_id,))
        conn.commit()
        return cursor.lastrowid
    return row[0]

def record_invocation(client_id):
    conn = get_db_connection()
    try:
        client_internal_id = get_or_create_client_id(conn, client_id)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO invocations (client_id) VALUES (?)", (client_internal_id,))
        conn.commit()
    finally:
        conn.close()

def fetch_usage_stats(days):
    conn = get_db_connection()
    query = """
        SELECT c.client_id, COUNT(i.id) AS invocation_count
        FROM invocations i
        INNER JOIN clients c ON i.client_id = c.id
        WHERE i.invoked_at >= DATETIME('now', ?)
        GROUP BY c.client_id;
    """
    cursor = conn.cursor()
    cursor.execute(query, (f'-{days} days',))
    results = cursor.fetchall()
    conn.close()
    return results
