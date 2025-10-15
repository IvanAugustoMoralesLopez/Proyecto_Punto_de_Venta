import tkinter as tk
from tkinter import ttk, messagebox
import funciones

def abrir_ventana_proveedores(parent):
    # Crear la ventana principal Toplevel
    ventana = tk.Toplevel(parent)
    ventana.title("Gestión de Proveedores")
    ventana.geometry("1100x650")
    ventana.resizable(False, False)
    ventana.transient(parent)
    ventana.grab_set()

    # --- Frames para la estructura ---
    # Frame para la lista de proveedores (arriba)
    frame_lista = ttk.Frame(ventana, padding="10")
    frame_lista.pack(fill="x", padx=10, pady=5)

    # Frame para el formulario de datos (abajo)
    frame_formulario = ttk.LabelFrame(ventana, text="Datos del Proveedor", padding="10")
    frame_formulario.pack(fill="x", padx=10, pady=5)

    # --- Lista de Proveedores (Treeview) ---
    columnas = ("id", "nombre", "cuit", "telefono", "email")
    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings", height=15)
    
    # Configuración de encabezados
    tree.heading("id", text="ID")
    tree.heading("nombre", text="Nombre / Razón Social")
    tree.heading("cuit", text="CUIT")
    tree.heading("telefono", text="Teléfono")
    tree.heading("email", text="Email")

    # Configuración de columnas
    tree.column("id", width=50, anchor=tk.CENTER)
    tree.column("nombre", width=300)
    tree.column("cuit", width=120, anchor=tk.CENTER)
    tree.column("telefono", width=150)
    tree.column("email", width=250)

    tree.pack(fill="both", expand=True)

    # --- Formulario de Datos ---
    # Fila 1
    tk.Label(frame_formulario, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_nombre = tk.Entry(frame_formulario, width=40)
    entry_nombre.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    
    tk.Label(frame_formulario, text="CUIT:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    entry_cuit = tk.Entry(frame_formulario)
    entry_cuit.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    # Fila 2
    tk.Label(frame_formulario, text="Teléfono:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_telefono = tk.Entry(frame_formulario)
    entry_telefono.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(frame_formulario, text="Email:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
    entry_email = tk.Entry(frame_formulario)
    entry_email.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

    # Fila 3
    tk.Label(frame_formulario, text="Dirección:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_direccion = tk.Entry(frame_formulario)
    entry_direccion.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

    # Fila 4 (Notas)
    tk.Label(frame_formulario, text="Notas:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
    entry_notas = tk.Text(frame_formulario, height=4, width=50)
    entry_notas.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

    # Campo oculto para el ID
    entry_id = tk.Entry(frame_formulario)

    # Ajustar el peso de las columnas del formulario para que se expandan
    frame_formulario.grid_columnconfigure(1, weight=1)
    frame_formulario.grid_columnconfigure(3, weight=1)

    # --- Botones ---
    frame_botones = ttk.Frame(ventana, padding="10")
    frame_botones.pack(fill="x")

    # --- Lógica de la Interfaz ---
    def cargar_proveedores():
        for item in tree.get_children():
            tree.delete(item)
        proveedores = funciones.listar_proveedores()
        for p in proveedores:
            # Solo se muestra algunas columnas en la lista, pero tenemos todos los datos
            tree.insert("", tk.END, values=(p[0], p[1], p[2], p[3], p[4]), iid=p[0])

    def limpiar_campos():
        entry_id.delete(0, tk.END)
        entry_nombre.delete(0, tk.END)
        entry_cuit.delete(0, tk.END)
        entry_telefono.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_direccion.delete(0, tk.END)
        entry_notas.delete("1.0", tk.END)
        if tree.selection():
            tree.selection_remove(tree.selection()[0])
        entry_nombre.focus()

    def seleccionar_proveedor(event):
        if not tree.selection():
            return
        
        id_seleccionado = tree.selection()[0]
        # Buscamos el proveedor completo en la lista obtenida de la BD
        proveedor_completo = next((p for p in funciones.listar_proveedores() if p[0] == int(id_seleccionado)), None)
        
        if proveedor_completo:
            limpiar_campos()
            entry_id.insert(0, proveedor_completo[0])
            entry_nombre.insert(0, proveedor_completo[1])
            entry_cuit.insert(0, proveedor_completo[2] or "")
            entry_telefono.insert(0, proveedor_completo[3] or "")
            entry_email.insert(0, proveedor_completo[4] or "")
            entry_direccion.insert(0, proveedor_completo[5] or "")
            entry_notas.insert("1.0", proveedor_completo[6] or "")

    tree.bind("<<TreeviewSelect>>", seleccionar_proveedor)

    def guardar_proveedor():
        nombre = entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El campo 'Nombre' es obligatorio.", parent=ventana)
            return

        datos = (
            entry_nombre.get(),
            entry_cuit.get() or None,
            entry_telefono.get() or None,
            entry_email.get() or None,
            entry_direccion.get() or None,
            entry_notas.get("1.0", tk.END).strip() or None
        )

        id_prov = entry_id.get()
        if id_prov:
            funciones.editar_proveedor(id_prov, *datos)
        else:
            funciones.agregar_proveedor(*datos)
        
        cargar_proveedores()
        limpiar_campos()

    def eliminar_proveedor():
        if not entry_id.get():
            messagebox.showerror("Error", "Debe seleccionar un proveedor para eliminar.", parent=ventana)
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este proveedor?", parent=ventana):
            funciones.borrar_proveedor(entry_id.get())
            cargar_proveedores()
            limpiar_campos()

    # Configuración de botones
    btn_guardar = ttk.Button(frame_botones, text="Guardar", command=guardar_proveedor)
    btn_guardar.pack(side="left", expand=True, fill="x", padx=5)

    btn_eliminar = ttk.Button(frame_botones, text="Eliminar", command=eliminar_proveedor)
    btn_eliminar.pack(side="left", expand=True, fill="x", padx=5)

    btn_limpiar = ttk.Button(frame_botones, text="Limpiar Campos", command=limpiar_campos)
    btn_limpiar.pack(side="left", expand=True, fill="x", padx=5)

    # Carga inicial de datos
    cargar_proveedores()