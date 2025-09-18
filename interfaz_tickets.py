import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

def creartickets():
    root = tk.Toplevel()
    root.title("Generador de Tickets Masivos")
    root.geometry("400x250")
    root.resizable(False, False)

    tk.Label(root, text="Nombre del Punto de Venta:", font=("Arial", 10)).pack(pady=5)
    entry_punto_venta = tk.Entry(root, font=("Arial", 10))
    entry_punto_venta.insert(0, "p_V_A1")
    entry_punto_venta.pack(pady=5)

    tk.Label(root, text="Cantidad de Tickets a Generar:", font=("Arial", 10)).pack(pady=5)
    entry_cantidad = tk.Entry(root, font=("Arial", 10))
    entry_cantidad.insert(0, "100")
    entry_cantidad.pack(pady=5)

    tk.Label(root, text="Progreso:", font=("Arial", 10)).pack(pady=5)
    barra_progreso = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    barra_progreso.pack(pady=5)

    def iniciar_carga():
        nombre_pv = entry_punto_venta.get().strip() or "p_V_A1"
        try:
            cantidad = int(entry_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero positivo.")
            return

        barra_progreso["maximum"] = cantidad
        barra_progreso["value"] = 0
        btn_iniciar.config(state="disabled")

        def proceso():
            for i in range(cantidad):
                time.sleep(0.05)
                barra_progreso["value"] += 1
                root.update_idletasks()
            messagebox.showinfo("Completado", f"Se generaron {cantidad} tickets para {nombre_pv}")
            btn_iniciar.config(state="normal")

        threading.Thread(target=proceso).start()

    btn_iniciar = tk.Button(root, text="Iniciar Carga", font=("Arial", 10), bg="#A8E6CF", command=iniciar_carga)
    btn_iniciar.pack(pady=10)
