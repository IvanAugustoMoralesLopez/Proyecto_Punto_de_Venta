import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from db import get_db_connection
from tkinter import ttk


def cobrar_ticket(articulos_agregados, metodo_pago, punto_de_venta, tipo_ticket, referencia):
    conexion, _ = get_db_connection()
    if not conexion:
        messagebox.showerror("Error", "❌ No se pudo conectar con la base de datos.")
        return

    cursor = conexion.cursor()

    try:
        monto_total = sum(art["importe"] for art in articulos_agregados)
        fecha_actual = datetime.now()

        # Insertar en tickets
        cursor.execute("""
            INSERT INTO tickets (punto_venta, metodo_pago, monto, fecha, tipo_ticket, referencia)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (punto_de_venta, metodo_pago, monto_total, fecha_actual, tipo_ticket, referencia))

        cursor.execute("SELECT @@IDENTITY AS id_ticket")
        id_ticket = cursor.fetchone()[0]

        for art in articulos_agregados:
            # Buscar ID del artículo por código
            cursor.execute("SELECT id, stock FROM articulos WHERE codigo = ?", (art["codigo"],))
            resultado = cursor.fetchone()

            if not resultado:
                raise Exception(f"❌ El artículo con código '{art['codigo']}' no existe.")

            id_articulo, stock_actual = resultado

            if art["cantidad"] > stock_actual:
                raise Exception(f"❌ Stock insuficiente para '{art['descripcion']}'. Disponible: {stock_actual}, solicitado: {art['cantidad']}")

            # Insertar detalle del ticket
            cursor.execute("""
                INSERT INTO detalle_ticket (id_ticket, id_articulo, cantidad, precio_unitario, nombre_articulo)
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_ticket,
                id_articulo,
                art["cantidad"],
                art["precio"],
                art["descripcion"]
            ))

            # Actualizar stock
            nuevo_stock = stock_actual - art["cantidad"]
            cursor.execute("UPDATE articulos SET stock = ? WHERE id = ?", (nuevo_stock, id_articulo))

        conexion.commit()
        messagebox.showinfo("Éxito", f"✅ Ticket #{id_ticket} registrado correctamente.")
        articulos_agregados.clear()

    except Exception as e:
        conexion.rollback()
        messagebox.showerror("Error", f"{e}")

def ventana_cobro(root, articulos_agregados):
    ventana = tk.Toplevel(root)
    ventana.title("Cobrar venta")
    ventana.geometry("300x350")
    ventana.resizable(False, False)

    tk.Label(ventana, text="Punto de venta:").pack(pady=5)
    entry_punto = tk.Entry(ventana)
    entry_punto.pack()

    tk.Label(ventana, text="Método de pago:").pack(pady=5)
    metodo_pago = tk.StringVar()
    opciones_pago = ["Efectivo", "Tarjeta", "Transferencia", "Cuenta Corriente"]
    metodo_pago.set(opciones_pago[0])
    tk.OptionMenu(ventana, metodo_pago, *opciones_pago).pack()

    tk.Label(ventana, text="Tipo de ticket:").pack(pady=5)
    tipo_ticket = tk.StringVar()
    opciones_tipo = ["Venta común", "Promoción", "Devolución"]
    tipo_ticket.set(opciones_tipo[0])
    tk.OptionMenu(ventana, tipo_ticket, *opciones_tipo).pack()

    tk.Label(ventana, text="Cliente (opcional):").pack(pady=5)
    entry_cliente = tk.Entry(ventana)
    entry_cliente.pack()

    def confirmar_cobro():
        punto = entry_punto.get().strip()
        metodo = metodo_pago.get()
        tipo = tipo_ticket.get()
        cliente = entry_cliente.get().strip()
        referencia = cliente if cliente else "Sin referencia"

        if not punto:
            messagebox.showerror("Error", "❌ Ingresá el punto de venta", parent=ventana)
            return

        if not articulos_agregados:
            messagebox.showerror("Error", "❌ No hay artículos en la venta", parent=ventana)
            return

        cobrar_ticket(articulos_agregados, metodo, punto, tipo, referencia)
        ventana.destroy()

    tk.Button(ventana, text="Confirmar cobro", command=confirmar_cobro, bg="#B7E998").pack(pady=15)
    tk.Button(ventana, text="Cancelar", command=ventana.destroy, bg="#FF9999").pack()
    
def mostrar_ultimos_tickets(root):
    ventana = tk.Toplevel(root)
    ventana.title("Últimos 10 Tickets")
    ventana.geometry("1000x800")
    ventana.resizable(False, False)

    frame = tk.Frame(ventana)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(
        frame,
        columns=("ID", "Fecha", "Pago", "Artículos", "Cantidad Total", "Importe Total"),
        show="headings",
        height=15
    )
    tree.pack(side="left", fill="both", expand=True)

    # Encabezados con ancho personalizado
    encabezados = {
        "ID": 60,
        "Fecha": 150,
        "Pago": 120,
        "Artículos": 400,
        "Cantidad Total": 100,
        "Importe Total": 120
    }

    for col, ancho in encabezados.items():
        tree.heading(col, text=col)
        tree.column(col, width=ancho, anchor="center")

    # Scroll vertical
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Cargar datos desde SQL Server
    conexion, _ = get_db_connection()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT TOP 10
            t.id AS ticket_id,
            t.fecha,
            t.metodo_pago,
            STRING_AGG(dt.nombre_articulo, ', ') AS articulos,
            SUM(dt.cantidad) AS cantidad_total,
            SUM(dt.cantidad * dt.precio_unitario) AS importe_total
        FROM tickets t
        JOIN detalle_ticket dt ON t.id = dt.id_ticket
        GROUP BY t.id, t.fecha, t.metodo_pago
        ORDER BY t.id DESC
    """)

    resultados = cursor.fetchall()
    if resultados:
        for fila in resultados:
            tree.insert("", "end", values=(
                fila[0], fila[1], fila[2], fila[3], fila[4],
                f"${fila[5]:.2f}"
            ))
    else:
        tree.insert("", "end", values=("—", "—", "—", "No hay tickets", "—", "—"))

    conexion.close()