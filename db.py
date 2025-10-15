import pyodbc
from config import CONNECTION_STRING

def get_db_connection():
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        print("❌ Error al conectar con la base de datos:", e)
        return None, None