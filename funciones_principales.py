import tkinter as tk
import numpy as np
import sympy as sp
import re
import conexionfb
import diccionarios
from CTkMessagebox import CTkMessagebox
import sys


## Pone el caracter en las entradas
def agregar_a_pantalla(entry, valor):
    actual = entry.get()
    entry.delete(0, tk.END)
    entry.insert(0, actual + str(valor))

def manejar_teclado(event, entry, etiqueta):
    tecla = event.keysym  # Obtener la tecla presionada
    caracter = event.char

    if tecla == "Return":  # Si se presiona Enter, calcular
        funciones_principales.calcular(entry.get(), etiqueta, entry)
        return "break"  # Evitar salto de línea en Entry

    elif tecla == "BackSpace":  # Borrar último carácter
        funciones_principales.delete_last(entry)
        return "break"  # Evitar comportamiento predeterminado

    elif caracter.isprintable():  # Agregar solo caracteres imprimibles
        entry.insert("insert", caracter)  # Insertar manualmente
        return "break"  # Evitar doble inserción

    return None

## Calculadora Principal

#funcion para dar resultado
def calcular(expresion, etiqueta, entry):
    print("Expresión ingresada:", expresion)  # Para depuración
    from conexionfb import current_user_id
    try:
        # Identificar el tipo de operación
        if "d/dx" in expresion or "d/dy" in expresion or "d/dz" in expresion:
            resultado = derivar(expresion)
            etiqueta.configure(text=f"{resultado}")
        elif "lim(" in expresion:
            resultado = limites(expresion)
            etiqueta.configure(text=f"{resultado}")
        elif "∫" in expresion:  # Integral ∫
            resultado = integrar(expresion)
            etiqueta.configure(text=f"{resultado}")
        elif "Σ" in expresion:  # Sumatoria Σ
            resultado = sumatoria(expresion)
            etiqueta.configure(text=f"{resultado}")
        elif "Π" in expresion:  # Productoria Π
            resultado = productoria(expresion)
            etiqueta.configure(text=f"{resultado}")
        else:
            operacion_original = expresion  # Guarda la operación original

            # Reemplazar operaciones especiales
            for simbolo, reemplazo in diccionarios.opernp.items():
                expresion = expresion.replace(simbolo, reemplazo)

            # logaritmo base x de a
            expresion = re.sub(r"log\((\d+),(\d+)\)", r"(np.log(\2) / np.log(\1))", expresion)

            # Raíz n-ésima y factorial
            expresion = re.sub(r"(\d+)√(\d+)", r"\2**(1/\1)", expresion)
            expresion = re.sub(r" √(\d+)", r"\1**(1/2)", expresion)
            expresion = re.sub(r"(\d+)!", r"sp.factorial(\1)", expresion)
            expresion = re.sub(r"∛(\d+)", r"\1**(1/3)", expresion)

            print("Expresión evaluada:", expresion)  # Para verificar qué se evalúa

            resultado = eval(expresion, {"np": np, "sp": sp})  # Evalúa con seguridad

            actualizar_pantalla(resultado, entry)
            etiqueta.configure(text=f"{resultado}")  # Uso correcto de configure

            # Registrar la operación en el historial
            if current_user_id: 
                operacion = f"{operacion_original} = {resultado}"
                conexionfb.registrar_historial(conexionfb.current_user_id, 'calculo', operacion)

    except Exception as e:
        etiqueta.configure(text="Error en la operación")
        CTkMessagebox(title="Error", message=f"No se pudo calcular: {e}", icon="cancel")
        return None

# Función que obtiene la expresión ingresada y la convierte en una expresión simbólica válida
def obtener_expresion(texto):

    x = sp.Symbol('x')  # Solo consideramos la variable 'x'
    
    # Convertir los operadores usando diccionario opersp
    for simbolo, reemplazo in diccionarios.opersp.items():
        if isinstance(reemplazo, str):
            texto = texto.replace(simbolo, reemplazo)
    
    # Reemplazos para logaritmos y raíces
    texto = re.sub(r"log\(([^,]+),([^)]+)\)", r"(sp.log(\1) / sp.log(\2))", texto)
    texto = re.sub(r"(\d+)√(\d+)", r"\2**(1/\1)", texto)  # Raíz n-ésima
    texto = re.sub(r"√(\d+)", r"\1**(1/2)", texto)  # Raíz cuadrada
    texto = re.sub(r"∛(\d+)", r"\1**(1/3)", texto)  # Raíz cúbica
    texto = re.sub(r"(\d+)!", r"sp.factorial(\1)", texto)  # Factorial
    
    try:
        expr = sp.sympify(texto, locals={"sp": sp, "x": x})  # Convertir a expresión simbólica
        return expr, x
    except Exception:
        CTkMessagebox(title="Error",message="Expresión inválida",icon="cancel")
        return None, x

# Eliminar símbolos de derivada, integral, sumatoria y productoria
def limpiar_expresion(expresion):
 
    # Eliminamos los símbolos de derivada (d/dx, d/dy, d/dz)
    expresion = expresion.replace("d/dx", "").replace("d/dy", "").replace("d/dz", "").strip()
    
    # Eliminamos el símbolo de la integral (∫)
    expresion = expresion.replace("∫", "").strip()
    
    # Eliminamos la notación de sumatoria Σ y productoria Π
    expresion = re.sub(r"Σ\(([^)]+)\)", r"\1", expresion)
    expresion = re.sub(r"Π\(([^)]+)\)", r"\1", expresion)
    
    # Eliminamos el símbolo de límite (lim)
    expresion = re.sub(r"lim\(([^)]+)\)", r"\1", expresion)
    
    return expresion

# Derivada de la función con respecto a x
def derivar(expresion):
    try:
        expresion = limpiar_expresion(expresion)  # Limpiar la expresión de símbolos no válidos
        expr, variables = obtener_expresion(expresion)
        if expr:
            derivada = sp.diff(expr, sp.symbols('x'))
            return f"Derivada: {derivada}"
    except Exception as e:
        CTkMessagebox(title="Error", message=f"No se pudo calcular la derivada: {e}", icon="cancel")
        return None

# Integración de la función con respecto a x
def integrar(expresion):
    try:
        expresion = limpiar_expresion(expresion)
        expr, variables = obtener_expresion(expresion)
        if expr:
            integral = sp.integrate(expr, sp.symbols('x'))
            return f"Integral: {integral} + C"
    except Exception as e:
        CTkMessagebox(title="Error", message=f"No se pudo calcular la integral: {e}", icon="cancel")
        return None

def sumatoria(expresion):
    expr, x = obtener_expresion(expresion)  # Obtener la expresión simbólica con x como variable
    if expr:
        try:
            # Evaluar la sumatoria directamente con valores numéricos
            suma_numerica = sum(expr.subs(x, n).evalf() for n in range(1, 11))
            
            return f"Sumatoria: {suma_numerica:.6f}"
        except Exception as e:
            CTkMessagebox(title="Error", message=f"No se pudo calcular la sumatoria: {e}", icon="cancel")
            return None


def productoria(expresion):
    expr, x = obtener_expresion(expresion)
    if expr:
        try:
            n = sp.Symbol('n')
            producto_simbolico = sp.product(expr.subs(x, n), (n, 1, 10))  # Productoria de n=1 a n=10
            producto_numerico = producto_simbolico.evalf()  # Evaluar la productoria numéricamente
            return f"Productoria: {producto_numerico:.6f}"  # Retornar la productoria numérica con 6 decimales
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular la productoria: {e}",icon="cancel")
            return None


import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, lambdify

def graficar_funcion(entry):
    
    from conexionfb import current_user_id
   
    expr, variables = obtener_expresion(entry.get())  # Obtener la expresión y las variables

    if expr:
        try:
            # Obtener las variables libres de la expresión (las que no son constantes ni parámetros)
            free_vars = expr.free_symbols
            
            # Verificar si la expresión tiene una o dos variables
            if len(free_vars) == 1:
                # Graficar en 2D cuando solo hay una variable (como 'x')
                if current_user_id: 
                    operacion = f"{entry.get()}"
                    conexionfb.registrar_historial(conexionfb.current_user_id, 'grafica', operacion)

                funcion_lambda = lambdify(free_vars, expr, 'numpy')  # Convertir SymPy a NumPy
                x_vals = np.linspace(-10, 10, 400)
                
                # Si solo hay una variable, graficar en 2D
                y_vals = funcion_lambda(x_vals)
                plt.plot(x_vals, y_vals, label=f"y = {expr}", color='r')
                plt.axhline(0, color='black', linewidth=0.5)
                plt.axvline(0, color='black', linewidth=0.5)
                plt.grid()
                plt.legend()
                plt.xlabel("Eje X") 
                plt.ylabel("Eje Y")
                plt.title(f"Gráfico de la Función {expr}")
                plt.show()


            elif len(free_vars) == 2:
                # Graficar en 3D cuando hay dos variables (como 'x' y 'y')
                if current_user_id: 
                    operacion = f"{entry.get()}"
                    conexionfb.registrar_historial(conexionfb.current_user_id, 'grafica', operacion)
                    
                funcion_lambda = lambdify(free_vars, expr, 'numpy')  # Convertir SymPy a NumPy
                x_vals = np.linspace(-10, 10, 400)
                y_vals = np.linspace(-10, 10, 400)
                X, Y = np.meshgrid(x_vals, y_vals)

                # Evaluamos Z como una función de X y Y
                Z = funcion_lambda(X, Y)

                # Crear la gráfica en 3D
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                ax.plot_surface(X, Y, Z, cmap='viridis')

                # Etiquetas y título
                ax.set_xlabel('Eje X')
                ax.set_ylabel('Eje Y')
                ax.set_zlabel('Eje Z')
                ax.set_title(f"Gráfico 3D de {expr}")

                plt.show()
            else:
                CTkMessagebox(tittle="Error",message= "La función debe tener una o dos variables.",icon="cancel")

        except Exception as e:
            CTkMessagebox(title="Error",message=f"No se pudo graficar la función: {e}",icon="cancel")
            print (e)



# Funciones para actualizar la pantalla
def actualizar_pantalla(valor,entrada):
    entrada.delete(0, tk.END) 
    entrada.insert(0, valor)  

# Funciones para los botones AC, DEL y Ans
def clear_all(entrada,etiqueta):
    entrada.delete(0, tk.END)  
    etiqueta.configure(text=" ")

def delete_last(entrada):
    current_text = entrada.get()
    entrada.delete(0, tk.END)
    entrada.insert(0, current_text[:-1])  # Eliminar el último carácter

def insert_answer(entry,etiqueta):
    agregar_a_pantalla(entry,etiqueta.cget("text"))

#cambio de signo
def toggle_sign(entrada):
    current_text = entrada.get()  # Obtener el texto actual del Entry
    if current_text:  # Verifica que no esté vacío
        if current_text[0] == '-':
            entrada.delete(0, tk.END)  # Limpiar el Entry
            entrada.insert(0, current_text[1:])  # Elimina el signo negativo
        else:
            entrada.delete(0, tk.END)  # Limpiar el Entry
            entrada.insert(0, '-' + current_text)



##modo oscuro     

def convertir_fraccion_decimal(etiqueta):
    try:
        resultado_actual = etiqueta.cget("text") 

        if "/" in resultado_actual: 
            resultado_decimal = float(sp.sympify(resultado_actual)) 
            etiqueta.configure(text=str(resultado_decimal))  # Mostrar como decimal
        else: 
            resultado_fraccion = sp.Rational(float(resultado_actual)) 
            etiqueta.configure(text=str(resultado_fraccion))  # Mostrar como fracción
    except:
        CTkMessagebox(title="Error",message="No se pudo convertir el resultado",icon="cancel")

def convertir_grados_decimal(etiqueta):
    try:
        resultado_actual = etiqueta.cget("text").strip()  # Quitar espacios en blanco
        
        # Intentar reconocer el formato grados, minutos y segundos
        match = re.match(r"(-?\d+)°\s*(\d+)'?\s*([\d.]+)''?", resultado_actual)
        
        if match:
            # Convertir a decimal
            grados = int(match.group(1))
            minutos = int(match.group(2))
            segundos = float(match.group(3))

            resultado_decimal = grados + (minutos / 60) + (segundos / 3600)
            etiqueta.configure(text=str(round(resultado_decimal, 6)))  # Mostrar como decimal
            
            if conexionfb.current_user_id: 
                operacion = f"conv_grados = {resultado_decimal}"
                conexionfb.registrar_historial(conexionfb.current_user_id, 'grad-dec', operacion)
        
        else:
            # Convertir a DMS
            try:
                resultado_decimal = float(resultado_actual)
            except ValueError:
                CTkMessagebox(title="Error",message="Formato no válido para conversión",icon="cancel")
                return

            grados = int(resultado_decimal)
            minutos_decimales = abs(resultado_decimal - grados) * 60
            minutos = int(minutos_decimales)
            segundos = round((minutos_decimales - minutos) * 60, 2)

            resultado_grados = f"{grados}° {minutos}' {segundos}''"
            etiqueta.configure(text=resultado_grados)  # Mostrar en formato DMS
            
            if conexionfb.current_user_id: 
                operacion = f"conv_grados = {resultado_grados}"
                conexionfb.registrar_historial(conexionfb.current_user_id, 'dec-grad', operacion)

    except Exception as e:
        CTkMessagebox(title="Error",message=f"No se pudo convertir el resultado: {str(e)}",icon="cancel")


def cerrar_aplicacion():
    sys.exit()

def informacion():
    CTkMessagebox(title="Info", 
        message=(
            "Creado y Desarrollado por Manuel Santiago Bastidas Gaona\n"
            "y Nicolas Palacios Quimbayo para programación de computadores"
        )
    )
