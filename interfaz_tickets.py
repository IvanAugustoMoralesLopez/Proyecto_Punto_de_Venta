import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime
from funciones import Ticket, obtener_articulos

activo = False
segundos_restantes = 0

def creartickets():
    root = tk.Tk()
    root.title("Generador Automático de Tickets")
    root.geometry("400x320")
    root.resizable(False, False)

    # --- Punto de venta ---
    tk.Label(root, text="Punto de Venta:", font=("Arial", 10)).pack(pady=5)
    combo_pv = ttk.Combobox(root, values=["p_V_A1", "p_V_B2", "p_V_C3"], font=("Arial", 10))
    combo_pv.current(0)
    combo_pv.pack(pady=5)

    # --- Botón switch ---
    btn_toggle = tk.Button(root, text="Iniciar Generación", font=("Arial", 10), bg="#4CAF50", fg="white")
    btn_toggle.pack(pady=20)

    # --- Estado dinámico ---
    estado_label = tk.Label(root, text="Estado: Inactivo", font=("Arial", 10))
    estado_label.pack(pady=5)

    # --- Barra de progreso ---
    barra = ttk.Progressbar(root, maximum=1200, length=250)
    barra.pack(pady=5)

    def generar_ticket(nombre_pv):
        metodo = random.choice(["Efectivo", "Tarjeta", "Transferencia", "Mercado Pago"])
        tipo = random.choice(["normal", "promo", "devolución"])
        referencia = f"REF-{random.randint(100000, 999999)}"
        fecha_actual = datetime.now()

        articulos_disponibles = obtener_articulos()
        if not articulos_disponibles:
            return

        seleccionados = random.sample(articulos_disponibles, k=random.randint(3, 7))
        detalle = []
        monto_total = 0

        for articulo in seleccionados:
            id_articulo = articulo[0]
            nombre_articulo = articulo[1]  # ← nombre del producto
            precio_unitario = articulo[2]
            cantidad = random.randint(1, 5)
            subtotal = precio_unitario * cantidad
            monto_total += subtotal
            detalle.append((id_articulo, precio_unitario, cantidad, nombre_articulo))

        # Crear el ticket con el monto calculado
        ticket = Ticket(nombre_pv, metodo, int(monto_total), fecha_actual, tipo, referencia)
        ticket.guardar()
        ticket.guardar_detalle(detalle)

    def actualizar_contador(nombre_pv):
        global segundos_restantes
        if activo:
            if segundos_restantes > 0:
                segundos_restantes -= 1
                estado_label.config(text=f"Estado: Activo (esperando {segundos_restantes} seg)")
                barra['value'] = delay_inicial - segundos_restantes
                root.after(1000, lambda: actualizar_contador(nombre_pv))
            else:
                generar_ticket(nombre_pv)
                iniciar_ciclo(nombre_pv)
        else:
            estado_label.config(text="Estado: Inactivo")
            barra['value'] = 0

    def iniciar_ciclo(nombre_pv):
        global segundos_restantes, delay_inicial
        delay_inicial = random.randint(60, 1200)
        segundos_restantes = delay_inicial
        estado_label.config(text=f"Estado: Activo (esperando {segundos_restantes} seg)")
        barra['maximum'] = delay_inicial
        barra['value'] = 0
        actualizar_contador(nombre_pv)

    def toggle():
        global activo
        nombre_pv = combo_pv.get()
        if not nombre_pv:
            messagebox.showerror("Error", "Seleccioná un punto de venta.")
            return

        if not activo:
            activo = True
            btn_toggle.config(text="Detener Generación", bg="#F44336")
            iniciar_ciclo(nombre_pv)
        else:
            activo = False
            btn_toggle.config(text="Iniciar Generación", bg="#4CAF50")

    btn_toggle.config(command=toggle)
    root.mainloop()
