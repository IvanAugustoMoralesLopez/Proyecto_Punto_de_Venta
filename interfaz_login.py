import tkinter as tk
from tkinter import ttk, messagebox 
from funciones import verificar_usuario 

print("[DEBUG] Iniciando interfaz_login.py (V3.1 - ttk.Frame)...")

class LoginFrame(ttk.Frame): 
    """Un Frame (ahora ttk.Frame) que contiene los widgets de login."""
    def __init__(self, master, on_success, on_cancel, **kwargs):
        print("[DEBUG] LoginFrame.__init__ INICIADO.")
        super().__init__(master, padding="20", **kwargs) 
        self.master = master
        self.on_success = on_success
        self.on_cancel = on_cancel
        
        self.master.title("Inicio de Sesión - Punto de Venta")
        self.master.geometry("350x200")
        self.master.resizable(False, False)
        self.master.eval('tk::PlaceWindow . center')

        self._crear_widgets()
        print("[DEBUG] LoginFrame.__init__ TERMINADO.")

    def _crear_widgets(self):
        print("[DEBUG] LoginFrame._crear_widgets INICIADO.")
        
        ttk.Label(self, text="Usuario:", font=("Arial", 10)).pack(pady=5)
        self.entry_usuario = ttk.Entry(self, font=("Arial", 10))
        self.entry_usuario.pack(fill="x", pady=5)
        self.entry_usuario.focus()

        ttk.Label(self, text="Contraseña:", font=("Arial", 10)).pack(pady=5)
        self.entry_pass = ttk.Entry(self, show="*", font=("Arial", 10))
        self.entry_pass.pack(fill="x", pady=5)

        # Frame para botones (puede ser ttk también)
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=10)

        btn_ingresar = ttk.Button(button_frame, text="Ingresar", command=self.intentar_login)
        btn_ingresar.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        btn_cancelar = ttk.Button(button_frame, text="Cancelar", command=self.on_cancel) 
        btn_cancelar.pack(side="right", expand=True, fill="x", padx=(5, 0))

        self.master.bind('<Return>', lambda event: self.intentar_login())
        self.master.protocol("WM_DELETE_WINDOW", self.on_cancel) 
        print("[DEBUG] LoginFrame._crear_widgets TERMINADO.")

    def intentar_login(self):
        print("[DEBUG] LoginFrame: Clic en 'Ingresar'.")
        username = self.entry_usuario.get()
        password = self.entry_pass.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Debe ingresar usuario y contraseña.", parent=self.master)
            return

        print("[DEBUG] LoginFrame: Llamando a funciones.verificar_usuario...")
        usuario_info = verificar_usuario(username, password)
        print(f"[DEBUG] LoginFrame: verificar_usuario devolvió: {usuario_info}")
        
        if usuario_info:
            self.on_success(usuario_info) 
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.", parent=self.master)
            self.entry_pass.delete(0, tk.END)

print("[DEBUG] interfaz_login.py (V3.1): Archivo importado.")