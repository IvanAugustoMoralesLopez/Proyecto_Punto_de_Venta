import pyodbc
from config import CONNECTION_STRING

def get_db_connection():
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn, conn.cursor()
    except Exception as e:
        print("Error al conectar con la base:", e)
        return None, None

def crear_tablas():
    conn, cursor = get_db_connection()
    if not conn:
        return

    try:
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='articulos' AND xtype='U')
        CREATE TABLE articulos (
            id INT IDENTITY(1,1) PRIMARY KEY,
            codigo VARCHAR(20),
            descripcion VARCHAR(255),
            precio DECIMAL(10,2),
            stock INT
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tickets' AND xtype='U')
        CREATE TABLE tickets (
            id INT IDENTITY(1,1) PRIMARY KEY,
            fecha DATETIME DEFAULT GETDATE(),
            punto_venta VARCHAR(50) DEFAULT 'Desconocido',
            metodo_pago VARCHAR(30) DEFAULT 'Efectivo',
            tipo_ticket VARCHAR(30) DEFAULT 'General',
            monto DECIMAL(10,2) DEFAULT 0.00,
            referencia VARCHAR(50) DEFAULT 'Sin referencia'
            id_caja INT, 
            FOREIGN KEY (id_caja) REFERENCES caja(id) 
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detalle_ticket' AND xtype='U')
        CREATE TABLE detalle_ticket (
            id INT IDENTITY(1,1) PRIMARY KEY,
            id_ticket INT,
            id_articulo INT,
            cantidad INT,
            precio_unitario DECIMAL(10,2),
            nombre_articulo VARCHAR(255),
            FOREIGN KEY (id_ticket) REFERENCES tickets(id),
            FOREIGN KEY (id_articulo) REFERENCES articulos(id)
        )
        """)
        
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='caja' AND xtype='U')
        CREATE TABLE caja (
            id INT IDENTITY(1,1) PRIMARY KEY,
            fecha_apertura DATETIME,
            fecha_cierre DATETIME,
            monto_inicial DECIMAL(10,2),
            total_ventas_efectivo DECIMAL(10,2),
            total_ventas_tarjeta DECIMAL(10,2),
            total_ventas_otros DECIMAL(10,2),
            monto_final_esperado DECIMAL(10,2),
            monto_final_real DECIMAL(10,2),
            diferencia DECIMAL(10,2),
            estado VARCHAR(20) -- puede ser 'abierta' o 'cerrada'
        )
        """)

        conn.commit()
        print("✅ Tablas creadas o verificadas correctamente.")
    except Exception as e:
        print("❌ Error al crear tablas:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Iniciando configuración de base de datos...")
    crear_tablas()
    print("🎉 Listo para probar los cambios.")
