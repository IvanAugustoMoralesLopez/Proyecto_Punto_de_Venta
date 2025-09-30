import pyodbc
from config import CONNECTION_STRING
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

def verificar_caja_abierta():
    conn, cursor = get_db_connection()
    if not conn:
        return None
    try:
        cursor.execute("SELECT id, monto_inicial FROM caja WHERE estado = 'abierta'")
        return cursor.fetchone()
    except Exception as e:
        print(f"Error al verificar el estado de la caja abierta: {e}")
        return None
    finally:
        conn.close()

def abrir_caja(monto_inicial):
    conn, cursor = get_db_connection()
    if not conn:
        return None
    try:
        fecha_apertura = datetime.now()
        sql_query = "INSERT INTO caja (fecha_apertura, monto_inicial, estado) VALUES (?, ?, ?)"
        cursor.execute(sql_query, (fecha_apertura, monto_inicial, 'abierta'))
        conn.commit()
        
        cursor.execute("SELECT @@IDENTITY AS id")
        id_sesion = cursor.fetchone()[0]
        return id_sesion
    except Exception as e:
        print(f"Error al abrir caja: {e}")
        return None
    finally:
        conn.close()

def obtener_ventas_sesion(id_sesion):
    
    conn, cursor = get_db_connection()
    if not conn: return {}

    try:
        cursor.execute("SELECT fecha_apertura FROM caja WHERE id = ?", (id_sesion,))
        resultado = cursor.fetchone()
        if not resultado: return {}
        fecha_apertura = resultado[0]

        sql_query = "SELECT metodo_pago, SUM(monto) FROM tickets WHERE fecha >= ? GROUP BY metodo_pago"
        cursor.execute(sql_query, (fecha_apertura,))
        
        ventas = {"Efectivo": 0.0, "Tarjeta": 0.0, "Otros": 0.0}
        
        for metodo, total in cursor.fetchall():
            if metodo == 'Efectivo':
                ventas['Efectivo'] += float(total)
            elif metodo == 'Tarjeta':
                ventas['Tarjeta'] += float(total)
            else: # Agrupa Transferencia, Mercado Pago, etc.
                ventas['Otros'] += float(total)
        return ventas

    except Exception as e:
        print(f"Error al obtener ventas de la sesión: {e}")
        return {}
    finally:
        conn.close()

def cerrar_caja(id_sesion, monto_inicial, monto_final_real, ventas_sesion): 
    
    conn, cursor = get_db_connection()
    if not conn: return

    try:
        ventas_efectivo = ventas_sesion.get("Efectivo", 0.0)
        monto_final_esperado = float(monto_inicial) + ventas_efectivo
        diferencia = float(monto_final_real) - monto_final_esperado
        
        sql_query = """
            UPDATE caja SET fecha_cierre = ?, total_ventas_efectivo = ?, 
            total_ventas_tarjeta = ?, total_ventas_otros = ?, monto_final_esperado = ?, 
            monto_final_real = ?, diferencia = ?, estado = 'cerrada'
            WHERE id = ? """
        cursor.execute(sql_query, (
            datetime.now(), ventas_efectivo, ventas_sesion.get("Tarjeta", 0.0),
            ventas_sesion.get("Otros", 0.0), monto_final_esperado, monto_final_real, 
            diferencia, id_sesion
        ))
        conn.commit()
        print("Caja cerrada exitosamente.")
    except Exception as e:
        print(f"Error al cerrar la caja: {e}")
    finally:
        conn.close()