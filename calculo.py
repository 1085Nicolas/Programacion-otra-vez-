import firebase_admin
from firebase_admin import credentials, db, auth
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import numpy as np
import sympy as sp
import re
import conexionfb
import matplotlib.pyplot as plt
from sympy import lambdify
import subprocess
from conexionfb import iniciar_sesion

dicoperaciones = {
    "sen": "np.sin", "cos": "np.cos", "tan": "np.tan",
    "cot": "1/np.tan", "sec": "1/np.cos", "csc": "1/np.sin",
    "arcsn": "np.arcsin", "arccs": "np.arccos", "arctn": "np.arctan"
    , "²": "**2", "³": "**3", "^": "**", "⁻¹": "**-1",
    "ln": "np.log", "lg": "np.log10",
    "π": "np.pi", "e": "np.e","%": "/100"
}
dicsym = { 
    "sen": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "cot": lambda x: 1/sp.tan(x), "sec": lambda x: 1/sp.cos(x), "csc": lambda x: 1/sp.sin(x),
    "arcsn": sp.asin, "arccs": sp.acos, "arctn": sp.atan,
    "ln": sp.ln, "lg": sp.log,  
    "π": sp.pi, "e": sp.E, "²": "**2", "³": "**3", "^": "**", "⁻¹": "**-1"
}

def mostrar_instrucciones():
    mensaje = (
        "Para usar el modo grafico:\n"
        "1. Escribe la ecuacion.\n"
        "2. Dale en el boton graficar.\n"
        "Para usar integrales(solo se puede indefinidas):\n"
        "1. Escribe la ecuacion.\n"
        "2. Dale en el boton de integral.\n"
        "Para usar las derivadas:\n"
        "1. Escribe la ecuacion.\n"
        "2. Dale en el boton derivar.\n"
        "Para usar sumatorias (solo deja desde 1 a 10):\n"
        "1. Escribe la ecuacion.\n"
        "2. Dale en el boton sigma.\n"
    )

    messagebox.showinfo("Instrucciones", mensaje)

#menu e inicio de sesion
def abrir_calculadora(nombre_archivo,cerave):
    cerave.destroy()  # Cierra la ventana actual
    subprocess.Popen(["python", nombre_archivo])  # Abre la otra calculadorav


def mostrar_menu():
    # Crear una nueva ventana para el menú
    menu_window = tk.Toplevel(casio)
    menu_window.title("Menú")
    menu_window.geometry("300x200")
    menu_window.resizable(False, False)

    # Botón para iniciar sesión
    btn_iniciar_sesion = tk.Button(menu_window, text="Iniciar Sesión", command=iniciar_sesion)
    btn_iniciar_sesion.pack(pady=10)

    tk.Button(menu_window, text="Calculadora Científica", command=lambda: abrir_calculadora("calculadora_principal.py",casio)).pack(pady=10)
    tk.Button(menu_window, text="Calculadora de Resistencias", command=lambda: abrir_calculadora("resistencias.py",casio)).pack(pady=10)
    tk.Button(menu_window, text="Conversión de Unidades", command=lambda: abrir_calculadora("fisica.py",casio)).pack(pady=10)
    tk.Button(menu_window, text="matrices", command=lambda: abrir_calculadora("matrices.py",casio)).pack(pady=10)


#mostrar historial

def mostrar_historial(user_id):
    historial_window = tk.Toplevel(casio)
    historial_window.title("Historial")
    historial_window.geometry("400x300")

    try:
        historial_ref = db.reference(f'users/{user_id}/history')
        historial = historial_ref.get()

        if historial:
            for action_id, action_data in historial.items():
                action = action_data.get('action', 'Acción desconocida')
                timestamp = action_data.get('timestamp', 'Sin fecha')

                # Extraer el resultado de la operación guardada (asumiendo formato "Operación = Resultado")
                if " = " in action:
                    operacion, resultado = action.split(" = ", 1)
                else:
                    resultado = action  # Si no hay "=", asumir que todo es resultado

                # Mostrar cada entrada como un botón
                tk.Button(historial_window, text=f'{timestamp} - {action}',
                          command=lambda res=resultado: usar_resultado(res)).pack(fill='x', padx=5, pady=2)
        else:
            tk.Label(historial_window, text="No hay historial disponible.").pack()
    except Exception as e:
        print(f'Error al recuperar el historial: {e}')
        tk.Label(historial_window, text="Error al cargar el historial.").pack()

#registrar en el historial

def registrar_historial(user_id, action, details):
    if user_id is None:
        print("No se puede registrar historial, el ID de usuario es None.")
        return

    # Crea un nuevo registro de acción
    timestamp = datetime.utcnow().isoformat() + 'Z'  # Formato UTC
    action_id = db.reference(f'users/{user_id}/history').push().key
        
        # Cambiar el valor de 'action' a la operación específica
    db.reference(f'users/{user_id}/history/{action_id}').set({
        'action': details,  # Aquí se guarda la operación
        'timestamp': timestamp,
        'details': f'Operación realizada: {action}'  # Puedes mantener detalles adicionales si lo deseas
    })
    print(f'Historial registrado para el usuario {user_id}: {action}')

def usar_resultado(result):
    """Función para copiar el resultado en la calculadora"""
    isertar.insert(tk.END, result)  # Insertar el resultado seleccionado

#mostrar el historial de la calculadora

def mostrar_historial_calculadora():

    conexionfb.current_user_id
    
    if conexionfb.current_user_id is None:
        respuesta = messagebox.askyesno("Iniciar Sesión", 
            "Necesitas iniciar sesión para ver tu historial. ¿Deseas iniciar sesión ahora?")
        if respuesta:
            iniciar_sesion()
    else:
        mostrar_historial(conexionfb.current_user_id)

def calcular(expresion, tipo="normal"):
    try:
        operacion = expresion

        # Elegir el diccionario adecuado según el tipo de operación
        if tipo in ["derivada", "integral", "sumatoria"]:
            diccionario = dicsym  # SymPy para cálculos simbólicos
        else:
            diccionario = dicoperaciones  # NumPy para cálculos numéricos y gráficos

        # Reemplazar operadores con el diccionario adecuado
        for simbolo, reemplazo in diccionario.items():
            expresion = expresion.replace(simbolo, reemplazo)

        # Reemplazar log_b(a,b) → (log(a) / log(b))
        expresion = re.sub(r"log\(([^,]+),([^)]+)\)", r"(np.log(\1) / np.log(\2))", expresion)

        # Reemplazar raíces generales n√x → x**(1/n)
        expresion = re.sub(r"(\d+)√(\d+)", r"\2**(1/\1)", expresion)
        
        # Reemplazar raíz cuadrada y factorial
        expresion = re.sub(r"√(\d+)", r"\1**(1/2)", expresion)
        expresion = re.sub(r"(\d+)!", r"sp.factorial(\1)", expresion)
        expresion = re.sub(r"∛(\d+)", r"\1**(1/3)", expresion)

        # Evaluar la expresión
        resultado = eval(expresion)
        actualizar_pantalla(resultado)
        ver.config(text=f"{resultado}")

        # Registrar en historial si hay usuario logueado
        if conexionfb.current_user_id:
            operacion = f"{operacion} = {resultado}"
            registrar_historial(conexionfb.current_user_id, 'calculo', operacion)

    except Exception as e:
        actualizar_pantalla("Error")
        ver.config(text="Error en la operación")

# Funciones para actualizar la pantalla
def actualizar_pantalla(valor):
    isertar.delete(0, tk.END)  # Limpiar la pantalla
    isertar.insert(0, valor)  # Mostrar el nuevo valor

def agregar_a_pantalla(valor):
    actual = isertar.get()
    isertar.delete(0, tk.END)
    isertar.insert(0, actual + str(valor))

# Funciones para los botones AC, DEL y Ans
def clear_all():
    isertar.delete(0, tk.END)  # Limpiar el Entry
    ver.config(text=" ") 

def delete_last():
    current_text = isertar.get()
    isertar.delete(0, tk.END)
    isertar.insert(0, current_text[:-1])  # Eliminar el último carácter

def insert_answer():
    agregar_a_pantalla(ver.cget("text"))

#cambio de signo
def toggle_sign():
    current_text = isertar.get()  # Obtener el texto actual del Entry
    if current_text:  # Verifica que no esté vacío
        if current_text[0] == '-':
            isertar.delete(0, tk.END)  # Limpiar el Entry
            isertar.insert(0, current_text[1:])  # Elimina el signo negativo
        else:
            isertar.delete(0, tk.END)  # Limpiar el Entry
            isertar.insert(0, '-' + current_text)

def manejar_teclado(event):
    tecla = event.keysym  # Nombre de la tecla presionada
    caracter = event.char  # Caracter real ingresado (si existe)

    if tecla == "Return":  # Si es Enter, calcular resultado
        calcular(isertar.get())
    elif tecla == "BackSpace":  # Si es Backspace, borrar el último carácter
        delete_last()
    elif caracter.isprintable():  # Si es un carácter imprimible, agregarlo
        agregar_a_pantalla(caracter)
        return "break"  # Evitar que Tkinter lo agregue automáticamente

color_fondo = "white"
color_texto = "black"
color_boton = "lightgray"

def modooscuro ():
    global color_fondo
    global color_boton
    global color_texto
    if color_fondo == "white" :
        color_fondo = "#1E1E1E"
        color_texto = "#F8F8F2"
        color_boton = "#44475A"
    else :
        color_fondo = "white"
        color_texto = "black"
        color_boton = "lightgray"
    
    casio.configure(bg=color_fondo)
    # Actualizar los botones existentes
    for widget in casio.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg=color_boton, fg=color_texto)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=color_fondo, fg=color_texto)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=color_fondo, fg=color_texto, insertbackground=color_texto)

def obtener_expresion(texto):
    """Obtiene la expresión ingresada y la convierte en una expresión simbólica válida"""
    x = sp.Symbol('x')  # Definir la variable simbólica

    # 🔹 Convertir los operadores usando dicsym
    for simbolo, reemplazo in dicsym.items():
        if isinstance(reemplazo, str):  # Asegurar que sea un string
            texto = texto.replace(simbolo, reemplazo)
    
    # 🔹 Transformaciones adicionales
    texto = re.sub(r"log\(([^,]+),([^)]+)\)", r"(sp.log(\1) / sp.log(\2))", texto)  # log_b(a) → log(a)/log(b)
    texto = re.sub(r"(\d+)√(\d+)", r"\2**(1/\1)", texto)  # n√x → x**(1/n)
    texto = re.sub(r"√(\d+)", r"\1**(1/2)", texto)  # √x → x**(1/2)
    texto = re.sub(r"∛(\d+)", r"\1**(1/3)", texto)  # ∛x → x**(1/3)
    texto = re.sub(r"(\d+)!", r"sp.factorial(\1)", texto)  # n! → factorial(n)

    try:
        expr = sp.sympify(texto, locals={"sp": sp, "x": x})  # Convertir a expresión simbólica
        return expr, x
    except Exception:
        messagebox.showerror("Error", "Expresión inválida")
        return None, x


def derivar():
    """Calcula la derivada de la función ingresada"""
    expr, x = obtener_expresion(isertar.get())
    if expr:
        derivada = sp.diff(expr, x)
        actualizar_pantalla(derivada)
        h = actualizar_pantalla(derivada)
    if conexionfb.current_user_id:
            operacion = f"{h}"
            registrar_historial(conexionfb.current_user_id, 'derivada', operacion)

def integrar():
    """Calcula la integral de la función ingresada"""
    expr, x = obtener_expresion(isertar.get())
    if expr:
        integral = sp.integrate(expr, x)
        actualizar_pantalla(f"{integral} + C")
        h = actualizar_pantalla(f"{integral} + C")
    if conexionfb.current_user_id:
            operacion = f"{h}"
            registrar_historial(conexionfb.current_user_id, 'integral', operacion)

def sumatoria():
    """Calcula la sumatoria de la función ingresada"""
    expr, x = obtener_expresion(isertar.get())
    if expr:
        try:
            n = sp.Symbol('n')
            suma = sp.summation(expr.subs(x, n), (n, 1, 10))  # Sumatoria de n=1 a n=10
            actualizar_pantalla(suma)
            h = actualizar_pantalla(suma)
            if conexionfb.current_user_id:
                operacion = f"{h}"
                registrar_historial(conexionfb.current_user_id, 'sumatoria', operacion)
        except Exception:
            messagebox.showerror("Error", "No se pudo calcular la sumatoria")

def graficar_funcion():
    """Genera la gráfica de la función ingresada"""
    expr, x = obtener_expresion(isertar.get())
    if expr:
        
        try:
            h = expr
            funcion_lambda = lambdify(x, expr, 'numpy')  # Convertir SymPy a NumPy
            x_vals = np.linspace(-10, 10, 400)
            y_vals = funcion_lambda(x_vals)

            plt.plot(x_vals, y_vals, label=f"y = {expr}", color='r')
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)
            plt.grid()
            plt.legend()
            plt.xlabel("Eje X") 
            plt.ylabel("Eje Y")
            plt.title("Gráfico de la Función")
            plt.show()
            h = isertar.get()
            if conexionfb.current_user_id:
                operacion = f"{h}"
                registrar_historial(conexionfb.current_user_id, 'grafica', operacion)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo graficar la función: {e}")



def cerrar_aplicacion():
    casio.destroy()

# Inicializar variables

# Tkinter
casio = tk.Tk()
casio.geometry("330x655")
casio.resizable(False, False)
casio.configure(bg=color_fondo)
casio.bind("<Key>", manejar_teclado)  # Vincular teclado

# Etiqueta para mostrar el valor guardado
ver = tk.Label(casio, text="Valor guardado: ")
isertar = tk.Entry (casio,bg=color_fondo, fg=color_texto)
espacio = tk.Label (casio,bg=color_fondo, fg=color_texto)
espacio2 = tk.Label (casio,bg=color_fondo, fg=color_texto)

# Definimos los botones
boton0 = tk.Button(casio,bg=color_boton, fg=color_texto, text="0", width=8, height=4, command=lambda: agregar_a_pantalla(0))
boton1 = tk.Button(casio,bg=color_boton, fg=color_texto, text="1", width=8, height=4, command=lambda: agregar_a_pantalla(1))
boton2 = tk.Button(casio,bg=color_boton, fg=color_texto, text="2", width=8, height=4, command=lambda: agregar_a_pantalla(2))
boton3 = tk.Button(casio,bg=color_boton, fg=color_texto, text="3", width=8, height=4, command=lambda: agregar_a_pantalla(3))
boton4 = tk.Button(casio,bg=color_boton, fg=color_texto, text="4", width=8, height=4, command=lambda: agregar_a_pantalla(4))
boton5 = tk.Button(casio,bg=color_boton, fg=color_texto, text="5", width=8, height=4, command=lambda: agregar_a_pantalla(5))
boton6 = tk.Button(casio,bg=color_boton, fg=color_texto, text="6", width=8, height=4, command=lambda: agregar_a_pantalla(6))
boton7 = tk.Button(casio,bg=color_boton, fg=color_texto, text="7", width=8, height=4, command=lambda: agregar_a_pantalla(7))
boton8 = tk.Button(casio,bg=color_boton, fg=color_texto, text="8", width=8, height=4, command=lambda: agregar_a_pantalla(8))
boton9 = tk.Button(casio,bg=color_boton, fg=color_texto, text="9", width=8, height=4, command=lambda: agregar_a_pantalla(9))
botonigual = tk.Button(casio,bg=color_boton, fg=color_texto, text="=", width=8, height=4, command=lambda: calcular(isertar.get()))
botonpunto = tk.Button(casio,bg=color_boton, fg=color_texto, text=".", width=8, height=4,command=lambda: agregar_a_pantalla("."))
botonpts1 = tk.Button(casio,bg=color_boton, fg=color_texto, text="(", width=8, height=2,command=lambda: agregar_a_pantalla("("))
botonpts2 = tk.Button(casio,bg=color_boton, fg=color_texto, text=")", width=8, height=2,command=lambda: agregar_a_pantalla(")"))
botonsum = tk.Button(casio,bg=color_boton, fg=color_texto, text="+", width=8, height=4, command=lambda: agregar_a_pantalla("+"))
botonres = tk.Button(casio,bg=color_boton, fg=color_texto, text="-", width=8, height=4, command=lambda: agregar_a_pantalla("-"))
botonmul = tk.Button(casio,bg=color_boton, fg=color_texto, text="X", width=8, height=4, command=lambda: agregar_a_pantalla("*"))
botondiv = tk.Button(casio,bg=color_boton, fg=color_texto, text="/", width=8, height=4, command=lambda: agregar_a_pantalla("/"))
botonderivada = tk.Button(casio,bg=color_boton, fg=color_texto, text="d/dx", width=8, height=2, command=derivar)
botonelev = tk.Button(casio,bg=color_boton, fg=color_texto, text="^", width=8, height=2, command=lambda: agregar_a_pantalla("^"))
botonrc = tk.Button(casio,bg=color_boton, fg=color_texto, text="√", width=8, height=2, command=lambda: agregar_a_pantalla(" √"))
botonln = tk.Button(casio,bg=color_boton, fg=color_texto, text="ln", width=8, height=2, command=lambda: agregar_a_pantalla("ln("))
botonsen = tk.Button(casio,bg=color_boton, fg=color_texto, text="sen", width=8, height=2, command=lambda: agregar_a_pantalla("sin("))
botoncos = tk.Button(casio,bg=color_boton, fg=color_texto, text="cos", width=8, height=2, command=lambda: agregar_a_pantalla("cos("))
botontan = tk.Button(casio,bg=color_boton, fg=color_texto, text="tan", width=8, height=2, command=lambda: agregar_a_pantalla("tan("))
botoncot = tk.Button(casio,bg=color_boton, fg=color_texto, text="cot", width=8, height=2, command=lambda: agregar_a_pantalla("cot("))
botonsec = tk.Button(casio,bg=color_boton, fg=color_texto, text="sec", width=8, height=2, command=lambda: agregar_a_pantalla("sec("))
botoncsc = tk.Button(casio,bg=color_boton, fg=color_texto, text="csc", width=8, height=2, command=lambda: agregar_a_pantalla("csc("))
botonarcsen = tk.Button(casio,bg=color_boton, fg=color_texto, text="arcsen", width=8, height=2, command=lambda: agregar_a_pantalla("arcsin("))
botonarccos = tk.Button(casio,bg=color_boton, fg=color_texto, text="arccos", width=8, height=2, command=lambda: agregar_a_pantalla("arccos("))
botonarctan = tk.Button(casio,bg=color_boton, fg=color_texto, text="arctan", width=8, height=2, command=lambda: agregar_a_pantalla("arctan("))
botonintegral = tk.Button(casio,bg=color_boton, fg=color_texto,  text="∫", width=8, height=2, command=integrar)
botonrcu = tk.Button(casio,bg=color_boton, fg=color_texto, text="∛", width=8, height=2, command=lambda: agregar_a_pantalla("∛"))
botoncuad = tk.Button(casio,bg=color_boton, fg=color_texto, text="x²", width=8, height=2, command=lambda: agregar_a_pantalla("²"))
botoncubo = tk.Button(casio,bg=color_boton, fg=color_texto, text="x³", width=8, height=2, command=lambda: agregar_a_pantalla("³"))
botonpi = tk.Button(casio,bg=color_boton, fg=color_texto, text="π", width=8, height=2, command=lambda: agregar_a_pantalla("π"))
botoneuler = tk.Button(casio,bg=color_boton, fg=color_texto, text="e", width=8, height=2, command=lambda: agregar_a_pantalla("e"))
botoncoma = tk.Button(casio,bg=color_boton, fg=color_texto, text=",", width=8, height=2, command=lambda: agregar_a_pantalla(","))
botonsumatoria = tk.Button(casio,bg=color_boton, fg=color_texto, text="Σ", width=8, height=2, command=sumatoria)
botonl10 = tk.Button(casio,bg=color_boton, fg=color_texto, text="log", width=8, height=2, command=lambda: agregar_a_pantalla("lg("))
botonlbx = tk.Button(casio,bg=color_boton, fg=color_texto, text="logx(a)", width=8, height=2, command=lambda: agregar_a_pantalla("log("))
botonx = tk.Button(casio,bg=color_boton, fg=color_texto, text="x", width=8, height=2, command=lambda: agregar_a_pantalla("x"))
botony = tk.Button(casio,bg=color_boton, fg=color_texto, text="y", width=8, height=2, command=lambda: agregar_a_pantalla("y"))
boton1x = tk.Button(casio,bg=color_boton, fg=color_texto, text="x⁻¹", width=8, height=2, command=lambda: agregar_a_pantalla("⁻¹"))
botonraiz = tk.Button(casio,bg=color_boton, fg=color_texto, text="ⁿ√a", width=8, height=2, command=lambda: agregar_a_pantalla("√"))
boton_signo = tk.Button(casio,bg=color_boton, fg=color_texto, text="+/-", width=8, height=4, command=toggle_sign)
botonayuda = tk.Button(casio,bg=color_boton, fg=color_texto, text="ayuda",width = 8 , height = 2, command=mostrar_instrucciones)
botongrafica = tk.Button(casio,bg=color_boton, fg=color_texto, text="Graficar",width = 8 , height = 2, command=graficar_funcion)
botonoscuro = tk.Button(casio,bg=color_boton, fg=color_texto, text="cl/os",width = 8 , height = 2, command=lambda:modooscuro())
##botones de menus memorua y borrar
botonans = tk.Button(casio,bg=color_boton, fg=color_texto, text="Ans",width = 8 , height = 4, command=insert_answer)
botondel = tk.Button(casio,bg=color_boton, fg=color_texto, text="DEL",width = 8 , height = 4,command=delete_last)
botonac = tk.Button(casio,bg=color_boton, fg=color_texto, text="AC",width = 8 , height = 4,command=clear_all)
botoncerrar = tk.Button(casio,bg=color_boton, fg=color_texto, text="SALIR",width = 8 , height = 2,command=cerrar_aplicacion)
botonmenu = tk.Button(casio,bg=color_boton, fg=color_texto, text="MENU",width = 8 , height = 2, command=mostrar_menu )
botonm = tk.Button(casio,bg=color_boton, fg=color_texto, text="HISTORIAL",width = 8 , height = 2,command=lambda: mostrar_historial_calculadora())


#definimos donde van
ver.grid (row = 0, column = 0, columnspan=4)
isertar.grid (row = 1, column = 0, columnspan=4)
espacio2.grid (row =2, column = 0)
botonayuda.grid (row = 3, column = 0)
botonoscuro.grid (row = 3, column = 1)
botongrafica.grid (row = 9, column = 4)
botonmenu.grid (row = 3, column = 3)
botoncerrar.grid (row = 3, column = 4)
botonx.grid (row = 4, column = 0)
botony.grid (row = 4, column = 1)
botonpi.grid (row = 4, column = 2)
botoneuler.grid (row = 4, column = 3)
botonintegral.grid (row = 9, column = 2)
botonrcu.grid (row = 5, column = 0)
botonln.grid (row = 5, column = 1)
botonl10.grid (row = 5, column = 2)
botonlbx.grid (row = 5, column = 3)
boton1x.grid (row = 4, column = 4)
botonelev.grid (row = 6, column = 0)
botoncuad.grid (row = 6, column = 1)
botoncubo.grid (row = 6, column = 2)
botonraiz.grid (row = 6, column = 3)
botonrc.grid (row = 6, column = 4)
botonderivada.grid (row = 9, column = 1)
botonarcsen.grid (row = 7, column = 1)
botonarccos.grid (row = 7, column = 2)
botonarctan.grid (row = 7, column = 3)
botoncsc.grid (row = 7, column = 4)
botonsen.grid (row = 7, column = 0)
botoncos.grid (row = 8, column = 1)
botontan.grid (row = 8, column = 2)
botoncot.grid (row = 8, column = 3)
botonsec.grid (row = 8, column = 4)
botoncoma.grid (row = 5, column = 4)
botonpts1.grid (row = 8, column = 0)
botonpts2.grid (row = 9, column = 0)
botonsumatoria.grid (row = 9, column = 3)
botonm.grid (row = 3, column = 2)
espacio.grid (row = 10, column = 0)
boton7.grid (row = 11, column = 0)
boton8.grid (row = 11, column = 1)
boton9.grid (row = 11, column = 2)
botondel.grid (row = 11, column = 3)
botonac.grid (row = 11, column = 4)
boton4.grid (row = 12, column = 0)
boton5.grid (row = 12, column = 1)
boton6.grid (row = 12, column = 2)
botonmul.grid (row = 12, column = 3)
botondiv.grid (row = 12, column = 4)
boton1.grid (row = 13, column = 0)
boton2.grid (row = 13, column = 1)
boton3.grid (row = 13, column = 2)
botonsum.grid (row = 13, column = 3)
botonres.grid (row = 13, column = 4)
boton0.grid (row = 14, column = 0)
botonpunto.grid (row = 14, column = 1)
boton_signo.grid(row=14, column=2)
botonans.grid (row = 14, column = 3)
botonigual.grid(row=14, column=4)

# Iniciar el bucle principal
casio.mainloop()  