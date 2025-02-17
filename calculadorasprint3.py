import firebase_admin
from firebase_admin import credentials, db, auth
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import math

#variable id del usuario
current_user_id = None

# Inicializa la aplicación de Firebase
cred = credentials.Certificate("C:\\Users\\basti\\OneDrive\\Documentos\\programacion2024-2\\supercalculadoratilininsano-firebase-adminsdk-fbsvc-4b60c20dce.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://supercalculadoratilininsano-default-rtdb.firebaseio.com/'
})

#ventana inicio sesion

def iniciar_sesion():

    inicio = tk.Toplevel()
    inicio.title("Iniciar Sesión")
    inicio.geometry("388x260")

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
                registrar_historial(user.uid, 'login', 'Inicio de sesión exitoso')
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

#menu para graficas e inicio de sesion

def mostrar_menu():
    # Crear una nueva ventana para el menú
    menu_window = tk.Toplevel(casio)
    menu_window.title("Menú")
    menu_window.geometry("300x200")

    # Botón para iniciar sesión
    btn_iniciar_sesion = tk.Button(menu_window, text="Iniciar Sesión", command=iniciar_sesion)
    btn_iniciar_sesion.pack(pady=10)

    # Botón para graficar funciones (por ahora solo un placeholder)
    btn_graficar = tk.Button(menu_window, text="Graficar Funciones", command=lambda: messagebox.showinfo("Info", "Funcionalidad en desarrollo"))
    btn_graficar.pack(pady=10)

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
                tk.Label(historial_window, text=f'{timestamp} - {action}').pack()
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

#mostrar el historial de la calculadora

def mostrar_historial_calculadora():

    global current_user_id
    
    if current_user_id is None:
        respuesta = messagebox.askyesno("Iniciar Sesión", 
            "Necesitas iniciar sesión para ver tu historial. ¿Deseas iniciar sesión ahora?")
        if respuesta:
            iniciar_sesion()
    else:
        mostrar_historial(current_user_id)

##calculadora como tal

# Operaciones con 2 números
def calculadora1(op, num1, num2):
    if op == "+":
        return num1 + num2
    elif op == "-":
        return num1 - num2
    elif op == "*":
        return num1 * num2
    elif op == "/":
        return num1 / num2
    elif op == "%":
        return num1 * (num2 / 100)
    elif op == "^":
        return num1 ** num2
    elif op == "√":
        return  num2** (1 / num1)
    elif op == "logx":
        return math.log(num2) / math.log(num1)

# Operaciones con un solo número
def calculadoraun(op, num):
    if op == "2√":
        return num ** 0.5
    elif op == "∛":
        return num ** (1 / 3)
    elif op == "²":
        return num ** 2
    elif op == "³":
        return num ** 3
    elif op == "ln":
        return math.log(num)
    elif op == "log":
        return math.log10(num)
    elif op == "inverso":
        return num ** -1
    elif op == "sen":
        return math.sin(num)
    elif op == "cos":
        return math.cos(num)
    elif op == "tan":
        return math.tan(num)
    elif op == "cot":
        return 1 / math.tan(num)
    elif op == "sec":
        return 1 / math.cos(num)
    elif op == "csc":
        return 1 / math.sin(num)
    elif op == "arcsen":
        if num < 0 or num > 1:  
            raise ValueError("El valor debe estar entre 0 y 1 para arcsen.")
        return math.asin(num)
    elif op == "arccos":
        if num < 0 or num > 1: 
            raise ValueError("El valor debe estar entre 0 y 1 para arccos.")
        return math.acos(num)
    elif op == "arctan":
        return math.atan(num)
    elif op == "!":
        if num < 0 or int(num) != num: 
            raise ValueError("solo enteros positivos")
        return math.factorial(int(num))

# Funciones para actualizar la pantalla
def actualizar_pantalla(valor):
    isertar.delete(0, tk.END)  # Limpiar la pantalla
    isertar.insert(0, valor)  # Mostrar el nuevo valor

def agregar_a_pantalla(valor):
    actual = isertar.get()
    isertar.delete(0, tk.END)
    isertar.insert(0, actual + str(valor))

#calcular los valores de los botones

def guardar_valor_y_actualizar_op(signo):
    global num1, op
    valor_guardado = isertar.get()  # Obtener el valor de la entrada
    num1 = float(valor_guardado)  # Guardar el valor como número
    op = signo  # Guardar el signo de la operación
    ver.config(text=f"{num1} {op}")  # Actualizar la etiqueta
    isertar.delete(0, tk.END)  # Limpiar el Entry

#el igual para funciones que ingresan mas de 1 dato numerico ej: suma

def calcular():
    global num2
    valor_guardado = isertar.get()  # Obtener el valor de la entrada
    try:
        num2 = float(valor_guardado)  # Guardar el segundo número
        resultado = calculadora1(op, num1, num2)  # Realizar la operación
        # Mostrar la operación completa en la etiqueta
        ver.config(text=f"{num1} {op} {num2} = {resultado}")  # Actualizar la etiqueta
        actualizar_pantalla(resultado)  # Mostrar el resultado
        
        # Registrar el historial en Firebase
        if current_user_id:  # Si el usuario está logueado
            detalles = f"{num1} {op} {num2} = {resultado}"  # Registrar la operación con el resultado
            registrar_historial(current_user_id, 'calculadora', detalles)  # Registrar el historial de la operación

    except Exception as e:
        actualizar_pantalla("Error")  # Mostrar error en la pantalla
        ver.config(text="Error en la operación")  # Actualizar la etiqueta

#evalua funciones de 1 solo dato numerico sin necesidad de igual, ej : sen,cos

def calcular_funcion_unaria(funcion):
    valor_guardado = isertar.get()  # Obtener el valor de la entrada
    try:
        num = float(valor_guardado)  # Convertir a float
        resultado = calculadoraun(funcion, num)  # Calcular el resultado
        # Actualizar la pantalla y la etiqueta
        actualizar_pantalla(resultado)
        ver.config(text=f"{funcion}({num}) = {resultado}")

        # Registrar la operación en el historial
        if current_user_id:  # Solo si hay un usuario logueado
            operacion = f"{funcion}({num}) = {resultado}"
            registrar_historial(current_user_id, 'calculo', operacion)
    except Exception as e:
        actualizar_pantalla("Error")  # Mostrar error en la pantalla
        ver.config(text="Error en la operación")  # Actualizar la etiqueta

# Funciones para los botones AC, DEL y Ans
def clear_all():
    isertar.delete(0, tk.END)  # Limpiar el Entry
    ver.config(text="Valor guardado: ") 
    global num1, num2, op
    num1 = 0
    num2 = 0
    op = ""

def delete_last():
    current_text = isertar.get()
    isertar.delete(0, tk.END)
    isertar.insert(0, current_text[:-1])  # Eliminar el último carácter

def insert_answer():
    isertar.delete(0, tk.END)  # Limpiar el Entry
    isertar.insert(0, ver.cget("text").split('=')[-1].strip())  # Insertar el último resultado

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

#cerrar la app

def cerrar_aplicacion():
    casio.destroy()

# Inicializar variables
op = ""
num1 = 0
num2 = 0

# Tkinter
casio = tk.Tk()
casio.geometry("330x655")

# Definimos los botones
boton0 = tk.Button(casio, text="0", width=8, height=4, command=lambda: agregar_a_pantalla(0))
boton1 = tk.Button(casio, text="1", width=8, height=4, command=lambda: agregar_a_pantalla(1))
boton2 = tk.Button(casio, text="2", width=8, height=4, command=lambda: agregar_a_pantalla(2))
boton3 = tk.Button(casio, text="3", width=8, height=4, command=lambda: agregar_a_pantalla(3))
boton4 = tk.Button(casio, text="4", width=8, height=4, command=lambda: agregar_a_pantalla(4))
boton5 = tk.Button(casio, text="5", width=8, height=4, command=lambda: agregar_a_pantalla(5))
boton6 = tk.Button(casio, text="6", width=8, height=4, command=lambda: agregar_a_pantalla(6))
boton7 = tk.Button(casio, text="7", width=8, height=4, command=lambda: agregar_a_pantalla(7))
boton8 = tk.Button(casio, text="8", width=8, height=4, command=lambda: agregar_a_pantalla(8))
boton9 = tk.Button(casio, text="9", width=8, height=4, command=lambda: agregar_a_pantalla(9))
botonigual = tk.Button(casio, text="=", width=8, height=4, command=calcular)
botonpunto = tk.Button(casio, text=".", width=8, height=4,command=lambda: agregar_a_pantalla("."))
botonpts1 = tk.Button(casio, text="(", width=8, height=2,command=lambda: agregar_a_pantalla("("))
botonpts2 = tk.Button(casio, text=")", width=8, height=2,command=lambda: agregar_a_pantalla(")"))
botonsum = tk.Button(casio, text="+", width=8, height=4, command=lambda: guardar_valor_y_actualizar_op("+"))
botonres = tk.Button(casio, text="-", width=8, height=4, command=lambda: guardar_valor_y_actualizar_op("-"))
botonmul = tk.Button(casio, text="X", width=8, height=4, command=lambda: guardar_valor_y_actualizar_op("*"))
botondiv = tk.Button(casio, text="/", width=8, height=4, command=lambda: guardar_valor_y_actualizar_op("/"))
botonporcent = tk.Button(casio, text="%", width=8, height=2, command=lambda: guardar_valor_y_actualizar_op("%"))
botonelev = tk.Button(casio, text="^", width=8, height=2, command=lambda: guardar_valor_y_actualizar_op("^"))
botonrc = tk.Button(casio, text="√", width=8, height=2, command=lambda: calcular_funcion_unaria("2√"))
botonln = tk.Button(casio, text="ln", width=8, height=2, command=lambda: calcular_funcion_unaria("ln"))
botonsen = tk.Button(casio, text="sen", width=8, height=2, command=lambda: calcular_funcion_unaria("sen"))
botoncos = tk.Button(casio, text="cos", width=8, height=2, command=lambda: calcular_funcion_unaria("cos"))
botontan = tk.Button(casio, text="tan", width=8, height=2, command=lambda: calcular_funcion_unaria("tan"))
botoncot = tk.Button(casio, text="cot", width=8, height=2, command=lambda: calcular_funcion_unaria("cot"))
botonsec = tk.Button(casio, text="sec", width=8, height=2, command=lambda: calcular_funcion_unaria("sec"))
botoncsc = tk.Button(casio, text="csc", width=8, height=2, command=lambda: calcular_funcion_unaria("csc"))
botonarcsen = tk.Button(casio, text="arcsen", width=8, height=2, command=lambda: calcular_funcion_unaria("arcsen"))
botonarccos = tk.Button(casio, text="arccos", width=8, height=2, command=lambda: calcular_funcion_unaria("arccos"))
botonarctan = tk.Button(casio, text="arctan", width=8, height=2, command=lambda: calcular_funcion_unaria("arctan"))
botonfac = tk.Button(casio, text="x!", width=8, height=2, command=lambda: calcular_funcion_unaria("!"))
botonrcu = tk.Button(casio, text="∛", width=8, height=2, command=lambda: calcular_funcion_unaria("∛"))
botoncuad = tk.Button(casio, text="x²", width=8, height=2, command=lambda: calcular_funcion_unaria("²"))
botoncubo = tk.Button(casio, text="x³", width=8, height=2, command=lambda: calcular_funcion_unaria("³"))
botonpi = tk.Button(casio, text="π", width=8, height=2, command=lambda: agregar_a_pantalla(math.pi))
botoneuler = tk.Button(casio, text="e", width=8, height=2, command=lambda: agregar_a_pantalla(math.e))
botongrad = tk.Button(casio, text="°'", width=8, height=2, command=lambda: agregar_a_pantalla("°'"))
botonsd = tk.Button(casio, text="S⭤ D", width=8, height=2)
botonl10 = tk.Button(casio, text="log", width=8, height=2, command=lambda: calcular_funcion_unaria("log"))
botonlbx = tk.Button(casio, text="logx(a)", width=8, height=2, command=lambda: guardar_valor_y_actualizar_op("logx"))
botonx = tk.Button(casio, text="x", width=8, height=2, command=lambda: agregar_a_pantalla("x"))
botony = tk.Button(casio, text="y", width=8, height=2, command=lambda: agregar_a_pantalla("y"))
boton1x = tk.Button(casio, text="x⁻¹", width=8, height=2, command=lambda: calcular_funcion_unaria("inverso"))
botonraiz = tk.Button(casio, text="ⁿ√a", width=8, height=2, command=lambda: guardar_valor_y_actualizar_op("√"))
boton_signo = tk.Button(casio, text="+/-", width=8, height=4, command=toggle_sign)
#funciones complicadas
botonsumatoria = tk.Button(casio, text="Σ   ",width = 8 , height = 2)
botonderivada = tk.Button(casio, text="d/dx",width = 8 , height = 2)
botonintegral = tk.Button(casio, text="∫",width = 8 , height = 2)
##botones de menus memorua y borrar
botonans = tk.Button(casio, text="Ans",width = 8 , height = 4, command=insert_answer)
botondel = tk.Button(casio, text="DEL",width = 8 , height = 4,command=delete_last)
botonac = tk.Button(casio, text="AC",width = 8 , height = 4,command=clear_all)
botoncerrar = tk.Button(casio, text="SALIR",width = 8 , height = 2,command=cerrar_aplicacion)
botonmenu = tk.Button(casio, text="MENU",width = 8 , height = 2, command=mostrar_menu )
botonm = tk.Button(casio, text="HISTORIAL",width = 8 , height = 2,command=lambda: mostrar_historial_calculadora())
# Etiqueta para mostrar el valor guardado
ver = tk.Label(casio, text="Valor guardado: ")
isertar = tk.Entry (casio)
espacio = tk.Label (casio)
espacio2 = tk.Label (casio)

#definimos donde van
ver.grid (row = 0, column = 0, columnspan=4)
isertar.grid (row = 1, column = 0, columnspan=4)
espacio2.grid (row =2, column = 0)
botonsumatoria.grid (row = 3, column = 0)
botonintegral.grid (row = 3, column = 1)
botonderivada.grid (row = 3, column = 2)
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
botongrad.grid (row = 9, column = 0)
botonpts1.grid (row = 9, column = 1)
botonpts2.grid (row = 9, column = 2)
botonsd.grid (row = 9, column = 3)
botonm.grid (row = 9, column = 4)
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