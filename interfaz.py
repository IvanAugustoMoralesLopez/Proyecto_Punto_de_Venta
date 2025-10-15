import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import get_db_connection
from decimal import Decimal

def cobrar_ticket(articulos_agregados, metodo_pago, punto_de_venta, tipo_ticket, referencia, id_caja_actual):
    if not articulos_agregados:
        messagebox.showerror("Error", "❌ No hay artículos en la venta.")
        return False
        
    conn, cursor = get_db_connection()
    if not conn:
        messagebox.showerror("Error", "❌ No se pudo conectar con la base de datos.")
        return False

    try:
        monto_total = sum(art["precio"] * art["cantidad"] for art in articulos_agregados)
        fecha_actual = datetime.now()

        cursor.execute("""
            INSERT INTO tickets (punto_venta, metodo_pago, monto, fecha, tipo_ticket, referencia, id_caja)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (punto_de_venta, metodo_pago, monto_total, fecha_actual, tipo_ticket, referencia, id_caja_actual))

        cursor.execute("SELECT @@IDENTITY AS id_ticket")
        id_ticket = cursor.fetchone()[0]

        for art in articulos_agregados:
            # Se combina la comprobación y la actualización en una sola operación.
            sql_update_stock = """
                UPDATE articulos 
                SET stock = stock - ? 
                WHERE id = ? AND stock >= ?
            """
            
            cursor.execute(sql_update_stock, (art["cantidad"], art["id"], art["cantidad"]))
            
            # cursor.rowcount nos dice cuantas filas fueron editadas.
            # Si es 0, significa que la condición WHERE (stock >= cantidad) no se cumplió.
            if cursor.rowcount == 0:
                # Si falla la actualización de stock de un artículo, debemos deshacer toda la transacción.
                raise Exception(f"❌ Stock insuficiente para '{art['descripcion']}'. Venta cancelada.")

            # Si el update fue exitoso (rowcount > 0).
            cursor.execute("""
                INSERT INTO detalle_ticket (id_ticket, id_articulo, cantidad, precio_unitario, nombre_articulo)
                VALUES (?, ?, ?, ?, ?)
            """, (id_ticket, art["id"], art["cantidad"], art["precio"], art["descripcion"]))

        # Si todos los artículos se procesaron correctamente, confirmamos la transacción.
        conn.commit()
        messagebox.showinfo("Éxito", f"✅ Venta registrada correctamente.\nTicket #{id_ticket}")
        return True

    except Exception as e:
        # Si ocurre cualquier error (incluido el de stock), hacemos rollback.
        conn.rollback()
        messagebox.showerror("Error al registrar la venta", f"{e}")
        return False
    finally:
        if conn:
            conn.close()

def ventana_cobro(root, articulos_agregados, callback_limpiar_grilla, callback_actualizar_totales, id_sesion_actual):
    if not articulos_agregados:
        messagebox.showerror("Error", "No hay artículos en la venta para cobrar.", parent=root)
        return
        
    if not id_sesion_actual:
        messagebox.showerror("Error", "No hay una sesión de caja activa. No se puede cobrar.", parent=root)
        return

    ventana = tk.Toplevel(root)
    ventana.title("Cobrar Venta")
    ventana.geometry("300x300")
    ventana.resizable(False, False)
    ventana.transient(root)
    ventana.grab_set()

    frame = ttk.Frame(ventana, padding="15")
    frame.pack(expand=True, fill="both")

    ttk.Label(frame, text="Punto de venta:").pack(pady=(0,2))
    entry_punto = ttk.Entry(frame)
    entry_punto.pack(fill="x")
    entry_punto.insert(0, "Local Principal")

    ttk.Label(frame, text="Método de pago:").pack(pady=(10,2))
    combo_pago = ttk.Combobox(frame, values=["Efectivo", "Tarjeta", "Transferencia", "Cuenta Corriente"], state="readonly")
    combo_pago.pack(fill="x")
    combo_pago.current(0)

    ttk.Label(frame, text="Referencia (Cliente, etc.):").pack(pady=(10,2))
    entry_referencia = ttk.Entry(frame)
    entry_referencia.pack(fill="x")

    def confirmar_cobro():
        punto = entry_punto.get().strip()
        metodo = combo_pago.get()
        referencia = entry_referencia.get().strip() or "Sin referencia"
        tipo_ticket = "Venta"

        if not punto:
            messagebox.showerror("Dato requerido", "El punto de venta no puede estar vacío.", parent=ventana)
            return

        exito = cobrar_ticket(articulos_agregados, metodo, punto, tipo_ticket, referencia, id_sesion_actual)
        
        if exito:
            callback_limpiar_grilla()
            callback_actualizar_totales()
            ventana.destroy()

    btn_confirmar = ttk.Button(frame, text="Confirmar Cobro", command=confirmar_cobro)
    btn_confirmar.pack(pady=(20, 0), ipady=5, fill="x")

def mostrar_ultimos_tickets(root):
    ventana = tk.Toplevel(root)
    ventana.title("Últimos Tickets Registrados")
    ventana.geometry("950x400")
    ventana.transient(root)
    ventana.grab_set()

    frame = ttk.Frame(ventana, padding="10")
    frame.pack(fill="both", expand=True)

    columnas = ("ID", "Fecha", "Pago", "Artículos", "Total")
    tree = ttk.Treeview(frame, columns=columnas, show="headings")
    tree.pack(fill="both", expand=True, side="left")
    
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    tree.heading("ID", text="ID")
    tree.heading("Fecha", text="Fecha")
    tree.heading("Pago", text="Método de Pago")
    tree.heading("Artículos", text="Artículos")
    tree.heading("Total", text="Importe Total")
    tree.column("ID", width=60, anchor="center")
    tree.column("Fecha", width=150)
    tree.column("Pago", width=120)
    tree.column("Artículos", width=400)
    tree.column("Total", width=120, anchor="e")

    try:
        conn, cursor = get_db_connection()
        if not conn: return

        cursor.execute("""
            SELECT TOP 20 t.id, t.fecha, t.metodo_pago, t.monto,
            (SELECT STRING_AGG(d.nombre_articulo, ', ') FROM detalle_ticket d WHERE d.id_ticket = t.id) AS detalles
            FROM tickets t
            ORDER BY t.id DESC
        """)
        resultados = cursor.fetchall()
        for fila in resultados:
            tree.insert("", "end", values=(fila.id, fila.fecha.strftime('%Y-%m-%d %H:%M'), fila.metodo_pago, fila.detalles, f"${fila.monto:.2f}"))

    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los tickets: {e}")
    finally:
        if conn: conn.close()