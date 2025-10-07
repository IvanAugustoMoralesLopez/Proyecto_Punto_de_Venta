import matplotlib.pyplot as plt
import pandas as pd
from db import get_db_connection

def generar_grafico_ventas_por_articulo():
    conn, cursor = get_db_connection()
    query = """
    SELECT TOP 10 nombre_articulo, SUM(cantidad * precio_unitario) AS total_ventas
    FROM detalle_ticket
    GROUP BY nombre_articulo
    ORDER BY total_ventas DESC
    """
    cursor.execute(query)
    datos = cursor.fetchall()
    conn.close()

    nombres = [fila[0] for fila in datos]
    totales = [fila[1] for fila in datos]

    plt.figure(figsize=(10,6))
    plt.bar(nombres, totales, color='skyblue')
    plt.title("Ventas por Artículo")
    plt.xlabel("Artículo")
    plt.ylabel("Total Vendido ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def generar_grafico_cantidad_por_articulo():
    conn, cursor = get_db_connection()
    query = """
    SELECT TOP 10 nombre_articulo, SUM(cantidad) AS total_cantidad
    FROM detalle_ticket
    GROUP BY nombre_articulo
    ORDER BY total_cantidad DESC
    """
    cursor.execute(query)
    datos = cursor.fetchall()
    conn.close()

    nombres = [fila[0] for fila in datos]
    cantidades = [fila[1] for fila in datos]

    plt.figure(figsize=(8,8))
    plt.pie(cantidades, labels=nombres, autopct='%1.1f%%', startangle=140)
    plt.title("Cantidad Vendida por Artículo")
    plt.axis('equal')
    plt.show()

def generar_grafico_ventas_por_dia():
    conn, cursor = get_db_connection()
    query = """
    SELECT t.fecha, SUM(dt.cantidad * dt.precio_unitario) AS total_dia
    FROM detalle_ticket dt
    JOIN tickets t ON dt.id_ticket = t.id
    GROUP BY t.fecha
    ORDER BY t.fecha
    """
    cursor.execute(query)
    datos = cursor.fetchall()
    conn.close()

    fechas = [fila[0] for fila in datos]
    totales = [fila[1] for fila in datos]

    plt.figure(figsize=(10,6))
    plt.plot(fechas, totales, marker='o', linestyle='-', color='green')
    plt.title("Ventas por Día")
    plt.xlabel("Fecha")
    plt.ylabel("Total Vendido ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


