import pyodbc
from config import STRING_DE_CONEXION 


def get_db_connection():
    
    try:
        conn = pyodbc.connect(STRING_DE_CONEXION)
        return conn, conn.cursor()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None, None

# Funciones de Artículos (CRUD)

def agregar_articulo(codigo, descripcion, precio, stock):
    conn, cursor = get_db_connection()
    if not conn:
        return

    try:
        
        sql_query = "INSERT INTO articulos (codigo, descripcion, precio, stock) VALUES (?, ?, ?, ?)"
        cursor.execute(sql_query, (codigo, descripcion, precio, stock))
        conn.commit() # Confirmamos los cambios
    except Exception as e:
        print(f"Error al agregar el artículo: {e}")
    finally:
        conn.close() # Siempre cerramos la conexión

def buscar_articulo(texto_busqueda):
    conn, cursor = get_db_connection()
    if not conn:
        return []

    try:
        sql_query = "SELECT * FROM articulos WHERE descripcion LIKE ?"
        cursor.execute(sql_query, ('%' + texto_busqueda + '%',))
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al buscar artículos: {e}")
        return []
    finally:
        conn.close()


def listar_articulos():
    conn, cursor = get_db_connection()
    if not conn:
        return []
    try:
        cursor.execute("SELECT * FROM articulos ORDER BY descripcion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al listar artículos: {e}")
        return []
    finally:
        conn.close()

def editar_articulo(id, codigo, descripcion, precio, stock):
    conn, cursor = get_db_connection()
    if not conn:
        return
    try:
        sql_query = """
            UPDATE articulos
            SET codigo = ?, descripcion = ?, precio = ?, stock = ?
            WHERE id = ?
        """
        cursor.execute(sql_query, (codigo, descripcion, precio, stock, id))
        conn.commit()
    except Exception as e:
        print(f"Error al editar el artículo: {e}")
    finally:
        conn.close()

def borrar_articulo(id):
    conn, cursor = get_db_connection()
    if not conn:
        return
    try:
        sql_query = "DELETE FROM articulos WHERE id = ?"
        cursor.execute(sql_query, (id,))
        conn.commit()
    except Exception as e:
        print(f"Error al borrar el artículo: {e}")
    finally:
        conn.close()