
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from db import get_db_connection
from datetime import date


def generar_pdf(nombre_archivo, punto_venta):
    conn, cursor = get_db_connection()
    if not conn or not cursor:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
        return

    try:
        hoy = date.today()
        # 1. Total recaudado y cantidad de ventas (tickets) del día para el punto de venta
        cursor.execute("""
            SELECT COUNT(*) as total_tickets, ISNULL(SUM(monto),0) as total_recaudado
            FROM tickets
            WHERE punto_venta = ? AND CAST(fecha AS DATE) = ?
        """, (punto_venta, hoy))
        row = cursor.fetchone()
        total_tickets = row[0] or 0
        total_recaudado = row[1] or 0

        # 2. Top 10 productos más vendidos del día para el punto de venta
        cursor.execute("""
            SELECT TOP 10 dt.nombre_articulo, SUM(dt.cantidad) as total_vendido
            FROM detalle_ticket dt
            JOIN tickets t ON t.id = dt.id_ticket
            WHERE t.punto_venta = ? AND CAST(t.fecha AS DATE) = ?
            GROUP BY dt.nombre_articulo
            ORDER BY total_vendido DESC
        """, (punto_venta, hoy))
        articulos_top = cursor.fetchall()

        c = canvas.Canvas(nombre_archivo, pagesize=A4)
        width, height = A4
        titulo = f"Ventas del día de hoy - {hoy.strftime('%d/%m/%Y')}"
        c.setFont("Helvetica-Bold", 16)
        texto_ancho = c.stringWidth(titulo, "Helvetica-Bold", 16)
        c.drawString((width - texto_ancho) / 2, height - 50, titulo)

        y = height - 100
        c.setFont("Helvetica", 12)

        c.drawString(50, y, f"Punto de venta: {punto_venta}")
        y -= 20
        c.drawString(50, y, f"Total de ventas (tickets): {total_tickets}")
        y -= 20
        c.drawString(50, y, f"Total recaudado: ${total_recaudado: .2f}")
        y -= 40

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Top 10 artículos más vendidos:")
        y -= 20
        c.setFont("Helvetica", 12)
        for i, (articulo, cantidad) in enumerate(articulos_top, start=1):
            c.drawString(60, y, f"{i}. {articulo} - {cantidad} unidades")
            y -= 20

        c.save()
        messagebox.showinfo("PDF", f"El archivo '{nombre_archivo}' se guardó correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar el PDF: {e}")
    finally:
        cursor.close()
        conn.close()

def obtener_puntos_de_venta():
    conn, cursor = get_db_connection()
    if not conn or not cursor:
        return []
    try:
        cursor.execute("SELECT DISTINCT punto_venta FROM tickets")
        puntos = [row[0] for row in cursor.fetchall()]
        return puntos
    except Exception as e:
        print("Error al obtener puntos de venta:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def abrir_ventana_pdf(parent):
    ventana = tk.Toplevel(parent)
    ventana.title("Generar PDF de ventas")
    ventana.geometry("350x200")

    tk.Label(ventana, text="Selecciona punto de venta:").pack(pady=10)
    puntos = obtener_puntos_de_venta()
    combo = ttk.Combobox(ventana, values=puntos, state="readonly")
    combo.pack(pady=5)
    if puntos:
        combo.current(0)

    def generar_pdf_btn():
        punto = combo.get()
        if punto:
            nombre_archivo = f"ventas_{punto}.pdf"
            generar_pdf(nombre_archivo, punto)
        else:
            messagebox.showerror("Error", "Selecciona un punto de venta.")

    tk.Button(ventana, text="Generar PDF de ventas", command=generar_pdf_btn).pack(pady=20)


# Solo ejecutar la interfaz si este archivo es el principal
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Punto de Venta - Demo PDF")
    root.geometry("400x200")

    btn = tk.Button(root, text="Generar PDF", command=abrir_ventana_pdf)
    btn.pack(expand=True)

    root.mainloop()
