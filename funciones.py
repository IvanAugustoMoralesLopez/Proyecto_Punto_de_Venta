import sqlite3 

#Crea la base de datos y la tabla 
def crear_bd():
    conn=sqlite3.connect("base_datos.db")
    cursor= conn.cursor() 
    #Crea la tablita
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articulos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        codigo TEXT NOT NULL,
        descripcion TEXT NOT NULL, 
        precio REAL NOT NULL, 
        stock INTEGER NOT NULL 
    )          
    """)

    

    conn.commit() 
    conn.close() 

#agrega un articulo a la base de datos 

def agregar_articulo(codigo,descripcion,precio,stock): 
    conn= sqlite3.connect("base_datos.db")
    cursor= conn.cursor()

    cursor.execute("""
    INSERT INTO articulos (codigo, descripcion, precio, stock)
    VALUES (?, ?, ?, ?)
    """, (codigo, descripcion, precio, stock))

    
    conn.commit()
    conn.close()


#buscar un articulo por descripción 
def buscar_articulo(texto_busqueda): 
    conn=sqlite3.connect("base_datos.db")
    cursor=conn.cursor() 

    cursor.execute("""
                   SELECT * FROM articulos where descripcion like ? 
                   """, ('%' + texto_busqueda + '%',)) 
        
    resultados = cursor.fetchall()
    conn.close()
    return resultados
