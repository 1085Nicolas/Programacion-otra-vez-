import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from conexionfb import LoginApp, set_current_user, current_user_id
from interfaces import Cientifica, InterfazResistencia, Interfaz
import conexionfb 
from firebase_admin import db

def mostrar_historial_calculadora():
    def insertar_resultado(resultado):
        for widget in ctk.get_windows():
            if isinstance(widget, Cientifica):
                widget.entrada.delete(0, ctk.END)
                widget.entrada.insert(0, resultado)
                return
        CTkMessagebox(title="Error",message="No hay una calculadora científica abierta.")
    
    if conexionfb.current_user_id is None:
        respuesta = CTkMessagebox(title="Iniciar Sesión",message="Necesitas iniciar sesión para ver tu historial. ¿Deseas iniciar sesión ahora?")
        if respuesta:
            login_window = LoginApp()
            login_window.mainloop()
    else:
        historial_window = ctk.CTk()
        historial_window.title("Historial de Cálculos")
        historial_window.geometry("400x300")
        
        historial_ref = db.reference(f'users/{conexionfb.current_user_id}/history')
        historial = historial_ref.get()
        
        if historial:
            for action_id, action_data in historial.items():
                action = action_data.get('action', 'Acción desconocida')
                timestamp = action_data.get('timestamp', 'Sin fecha')
                
                if "=" in action:
                    operacion, resultado = action.split(" = ", 1)
                else:
                    resultado = action
                
                boton = ctk.CTkButton(historial_window, text=f'{timestamp} - {action}', command=lambda res=resultado: insertar_resultado(res))
                boton.pack(fill='x', padx=5, pady=2)
        else:
            ctk.CTkLabel(historial_window, text="No hay historial disponible.").pack()
        
        historial_window.mainloop()

class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Menú Principal")
        self.geometry("300x350")
        self.resizable(False, False)

        main_frame = ctk.CTkFrame(self, fg_color="#121212")
        main_frame.grid(row=0, column=0, padx=20, pady=20)

        title_label = ctk.CTkLabel(main_frame, text="Bienvenido", font=("Arial", 20, "bold"), text_color="#6A0DAD")
        title_label.grid(row=0, column=0, pady=(10, 20))

        self.login_button = ctk.CTkButton(main_frame, text="Iniciar sesión", fg_color="#6A0DAD", text_color="white", hover_color="#540A91", width=250, command=self.ir_inicio_sesion)
        self.login_button.grid(row=1, column=0, pady=10)

        self.cientifica_button = ctk.CTkButton(main_frame, text="Calculadora Científica", width=250, command=self.abrir_cientifica)
        self.cientifica_button.grid(row=2, column=0, pady=10)

        self.resistencia_button = ctk.CTkButton(main_frame, text="Calculadora de Resistencia", width=250, command=self.abrir_resistencia)
        self.resistencia_button.grid(row=3, column=0, pady=10)

        self.matrices_button = ctk.CTkButton(main_frame, text="Calculadora de Matrices", width=250, command=self.abrir_matrices)
        self.matrices_button.grid(row=4, column=0, pady=10)

        self.historial_button = ctk.CTkButton(main_frame, text="Ver Historial", width=250, command=mostrar_historial_calculadora)
        self.historial_button.grid(row=5, column=0, pady=10)

    def ir_inicio_sesion(self):
        login_window = LoginApp()
        login_window.mainloop()
        if conexionfb.current_user_id:
            self.login_button.grid_forget()

    def abrir_cientifica(self):
        self.withdraw()
        cientifica_window = Cientifica()
        cientifica_window.mainloop()
        self.deiconify()

    def abrir_resistencia(self):
        self.withdraw()
        resistencia_window = InterfazResistencia(self)
        resistencia_window.ventana.mainloop()
        self.deiconify()

    def abrir_matrices(self):
        self.withdraw()
        matrices_window = ctk.CTkToplevel(self)
        matrices_window.title("Calculadora de Matrices")
        Interfaz(matrices_window) 
        matrices_window.mainloop()
        self.deiconify()

if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()
