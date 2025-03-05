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
import diccionarios


## Pone el caracter en las entradas
def agregar_a_pantalla(entry, valor):
    actual = entry.get()
    entry.delete(0, tk.END)
    entry.insert(0, actual + str(valor))

#mostrar historial
##vapatk


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
        actualizar_pantalla("Error", entry)
        etiqueta.configure(text="Error en la operación")
        print(f"Error en calcular: {e}")  # Muestra el error en consola

# Función que obtiene la expresión ingresada y la convierte en una expresión simbólica válida
def obtener_expresion(texto):
    """Obtiene la expresión ingresada y la convierte en una expresión simbólica válida"""
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
        messagebox.showerror("Error", "Expresión inválida")
        return None, x

# Eliminar símbolos de derivada, integral, sumatoria y productoria
def limpiar_expresion(expresion):
    """Elimina los símbolos relacionados con derivadas, integrales, sumatorias y productorias"""
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
            # Realizamos la derivada con respecto a x
            derivada = sp.diff(expr, sp.symbols('x'))
            return f"Derivada: {derivada}"
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo calcular la derivada: {e}")
        return None

# Integración de la función con respecto a x
def integrar(expresion):
    try:
        expresion = limpiar_expresion(expresion)  # Limpiar la expresión de símbolos no válidos
        expr, variables = obtener_expresion(expresion)
        if expr:
            # Realizamos la integral con respecto a x
            integral = sp.integrate(expr, sp.symbols('x'))
            return f"Integral: {integral} + C"
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo calcular la integral: {e}")
        return None

# Sumatoria de la expresión de 1 a 10
def sumatoria(expresion):
    """Calcula la sumatoria de la función ingresada"""
    expr, x = obtener_expresion(expresion)  # Obtener la expresión simbólica de la entrada
    if expr:
        try:
            n = sp.Symbol('n')  # Definir la variable de la sumatoria
            # Evaluamos la sumatoria de n=1 a n=10 usando `subs` para reemplazar x por n
            suma_simbolica = sp.summation(expr.subs(x, n), (n, 1, 10))  # Sumatoria de n=1 a n=10
            suma_numerica = suma_simbolica.evalf()  # Evaluar la sumatoria numéricamente
            return f"Sumatoria: {suma_numerica}"  # Retornar la sumatoria numérica
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular la sumatoria: {e}")
            return None

# Productoria de la expresión de 1 a 10
def productoria(expresion):
    """Calcula la productoria de la función ingresada"""
    expr, x = obtener_expresion(expresion)
    if expr:
        try:
            n = sp.Symbol('n')
            # Evaluamos la productoria de n=1 a n=10
            producto = sp.product(expr.subs(x, n), (n, 1, 10))  # Productoria de n=1 a n=10
            return f"Productoria: {producto}"
        except Exception:
            messagebox.showerror("Error", "No se pudo calcular la productoria")
            return None

import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, lambdify

def graficar_funcion(entry):
    """Genera la gráfica de la función ingresada"""
    expr, variables = obtener_expresion(entry.get())  # Obtener la expresión y las variables

    if expr:
        try:
            # Obtener las variables libres de la expresión (las que no son constantes ni parámetros)
            free_vars = expr.free_symbols
            
            # Verificar si la expresión tiene una o dos variables
            if len(free_vars) == 1:
                # Graficar en 2D cuando solo hay una variable (como 'x')
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
                messagebox.showerror("Error", "La función debe tener una o dos variables.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo graficar la función: {e}")
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
            etiqueta.config(text=str(resultado_decimal))  # Mostrar como decimal
        else: 
            resultado_fraccion = sp.Rational(float(resultado_actual)) 
            etiqueta.config(text=str(resultado_fraccion))  # Mostrar como fracción
    except:
        messagebox.showerror("Error", "No se pudo convertir el resultado")

def convertir_grados_decimal(etiqueta):
    try:
        resultado_actual = etiqueta.cget("text") 

        match = re.match(r"(-?\d+)° (\d+)' ([\d.]+)''", resultado_actual)
        
        if match:
            #convertir a decimal
            grados = int(match.group(1))
            minutos = int(match.group(2))
            segundos = float(match.group(3))

            resultado_decimal = grados + (minutos / 60) + (segundos / 3600)
            etiqueta.config(text=str(round(resultado_decimal, 6)))  # Mostrar como decimal
            if conexionfb.current_user_id: 
                 operacion = f"conv_grados = {resultado_decimal}"
                 conexionfb.registrar_historial(conexionfb.current_user_id, 'grad-dec', operacion)
        else:
            #convertir a DMS
            resultado_decimal = float(resultado_actual)
            grados = int(resultado_decimal) 
            minutos_decimales = abs(resultado_decimal - grados) * 60 
            minutos = int(minutos_decimales) 
            segundos = round((minutos_decimales - minutos) * 60, 2) 

            resultado_grados = f"{grados}° {minutos}' {segundos}''"
            etiqueta.config(text=resultado_grados)  # Mostrar en formato DMS
            if conexionfb.current_user_id: 
                operacion = f"conv_grados = {resultado_grados}"  
                conexionfb.registrar_historial(conexionfb.current_user_id, 'dec-grad', operacion)

    except:
        messagebox.showerror("Error", "No se pudo convertir el resultado")

def cerrar_aplicacion(self):

        self.quit()  # Detener el bucle principal de Tkinter
        self.destroy()