# firebase.py
import firebase_admin
from firebase_admin import credentials, db, auth
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Inicializa la aplicación de Firebase
cred = credentials.Certificate("C:\\Users\\basti\\OneDrive\\Documentos\\programacion2024-2\\supercalculadoratilininsano-firebase-adminsdk-fbsvc-4b60c20dce.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://supercalculadoratilininsano-default-rtdb.firebaseio.com/'
})

current_user_id = None

def iniciar_sesion():

    inicio = tk.Toplevel()
    inicio.title("Iniciar Sesión")
    inicio.geometry("388x260")
    inicio.resizable(False, False)

    # Crear y configurar los widgets
    usuario = tk.Label(inicio, text="Usuario o correo")
    ise = tk.Entry(inicio, font="Helvetica 18")
    contraseña = tk.Label(inicio, text="Contraseña")
    isc = tk.Entry(inicio, font="Helvetica 18", show="*")
    iniciose = tk.Label(inicio, text=" ")
    
    def validar_inicio_sesion():

        global current_user_id
        email = ise.get().strip()
        password = isc.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
            
        try:
            user = auth.get_user_by_email(email)
            if user:
                current_user_id = user.uid
                messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
                inicio.destroy()
                return user.uid
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar sesión: {str(e)}")
            return None

    def crear_cuenta():

        email = ise.get().strip()
        password = isc.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
            
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            registrar_historial(user.uid, 'create_account', 'Cuenta creada exitosamente')
            messagebox.showinfo("Éxito", "Cuenta creada exitosamente")
            return user.uid
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la cuenta: {str(e)}")
            return None

    # Crear los botones
    iniciar_btn = tk.Button(inicio, text="Iniciar", command=validar_inicio_sesion)
    crear_btn = tk.Button(inicio, text="Crear Cuenta", command=crear_cuenta)
    nada_btn = tk.Button(inicio, text="Continuar sin iniciar sesión", command=inicio.destroy)

    # Organizar los widgets usando grid
    usuario.grid(row=0, column=1, pady=5)
    ise.grid(row=1, column=1, pady=5)
    contraseña.grid(row=2, column=1, pady=5)
    isc.grid(row=3, column=1, pady=5)
    iniciose.grid(row=4, column=1, pady=5)
    iniciar_btn.grid(row=5, column=2, pady=5)
    crear_btn.grid(row=5, column=0, pady=5)
    nada_btn.grid(row=6, column=1, pady=5)
