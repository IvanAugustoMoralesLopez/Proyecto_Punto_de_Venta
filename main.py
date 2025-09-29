import tkinter as tk
from tkinter import ttk  
from tkinter import messagebox 
import funciones
from interfaz_tickets import creartickets 
from graficos import (
    generar_grafico_ventas_por_articulo,
    generar_grafico_cantidad_por_articulo,
    generar_grafico_ventas_por_dia
)

articulos_agregados = []
checks_articulos = []


root = tk.Tk()
root.title("Punto de Venta")


def abrir_ventana_inventario():
    """Crea y muestra la ventana para gestionar el inventario."""
    inventario_win = tk.Toplevel(root)
    inventario_win.title("Gestión de Inventario")
    inventario_win.geometry("900x600")

    # --- Frames para organizar la ventana ---
    frame_lista = tk.Frame(inventario_win, bd=2, relief="groove")
    frame_lista.pack(pady=10, padx=10, fill="both", expand=True)

    frame_controles = tk.Frame(inventario_win, bd=2, relief="groove")
    frame_controles.pack(pady=10, padx=10, fill="x")

    # --- Treeview para mostrar la lista de artículos ---
    columnas = ("id", "codigo", "descripcion", "precio", "stock")
    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings")
    
    # encabezados
    tree.heading("id", text="ID")
    tree.heading("codigo", text="Código")
    tree.heading("descripcion", text="Descripción")
    tree.heading("precio", text="Precio")
    tree.heading("stock", text="Stock")

    # Ajustar ancho de columnas
    tree.column("id", width=50, anchor=tk.CENTER)
    tree.column("codigo", width=100, anchor=tk.CENTER)
    tree.column("descripcion", width=350)
    tree.column("precio", width=100, anchor=tk.E) # Alineado a la derecha 
    tree.column("stock", width=100, anchor=tk.CENTER)
    
    tree.pack(fill="both", expand=True)

    # --- Campos de entrada y etiquetas en el frame de controles ---
    tk.Label(frame_controles, text="Código:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_codigo = tk.Entry(frame_controles, width=30)
    entry_codigo.grid(row=0, column=1, padx=5, pady=5)
    
    # Campo oculto para guardar el ID del artículo seleccionado
    entry_id = tk.Entry(frame_controles)

    tk.Label(frame_controles, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_descripcion = tk.Entry(frame_controles, width=50)
    entry_descripcion.grid(row=1, column=1, padx=5, pady=5, columnspan=2)

    tk.Label(frame_controles, text="Precio:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    entry_precio = tk.Entry(frame_controles, width=20)
    entry_precio.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_controles, text="Stock:").grid(row=1, column=3, padx=5, pady=5, sticky="w")
    entry_stock = tk.Entry(frame_controles, width=20)
    entry_stock.grid(row=1, column=4, padx=5, pady=5)
    
    # --- Funciones internas de la ventana de inventario ---
    
    def cargar_articulos():
        """Limpia el Treeview y carga todos los artículos de la BD."""
        # Limpiar tabla
        for item in tree.get_children():
            tree.delete(item)
        # Cargar datos
        articulos = funciones.listar_articulos()
        for art in articulos:
            # Formatear el precio para que se muestre con dos decimales
            precio_formateado = f"{art[3]:.2f}"
            tree.insert("", tk.END, values=(art[0], art[1], art[2], precio_formateado, art[4]))
    
    def limpiar_campos():
        """Limpia los campos de entrada y la selección."""
        entry_id.delete(0, tk.END)
        entry_codigo.delete(0, tk.END)
        entry_descripcion.delete(0, tk.END)
        entry_precio.delete(0, tk.END)
        entry_stock.delete(0, tk.END)
        tree.selection_remove(tree.selection()) # Deseleccionar fila
        entry_codigo.focus()

    def seleccionar_articulo(event):
        """Al seleccionar un artículo, llena los campos con sus datos."""
        item_seleccionado = tree.selection()
        if not item_seleccionado:
            return
        
        item = tree.item(item_seleccionado)
        valores = item['values']

        limpiar_campos() # Limpia por si acaso
        
        entry_id.insert(0, valores[0])
        entry_codigo.insert(0, valores[1])
        entry_descripcion.insert(0, valores[2])
        entry_precio.insert(0, valores[3])
        entry_stock.insert(0, valores[4])
    
    tree.bind("<<TreeviewSelect>>", seleccionar_articulo)

    def guardar_articulo():
        
        # Validaciones básicas
        if not entry_codigo.get() or not entry_descripcion.get() or not entry_precio.get() or not entry_stock.get():
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=inventario_win)
            return

        try:
            precio = float(entry_precio.get())
            stock = int(entry_stock.get())
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser números válidos.", parent=inventario_win)
            return
        
        id_articulo = entry_id.get()
        if id_articulo: # Si hay un ID, es una edición
            funciones.editar_articulo(id_articulo, entry_codigo.get(), entry_descripcion.get(), precio, stock)
        else: # Si no hay ID, es una creación
            funciones.agregar_articulo(entry_codigo.get(), entry_descripcion.get(), precio, stock)
        
        cargar_articulos()
        limpiar_campos()

    def eliminar_articulo():
        
        if not entry_id.get():
            messagebox.showerror("Error", "Debe seleccionar un artículo para eliminar.", parent=inventario_win)
            return
        
        confirmar = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este artículo?", parent=inventario_win)
        if confirmar:
            funciones.borrar_articulo(entry_id.get())
            cargar_articulos()
            limpiar_campos()

    # --- Botones en el frame de controles ---
    btn_guardar = tk.Button(frame_controles, text="Guardar", command=guardar_articulo, bg="#B7E998")
    btn_guardar.grid(row=0, column=5, padx=10, pady=5, sticky="ew")

    btn_eliminar = tk.Button(frame_controles, text="Eliminar", command=eliminar_articulo, bg="#F8A894")
    btn_eliminar.grid(row=1, column=5, padx=10, pady=5, sticky="ew")

    btn_limpiar = tk.Button(frame_controles, text="Limpiar Campos", command=limpiar_campos)
    btn_limpiar.grid(row=0, column=6, rowspan=2, padx=10, pady=5, sticky="ns")

    # Cargar los datos iniciales al abrir la ventana
    cargar_articulos()


def buscar_en_bd():
    global articulos_agregados

    texto = barra_busca.get()

    try:
        cantidad = int(barra_cant.get())
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        tk.messagebox.showerror("Cantidad inválida", "Ingresá una cantidad válida mayor a cero.")
        return

    resultados = funciones.buscar_articulo(texto)

    if not resultados:
        tk.messagebox.showinfo("Sin resultados", "No se encontraron productos que coincidan.")
        return

    r = resultados[0]  # Tomamos el primero que coincida
    articulo = {
        "codigo": r[1],         # Código
        "descripcion": r[2],    # Descripción
        "precio": r[3],         # Precio unitario
        "cantidad": cantidad,
        "importe": r[3] * cantidad
    }
    articulos_agregados.append(articulo)

    mostrar_articulos_en_grilla()
    actualizar_totales()
    
def mostrar_articulos_en_grilla():
    checks_articulos.clear()  # Limpiamos la lista para evitar duplicados

    for fila_num, art in enumerate(articulos_agregados, start=1):
        tk.Label(info_articulos, text=art["codigo"], font=("Arial", 11),
                 bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=0, sticky="nsew")
        tk.Label(info_articulos, text=art["descripcion"], font=("Arial", 11),
                 bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=1, sticky="nsew")
        tk.Label(info_articulos, text=art["cantidad"], font=("Arial", 11),
                 bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=2, sticky="nsew")
        tk.Label(info_articulos, text=f"${art['precio']:.2f}", font=("Arial", 11),
                 bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=3, sticky="nsew")
        tk.Label(info_articulos, text=f"${art['importe']:.2f}", font=("Arial", 11),
                 bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=4, sticky="nsew")

        # Checkbox para seleccionar artículo
        var_check = tk.BooleanVar()
        check = tk.Checkbutton(info_articulos, variable=var_check, bg="#FFFFFF")
        check.grid(row=fila_num, column=5, sticky="nsew")
        checks_articulos.append(var_check)


        
def actualizar_totales():
    subtotal = sum(art["importe"] for art in articulos_agregados)
    descuento = 0  # Podés agregar lógica de descuento si querés
    total = subtotal - descuento

    # Actualizar los labels visuales
    valor_subt.config(text=f"${subtotal:.2f}")
    valor_desc.config(text=f"${descuento:.2f}")
    valor_tot.config(text=f"${total:.2f}")
    

def mostrar_encabezados():
    columnas = ["Código", "Descripción", "Cantidad", "Precio Unitario", "Importe", "Seleccionar"]
    for i, texto_col in enumerate(columnas):
        label = tk.Label(info_articulos, text=texto_col, bg="#96C9D9",
                         font=("Arial", 12, "bold"), anchor="center",
                         relief="solid", bd=1, padx=50, pady=4)
        label.grid(row=0, column=i, sticky="nsew")

        # Asignamos peso proporcional a cada columna
        info_articulos.grid_columnconfigure(i, weight=1)



def mostrar_graficos():
    generar_grafico_ventas_por_articulo()
    generar_grafico_cantidad_por_articulo()
    generar_grafico_ventas_por_dia()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

header_opciones = tk.Frame(bg="#ADB2B4", height=50, bd=3, relief="ridge")
parte_busqueda = tk.Frame(root, bg="#CFCFCF", height=40)
body = tk.Frame(root, bg="#CFCFCF") 

# Contenedor que reemplaza a info_articulos
contenedor_scroll = tk.Frame(root)
contenedor_scroll.place(relx=0.02, rely=0.143, relwidth=0.78, relheight=0.828)

canvas = tk.Canvas(contenedor_scroll, bg="#F5F5F5")
scrollbar = tk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#F5F5F5")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Este es tu nuevo info_articulos
info_articulos = scrollable_frame

bloque_totales = tk.Frame(body, bg="#C2DBE4", bd=1, relief="solid")

header_opciones.pack(fill="x")
parte_busqueda.pack(fill="x")
body.pack(fill="both", expand=True)

bloque_totales.place(relx=0.81, rely=0.071, relwidth=0.16, relheight=0.143) 

mostrar_encabezados()

btn_buscar = tk.Button(root, text="Buscar", command=buscar_en_bd, bg="#DDEEFF")
btn_buscar.place(relx=0.42, rely=0.071, relwidth=0.08)

barra_busca = tk.Entry(root, bd=3, relief="ridge")
barra_busca.place(relx=0.10, rely=0.071, relwidth=0.3)

texto_cant = tk.Label(root, text="Cantidad:")
texto_cant.place(relx=0.81, rely=0.071)

barra_cant = tk.Entry(root, bd=3, relief="ridge")  
barra_cant.place(relx=0.87, rely=0.071, relwidth=0.1)


btn_inventario = tk.Button(header_opciones, text="Inventario", padx=10, pady=1, font=("Inter", 8), command=abrir_ventana_inventario)
btn_inventario.pack(side="left", padx=5, pady=5)  

buttons = ["Ventas"]
for text in buttons:
    btn = tk.Button(header_opciones, text=text, padx=10, pady=1, font=("Inter", 8))
    btn.pack(side="left", padx=5, pady=5)

btn_detalle_de_venta = tk.Button(header_opciones, text="Graficos de venta", padx=10, pady=1, font=("Inter", 8), command=mostrar_graficos)
btn_detalle_de_venta.pack(side="left", padx=15, pady=5)

btn_generar_ticket = tk.Button(header_opciones, text="Generar Ticket", padx=10, pady=1, font=("Inter", 8),command=creartickets )
btn_generar_ticket.pack(side="left", padx=8, pady=5)

btn_cerrar = tk.Button(header_opciones, text="Cerrar Caja", padx=10, pady=1, bg="#ffdddd", font=("Inter", 8))
btn_cerrar.pack(side="right", padx=10, pady=1)

texto_total_venta = tk.Label(body, text="Totales de Venta:")
texto_total_venta.place(relx=0.81, rely=0.030)

texto_subt = tk.Label(bloque_totales, text="Subtotal:", bg="#CFCFCF", bd=1, relief="solid")
texto_subt.place(relx=0.062, rely=0.1)

texto_desc = tk.Label(bloque_totales, text="Desc/int:", bg="#CFCFCF", bd=1, relief="solid")
texto_desc.place(relx=0.062, rely=0.4)

texto_total = tk.Label(bloque_totales, text="TOTAL:", bg="#CFCFCF", bd=1, relief="solid")
texto_total.place(relx=0.062, rely=0.7)

valor_subt = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_subt.place(relx=0.625, rely=0.1)

valor_desc = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_desc.place(relx=0.625, rely=0.4)

valor_tot = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_tot.place(relx=0.625, rely=0.7)

def ventana_agregar_producto():
    ventana=tk.Toplevel(root)
    ventana.title("agregar productos")
    ventana.geometry("300x250")
    ventana.resizable(False,False)

    tk.Label(ventana, text="codigo").pack(pady=5)
    entry_codigo=tk.Entry(ventana)
    entry_codigo.pack()

    tk.Label(ventana, text="Descripción:").pack(pady=5)
    entry_descripcion = tk.Entry(ventana)
    entry_descripcion.pack()

    tk.Label(ventana, text="Precio:").pack(pady=5)
    entry_precio = tk.Entry(ventana)
    entry_precio.pack()

    tk.Label(ventana, text="Stock:").pack(pady=5)
    entry_stock = tk.Entry(ventana)
    entry_stock.pack()
    
    def guardar_producto():
        try:
            codigo = entry_codigo.get()
            descripcion = entry_descripcion.get()
            precio = float(entry_precio.get())
            stock = int(entry_stock.get())
            funciones.agregar_articulo(codigo, descripcion, precio, stock)
            messagebox.showinfo("Éxito", "✅ Producto agregado correctamente")
            ventana.destroy()
            buscar_en_bd()
        except Exception as e:
            messagebox.showerror("Error", f"❌ Datos inválidos: {e}")
    
    tk.Button(ventana, text="Agregar", command=guardar_producto, bg="#B7E998").pack(pady=15)  


    
btn_presupuesto = tk.Button(body, text="Presupuesto", padx=10, pady=1, bg="#C3C5C2", font=("Inter", 8), bd=1, relief="solid")
btn_presupuesto.place(relx=0.81, rely=0.286, relwidth=0.16, relheight=0.071)

btn_cobrar = tk.Button(body, text="Cobrar", padx=10, pady=1, bg="#8CCFFF", font=("Inter", 8), bd=1, relief="solid")
btn_cobrar.place(relx=0.81, rely=0.4, relwidth=0.16, relheight=0.071)

def limpiar_resultados(): 
    global articulos_agregados
    articulos_agregados.clear()  # Esto sí borra la lista real

    for widget in info_articulos.winfo_children():
        info_articulos.grid_columnconfigure(info_articulos.children[widget._name], weight=1)
        if widget.grid_info()['row'] != 0:
            widget.destroy()
    
        
btn_nueva_venta = tk.Button(body, text="Nueva Venta",command=limpiar_resultados, padx=10, pady=1, bg="#B7E998", font=("Inter", 8), bd=1, relief="solid")
btn_nueva_venta.place(relx=0.81, rely=0.514, relwidth=0.16, relheight=0.071)

def eliminar_articulos():
    global articulos_agregados
    nuevos_articulos = []

    for i, art in enumerate(articulos_agregados):
        if not checks_articulos[i].get():
            nuevos_articulos.append(art)

    articulos_agregados = nuevos_articulos
    mostrar_articulos_en_grilla()
    actualizar_totales()

btn_eliminar_articulo = tk.Button(body, text="Eliminar articulo",command=eliminar_articulos, padx=10, pady=1, bg="#F8A894", font=("Inter", 8), bd=1, relief="solid")
btn_eliminar_articulo.place(relx=0.81, rely=0.628, relwidth=0.16, relheight=0.071) 

btn_agregar_producto = tk.Button( body, text="Agregar Producto", padx=10, pady=1, bg="#A8E6CF", font=("Inter", 8), bd=1, relief="solid", command=ventana_agregar_producto)
btn_agregar_producto.place(relx=0.81, rely=0.742, relwidth=0.16, relheight=0.071)

root.mainloop()