import tkinter as tk
from tkinter import ttk, messagebox
import funciones


print("[DEBUG] Iniciando interfaz_usuarios.py...")

def abrir_ventana_gestion_usuarios(parent):
    """Crea y muestra la ventana para gestionar usuarios."""
    print("[DEBUG] interfaz_usuarios: Iniciando abrir_ventana_gestion_usuarios...")

    ventana = tk.Toplevel(parent)
    ventana.title("Gestión de Usuarios")
    ventana.geometry("800x600") 
    ventana.resizable(False, False)
    ventana.transient(parent)
    ventana.grab_set()

    # --- Frames para estructura ---
    frame_lista = ttk.Frame(ventana, padding="10")
    frame_lista.pack(pady=5, padx=10, fill="both", expand=True)

    frame_formulario = ttk.LabelFrame(ventana, text="Datos del Usuario", padding="10")
    frame_formulario.pack(pady=5, padx=10, fill="x")
    
    frame_botones = ttk.Frame(ventana, padding="10")
    frame_botones.pack(pady=5, padx=10, fill="x")

    # --- Lista de Usuarios (Treeview) ---
    columnas = ("id", "username", "nombre", "rol")
    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings", height=15)
    
    tree.heading("id", text="ID")
    tree.heading("username", text="Username")
    tree.heading("nombre", text="Nombre Completo")
    tree.heading("rol", text="Rol")

    tree.column("id", width=50, anchor=tk.CENTER)
    tree.column("username", width=150)
    tree.column("nombre", width=300)
    tree.column("rol", width=100, anchor=tk.CENTER)

    # Scrollbar para la lista
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- Formulario de Datos ---
    # Fila 1: Username y Nombre Completo
    tk.Label(frame_formulario, text="Username:*").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_username = ttk.Entry(frame_formulario, width=30)
    entry_username.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    
    tk.Label(frame_formulario, text="Nombre Completo:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    entry_nombre = ttk.Entry(frame_formulario, width=40)
    entry_nombre.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    # Fila 2: Rol y Contraseña
    tk.Label(frame_formulario, text="Rol:*").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    # Usamos Combobox para roles definidos
    combo_rol = ttk.Combobox(frame_formulario, values=["vendedor", "admin"], state="readonly", width=27) 
    combo_rol.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    combo_rol.set("vendedor") # Rol por defecto

    tk.Label(frame_formulario, text="Contraseña:*").grid(row=1, column=2, sticky="w", padx=5, pady=5)
    entry_password = ttk.Entry(frame_formulario, show="*", width=40)
    entry_password.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
    tk.Label(frame_formulario, text="(* Obligatorio para nuevo usuario)", font=("Arial", 8)).grid(row=2, column=3, sticky="w", padx=5)


    # Campo oculto para el ID
    entry_id = ttk.Entry(frame_formulario) 
    
    # Configurar expansión de columnas
    frame_formulario.grid_columnconfigure(1, weight=1)
    frame_formulario.grid_columnconfigure(3, weight=1)

    # --- Lógica de la Interfaz ---
    
    def cargar_usuarios():
        """Carga o recarga los usuarios en el Treeview."""
        print("[DEBUG] interfaz_usuarios: Cargando lista de usuarios...")
        # Limpiar lista actual
        for item in tree.get_children():
            tree.delete(item)
        # Obtener usuarios (función a crear en funciones.py)
        try:
            usuarios_db = funciones.listar_usuarios() 
            for u in usuarios_db:
                # Insertamos ID, Username, Nombre, Rol
                tree.insert("", tk.END, values=(u.id, u.username, u.nombre_completo, u.rol), iid=u.id)
            print(f"[DEBUG] interfaz_usuarios: {len(usuarios_db)} usuarios cargados.")
        except AttributeError:
             print("[ERROR] interfaz_usuarios: 'listar_usuarios' no existe o no devuelve objetos válidos.")
             messagebox.showerror("Error", "No se pudo cargar la lista de usuarios. La función 'listar_usuarios' podría faltar.", parent=ventana)
        except Exception as e:
            print(f"[ERROR] interfaz_usuarios: Error al cargar usuarios: {e}")
            messagebox.showerror("Error", f"No se pudo cargar la lista de usuarios:\n{e}", parent=ventana)


    def limpiar_campos():
        """Limpia los campos del formulario y deselecciona la lista."""
        print("[DEBUG] interfaz_usuarios: Limpiando campos...")
        entry_id.delete(0, tk.END)
        entry_username.config(state="normal") # Habilitar username al limpiar
        entry_username.delete(0, tk.END)
        entry_nombre.delete(0, tk.END)
        combo_rol.set("vendedor")
        entry_password.delete(0, tk.END)
        if tree.selection():
            tree.selection_remove(tree.selection()[0])
        entry_username.focus()
        print("[DEBUG] interfaz_usuarios: Campos limpios.")

    def seleccionar_usuario(event):
        """Carga los datos del usuario seleccionado en el formulario."""
        if not tree.selection():
            return
        
        id_seleccionado = tree.selection()[0]
        usuario_seleccionado = tree.item(id_seleccionado)['values']
        print(f"[DEBUG] interfaz_usuarios: Seleccionado usuario ID: {id_seleccionado}")
        
        limpiar_campos()
        entry_id.insert(0, usuario_seleccionado[0])      # ID
        entry_username.insert(0, usuario_seleccionado[1]) # Username
        entry_username.config(state="readonly") # No permitir editar username
        entry_nombre.insert(0, usuario_seleccionado[2])   # Nombre
        combo_rol.set(usuario_seleccionado[3])          # Rol
        # La contraseña no se carga por seguridad, solo se establece si se quiere cambiar
        print("[DEBUG] interfaz_usuarios: Datos cargados en formulario.")

    tree.bind("<<TreeviewSelect>>", seleccionar_usuario)

    def guardar_usuario():
        """Guarda un usuario nuevo o edita uno existente."""
        username = entry_username.get().strip()
        nombre = entry_nombre.get().strip() or None # Permitir nombre vacío (NULL en BD)
        rol = combo_rol.get()
        password = entry_password.get() # No quitar strip() a la contraseña
        id_usuario = entry_id.get()

        print(f"[DEBUG] interfaz_usuarios: Intentando guardar. ID='{id_usuario}', User='{username}'")

        if not username:
            messagebox.showerror("Error", "El campo 'Username' es obligatorio.", parent=ventana)
            return
        if not rol:
            messagebox.showerror("Error", "Debe seleccionar un 'Rol'.", parent=ventana)
            return

        # Validar contraseña: Obligatoria si es NUEVO usuario, opcional si es EDICIÓN
        if not id_usuario and not password: # Es nuevo y no puso contraseña
             messagebox.showerror("Error", "La 'Contraseña' es obligatoria para nuevos usuarios.", parent=ventana)
             return

        try:
            if id_usuario: # Editar usuario existente
                print("[DEBUG] interfaz_usuarios: Llamando a funciones.editar_usuario...")
                # La función editar_usuario debe manejar si la contraseña viene vacía (no cambiar) o no
                funciones.editar_usuario(id_usuario, username, nombre, rol, password or None) 
            else: # Agregar nuevo usuario
                print("[DEBUG] interfaz_usuarios: Llamando a funciones.agregar_usuario...")
                # La función agregar_usuario debe hashear la contraseña
                funciones.agregar_usuario(username, nombre, rol, password) 
            
            print("[DEBUG] interfaz_usuarios: Guardado exitoso. Recargando y limpiando...")
            cargar_usuarios()
            limpiar_campos()
        except AttributeError as ae:
            print(f"[ERROR] interfaz_usuarios: Función no encontrada: {ae}")
            messagebox.showerror("Error de Función", f"La función necesaria ({'agregar_usuario' if not id_usuario else 'editar_usuario'}) no existe.", parent=ventana)
        except Exception as e:
            print(f"[ERROR] interfaz_usuarios: Error al guardar: {e}")
            # Podría ser por username duplicado, error de BD, etc.
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el usuario:\n{e}", parent=ventana)


    def eliminar_usuario():
        """Elimina el usuario seleccionado."""
        id_usuario = entry_id.get()
        if not id_usuario:
            messagebox.showerror("Error", "Debe seleccionar un usuario para eliminar.", parent=ventana)
            return
        
        # Seguridad: No permitir borrar el usuario 'admin'
        if entry_username.get() == 'admin':
             messagebox.showerror("Error", "No se puede eliminar al usuario administrador principal ('admin').", parent=ventana)
             return

        print(f"[DEBUG] interfaz_usuarios: Intentando eliminar usuario ID: {id_usuario}")
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este usuario?", parent=ventana):
            try:
                print("[DEBUG] interfaz_usuarios: Llamando a funciones.borrar_usuario...")
                funciones.borrar_usuario(id_usuario)
                print("[DEBUG] interfaz_usuarios: Eliminación exitosa. Recargando y limpiando...")
                cargar_usuarios()
                limpiar_campos()
            except AttributeError:
                 print("[ERROR] interfaz_usuarios: 'borrar_usuario' no existe.")
                 messagebox.showerror("Error de Función", "La función 'borrar_usuario' no existe.", parent=ventana)
            except Exception as e:
                print(f"[ERROR] interfaz_usuarios: Error al eliminar: {e}")
                messagebox.showerror("Error al Eliminar", f"No se pudo eliminar el usuario:\n{e}", parent=ventana)

    # --- Botones ---
    btn_guardar = ttk.Button(frame_botones, text="Guardar", command=guardar_usuario)
    btn_guardar.pack(side="left", expand=True, fill="x", padx=5)

    btn_eliminar = ttk.Button(frame_botones, text="Eliminar", command=eliminar_usuario)
    btn_eliminar.pack(side="left", expand=True, fill="x", padx=5)

    btn_limpiar = ttk.Button(frame_botones, text="Limpiar Campos", command=limpiar_campos)
    btn_limpiar.pack(side="left", expand=True, fill="x", padx=5)

    # --- Carga inicial ---
    cargar_usuarios() 
    print("[DEBUG] interfaz_usuarios: Ventana de gestión de usuarios lista.")


# --- Bloque para probar esta ventana de forma independiente (opcional) ---
if __name__ == '__main__':
    print("[DEBUG] interfaz_usuarios: Ejecutando en modo de prueba independiente...")
    # Esto solo se ejecuta si corres python interfaz_usuarios.py directamente
    
    
    
    class MockFunciones:
        _usuarios = [
            {'id': 1, 'username': 'admin', 'nombre_completo': 'Admin Principal', 'rol': 'admin', 'password_hash': 'hash_admin'},
            {'id': 2, 'username': 'vendedor1', 'nombre_completo': 'Juan Perez', 'rol': 'vendedor', 'password_hash': 'hash_juan'},
        ]
        _next_id = 3

        def listar_usuarios(self):
            print("[MOCK] listar_usuarios llamado")
            # Convertimos dicts a objetos simples para simular fetchone()
            class UserRow:
                def __init__(self, d):
                    self.__dict__.update(d)
            return [UserRow(u) for u in self._usuarios]

        def agregar_usuario(self, username, nombre, rol, password):
            print(f"[MOCK] agregar_usuario llamado: u={username}, n={nombre}, r={rol}, p={'***' if password else 'N/A'}")
            if any(u['username'] == username for u in self._usuarios):
                 raise Exception(f"Username '{username}' ya existe (mock).")
            nuevo = {'id': self._next_id, 'username': username, 'nombre_completo': nombre, 'rol': rol, 'password_hash': f'hash_{username}'}
            self._usuarios.append(nuevo)
            self._next_id += 1

        def editar_usuario(self, id_usuario, username, nombre, rol, password):
            print(f"[MOCK] editar_usuario llamado: id={id_usuario}, u={username}, n={nombre}, r={rol}, p={'***' if password else 'N/A'}")
            for u in self._usuarios:
                if u['id'] == int(id_usuario):
                    u['nombre_completo'] = nombre
                    u['rol'] = rol
                    if password: # Si se proporcionó nueva contraseña
                         u['password_hash'] = f'hash_nuevo_{username}'
                    return
            raise Exception(f"Usuario ID {id_usuario} no encontrado (mock).")

        def borrar_usuario(self, id_usuario):
             print(f"[MOCK] borrar_usuario llamado: id={id_usuario}")
             self._usuarios = [u for u in self._usuarios if u['id'] != int(id_usuario)]

    funciones = MockFunciones() 
    

    root = tk.Tk()
    root.title("Prueba Usuarios")
    
    # Botón para abrir la ventana de gestión
    btn_abrir = ttk.Button(root, text="Abrir Gestión Usuarios", 
                            command=lambda: abrir_ventana_gestion_usuarios(root))
    btn_abrir.pack(padx=50, pady=50)
    
    root.mainloop()

print("[DEBUG] interfaz_usuarios.py: Archivo importado/ejecutado.")