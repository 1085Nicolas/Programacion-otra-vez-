import firebase_admin
from firebase_admin import credentials, db, auth
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import numpy as np
import sympy as sp
import re
import conexionfb
from conexionfb import iniciar_sesion
import subprocess

dicoperaciones = {
    "sen": "np.sin", "cos": "np.cos", "tan": "np.tan",
    "cot": "1/np.tan", "sec": "1/np.cos", "csc": "1/np.sin",
    "arcsn": "np.arcsin", "arccs": "np.arccos", "arctn": "np.arctan"
    , "²": "**2", "³": "**3", "^": "**", "⁻¹": "**-1",
    "ln": "np.log", "lg": "np.log10",
    "π": "np.pi", "e": "np.e","%": "/100"
}

def abrir_calculadora(nombre_archivo,cerave):
    cerave.destroy()  # Cierra la ventana actual
    subprocess.Popen(["python", nombre_archivo])  # Abre la otra calculadora

# Botones para abrir otras calculadoras

def mostrar_menu():
    # Crear una nueva ventana para el menú
    menu_window = tk.Toplevel(casio)
    menu_window.title("Menú")
    menu_window.geometry("300x300")
    menu_window.resizable(False, False)

    # Botón para iniciar sesión
    btn_iniciar_sesion = tk.Button(menu_window, text="Iniciar Sesión", command=iniciar_sesion)
    btn_iniciar_sesion.pack(pady=10)

    tk.Button(menu_window, text="Calculadora Grafica", command=lambda: abrir_calculadora("calculo.py",casio)).pack(pady=10)
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

    timestamp = datetime.utcnow().isoformat() + 'Z'
    action_id = db.reference(f'users/{user_id}/history').push().key
        
    db.reference(f'users/{user_id}/history/{action_id}').set({
        'action': details,  # Aquí se guarda la operación
        'timestamp': timestamp,
        'details': f'Operación realizada: {action}'
    })
    print(f'Historial registrado para el usuario {user_id}: {action}')

def usar_resultado(result):
    isertar.insert(tk.END, result) 

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

##calculadora como tal

def calcular(expresion):
    try:
        operacion = expresion

        for simbolo, reemplazo in dicoperaciones.items():
            expresion = expresion.replace(simbolo, reemplazo)

        # logaritmo base x de a
        expresion = re.sub(r"log\(([^,]+),([^)]+)\)", r"(np.log(\1) / np.log(\2))", expresion)

        # raiz x de a
        expresion = re.sub(r"(\d+)√(\d+)", r"\2**(1/\1)", expresion)

        #4 raiz cuadrada,cubica o factorial
        expresion = re.sub(r" √(\d+)", r"\1**(1/2)", expresion)
        expresion = re.sub(r"(\d+)!", r"sp.factorial(\1)", expresion)
        expresion = re.sub(r"∛(\d+)", r"\1**(1/3)", expresion)
        resultado = eval(expresion)
        actualizar_pantalla(resultado)
        ver.config(text=f"{resultado}")
        # Registrar la operación en el historial
        if conexionfb.current_user_id: 
            operacion = f"{operacion} = {resultado}"
            registrar_historial(conexionfb.current_user_id, 'calculo', operacion)
    except Exception as e:
        actualizar_pantalla("Error")  # Mostrar error en la pantalla
        ver.config(text="Error en la operación") 

# Funciones para actualizar la pantalla
def actualizar_pantalla(valor):
    isertar.delete(0, tk.END) 
    isertar.insert(0, valor)  

def agregar_a_pantalla(valor):
    actual = isertar.get()
    isertar.delete(0, tk.END)
    isertar.insert(0, actual + str(valor))

# Funciones para los botones AC, DEL y Ans
def clear_all():
    isertar.delete(0, tk.END)  
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
    caracter = event.char  

    if tecla == "Return": 
        calcular(isertar.get())
    elif tecla == "BackSpace": 
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

    for widget in casio.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg=color_boton, fg=color_texto)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=color_fondo, fg=color_texto)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=color_fondo, fg=color_texto, insertbackground=color_texto)       

def convertir_fraccion_decimal():
    try:
        resultado_actual = ver.cget("text") 

        if "/" in resultado_actual: 
            resultado_decimal = float(sp.sympify(resultado_actual)) 
            ver.config(text=str(resultado_decimal))  # Mostrar como decimal
        else: 
            resultado_fraccion = sp.Rational(float(resultado_actual)) 
            ver.config(text=str(resultado_fraccion))  # Mostrar como fracción
    except:
        messagebox.showerror("Error", "No se pudo convertir el resultado")

def convertir_grados_decimal():
    try:
        resultado_actual = ver.cget("text") 

        match = re.match(r"(-?\d+)° (\d+)' ([\d.]+)''", resultado_actual)
        
        if match:
            #convertir a decimal
            grados = int(match.group(1))
            minutos = int(match.group(2))
            segundos = float(match.group(3))

            resultado_decimal = grados + (minutos / 60) + (segundos / 3600)
            ver.config(text=str(round(resultado_decimal, 6)))  # Mostrar como decimal
            if conexionfb.current_user_id: 
                 operacion = f"conv_grados = {resultado_decimal}"
                 registrar_historial(conexionfb.current_user_id, 'grad-dec', operacion)
        else:
            #convertir a DMS
            resultado_decimal = float(resultado_actual)
            grados = int(resultado_decimal) 
            minutos_decimales = abs(resultado_decimal - grados) * 60 
            minutos = int(minutos_decimales) 
            segundos = round((minutos_decimales - minutos) * 60, 2) 

            resultado_grados = f"{grados}° {minutos}' {segundos}''"
            ver.config(text=resultado_grados)  # Mostrar en formato DMS
            if conexionfb.current_user_id: 
                operacion = f"conv_grados = {resultado_grados}"  
                registrar_historial(conexionfb.current_user_id, 'dec-grad', operacion)

    except:
        messagebox.showerror("Error", "No se pudo convertir el resultado")

def cerrar_aplicacion():
    casio.destroy()

# Tkinter
casio = tk.Tk()
casio.geometry("330x655")
casio.resizable(False, False)
casio.configure(bg=color_fondo)
casio.bind("<Key>", manejar_teclado)

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
botonporcent = tk.Button(casio,bg=color_boton, fg=color_texto, text="%", width=8, height=2, command=lambda: agregar_a_pantalla("%"))
botonelev = tk.Button(casio,bg=color_boton, fg=color_texto, text="^", width=8, height=2, command=lambda: agregar_a_pantalla("^"))
botonrc = tk.Button(casio,bg=color_boton, fg=color_texto, text="√", width=8, height=2, command=lambda: agregar_a_pantalla(" √"))
botonln = tk.Button(casio,bg=color_boton, fg=color_texto, text="ln", width=8, height=2, command=lambda: agregar_a_pantalla("ln"))
botonsen = tk.Button(casio,bg=color_boton, fg=color_texto, text="sen", width=8, height=2, command=lambda: agregar_a_pantalla("sen("))
botoncos = tk.Button(casio,bg=color_boton, fg=color_texto, text="cos", width=8, height=2, command=lambda: agregar_a_pantalla("cos("))
botontan = tk.Button(casio,bg=color_boton, fg=color_texto, text="tan", width=8, height=2, command=lambda: agregar_a_pantalla("tan("))
botoncot = tk.Button(casio,bg=color_boton, fg=color_texto, text="cot", width=8, height=2, command=lambda: agregar_a_pantalla("cot("))
botonsec = tk.Button(casio,bg=color_boton, fg=color_texto, text="sec", width=8, height=2, command=lambda: agregar_a_pantalla("sec("))
botoncsc = tk.Button(casio,bg=color_boton, fg=color_texto, text="csc", width=8, height=2, command=lambda: agregar_a_pantalla("csc("))
botonarcsen = tk.Button(casio,bg=color_boton, fg=color_texto, text="arcsen", width=8, height=2, command=lambda: agregar_a_pantalla("arcsn("))
botonarccos = tk.Button(casio,bg=color_boton, fg=color_texto, text="arccos", width=8, height=2, command=lambda: agregar_a_pantalla("arccs("))
botonarctan = tk.Button(casio,bg=color_boton, fg=color_texto, text="arctan", width=8, height=2, command=lambda: agregar_a_pantalla("arctn("))
botonfac = tk.Button(casio,bg=color_boton, fg=color_texto, text="x!", width=8, height=2, command=lambda: agregar_a_pantalla("!"))
botonrcu = tk.Button(casio,bg=color_boton, fg=color_texto, text="∛", width=8, height=2, command=lambda: agregar_a_pantalla("∛"))
botoncuad = tk.Button(casio,bg=color_boton, fg=color_texto, text="x²", width=8, height=2, command=lambda: agregar_a_pantalla("²"))
botoncubo = tk.Button(casio,bg=color_boton, fg=color_texto, text="x³", width=8, height=2, command=lambda: agregar_a_pantalla("³"))
botonpi = tk.Button(casio,bg=color_boton, fg=color_texto, text="π", width=8, height=2, command=lambda: agregar_a_pantalla("π"))
botoneuler = tk.Button(casio,bg=color_boton, fg=color_texto, text="e", width=8, height=2, command=lambda: agregar_a_pantalla("e"))
botoncoma = tk.Button(casio,bg=color_boton, fg=color_texto, text=",", width=8, height=2, command=lambda: agregar_a_pantalla(","))
botonsd = tk.Button(casio,bg=color_boton, fg=color_texto, text="S⭤ D", width=8, height=2, command=lambda : convertir_fraccion_decimal())
botonl10 = tk.Button(casio,bg=color_boton, fg=color_texto, text="log", width=8, height=2, command=lambda: agregar_a_pantalla("lg("))
botonlbx = tk.Button(casio,bg=color_boton, fg=color_texto, text="logx(a)", width=8, height=2, command=lambda: agregar_a_pantalla("log("))
botonx = tk.Button(casio,bg=color_boton, fg=color_texto, text="x", width=8, height=2, command=lambda: agregar_a_pantalla("x"))
botony = tk.Button(casio,bg=color_boton, fg=color_texto, text="y", width=8, height=2, command=lambda: agregar_a_pantalla("y"))
boton1x = tk.Button(casio,bg=color_boton, fg=color_texto, text="x⁻¹", width=8, height=2, command=lambda: agregar_a_pantalla("⁻¹"))
botonraiz = tk.Button(casio,bg=color_boton, fg=color_texto, text="ⁿ√a", width=8, height=2, command=lambda: agregar_a_pantalla("√"))
boton_signo = tk.Button(casio,bg=color_boton, fg=color_texto, text="+/-", width=8, height=4, command=toggle_sign)
botonayuda = tk.Button(casio,bg=color_boton, fg=color_texto, text="ayuda",width = 8 , height = 2)
botongrados = tk.Button(casio,bg=color_boton, fg=color_texto, text="°",width = 8 , height = 2, command=lambda : convertir_grados_decimal())
botonoscuro = tk.Button(casio,bg=color_boton, fg=color_texto, text="cl/os",width = 8 , height = 2, command=lambda:modooscuro())
botonans = tk.Button(casio,bg=color_boton, fg=color_texto, text="Ans",width = 8 , height = 4, command=insert_answer)
botondel = tk.Button(casio,bg=color_boton, fg=color_texto, text="DEL",width = 8 , height = 4,command=delete_last)
botonac = tk.Button(casio,bg=color_boton, fg=color_texto, text="AC",width = 8 , height = 4,command=clear_all)
botoncerrar = tk.Button(casio,bg=color_boton, fg=color_texto, text="SALIR",width = 8 , height = 2,command=cerrar_aplicacion)
botonmenu = tk.Button(casio,bg=color_boton, fg=color_texto, text="MENU",width = 8 , height = 2, command=mostrar_menu )
botonm = tk.Button(casio,bg=color_boton, fg=color_texto, text="HISTORIAL",width = 8 , height = 2,command=lambda: mostrar_historial_calculadora())

ver.grid (row = 0, column = 0, columnspan=4)
isertar.grid (row = 1, column = 0, columnspan=4)
espacio2.grid (row =2, column = 0)
botonayuda.grid (row = 3, column = 0)
botonoscuro.grid (row = 3, column = 1)
botongrados.grid (row = 9, column = 4)
botonmenu.grid (row = 3, column = 3)
botoncerrar.grid (row = 3, column = 4)
botonx.grid (row = 4, column = 0)
botony.grid (row = 4, column = 1)
botonpi.grid (row = 4, column = 2)
botoneuler.grid (row = 4, column = 3)
botonfac.grid (row = 4, column = 4)
botonrcu.grid (row = 5, column = 0)
botonln.grid (row = 5, column = 1)
botonl10.grid (row = 5, column = 2)
botonlbx.grid (row = 5, column = 3)
boton1x.grid (row = 5, column = 4)
botonelev.grid (row = 6, column = 0)
botoncuad.grid (row = 6, column = 1)
botoncubo.grid (row = 6, column = 2)
botonraiz.grid (row = 6, column = 3)
botonrc.grid (row = 6, column = 4)
botonporcent.grid (row = 7, column = 0)
botonarcsen.grid (row = 7, column = 1)
botonarccos.grid (row = 7, column = 2)
botonarctan.grid (row = 7, column = 3)
botoncsc.grid (row = 7, column = 4)
botonsen.grid (row = 8, column = 0)
botoncos.grid (row = 8, column = 1)
botontan.grid (row = 8, column = 2)
botoncot.grid (row = 8, column = 3)
botonsec.grid (row = 8, column = 4)
botoncoma.grid (row = 9, column = 0)
botonpts1.grid (row = 9, column = 1)
botonpts2.grid (row = 9, column = 2)
botonsd.grid (row = 9, column = 3)
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

casio.mainloop()  
