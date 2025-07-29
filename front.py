import tkinter as tk

root = tk.Tk()
root.title("Punto de Venta")

# Detectar resolución de pantalla
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# Frames principales
header_opciones = tk.Frame(bg="#ADB2B4", height=50, bd=3, relief="ridge")
parte_busqueda = tk.Frame(root, bg="#CFCFCF", height=40)
body = tk.Frame(root, bg="#CFCFCF") 
info_articulos = tk.Frame(root, bg="#F5F5F5", bd=1, relief="solid")
bloque_totales = tk.Frame(body, bg="#C2DBE4", bd=1, relief="solid")

# Posicionamiento
header_opciones.pack(fill="x")
parte_busqueda.pack(fill="x")
body.pack(fill="both", expand=True)

# Adaptativo: proporciones basadas en 1000x700
info_articulos.place(relx=0.02, rely=0.143, relwidth=0.78, relheight=0.828)
bloque_totales.place(relx=0.81, rely=0.071, relwidth=0.16, relheight=0.143)

# Buscar
texto_busca = tk.Label(root, text="Buscar Articulo:")
texto_busca.place(relx=0.02, rely=0.071)

barra_busca = tk.Entry(root, bd=3, relief="ridge")
barra_busca.place(relx=0.10, rely=0.071, relwidth=0.3)

# Cantidad
texto_cant = tk.Label(root, text="Cantidad:")
texto_cant.place(relx=0.81, rely=0.071)

barra_cant = tk.Entry(root, bd=3, relief="ridge")  
barra_cant.place(relx=0.87, rely=0.071, relwidth=0.1)

# Botones en el header
buttons = ["Ventas", "Crear Ticket/s"] # Algunos de los botones que no los llevamos a cabo por no tener importancia para este mini proyecto: "Inventario", "Clientes", "Historial de Ventas", "Historial de Caja"
for text in buttons:
    btn = tk.Button(header_opciones, text=text, padx=10, pady=1, font=("Inter", 8))
    btn.pack(side="left", padx=5, pady=5)

# Botón "Cerrar Caja" separado
btn_cerrar = tk.Button(header_opciones, text="Cerrar Caja", padx=10, pady=1, bg="#ffdddd", font=("Inter", 8))
btn_cerrar.pack(side="right", padx=10, pady=1)

# Sub-bloque para los encabezados
encabezado = tk.Frame(info_articulos, bg="#96C9D9")
encabezado.pack(fill="x")

# Encabezados
columnas = ["Código", "Descripción", "Cantidad", "Precio Unitario", "Importe"]
anchos = [10, 40, 10, 10, 7]

for i, (texto, ancho) in enumerate(zip(columnas, anchos)):
    label = tk.Label(encabezado, text=texto, bg="#f0f0f0", font=("Arial", 10),
                     width=ancho, anchor="center", relief="solid", bd=1)
    label.grid(row=0, column=i, sticky="nsew")

for i in range(len(columnas)):
    encabezado.grid_columnconfigure(i, weight=1)

# Totales de Venta
texto_total_venta = tk.Label(body, text="Totales de Venta:")
texto_total_venta.place(relx=0.81, rely=0.030)

# Textos dentro de bloque_totales
texto_subt = tk.Label(bloque_totales, text="Subtotal:", bg="#CFCFCF", bd=1, relief="solid")
texto_subt.place(relx=0.062, rely=0.1)

texto_desc = tk.Label(bloque_totales, text="Desc/int:", bg="#CFCFCF", bd=1, relief="solid")
texto_desc.place(relx=0.062, rely=0.4)

texto_total = tk.Label(bloque_totales, text="TOTAL:", bg="#CFCFCF", bd=1, relief="solid")
texto_total.place(relx=0.062, rely=0.7)

# Valores de los textos
valor_subt = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_subt.place(relx=0.625, rely=0.1)

valor_desc = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_desc.place(relx=0.625, rely=0.4)

valor_tot = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
valor_tot.place(relx=0.625, rely=0.7)

# Botones de acción
btn_presupuesto = tk.Button(body, text="Presupuesto", padx=10, pady=1, bg="#C3C5C2", font=("Inter", 8), bd=1, relief="solid")
btn_presupuesto.place(relx=0.81, rely=0.286, relwidth=0.16, relheight=0.071)

btn_cobrar = tk.Button(body, text="Cobrar", padx=10, pady=1, bg="#8CCFFF", font=("Inter", 8), bd=1, relief="solid")
btn_cobrar.place(relx=0.81, rely=0.4, relwidth=0.16, relheight=0.071)

btn_nueva_venta = tk.Button(body, text="Nueva Venta", padx=10, pady=1, bg="#B7E998", font=("Inter", 8), bd=1, relief="solid")
btn_nueva_venta.place(relx=0.81, rely=0.514, relwidth=0.16, relheight=0.071)

btn_eliminar_articulo = tk.Button(body, text="Eliminar articulo", padx=10, pady=1, bg="#F8A894", font=("Inter", 8), bd=1, relief="solid")
btn_eliminar_articulo.place(relx=0.81, rely=0.628, relwidth=0.16, relheight=0.071)

root.mainloop()