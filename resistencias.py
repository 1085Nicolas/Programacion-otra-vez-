import tkinter as tk
import conexionfb
from conexionfb import iniciar_sesion
import subprocess

resistencias = tk.Tk()
resistencias.title("Calculadora de Resistencias")
resistencias.geometry("300x300")
resistencias.resizable(False,False)

opciones = ["negro", "marron", "rojo", "naranja", "amarillo", "verde", "azul", "violeta", "gris", "blanco"]
colores = {
    "negro": "black", "marron": "brown", "rojo": "red", "naranja": "orange", "amarillo": "yellow",
    "verde": "green", "azul": "blue", "violeta": "purple", "gris": "gray", "blanco": "white"
}
valores = {
    "negro": 0, "marron": 1, "rojo": 2, "naranja": 3, "amarillo": 4,
    "verde": 5, "azul": 6, "violeta": 7, "gris": 8, "blanco": 9
}

var1 = tk.StringVar(value=opciones[0])
var2 = tk.StringVar(value=opciones[0])
var3 = tk.StringVar(value=opciones[0])
var4 = tk.StringVar(value="±5%")

def calcular_resistencia():
    try:
        banda1 = valores[var1.get()]
        banda2 = valores[var2.get()]
        multiplicador = 10 ** valores[var3.get()]
        tolerancia = var4.get()
        
        resistencia = (banda1 * 10 + banda2) * multiplicador
        resultado.config(text=f"Resistencia: {resistencia} Ω ± {tolerancia}") 

        if conexionfb.current_user_id: 
            operacion = f"{operacion} = {resistencia}"
            registrar_historial(conexionfb.current_user_id, 'resistencia', operacion)
    except KeyError:
        resultado.config(text="Error en la selección", fg="red")

# Creación de los OptionMenu con colores en los textos
def crear_menu(variable):
    menu = tk.OptionMenu(resistencias, variable, *opciones)
    menu.config(fg="black") 
    for i, color in enumerate(opciones):
        menu["menu"].entryconfig(i, foreground=colores[color])  # Colorea cada opción en su respectivo color
    return menu

def abrir_calculadora(nombre_archivo,cerave):
    cerave.destroy() 
    subprocess.Popen(["python", nombre_archivo]) 

def mostrar_menu():
    menu_window = tk.Toplevel(resistencias)
    menu_window.title("Menú")
    menu_window.geometry("300x200")
    menu_window.resizable(False, False)

    # Botón para iniciar sesión
    btn_iniciar_sesion = tk.Button(menu_window, text="Iniciar Sesión", command=iniciar_sesion)
    btn_iniciar_sesion.pack(pady=10)

    tk.Button(menu_window, text="Calculadora Científica", command=lambda: abrir_calculadora("calculadora_principal.py",resistencias)).pack(pady=10)
    tk.Button(menu_window, text="Calculadora Grafica", command=lambda: abrir_calculadora("calculo.py",resistencias)).pack(pady=10)
    tk.Button(menu_window, text="Conversión de Unidades", command=lambda: abrir_calculadora("fisica.py",resistencias)).pack(pady=10)
    tk.Button(menu_window, text="matrices", command=lambda: abrir_calculadora("matrices.py",resistencias)).pack(pady=10)

# Creación de los OptionMenu
codigo1 = crear_menu(var1)
codigo2 = crear_menu(var2)
codigo3 = crear_menu(var3)
codigo4 = tk.OptionMenu(resistencias, var4, "±5%", "±10%")
codigo4.config(fg="black")

codigo1.pack(pady=5)
codigo2.pack(pady=5)
codigo3.pack(pady=5)
codigo4.pack(pady=5)

botonmenu = tk.Button(resistencias, text="menu", command=mostrar_menu)
boton_calcular = tk.Button(resistencias, text="Calcular", command=calcular_resistencia)
boton_calcular.pack(pady=10)
resultado = tk.Label(resistencias, text="Resistencia: ",font=("Arial", 12))
resultado.pack()
botonmenu.pack(pady=10)

resistencias.mainloop()
