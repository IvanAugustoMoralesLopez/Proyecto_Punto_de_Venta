import tkinter as tk
from tkinter import ttk
from db import get_db_connection  # Asegurate que esté bien importado

def ventana_busqueda():
    ventana = tk.Tk()
    ventana.title("Buscar tickets")
    ventana.geometry("600x400")

    conn, cursor = get_db_connection()
    if not conn or not cursor:
        tk.Label(ventana, text="Error al conectar con la base de datos").pack(pady=20)
        ventana.mainloop()
        return

    try:
        cursor.execute("SELECT TOP (1000) punto_venta FROM PuntoVenta.dbo.tickets")
        resultados = [row.punto_venta for row in cursor.fetchall()]
    except Exception as e:
        tk.Label(ventana, text=f"Error al ejecutar la consulta: {e}").pack(pady=20)
        ventana.mainloop()
        return

    tk.Label(ventana, text="Seleccionar punto de venta:").pack(pady=10)
    combo = ttk.Combobox(ventana, values=resultados)
    combo.pack(pady=5)

    def mostrar_seleccion():
        seleccionado = combo.get()
        print(f"Punto de venta seleccionado: {seleccionado}")

    tk.Button(ventana, text="Buscar", command=mostrar_seleccion).pack(pady=20)
    ventana.mainloop()

# 🔧 Llamada libre para testeo
if __name__ == "__main__":
    ventana_busqueda()
