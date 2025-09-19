import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
from datetime import datetime
from config import ENTORNO
from funciones import Ticket

def creartickets():
    root = tk.Tk()
    root.title("Generador de Tickets")
    root.geometry("400x300")
    root.resizable(False, False)

    # --- Punto de venta ---
    tk.Label(root, text="Punto de Venta:", font=("Arial", 10)).pack(pady=5)
    combo_pv = ttk.Combobox(root, values=["p_V_A1", "p_V_B2", "p_V_C3"], font=("Arial", 10))
    combo_pv.current(0)
    combo_pv.pack(pady=5)

    # --- Cantidad de tickets ---
    tk.Label(root, text="Cantidad de Tickets a Generar:", font=("Arial", 10)).pack(pady=5)
    entry_cantidad = tk.Entry(root, font=("Arial", 10))
    entry_cantidad.insert(0, "100")
    entry_cantidad.pack(pady=5)

    # --- Barra de progreso ---
    tk.Label(root, text="Progreso:", font=("Arial", 10)).pack(pady=5)
    barra_progreso = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    barra_progreso.pack(pady=5)

    # --- Botón de carga ---
    btn_iniciar = tk.Button(root, text="Iniciar Carga", font=("Arial", 10), bg="#4CAF50", fg="white", state="disabled")
    btn_iniciar.pack(pady=10)

    # --- Validación dinámica ---
    def validar_campos(*args):
        try:
            cantidad = int(entry_cantidad.get())
            punto_venta = combo_pv.get()
            if cantidad > 0 and punto_venta:
                btn_iniciar.config(state="normal")
            else:
                btn_iniciar.config(state="disabled")
        except ValueError:
            btn_iniciar.config(state="disabled")

    entry_cantidad.bind("<KeyRelease>", validar_campos)
    combo_pv.bind("<<ComboboxSelected>>", validar_campos)

    # --- Proceso de generación ---
    def proceso(cantidad, nombre_pv):
        barra_progreso["value"] = 0
        barra_progreso["maximum"] = cantidad

        for i in range(cantidad):
            metodo = random.choice(["Efectivo", "Tarjeta", "Transferencia", "Mercado Pago"])
            monto = random.randint(1000, 50000)
            tipo = random.choice(["normal", "promo", "devolución"])
            referencia = f"REF-{random.randint(100000, 999999)}"
            fecha_actual = datetime.now()

            ticket = Ticket(
                punto_venta=nombre_pv,
                metodo_pago=metodo,
                monto=monto,
                fecha=fecha_actual,
                tipo_ticket=tipo,
                referencia=referencia
            )

            ticket.guardar()
            barra_progreso["value"] += 1
            root.update_idletasks()

        messagebox.showinfo("Completado", f"Se generaron {cantidad} tickets para {nombre_pv}")
        btn_iniciar.config(state="disabled")

    # --- Iniciar hilo ---
    def iniciar_proceso():
        try:
            cantidad = int(entry_cantidad.get())
            nombre_pv = combo_pv.get()
            if cantidad <= 0 or not nombre_pv:
                raise ValueError
            btn_iniciar.config(state="disabled")
            threading.Thread(target=lambda: proceso(cantidad, nombre_pv)).start()
        except ValueError:
            messagebox.showerror("Error", "Ingresá una cantidad válida y seleccioná un punto de venta.")

    btn_iniciar.config(command=iniciar_proceso)

    # --- Ejecutar interfaz ---
    root.mainloop()
