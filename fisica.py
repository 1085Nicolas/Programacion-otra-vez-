import tkinter as tk
from tkinter import messagebox
from firebase_admin import credentials, db, auth
import conexionfb
from conexionfb import iniciar_sesion
import subprocess
from datetime import datetime

# Crear la ventana principal
fisica = tk.Tk()
fisica.title("Conversor de Unidades")
fisica.geometry("345x510")
fisica.resizable(False, False)

# Diccionario con categorías y sus unidades correspondientes
unidades = {
    "Longitud": {"metros": 1, "kilómetros": 0.001, "centímetros": 100, "milímetros": 1000, "pulgadas": 39.3701, "pies": 3.28084},
    "Masa": {"gramos": 1, "kilogramos": 0.001, "miligramos": 1000, "toneladas": 0.000001, "libras": 0.00220462},
    "Tiempo": {"segundos": 1, "minutos": 1/60, "horas": 1/3600, "días": 1/86400},
    "Temperatura": {"Celsius": "C", "Fahrenheit": "F", "Kelvin": "K"},
    "Volumen": {"litros": 1, "mililitros": 1000, "galones": 0.264172, "metros cúbicos": 0.001},
    "Energía": {"julios": 1, "kilojulios": 0.001, "calorías": 0.239006, "kilocalorías": 0.000239},
    "Velocidad": {"m/s": 1, "km/h": 3.6, "mph": 2.23694},
    "Área": {"m²": 1, "cm²": 10000, "km²": 0.000001, "hectáreas": 0.0001},
    "Presión": {"Pascales": 1, "atmósferas": 0.00000986923, "barras": 0.00001, "PSI": 0.000145038},
    "Potencia": {"vatios": 1, "kilovatios": 0.001, "caballos de fuerza": 0.00134102},
    "Frecuencia": {"Hertz": 1, "Kilohertz": 0.001, "Megahertz": 0.000001, "Gigahertz": 0.000000001}
}

# Variables para seleccionar categorías y unidades
categoria_var = tk.StringVar(value="Longitud")
unidad_origen_var = tk.StringVar(value="metros")
unidad_destino_var = tk.StringVar(value="kilómetros")
valor_var = tk.StringVar()

# Función para actualizar las unidades según la categoría seleccionada
def actualizar_unidades(*args):
    categoria = categoria_var.get()
    opciones = list(unidades[categoria].keys())
    
    unidad_origen_var.set(opciones[0])
    unidad_destino_var.set(opciones[1])

    menu_origen["menu"].delete(0, "end")
    menu_destino["menu"].delete(0, "end")

    for unidad in opciones:
        menu_origen["menu"].add_command(label=unidad, command=tk._setit(unidad_origen_var, unidad))
        menu_destino["menu"].add_command(label=unidad, command=tk._setit(unidad_destino_var, unidad))

# Función para convertir unidades
def convertir():
    try:
        valor = float(valor_var.get())
        categoria = categoria_var.get()
        unidad_origen = unidad_origen_var.get()
        unidad_destino = unidad_destino_var.get()

        if categoria == "Temperatura":
            resultado = convertir_temperatura(valor, unidad_origen, unidad_destino)
        else:
            factor_origen = unidades[categoria][unidad_origen]
            factor_destino = unidades[categoria][unidad_destino]
            resultado = valor * (factor_destino / factor_origen)

        etiqueta_resultado.config(text=f"{valor} {unidad_origen} = {resultado:.4f} {unidad_destino}")
        if conexionfb.current_user_id:  # Solo si hay un usuario logueado
            operacion = f"{valor} {unidad_origen} = {resultado:.4f} {unidad_destino}"
            registrar_historial(conexionfb.current_user_id, 'fisica', operacion)

    except ValueError:
        etiqueta_resultado.config(text="Ingrese un número válido")

# Función especial para convertir temperatura
def convertir_temperatura(valor, origen, destino):
    if origen == destino:
        return valor
    if origen == "Celsius":
        return (valor * 9/5 + 32) if destino == "Fahrenheit" else (valor + 273.15)
    if origen == "Fahrenheit":
        return ((valor - 32) * 5/9) if destino == "Celsius" else ((valor - 32) * 5/9 + 273.15)
    if origen == "Kelvin":
        return (valor - 273.15) if destino == "Celsius" else ((valor - 273.15) * 9/5 + 32)

    if conexionfb.current_user_id:  # Solo si hay un usuario logueado
        operacion = f"{valor}{origen} = {destino}"
        registrar_historial(conexionfb.current_user_id, 'fisica', operacion)

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

def agregar_a_pantalla(valor):
    actual = entrada_valor.get()
    entrada_valor.delete(0, tk.END)
    entrada_valor.insert(0, actual + str(valor))

# Funciones para los botones AC, DEL y Ans
def clear_all():
    entrada_valor.delete(0, tk.END)  # Limpiar el Entry
    etiqueta_resultado.config(text=" ") 

def delete_last():
    current_text = entrada_valor.get()
    entrada_valor.delete(0, tk.END)
    entrada_valor.insert(0, current_text[:-1])  # Eliminar el último carácter

def insert_answer():
    agregar_a_pantalla(etiqueta_resultado.cget("text"))

def mostrar_instrucciones():
    mensaje = (
        "Para usar el modo de conversión de unidades:\n"
        "1. Escoge la magnitud que quieres convertir.\n"
        "2. Selecciona la unidad en la cual tienes el valor.\n"
        "3. Elige la unidad a la cual quieres convertir.\n"
        "4. Escribe el valor y presiona 'Enter'.\n"
    )

    messagebox.showinfo("Instrucciones", mensaje)

#cambio de signo
def toggle_sign():
    current_text = entrada_valor.get()  # Obtener el texto actual del Entry
    if current_text:  # Verifica que no esté vacío
        if current_text[0] == '-':
            entrada_valor.delete(0, tk.END)  # Limpiar el Entry
            entrada_valor.insert(0, current_text[1:])  # Elimina el signo negativo
        else:
            entrada_valor.delete(0, tk.END)  # Limpiar el Entry
            entrada_valor.insert(0, '-' + current_text)

def manejar_teclado(event):
    tecla = event.keysym  # Nombre de la tecla presionada
    caracter = event.char  # Caracter real ingresado (si existe)

    if tecla == "Return":  # Si es Enter, calcular resultado
        convertir()
    elif tecla == "BackSpace":  # Si es Backspace, borrar el último carácter
        delete_last()
    elif caracter.isprintable():  # Si es un carácter imprimible, agregarlo
        agregar_a_pantalla(caracter)
        return "break"  # Evitar que Tkinter lo agregue automáticamente

def mostrar_historial(user_id):
    historial_window = tk.Toplevel(fisica)
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

def abrir_calculadora(nombre_archivo,cerave):
    cerave.destroy()  # Cierra la ventana actual
    subprocess.Popen(["python", nombre_archivo])  # Abre la otra calculadora

# Botones para abrir otras calculadoras

def mostrar_menu():
    # Crear una nueva ventana para el menú
    menu_window = tk.Toplevel(fisica)
    menu_window.title("Menú")
    menu_window.geometry("300x200")
    menu_window.resizable(False, False)

    # Botón para iniciar sesión
    btn_iniciar_sesion = tk.Button(menu_window, text="Iniciar Sesión", command=iniciar_sesion)
    btn_iniciar_sesion.pack(pady=10)

    tk.Button(menu_window, text="Calculadora Cientifica", command=lambda: abrir_calculadora("calculadora_principal.py",fisica)).pack(pady=10)
    tk.Button(menu_window, text="Calculadora Grafica", command=lambda: abrir_calculadora("calculo.py",fisica)).pack(pady=10)
    tk.Button(menu_window, text="Calculadora de Resistencias", command=lambda: abrir_calculadora("resistencias.py",fisica)).pack(pady=10)
    tk.Button(menu_window, text="matrices", command=lambda: abrir_calculadora("matrices.py",fisica)).pack(pady=10)

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
    
    fisica.configure(bg=color_fondo)
    # Actualizar los botones existentes
    for widget in fisica.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg=color_boton, fg=color_texto)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=color_fondo, fg=color_texto)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=color_fondo, fg=color_texto, insertbackground=color_texto)
    
def cerrar_aplicacion():
    fisica.destroy()

color_fondo = "white"
color_texto = "black"
color_boton = "lightgray"

fisica.bind("<Key>", manejar_teclado) 

magnitud = tk.Label(fisica, text="magnitud")
inicial = tk.Label(fisica, text="unidad")
final = tk.Label(fisica, text="unidad 2")
etiqueta_resultado = tk.Label(fisica, text="Resultado: ",font=("Arial",12))
espacio = tk.Label(fisica)
espacio2 = tk.Label(fisica)

menu_categoria = tk.OptionMenu(fisica, categoria_var, *unidades.keys(), command=actualizar_unidades)
menu_origen = tk.OptionMenu(fisica, unidad_origen_var, *unidades["Longitud"].keys())
menu_destino = tk.OptionMenu(fisica, unidad_destino_var, *unidades["Longitud"].keys())
entrada_valor = tk.Entry(fisica, textvariable=valor_var,font=("Arial",16))
menu_categoria.config(width=7, font=("Arial", 8))
menu_origen.config(width=7, font=("Arial", 8))
menu_destino.config(width=7, font=("Arial", 8))

boton0 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="0", width=11, height=4, command=lambda: agregar_a_pantalla(0))
boton1 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="1", width=11, height=4, command=lambda: agregar_a_pantalla(1))
boton2 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="2", width=11, height=4, command=lambda: agregar_a_pantalla(2))
boton3 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="3", width=11, height=4, command=lambda: agregar_a_pantalla(3))
boton4 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="4", width=11, height=4, command=lambda: agregar_a_pantalla(4))
boton5 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="5", width=11, height=4, command=lambda: agregar_a_pantalla(5))
boton6 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="6", width=11, height=4, command=lambda: agregar_a_pantalla(6))
boton7 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="7", width=11, height=4, command=lambda: agregar_a_pantalla(7))
boton8 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="8", width=11, height=4, command=lambda: agregar_a_pantalla(8))
boton9 = tk.Button(fisica, bg=color_boton, fg=color_texto, text="9", width=11, height=4, command=lambda: agregar_a_pantalla(9))

botonans = tk.Button(fisica, bg=color_boton, fg=color_texto, text="Ans", width=11, height=4, command=insert_answer)
botondel = tk.Button(fisica, bg=color_boton, fg=color_texto, text="DEL", width=11, height=4, command=delete_last)
botonac = tk.Button(fisica, bg=color_boton, fg=color_texto, text="AC", width=11, height=4, command=clear_all)
botoncerrar = tk.Button(fisica, bg=color_boton, fg=color_texto, text="SALIR", width=11, height=2, command=cerrar_aplicacion)
botonmenu = tk.Button(fisica, bg=color_boton, fg=color_texto, text="MENU", width=11, height=2, command=mostrar_menu)
botonm = tk.Button(fisica, bg=color_boton, fg=color_texto, text="HISTORIAL", width=11, height=4, command=lambda: mostrar_historial_calculadora())

boton_signo = tk.Button(fisica, bg=color_boton, fg=color_texto, text="+/-", width=11, height=4, command=toggle_sign)
botonpunto = tk.Button(fisica, bg=color_boton, fg=color_texto, text=".", width=11, height=4, command=lambda: agregar_a_pantalla("."))
botonayuda = tk.Button(fisica, bg=color_boton, fg=color_texto, text="ayuda", width=11, height=2,command=mostrar_instrucciones)
boton_igual = tk.Button(fisica, bg=color_boton, fg=color_texto, text="=", width=11, height=4, command=convertir)
botonoscuro = tk.Button(fisica, bg=color_boton, fg=color_texto, text="cl/os", width=11, height=2, command=lambda: modooscuro())



etiqueta_resultado.grid (row=0, column=0, columnspan=3)
entrada_valor.grid (row=1, column=0, columnspan=3)
espacio.grid (row=2, column=0)
magnitud.grid (row=3,column=1)
menu_categoria.grid (row=3,column=2)
inicial.grid (row=4,column=1)
menu_origen.grid (row=4,column=2)
final.grid (row=5,column=1)
menu_destino.grid (row=5,column=2)
espacio2.grid (row=6,column=0)
botonoscuro.grid(row=7, column=0)
botonayuda.grid(row=7, column=1)
botonmenu.grid(row=7, column=2)
botoncerrar.grid(row=7, column=3)
boton7.grid(row=8, column=0)
boton8.grid(row=8, column=1)
boton9.grid(row=8, column=2)
botonm.grid(row=8, column=3)
boton4.grid(row=9, column=0)
boton5.grid(row=9, column=1)
boton6.grid(row=9, column=2)
botonac.grid(row=9, column=3)
boton1.grid(row=10, column=0)
boton2.grid(row=10, column=1)
boton3.grid(row=10, column=2)
botondel.grid(row=10, column=3)
boton0.grid(row=11, column=0)
botonpunto.grid(row=11, column=1)
boton_signo.grid(row=11, column=2)
boton_igual.grid(row=11, column=3)



# Vincular el cambio de categoría con la actualización de unidades
categoria_var.trace_add("write", actualizar_unidades)

fisica.mainloop()
