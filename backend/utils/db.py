import sqlite3
import os
from config import DATA_DIR

DB_PATH = os.path.join(DATA_DIR, "multilinks.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de visitas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS visitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subdominio TEXT NOT NULL,
        fecha TEXT NOT NULL,
        user_agent TEXT,
        referrer TEXT
    )
    ''')
    
    # Tabla de clicks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clicks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subdominio TEXT NOT NULL,
        boton TEXT NOT NULL,
        fecha TEXT NOT NULL
    )
    ''')
    
    # Índices para consultas rápidas
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_visitas_sub ON visitas(subdominio)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clicks_sub ON clicks(subdominio)')
    
    conn.commit()
    conn.close()

# Inicializar la base de datos automáticamente al importar este módulo
init_db()
