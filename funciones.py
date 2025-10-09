import pyodbc
from config import CONNECTION_STRING
from datetime import datetime
from decimal import Decimal, InvalidOperation

def get_db_connection():
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn, conn.cursor()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None, None

def agregar_articulo(codigo, descripcion, precio, stock):
    conn, cursor = get_db_connection()
    if not conn: return
    try:
        sql = "INSERT INTO articulos (codigo, descripcion, precio, stock) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (codigo, descripcion, precio, stock))
        conn.commit()
    except Exception as e:
        print(f"Error al agregar el artículo: {e}")
    finally:
        if conn: conn.close()

def buscar_articulo(texto_busqueda):
    conn, cursor = get_db_connection()
    if not conn: return []
    try:
        sql = "SELECT * FROM articulos WHERE codigo = ? OR descripcion LIKE ?"
        cursor.execute(sql, (texto_busqueda, '%' + texto_busqueda + '%'))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al buscar artículos: {e}")
        return []
    finally:
        if conn: conn.close()

def listar_articulos():
    conn, cursor = get_db_connection()
    if not conn: return []
    try:
        cursor.execute("SELECT * FROM articulos ORDER BY descripcion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al listar artículos: {e}")
        return []
    finally:
        if conn: conn.close()

def editar_articulo(id, codigo, descripcion, precio, stock):
    conn, cursor = get_db_connection()
    if not conn: return
    try:
        sql = "UPDATE articulos SET codigo = ?, descripcion = ?, precio = ?, stock = ? WHERE id = ?"
        cursor.execute(sql, (codigo, descripcion, precio, stock, id))
        conn.commit()
    except Exception as e:
        print(f"Error al editar el artículo: {e}")
    finally:
        if conn: conn.close()

def borrar_articulo(id):
    conn, cursor = get_db_connection()
    if not conn: return
    try:
        cursor.execute("DELETE FROM articulos WHERE id = ?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error al borrar el artículo: {e}")
    finally:
        if conn: conn.close()

def obtener_articulos():
    conn, cursor = get_db_connection()
    if not conn: return []
    try:
        cursor.execute("SELECT id, descripcion, precio FROM articulos ORDER BY descripcion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener artículos: {e}")
        return []
    finally:
        if conn: conn.close()

class Ticket:
    def __init__(self, punto_venta, metodo_pago, monto, fecha, tipo_ticket, referencia, id_caja=None):
        self.punto_venta = punto_venta
        self.metodo_pago = metodo_pago
        self.monto = monto
        self.fecha = fecha
        self.tipo_ticket = tipo_ticket
        self.referencia = referencia
        self.id_caja = id_caja
        self.id = None

    def guardar(self):
        conn, cursor = get_db_connection()
        if not conn: return
        try:
            sql = "INSERT INTO tickets (punto_venta, metodo_pago, monto, fecha, tipo_ticket, referencia, id_caja) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(sql, (self.punto_venta, self.metodo_pago, self.monto, self.fecha, self.tipo_ticket, self.referencia, self.id_caja))
            conn.commit()
            cursor.execute("SELECT @@IDENTITY AS id")
            self.id = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error al guardar el ticket: {e}")
        finally:
            if conn: conn.close()

    def guardar_detalle(self, detalle):
        conn, cursor = get_db_connection()
        if not conn: return
        try:
            for item in detalle:
                id_articulo, precio, cantidad, nombre = item
                sql = "INSERT INTO detalle_ticket (id_ticket, id_articulo, cantidad, precio_unitario, nombre_articulo) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (self.id, id_articulo, cantidad, float(precio), nombre))
            conn.commit()
        except Exception as e:
            print(f"Error al guardar el detalle del ticket: {e}")
        finally:
            if conn: conn.close()

def verificar_caja_abierta():
    conn, cursor = get_db_connection()
    if not conn: return None
    try:
        cursor.execute("SELECT id, monto_inicial FROM caja WHERE estado = 'abierta'")
        return cursor.fetchone()
    except Exception as e:
        print(f"Error al verificar el estado de la caja: {e}")
        return None
    finally:
        if conn: conn.close()

def abrir_caja(monto_inicial):
    conn, cursor = get_db_connection()
    if not conn: return None
    try:
        sql = "INSERT INTO caja (fecha_apertura, monto_inicial, estado) VALUES (?, ?, ?)"
        cursor.execute(sql, (datetime.now(), monto_inicial, 'abierta'))
        conn.commit()
        cursor.execute("SELECT @@IDENTITY AS id")
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error al abrir caja: {e}")
        return None
    finally:
        if conn: conn.close()

def obtener_ventas_sesion(id_sesion):
    conn, cursor = get_db_connection()
    if not conn: return {}
    try:
        cursor.execute("SELECT fecha_apertura FROM caja WHERE id = ?", (id_sesion,))
        resultado = cursor.fetchone()
        if not resultado: return {}
        fecha_apertura = resultado[0]

        sql = "SELECT metodo_pago, SUM(monto) FROM tickets WHERE fecha >= ? AND id_caja = ? GROUP BY metodo_pago"
        cursor.execute(sql, (fecha_apertura, id_sesion))
        
        ventas = {"Efectivo": Decimal("0.0"), "Tarjeta": Decimal("0.0"), "Otros": Decimal("0.0")}
        for metodo, total in cursor.fetchall():
            if total is None: continue
            if metodo == 'Efectivo':
                ventas['Efectivo'] += total
            elif metodo in ('Tarjeta', 'Cuenta Corriente'):
                ventas['Tarjeta'] += total
            else:
                ventas['Otros'] += total
        return ventas
    except Exception as e:
        print(f"Error al obtener ventas de la sesión: {e}")
        return {}
    finally:
        if conn: conn.close()

def cerrar_caja(id_sesion, monto_inicial, monto_final_real, ventas_sesion):
    conn, cursor = get_db_connection()
    if not conn: return
    try:
        monto_inicial_dec = Decimal(str(monto_inicial))
        monto_final_real_dec = Decimal(str(monto_final_real))
        ventas_efectivo = ventas_sesion.get("Efectivo", Decimal("0.0"))

        monto_final_esperado = monto_inicial_dec + ventas_efectivo
        diferencia = monto_final_real_dec - monto_final_esperado
        
        sql = """
            UPDATE caja SET fecha_cierre = ?, total_ventas_efectivo = ?, 
            total_ventas_tarjeta = ?, total_ventas_otros = ?, monto_final_esperado = ?, 
            monto_final_real = ?, diferencia = ?, estado = 'cerrada'
            WHERE id = ? """
        cursor.execute(sql, (
            datetime.now(), 
            ventas_efectivo, 
            ventas_sesion.get("Tarjeta", Decimal("0.0")),
            ventas_sesion.get("Otros", Decimal("0.0")), 
            monto_final_esperado, 
            monto_final_real_dec, 
            diferencia, 
            id_sesion
        ))
        conn.commit()
        print("Caja cerrada exitosamente.")
    except Exception as e:
        print(f"Error al cerrar la caja: {e}")
    finally:
        if conn: conn.close()