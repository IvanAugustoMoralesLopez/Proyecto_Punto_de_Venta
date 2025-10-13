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
from datetime import datetime
from generar_pdf_tkinter import abrir_ventana_pdf
from interfaz import ventana_cobro, mostrar_ultimos_tickets
from decimal import Decimal, InvalidOperation

# --- Globales ---
articulos_agregados = []
checks_articulos = []
id_sesion_actual = None
monto_inicial_caja = Decimal("0.00")

# Globales para la búsqueda autocompletable
lista_articulos_completa = []
mapa_articulos = {}

# --- Funciones de Lógica de la App ---

def cargar_lista_completa_articulos():
    """Carga todos los artículos de la BD para la búsqueda autocompletable."""
    global lista_articulos_completa, mapa_articulos
    articulos_db = funciones.listar_articulos()
    
    lista_articulos_completa.clear()
    mapa_articulos.clear()

    for art in articulos_db:
        texto_display = f"{art[2]} - ${art[3]:.2f}"
        lista_articulos_completa.append(texto_display)
        mapa_articulos[texto_display] = {
            "id": art[0], "codigo": art[1], "descripcion": art[2], "precio": art[3]
        }

def actualizar_sugerencias(event=None):
    """Filtra y muestra la lista de sugerencias debajo de la barra de búsqueda."""
    texto_actual = barra_busca.get()
    
    if not texto_actual:
        lista_sugerencias.place_forget()
        return

    nuevos_valores = [
        item for item in lista_articulos_completa 
        if texto_actual.lower() in item.lower()
    ]
    
    if nuevos_valores:
        lista_sugerencias.delete(0, tk.END)
        for item in nuevos_valores:
            lista_sugerencias.insert(tk.END, item)
        
        x, y, ancho, alto = barra_busca.winfo_x(), barra_busca.winfo_y(), barra_busca.winfo_width(), barra_busca.winfo_height()
        lista_sugerencias.place(x=x, y=y + alto, width=ancho, height=150)
        lista_sugerencias.lift()
    else:
        lista_sugerencias.place_forget()

def seleccionar_articulo_de_lista(event=None):
    """Se ejecuta al seleccionar un item de la lista de sugerencias."""
    if not lista_sugerencias.curselection():
        return
        
    seleccion = lista_sugerencias.get(lista_sugerencias.curselection())
    
    if seleccion in mapa_articulos:
        datos_articulo = mapa_articulos[seleccion]
        try:
            cantidad = int(barra_cant.get())
            if cantidad <= 0: raise ValueError
        except ValueError:
            cantidad = 1
            barra_cant.delete(0, tk.END)
            barra_cant.insert(0, "1")

        articulo = {
            "id": datos_articulo["id"],
            "codigo": datos_articulo["codigo"],
            "descripcion": datos_articulo["descripcion"],
            "descripcion_original": datos_articulo["descripcion"],
            "precio": Decimal(str(datos_articulo["precio"])),
            "precio_original": Decimal(str(datos_articulo["precio"])),
            "cantidad": cantidad,
            "importe": Decimal(str(datos_articulo["precio"])) * cantidad
        }
        
        articulos_agregados.append(articulo)
        mostrar_articulos_en_grilla()
        actualizar_totales()
        
        barra_busca.delete(0, tk.END)
        lista_sugerencias.place_forget()

def abrir_ventana_descuento():
    indices_seleccionados = [i for i, var in enumerate(checks_articulos) if var.get()]
    if not indices_seleccionados:
        messagebox.showwarning("Sin selección", "Por favor, seleccione al menos un artículo para aplicar un descuento.")
        return

    win_desc = tk.Toplevel(root)
    win_desc.title("Aplicar Descuento a Selección")
    win_desc.geometry("300x150")
    win_desc.resizable(False, False)
    win_desc.transient(root)
    win_desc.grab_set()

    frame = ttk.Frame(win_desc, padding="15")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Porcentaje de descuento (%):").pack(pady=5)
    entry_porcentaje = ttk.Entry(frame, justify="center")
    entry_porcentaje.pack(fill="x", pady=(0, 10))
    entry_porcentaje.focus()

    def confirmar_descuento():
        try:
            porcentaje_desc = Decimal(entry_porcentaje.get().replace(",", "."))
            if porcentaje_desc <= 0:
                raise ValueError("El descuento debe ser mayor a cero.")
        except (ValueError, InvalidOperation):
            messagebox.showerror("Dato inválido", "Por favor, ingrese un número válido para el porcentaje.", parent=win_desc)
            return
        
        for index in indices_seleccionados:
            art = articulos_agregados[index]
            descuento = art["precio_original"] * (porcentaje_desc / Decimal("100"))
            nuevo_precio = art["precio_original"] - descuento
            art["precio"] = nuevo_precio
            art["descripcion"] = f"{art['descripcion_original']} ({porcentaje_desc:.0f}% OFF)"
            art["importe"] = nuevo_precio * art["cantidad"]

        mostrar_articulos_en_grilla()
        actualizar_totales()
        win_desc.destroy()

    ttk.Button(frame, text="Confirmar Descuento", command=confirmar_descuento).pack(pady=15, ipady=5)

def ventana_apertura_caja(root):
    global id_sesion_actual, monto_inicial_caja

    caja_existente = funciones.verificar_caja_abierta()
    if caja_existente:
        if messagebox.askyesno("Caja Abierta", "Ya existe una sesión de caja abierta. ¿Desea continuar con esa sesión?"):
            id_sesion_actual, monto_inicial_caja = caja_existente
            monto_inicial_caja = Decimal(str(monto_inicial_caja))
            cargar_lista_completa_articulos()
            root.deiconify()
            return
        else:
            root.destroy()
            return

    apertura_win = tk.Toplevel(root)
    apertura_win.title("Apertura de Caja")
    apertura_win.geometry("300x150")
    apertura_win.resizable(False, False)
    apertura_win.transient(root)
    apertura_win.grab_set()

    tk.Label(apertura_win, text="Ingrese el monto inicial en caja:", font=("Arial", 10)).pack(pady=10)
    entry_monto = tk.Entry(apertura_win, font=("Arial", 12), justify='center')
    entry_monto.pack(pady=5, padx=20, fill='x')
    entry_monto.focus()

    def confirmar_apertura():
        global id_sesion_actual, monto_inicial_caja
        try:
            monto_str = entry_monto.get().replace(",",".")
            monto_decimal = Decimal(monto_str)
            if monto_decimal < 0: raise ValueError("El monto no puede ser negativo")

            id_sesion = funciones.abrir_caja(float(monto_decimal))
            if id_sesion:
                id_sesion_actual, monto_inicial_caja = id_sesion, monto_decimal
                cargar_lista_completa_articulos()
                apertura_win.destroy()
                root.deiconify()
            else:
                messagebox.showerror("Error de Base de Datos", "No se pudo registrar la apertura de caja.", parent=apertura_win)
        except (ValueError, InvalidOperation) as e:
            messagebox.showerror("Dato inválido", f"Por favor, ingrese un número válido.\n{e}", parent=apertura_win)

    tk.Button(apertura_win, text="Confirmar", command=confirmar_apertura, bg="#B7E998").pack(pady=10)
    apertura_win.protocol("WM_DELETE_WINDOW", root.destroy)

def gestionar_cierre_caja():
    if not id_sesion_actual:
        messagebox.showwarning("Advertencia", "No hay una sesión de caja activa para cerrar.")
        return

    ventas = funciones.obtener_ventas_sesion(id_sesion_actual)
    monto_esperado = monto_inicial_caja + ventas.get("Efectivo", Decimal("0.0"))

    cierre_win = tk.Toplevel(root)
    cierre_win.title("Cierre de Caja")
    cierre_win.geometry("400x450")
    cierre_win.resizable(False, False)
    cierre_win.transient(root)
    cierre_win.grab_set()
    
    frame = tk.Frame(cierre_win, padx=15, pady=15)
    frame.pack(fill='both', expand=True)

    def crear_fila(fila, etiqueta, valor):
        tk.Label(frame, text=etiqueta).grid(row=fila, column=0, sticky='w', pady=2)
        tk.Label(frame, text=f"${valor:.2f}", font=("Arial", 10, "bold")).grid(row=fila, column=1, sticky='e', pady=2)

    tk.Label(frame, text="Resumen de Caja", font=("Arial", 14, "bold")).grid(row=0, columnspan=2, pady=10)
    crear_fila(1, "Monto Inicial:", monto_inicial_caja)
    crear_fila(2, "Ventas en Efectivo:", ventas.get('Efectivo', Decimal('0.0')))
    crear_fila(3, "Ventas con Tarjeta:", ventas.get('Tarjeta', Decimal('0.0')))
    crear_fila(4, "Ventas (Otros Medios):", ventas.get('Otros', Decimal('0.0')))
    ttk.Separator(frame, orient='horizontal').grid(row=5, columnspan=2, sticky='ew', pady=10)
    tk.Label(frame, text="Monto Esperado en Caja:", font=("Arial", 11, "bold")).grid(row=6, column=0, sticky='w', pady=5)
    tk.Label(frame, text=f"${monto_esperado:.2f}", font=("Arial", 11, "bold")).grid(row=6, column=1, sticky='e', pady=5)

    tk.Label(frame, text="Monto Real (Contado):", font=("Arial", 10)).grid(row=7, column=0, sticky='w', pady=10)
    entry_monto_real = tk.Entry(frame, font=("Arial", 12), justify='center')
    entry_monto_real.grid(row=7, column=1, sticky='ew')
    entry_monto_real.focus()

    label_diferencia = tk.Label(frame, text="Diferencia: $0.00", font=("Arial", 12, "bold"), fg="blue")
    label_diferencia.grid(row=8, columnspan=2, pady=10)

    def calcular_diferencia(event=None):
        try:
            monto_real_val = Decimal(entry_monto_real.get())
            diferencia = monto_real_val - monto_esperado
            color = "red" if diferencia < 0 else "green" if diferencia > 0 else "blue"
            label_diferencia.config(text=f"Diferencia: ${diferencia:.2f}", fg=color)
        except (ValueError, InvalidOperation):
            label_diferencia.config(text="Diferencia: ---", fg="black")
    
    entry_monto_real.bind("<KeyRelease>", calcular_diferencia)

    def confirmar_cierre():
        try:
            monto_real = Decimal(entry_monto_real.get())
            if messagebox.askyesno("Confirmar Cierre", "¿Está seguro de cerrar la caja?", parent=cierre_win):
                funciones.cerrar_caja(id_sesion_actual, monto_inicial_caja, monto_real, ventas)
                messagebox.showinfo("Caja Cerrada", "La aplicación se cerrará.", parent=cierre_win)
                root.destroy()
        except (ValueError, InvalidOperation):
            messagebox.showerror("Dato inválido", "Ingrese un monto real válido.", parent=cierre_win)

    tk.Button(frame, text="Confirmar y Salir", command=confirmar_cierre, bg="#F8A894").grid(row=9, columnspan=2, sticky='ew', pady=15, ipady=5)

def abrir_ventana_inventario():
    inventario_win = tk.Toplevel(root)
    inventario_win.title("Gestión de Inventario")
    inventario_win.geometry("900x600")

    frame_lista = tk.Frame(inventario_win, bd=2, relief="groove")
    frame_lista.pack(pady=10, padx=10, fill="both", expand=True)
    frame_controles = tk.Frame(inventario_win, bd=2, relief="groove")
    frame_controles.pack(pady=10, padx=10, fill="x")

    columnas = ("id", "codigo", "descripcion", "precio", "stock")
    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings")
    tree.heading("id", text="ID")
    tree.heading("codigo", text="Código")
    tree.heading("descripcion", text="Descripción")
    tree.heading("precio", text="Precio")
    tree.heading("stock", text="Stock")
    tree.column("id", width=50, anchor=tk.CENTER)
    tree.column("codigo", width=100, anchor=tk.CENTER)
    tree.column("descripcion", width=350)
    tree.column("precio", width=100, anchor=tk.E)
    tree.column("stock", width=100, anchor=tk.CENTER)
    tree.pack(fill="both", expand=True)

    tk.Label(frame_controles, text="Código:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_codigo = tk.Entry(frame_controles, width=30)
    entry_codigo.grid(row=0, column=1, padx=5, pady=5)
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
    
    def cargar_articulos():
        for item in tree.get_children():
            tree.delete(item)
        articulos = funciones.listar_articulos()
        for art in articulos:
            precio_formateado = f"{art[3]:.2f}"
            tree.insert("", tk.END, values=(art[0], art[1], art[2], precio_formateado, art[4]))
    
    def limpiar_campos():
        entry_id.delete(0, tk.END)
        entry_codigo.delete(0, tk.END)
        entry_descripcion.delete(0, tk.END)
        entry_precio.delete(0, tk.END)
        entry_stock.delete(0, tk.END)
        if tree.selection():
            tree.selection_remove(tree.selection()[0])
        entry_codigo.focus()

    def seleccionar_articulo(event):
        item_seleccionado = tree.selection()
        if not item_seleccionado: return
        item = tree.item(item_seleccionado)
        valores = item['values']
        limpiar_campos()
        entry_id.insert(0, valores[0])
        entry_codigo.insert(0, valores[1])
        entry_descripcion.insert(0, valores[2])
        entry_precio.insert(0, valores[3])
        entry_stock.insert(0, valores[4])
    
    tree.bind("<<TreeviewSelect>>", seleccionar_articulo)

    def guardar_articulo():
        if not all([entry_codigo.get(), entry_descripcion.get(), entry_precio.get(), entry_stock.get()]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=inventario_win)
            return
        try:
            precio = float(entry_precio.get().replace(",", "."))
            stock = int(entry_stock.get())
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser números válidos.", parent=inventario_win)
            return
        
        id_articulo = entry_id.get()
        if id_articulo:
            funciones.editar_articulo(id_articulo, entry_codigo.get(), entry_descripcion.get(), precio, stock)
        else:
            funciones.agregar_articulo(entry_codigo.get(), entry_descripcion.get(), precio, stock)
        
        cargar_articulos()
        limpiar_campos()

    def eliminar_articulo():
        if not entry_id.get():
            messagebox.showerror("Error", "Debe seleccionar un artículo para eliminar.", parent=inventario_win)
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este artículo?", parent=inventario_win):
            funciones.borrar_articulo(entry_id.get())
            cargar_articulos()
            limpiar_campos()

    btn_guardar = tk.Button(frame_controles, text="Guardar", command=guardar_articulo, bg="#B7E998")
    btn_guardar.grid(row=0, column=5, padx=10, pady=5, sticky="ew")
    btn_eliminar = tk.Button(frame_controles, text="Eliminar", command=eliminar_articulo, bg="#F8A894")
    btn_eliminar.grid(row=1, column=5, padx=10, pady=5, sticky="ew")
    btn_limpiar = tk.Button(frame_controles, text="Limpiar Campos", command=limpiar_campos)
    btn_limpiar.grid(row=0, column=6, rowspan=2, padx=10, pady=5, sticky="ns")
    cargar_articulos()

def mostrar_articulos_en_grilla():
    for widget in info_articulos.winfo_children():
        if int(widget.grid_info()["row"]) > 0:
            widget.destroy()

    checks_articulos.clear()
    for fila_num, art in enumerate(articulos_agregados, start=1):
        tk.Label(info_articulos, text=art["codigo"], font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=0, sticky="nsew")
        tk.Label(info_articulos, text=art["descripcion"], font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=1, sticky="nsew")
        tk.Label(info_articulos, text=art["cantidad"], font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=2, sticky="nsew")
        tk.Label(info_articulos, text=f"${art['precio']:.2f}", font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=3, sticky="nsew")
        tk.Label(info_articulos, text=f"${art['importe']:.2f}", font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=4, sticky="nsew")
        var_check = tk.BooleanVar()
        check = tk.Checkbutton(info_articulos, variable=var_check, bg="#FFFFFF")
        check.grid(row=fila_num, column=5, sticky="nsew")
        checks_articulos.append(var_check)
        
def actualizar_totales():
    subtotal_bruto = sum(art["precio_original"] * art["cantidad"] for art in articulos_agregados)
    total_neto = sum(art["importe"] for art in articulos_agregados)
    descuento = subtotal_bruto - total_neto
    valor_subt.config(text=f"${subtotal_bruto:.2f}")
    valor_desc.config(text=f"${descuento:.2f}")
    valor_tot.config(text=f"${total_neto:.2f}")
    
def mostrar_encabezados():
    columnas = ["Código", "Descripción", "Cantidad", "Precio Unit.", "Importe", "Seleccionar"]
    for i, texto_col in enumerate(columnas):
        label = tk.Label(info_articulos, text=texto_col, bg="#96C9D9", font=("Arial", 12, "bold"), anchor="center", relief="solid", bd=1, padx=50, pady=4)
        label.grid(row=0, column=i, sticky="nsew")
        info_articulos.grid_columnconfigure(i, weight=1 if i != 5 else 0)

def mostrar_graficos():
    generar_grafico_ventas_por_articulo()
    generar_grafico_cantidad_por_articulo()
    generar_grafico_ventas_por_dia()

def ventana_agregar_producto():
    ventana = tk.Toplevel(root)
    ventana.title("Agregar productos")
    ventana.geometry("300x250")
    ventana.resizable(False,False)
    tk.Label(ventana, text="Código").pack(pady=5)
    entry_codigo = tk.Entry(ventana)
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
            precio = float(entry_precio.get().replace(",", "."))
            stock = int(entry_stock.get())
            funciones.agregar_articulo(codigo, descripcion, precio, stock)
            messagebox.showinfo("Éxito", "✅ Producto agregado correctamente", parent=ventana)
            ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"❌ Datos inválidos: {e}", parent=ventana)
    
    tk.Button(ventana, text="Agregar", command=guardar_producto, bg="#B7E998").pack(pady=15)

def limpiar_resultados(): 
    global articulos_agregados
    articulos_agregados.clear()
    mostrar_articulos_en_grilla()
    actualizar_totales()
        
def eliminar_articulos_seleccionados():
    global articulos_agregados
    indices_a_mantener = [i for i, var in enumerate(checks_articulos) if not var.get()]
    articulos_agregados = [articulos_agregados[i] for i in indices_a_mantener]
    mostrar_articulos_en_grilla()
    actualizar_totales()

def calcular_presupuesto_seleccionados():
    if len(checks_articulos) != len(articulos_agregados):
        messagebox.showerror("Error", "La selección no está sincronizada. Intenta agregar o eliminar artículos de nuevo.")
        return
    
    seleccionados = [art for var, art in zip(checks_articulos, articulos_agregados) if var.get()]
    
    if not seleccionados:
        messagebox.showinfo("Presupuesto", "No hay productos seleccionados.")
        return
        
    total_presupuesto = sum(art.get("importe", 0) for art in seleccionados)
    messagebox.showinfo("Presupuesto", f"El total de los productos seleccionados es: ${total_presupuesto:.2f}")

root = tk.Tk()
root.title("Punto de Venta")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
header_opciones = tk.Frame(bg="#ADB2B4", height=50, bd=3, relief="ridge")
parte_busqueda = tk.Frame(root, bg="#CFCFCF", height=40)
body = tk.Frame(root, bg="#CFCFCF") 
contenedor_scroll = tk.Frame(root)
contenedor_scroll.place(relx=0.02, rely=0.143, relwidth=0.78, relheight=0.828)
canvas = tk.Canvas(contenedor_scroll, bg="#F5F5F5")
scrollbar = tk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#F5F5F5")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
info_articulos = scrollable_frame
bloque_totales = tk.Frame(body, bg="#C2DBE4", bd=1, relief="solid")
header_opciones.pack(fill="x")
parte_busqueda.pack(fill="x")
body.pack(fill="both", expand=True)
bloque_totales.place(relx=0.81, rely=0.071, relwidth=0.16, relheight=0.143) 
mostrar_encabezados()

barra_busca = tk.Entry(root, font=("Arial", 11))
barra_busca.place(relx=0.10, rely=0.071, relwidth=0.4)
lista_sugerencias = tk.Listbox(root, font=("Arial", 10))
barra_busca.bind('<KeyRelease>', actualizar_sugerencias)
lista_sugerencias.bind('<Double-1>', seleccionar_articulo_de_lista)
lista_sugerencias.bind('<Return>', seleccionar_articulo_de_lista)
root.bind('<Button-1>', lambda e: lista_sugerencias.place_forget() if e.widget != lista_sugerencias and e.widget != barra_busca else None)

texto_cant = tk.Label(root, text="Cantidad:")
texto_cant.place(relx=0.81, rely=0.071)
barra_cant = tk.Entry(root, bd=3, relief="ridge")
barra_cant.place(relx=0.87, rely=0.071, relwidth=0.1)
barra_cant.insert(0, "1")
btn_inventario = tk.Button(header_opciones, text="Inventario", padx=10, pady=1, font=("Inter", 8), command=abrir_ventana_inventario)
btn_inventario.pack(side="left", padx=5, pady=5)
tk.Button(header_opciones, text="Ventas", padx=10, pady=1, font=("Inter", 8), command=lambda: mostrar_ultimos_tickets(root)).pack(side="left", padx=5, pady=5)
tk.Button(header_opciones, text="Graficos de venta", padx=10, pady=1, font=("Inter", 8), command=mostrar_graficos).pack(side="left", padx=15, pady=5)
tk.Button(header_opciones, text="Generar Ticket", padx=10, pady=1, font=("Inter", 8), command=creartickets).pack(side="left", padx=8, pady=5)
tk.Button(header_opciones, text= "Generar PDF", padx=10, pady=1, font=("Inter", 8), command=lambda: abrir_ventana_pdf(root)).pack(side="left", padx=8, pady=5)
tk.Button(header_opciones, text="Cerrar Caja", padx=10, pady=1, bg="#ffdddd", font=("Inter", 8), command=gestionar_cierre_caja).pack(side="right", padx=10, pady=1)
texto_total_venta = tk.Label(body, text="Totales de Venta:")
texto_total_venta.place(relx=0.81, rely=0.030)
tk.Label(bloque_totales, text="Subtotal:", bg="#CFCFCF", bd=1, relief="solid").place(relx=0.062, rely=0.1)
tk.Label(bloque_totales, text="Desc/int:", bg="#CFCFCF", bd=1, relief="solid").place(relx=0.062, rely=0.4)
tk.Label(bloque_totales, text="TOTAL:", bg="#CFCFCF", bd=1, relief="solid").place(relx=0.062, rely=0.7)
valor_subt = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_subt.place(relx=0.625, rely=0.1)
valor_desc = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_desc.place(relx=0.625, rely=0.4)
valor_tot = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_tot.place(relx=0.625, rely=0.7)
btn_cobrar = tk.Button(body, text="Cobrar", padx=10, pady=1, bg="#8CCFFF", font=("Inter", 8), bd=1, relief="solid", 
                        command=lambda: ventana_cobro(root, articulos_agregados, limpiar_resultados, actualizar_totales, id_sesion_actual))
btn_cobrar.place(relx=0.81, rely=0.3, relwidth=0.16, relheight=0.071)
btn_presupuesto = tk.Button(body, text="Presupuesto", command=calcular_presupuesto_seleccionados, padx=10, pady=1, bg="#C3C5C2", font=("Inter", 8), bd=1, relief="solid")
btn_presupuesto.place(relx=0.81, rely=0.8, relwidth=0.16, relheight=0.071) # Ajusta 'rely' si es necesario
btn_nueva_venta = tk.Button(body, text="Nueva Venta",command=limpiar_resultados, padx=10, pady=1, bg="#B7E998", font=("Inter", 8), bd=1, relief="solid")
btn_nueva_venta.place(relx=0.81, rely=0.4, relwidth=0.16, relheight=0.071)
btn_eliminar_articulo = tk.Button(body, text="Eliminar Articulo", command=eliminar_articulos_seleccionados, padx=10, pady=1, bg="#F8A894", font=("Inter", 8), bd=1, relief="solid")
btn_eliminar_articulo.place(relx=0.81, rely=0.5, relwidth=0.16, relheight=0.071)
btn_aplicar_descuento = tk.Button(body, text="Aplicar Descuento", command=abrir_ventana_descuento, padx=10, pady=1, bg="#FDFD96", font=("Inter", 8), bd=1, relief="solid")
btn_aplicar_descuento.place(relx=0.81, rely=0.6, relwidth=0.16, relheight=0.071)
btn_agregar_producto = tk.Button(body, text="Agregar Producto", padx=10, pady=1, bg="#A8E6CF", font=("Inter", 8), bd=1, relief="solid", command=ventana_agregar_producto)
btn_agregar_producto.place(relx=0.81, rely=0.7, relwidth=0.16, relheight=0.071)

if __name__ == "__main__":
    
    ventana_apertura_caja(root)
    root.mainloop()