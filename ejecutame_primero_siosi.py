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
            id INT PRIMARY KEY,
            codigo VARCHAR(20),
            descripcion VARCHAR(255),
            precio DECIMAL(10,2),
            stock INT
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tickets' AND xtype='U')
        CREATE TABLE tickets (
            id INT PRIMARY KEY IDENTITY(1,1),
            fecha DATETIME,
            punto_venta VARCHAR(50),
            metodo_pago VARCHAR(50),
            monto_total DECIMAL(10,2)
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detalle_ticket' AND xtype='U')
        CREATE TABLE detalle_ticket (
            id INT PRIMARY KEY IDENTITY(1,1),
            id_ticket INT,
            id_articulo INT,
            cantidad INT,
            precio_unitario DECIMAL(10,2),
            nombre_articulo VARCHAR(255),
            FOREIGN KEY (id_ticket) REFERENCES tickets(id),
            FOREIGN KEY (id_articulo) REFERENCES articulos(id)
        )
        """)

        conn.commit()
        print("✅ Tablas creadas o verificadas correctamente.")
    except Exception as e:
        print("❌ Error al crear tablas:", e)
    finally:
        conn.close()

def cargar_articulos():
    conn, cursor = get_db_connection()
    if not conn:
        return

    try:
        articulos = [

          (1, "001", "Pepsi 1.5L", 450.00, 30),
          (2, "002", "Agua 500ml", 300.00, 50),
          (4, "290", "Alto-Guiso", 1500.00, 20),
          (5, "444", "Monster - Cargada desde la pc de Ivan", 2400.00, 100),
          (6, "555", "Test para villa", 10000.00, 100),
          (7, "202", "Pastel-de-papa", 2000.00, 50000),
          (11, "423", "cargado-desde-abril", 5000.00, 1),
          (12, "137", "you-got-the-best-of-me", 1343.40, 2013),
          (14, "303", "alfajorcito-el-gordito", 100.00, 1),
          (15, "TEC001", "Mouse inalámbrico Logitech", 4500.00, 50),
          (16, "TEC002", "Teclado mecánico Redragon", 9800.00, 30),
          (17, "TEC003", "Auriculares Bluetooth JBL", 12500.00, 40),
          (18, "TEC004", "Monitor LED 24\" Samsung", 62000.00, 15),
          (19, "TEC005", "Cable USB-C reforzado", 1800.00, 100),
          (20, "TEC006", "Cargador portátil 10000mAh", 5200.00, 25),
          (21, "TEC007", "Soporte notebook ajustable", 3100.00, 40),
          (22, "TEC008", "Hub USB 4 puertos", 2700.00, 35),
          (23, "TEC009", "Webcam HD Logitech", 8900.00, 20),
          (24, "TEC010", "Parlante Bluetooth Xiaomi", 15800.00, 16),
          (25, "ALI001", "Pack de 6 aguas saborizadas", 2100.00, 60),
          (26, "ALI002", "Caja de alfajores artesanales", 3500.00, 25),
          (27, "ALI003", "Yerba mate 1kg Taragüí", 1800.00, 80),
          (28, "ALI004", "Café molido La Virginia 500g", 2200.00, 45),
          (29, "ALI005", "Galletitas surtidas 500g", 950.00, 70),
          (30, "ALI006", "Arroz largo fino 1kg", 750.00, 100),
          (31, "ALI007", "Aceite de girasol 900ml", 1200.00, 60),
          (32, "ALI008", "Fideos tirabuzón 500g", 650.00, 90),
          (33, "ALI009", "Salsa lista tomate 340g", 980.00, 50),
          (34, "ALI010", "Azúcar común 1kg", 780.00, 85),
          (35, "LIB001", "Cuaderno tapa dura 100 hojas", 1100.00, 75),
          (36, "LIB002", "Lapicera gel negra x3", 750.00, 90),
          (37, "LIB003", "Resaltadores pastel x5", 1350.00, 40),
          (38, "LIB004", "Agenda semanal 2025", 2100.00, 30),
          (39, "LIB005", "Cartuchera triple compartimiento", 2400.00, 20),
          (40, "LIB006", "Block de hojas A4", 950.00, 60),
          (41, "LIB007", "Corrector líquido x2", 680.00, 45),
          (42, "LIB008", "Set de lápices de colores x12", 1200.00, 50),
          (43, "LIB009", "Regla flexible 30cm", 400.00, 80),
          (44, "LIB010", "Marcadores permanentes x4", 890.00, 35),
          (45, "HOG001", "Set de vasos térmicos x4", 4300.00, 25),
          (46, "HOG002", "Toalla de baño premium", 2700.00, 50),
          (47, "HOG003", "Lámpara LED escritorio", 5200.00, 22),
          (48, "HOG004", "Organizador multiuso plástico", 1600.00, 60),
          (49, "HOG005", "Cortina blackout 1.40x2.00", 8900.00, 10),
          (50, "HOG006", "Almohada viscoelástica", 3400.00, 30),
          (51, "HOG007", "Set de cubiertos x24", 7800.00, 18),
          (52, "HOG008", "Cesto de ropa plegable", 2100.00, 40),
          (53, "HOG009", "Reloj de pared moderno", 3200.00, 25),
          (54, "HOG010", "Porta especias giratorio", 2900.00, 20),
          (55, "IND011", "Buzo canguro unisex", 7400.00, 28),
          (56, "IND012", "Medias deportivas x3", 1800.00, 60),
          (57, "IND013", "Camisa casual manga larga", 6200.00, 22),
          (58, "IND014", "Short de baño estampado", 4100.00, 30),
          (59, "IND015", "Cinturón cuero clásico", 3500.00, 15),
          (60, "IND016", "Vestido de verano estampado", 8900.00, 12),
          (61, "IND017", "Pijama algodón adulto", 5200.00, 20),
          (62, "IND018", "Bufanda tejida artesanal", 3100.00, 25),
          (63, "IND019", "Guantes térmicos invierno", 2700.00, 18),
          (64, "IND020", "Campera inflable liviana", 11500.00, 10),
          (65, "HER011", "Destornillador multipunta", 2100.00, 40),
          (66, "HER012", "Martillo carpintero 16oz", 3200.00, 25),
          (67, "HER013", "Llave ajustable 10\"", 2800.00, 30),
          (68, "HER014", "Cinta métrica 5m", 950.00, 50),
          (69, "HER015", "Nivel de burbuja 30cm", 1100.00, 35),
          (70, "HER016", "Taladro eléctrico 650W", 18500.00, 10),
          (71, "HER017", "Caja de herramientas básica", 9200.00, 12),
          (72, "HER018", "Pinza universal 8\"", 1600.00, 40),
          (73, "HER019", "Juego de llaves Allen x10", 1400.00, 45),
          (74, "HER020", "Sierra manual para madera", 2100.00, 20),
          (75, "JUG011", "Set de bloques didácticos", 3200.00, 30),
          (76, "JUG012", "Muñeca articulada con accesorios", 5800.00, 20),
          (77, "JUG013", "Auto a fricción metálico", 2700.00, 40),
          (78, "JUG014", "Pelota de fútbol infantil", 1900.00, 35),
          (79, "JUG015", "Rompecabezas 500 piezas", 2400.00, 25),
          (80, "JUG016", "Juego de mesa familiar", 6200.00, 18),
          (81, "JUG017", "Set de pinturas lavables", 1500.00, 50),
          (82, "JUG018", "Libro de cuentos ilustrado", 1800.00, 40),
          (83, "JUG019", "Pistola de burbujas recargable", 2100.00, 30),
          (84, "JUG020", "Masa moldeable x6 colores", 1300.00, 60),
          (85, "LIM011", "Detergente concentrado 750ml", 950.00, 80),
          (86, "LIM012", "Lavandina perfumada 1L", 780.00, 70),
          (87, "LIM013", "Desinfectante multiuso 500ml", 1200.00, 60),
          (88, "LIM014", "Esponja doble acción x2", 650.00, 90),
          (89, "LIM015", "Trapo de piso absorbente", 1100.00, 50),
          (90, "LIM016", "Limpiavidrios con gatillo", 1400.00, 40),
          (91, "LIM017", "Cepillo de mano ergonómico", 850.00, 45),
          (92, "LIM018", "Guantes de látex x2", 700.00, 60),
          (93, "LIM019", "Bolsa de residuos 30L x10", 950.00, 55),
          (94, "LIM020", "Ambientador aerosol lavanda", 1200.00, 35),
          (95, "MAS011", "Bolsa de alimento perro 3kg", 4200.00, 25),
          (96, "MAS012", "Pelota mordedora resistente", 1100.00, 40),
          (97, "MAS013", "Collar ajustable mediano", 1800.00, 30),
          (98, "MAS014", "Comedero doble plástico", 2200.00, 20),
          (99, "MAS015", "Shampoo neutro 250ml", 1500.00, 35),
          (100, "MAS016", "Bolsitas higiénicas x50", 950.00, 45),
          (101, "MAS017", "Cama acolchada para mascotas", 7800.00, 15),
          (102, "MAS018", "Juguete chirriante en forma de hueso", 1300.00, 50),
          (103, "MAS019", "Arnés ajustable con correa", 3200.00, 18),
          (104, "MAS020", "Cepillo de pelo para mascotas", 2100.00, 22)                        

         ]

        for art in articulos:
            cursor.execute("IF NOT EXISTS (SELECT 1 FROM articulos WHERE id = ?) INSERT INTO articulos (id, codigo, descripcion, precio, stock) VALUES (?, ?, ?, ?, ?)", (art[0], *art))
        
        conn.commit()
        print(f"✅ Se cargaron {len(articulos)} artículos.")
    except Exception as e:
        print("❌ Error al cargar artículos:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Iniciando configuración de base de datos...")
    crear_tablas()
    cargar_articulos()
    print("🎉 Listo para probar los cambios.")
