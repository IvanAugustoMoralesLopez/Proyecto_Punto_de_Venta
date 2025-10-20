import pyodbc
from config import CONNECTION_STRING

print("[DEBUG] Iniciando db.py...")

def get_db_connection():
    print("[DEBUG] db.py: Llamando a get_db_connection()...")
    try:
        print("[DEBUG] db.py: Intentando pyodbc.connect()...")
        
        print(f"[DEBUG] db.py: Usando string: {CONNECTION_STRING}")
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        print("[DEBUG] db.py: Conexión y cursor CREADOS exitosamente.")
        return conn, cursor
    except Exception as e:
        print("❌ [ERROR] db.py: Error al conectar con la base de datos:", e)
        print("    Asegúrate de que SQL Server esté corriendo y que el driver 'ODBC Driver 17' esté instalado.")
        return None, None

print("[DEBUG] db.py: Archivo importado.")