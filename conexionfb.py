import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import firebase_admin
from firebase_admin import credentials, db, auth
import datetime


cred = credentials.Certificate("C:\\Users\\basti\\OneDrive\\Documentos\\programacion2024-2\\supercalculadoratilininsano-firebase-adminsdk-fbsvc-4b60c20dce.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://supercalculadoratilininsano-default-rtdb.firebaseio.com/'
})

# Global variable to keep the session active
current_user_id = None

def set_current_user(user_id):
    global current_user_id
    current_user_id = user_id

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CTk Login")
        self.geometry("400x350")
        self.resizable(False, False)

        main_frame = ctk.CTkFrame(self, fg_color="#121212")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tabview = ctk.CTkTabview(main_frame, width=300)
        tabview.pack(pady=20)

        login_tab = tabview.add("Login")
        register_tab = tabview.add("Sign Up")

        title_label = ctk.CTkLabel(login_tab, text="Welcome Back!", font=("Arial", 20, "bold"), text_color="#6A0DAD")
        title_label.pack(pady=(10, 5))

        self.email_entry = ctk.CTkEntry(login_tab, placeholder_text="📧 Email", width=250)
        self.email_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(login_tab, placeholder_text="🔑 Password", width=250, show="*")
        self.password_entry.pack(pady=5)

        login_button = ctk.CTkButton(login_tab, text="Login", fg_color="#6A0DAD", text_color="white", hover_color="#540A91", width=250, command=self.validar_inicio_sesion)
        login_button.pack(pady=(20, 5))

        register_label = ctk.CTkLabel(register_tab, text="Create an Account", font=("Arial", 20, "bold"), text_color="#6A0DAD")
        register_label.pack(pady=(10, 5))

        self.reg_email_entry = ctk.CTkEntry(register_tab, placeholder_text="📧 Email", width=250)
        self.reg_email_entry.pack(pady=5)

        self.reg_password_entry = ctk.CTkEntry(register_tab, placeholder_text="🔑 Password", width=250, show="*")
        self.reg_password_entry.pack(pady=5)

        self.confirm_password_entry = ctk.CTkEntry(register_tab, placeholder_text="🔁 Confirm Password", width=250, show="*")
        self.confirm_password_entry.pack(pady=5)

        register_button = ctk.CTkButton(register_tab, text="Sign Up", fg_color="#6A0DAD", text_color="white", hover_color="#540A91", width=250, command=self.crear_cuenta)
        register_button.pack(pady=(20, 5))

    def validar_inicio_sesion(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            CTkMessagebox(title="Error",message="Por favor complete todos los campos",icon="cancel")
            return

        try:
            user = auth.get_user_by_email(email)
            if user:
                global current_user_id
                current_user_id = user.uid  # Guardar el usuario actual
                set_current_user(user.uid)  # Mantener la sesión activa
                CTkMessagebox(title="Éxito",message="Inicio de sesión exitoso")
                self.destroy()
        except Exception as e:
            CTkMessagebox(title="Error",message=f"Error al iniciar sesión: {str(e)}",icon="cancel")

    def crear_cuenta(self):
        email = self.reg_email_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not email or not password or not confirm_password:
            CTkMessagebox(title="Error",message="Por favor complete todos los campos",icon="cancel")
            return
        
        if password != confirm_password:
            CTkMessagebox(title="Error",message="Las contraseñas no coinciden",icon="cancel")
            return

        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            CTkMessagebox(title="Éxito",message="Cuenta creada exitosamente",icon="cancel")
        except Exception as e:
            CTkMessagebox(title="Error",message=f"Error al crear la cuenta: {str(e)}",icon="cancel")


def registrar_historial(tipo, operacion, resultado):
    if current_user_id:
        historial_ref = db.reference(f'users/{current_user_id}/history')
        nueva_entrada = {
            'action': f"{operacion} = {resultado}",
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': tipo
        }
        historial_ref.push(nueva_entrada)
    else:
        CTkMessagebox(title="Error",message="Debes iniciar sesión para guardar en el historial.",icon="cancel")

def mostrar_historial_calculadora(entry):
    if current_user_id is None:
        respuesta = CTkMessagebox(title="Iniciar Sesión",message="Necesitas iniciar sesión para ver tu historial. ¿Deseas iniciar sesión ahora?")
        if respuesta:
            login_window = LoginApp()
            login_window.mainloop()
    else:
        historial_window = ctk.CTk()
        historial_window.title("Historial de Cálculos")
        historial_window.geometry("400x300")
        
        historial_ref = db.reference(f'users/{current_user_id}/history')
        historial = historial_ref.get()
        
        if historial:
            for action_id, action_data in historial.items():
                action = action_data.get('action', 'Acción desconocida')
                timestamp = action_data.get('timestamp', 'Sin fecha')
                
                if "=" in action:
                    operacion, resultado = action.split(" = ", 1)
                else:
                    resultado = action
                
                boton = ctk.CTkButton(historial_window, text=f'{timestamp} - {action}', command=lambda res=resultado: entry.delete(0, ctk.END) or entry.insert(0, res))
                boton.pack(fill='x', padx=5, pady=2)
        else:
            ctk.CTkLabel(historial_window, text="No hay historial disponible.").pack()
        
        historial_window.mainloop()