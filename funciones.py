import pyodbc
from config import CONNECTION_STRING
from tkinter import messagebox
from datetime import datetime


def get_db_connection():
    
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
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

def obtener_articulos():
    conn, cursor = get_db_connection()
    if not conn:
        return []

    try:
        cursor.execute("SELECT id, descripcion, precio FROM articulos ORDER BY descripcion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener artículos: {e}")
        return []
    finally:
        conn.close()

class Ticket:
    def __init__(self, punto_venta, metodo_pago, monto, fecha, tipo_ticket, referencia):
        self.punto_venta = punto_venta
        self.metodo_pago = metodo_pago
        self.monto = monto
        self.fecha = fecha
        self.tipo_ticket = tipo_ticket
        self.referencia = referencia
        self.id = None  # Se asigna al guardar

    def guardar(self):
        conn, cursor = get_db_connection()
        if not conn:
            print("No se pudo establecer la conexión para guardar el ticket.")
            return

        try:
            cursor.execute("""
                INSERT INTO tickets (punto_venta, metodo_pago, monto, fecha, tipo_ticket, referencia)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.punto_venta, self.metodo_pago, self.monto, self.fecha, self.tipo_ticket, self.referencia))
            conn.commit()

            cursor.execute("SELECT @@IDENTITY AS id")
            self.id = cursor.fetchone()[0]

        except Exception as e:
            print(f"Error al guardar el ticket: {e}")
        finally:
            conn.close()

    def guardar_detalle(self, detalle):
        """
        Guarda el detalle del ticket. Cada ítem incluye:
        (id_articulo, precio_unitario, cantidad, nombre_articulo)
        """
        conn, cursor = get_db_connection()
        if not conn:
            print("No se pudo establecer la conexión para guardar el detalle.")
            return

        try:
            for id_articulo, precio, cantidad, nombre_articulo in detalle:
                cursor.execute("""
                    INSERT INTO detalle_ticket (id_ticket, id_articulo, cantidad, precio_unitario, nombre_articulo)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.id, id_articulo, cantidad, precio, nombre_articulo))
            conn.commit()

        except Exception as e:
            print(f"Error al guardar el detalle del ticket: {e}")
        finally:
            conn.close()