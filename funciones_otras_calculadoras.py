import tkinter as tk
import conexionfb
import subprocess


##Calculadoras resistencias

from diccionarios import valores, tolerancias

def calcular_resistencia(banda1, banda2, banda3, banda4,etiqueta):
    try:
        # Obtener los valores de las bandas
        banda1_valor = valores[banda1.get()]
        banda2_valor = valores[banda2.get()]
        multiplicador = 10 ** valores[banda3.get()]
        tolerancia = tolerancias[banda4.get()]

        # Calcular la resistencia
        resistencia = (banda1_valor * 10 + banda2_valor) * multiplicador
        resultado = f"Resistencia: {resistencia} Ω {tolerancia}"
        etiqueta.configure(text=resultado)
        from conexionfb import current_user_id
        if current_user_id:  # Solo si hay un usuario logueado
            operacion = f"{operacion} = {resistencia}"
            conexionfb.registrar_historial(current_user_id, 'resistencia', operacion)

    except KeyError:
        return "Error en la selección"

def seleccionar_color(banda, opciones, button, colores):
    # Cambia el color según la selección
    color = opciones[(opciones.index(banda.get()) + 1) % len(opciones)]
    banda.set(color)
    button.configure(fg_color=colores[color], hover_color=colores[color])  # Evita el cambio de color en hover

## Calculadora unidades fisicas

from diccionarios import unidades

# Variables globales
categoria_var = "Longitud"
unidad_origen_var = "metros"
unidad_destino_var = "kilómetros"
valor_var = ""

# Función para actualizar las unidades según la categoría seleccionada
def actualizar_unidades(categoria):
    opciones = list(diccionarios.unidades[categoria].keys())

    # Asignamos las unidades por defecto
    unidad_origen_var = opciones[0]
    unidad_destino_var = opciones[1]

    return opciones, unidad_origen_var, unidad_destino_var

# Función para convertir unidades

from diccionarios import unidades


def convertir(unidades, categoria_var, unidad_origen_var, unidad_destino_var, valor, etiqueta_resultado):
    try:
        categoria = categoria_var.get()
        unidad_origen = unidad_origen_var.get()
        unidad_destino = unidad_destino_var.get()

        factor_origen = unidades[categoria][unidad_origen]
        factor_destino = unidades[categoria][unidad_destino]
        resultado = valor * (factor_destino / factor_origen)

        etiqueta_resultado.configure(text=f"{valor} {unidad_origen} = {resultado:.4f} {unidad_destino}")
    except ValueError:
        etiqueta_resultado.configure(text="Ingrese un número válido")



def clear_all(entry, etiqueta):
    entry.delete(0, ctk.END)
    etiqueta.configure(text="Resultado")

def delete_last(entry):
    current_text = entry.get()
    entry.delete(0, ctk.END)
    entry.insert(0, current_text[:-1])



## Calculadora Matrices

import sympy as sp
from tkinter import messagebox
import customtkinter as ctk

def crear_matriz(filas, columnas, frame, editable=True):
    from interfaces import Interfaz
    matriz = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            entrada = ctk.CTkEntry(frame, width=50, font=("Arial", 12))
            entrada.grid(row=i, column=j, padx=5, pady=5)
            if not editable:
                entrada.configure(state="readonly", fg_color="lightgray")  # Cambiar el color de fondo si no es editable
            fila.append(entrada)
        matriz.append(fila)
    return matriz

def obtener_matriz(matriz):
    try:
        return sp.Matrix([[sp.sympify(entry.get()) for entry in fila] for fila in matriz])
    except:
        messagebox.showerror("Error", "Valores inválidos en la matriz")
        return None

def mostrar_resultado(matriz_resultado):
    for widget in frame_resultado.winfo_children():
        widget.destroy()
    
    filas, columnas = matriz_resultado.shape
    resultado_entrada = crear_matriz(filas, columnas, frame_resultado, editable=False)
    
    for i in range(filas):
        for j in range(columnas):
            resultado_entrada[i][j].configure(state="normal")
            resultado_entrada[i][j].insert(0, str(matriz_resultado[i, j]))
            resultado_entrada[i][j].configure(state="readonly")

def calcular_operacion(operacion):
    matriz = obtener_matriz(matriz_entrada)
    if matriz is None:
        return
    
    try:
        if operacion == "Determinante":
            resultado = matriz.det()
            texto_resultado.configure(text=f"Det: {resultado}", font=("Arial", 14))
            return
        elif operacion == "Inversa":
            if matriz.det() == 0:
                raise ValueError("La matriz no es invertible.")
            resultado = matriz.inv()
        elif operacion == "Transpuesta":
            resultado = matriz.T
        elif operacion == "Multiplicar por Escalar":
            escalar = sp.sympify(entrada_escalar.get())
            resultado = matriz * escalar
        else:
            resultado = None
        
        if resultado is not None:
            mostrar_resultado(resultado)
    except Exception as e:
        messagebox.showerror("Error", f"Operación no válida: {e}")
        print (e)

# Función para cambiar el modo de la interfaz
movistar = "dark"  # Modo inicial
def cambiarmodo():
    global movistar
    if movistar == "dark":
        movistar = "light"  # Cambiar a "light"
        ctk.set_appearance_mode("light")  # Cambiar a modo claro
    else:
        movistar = "dark"  # Cambiar a "dark"
        ctk.set_appearance_mode("dark")

def generar_matriz():
    global matriz_entrada
    try:
        filas = min(5, int(entrada_filas.get()))  # Limitar a 5 filas
        columnas = min(5, int(entrada_columnas.get()))  # Limitar a 5 columnas
        if filas <= 0 or columnas <= 0:
            raise ValueError("Las filas y columnas deben ser mayores que 0.")
    except ValueError as e:
        messagebox.showerror("Error", f"Entrada no válida: {e}")
        return
    
    for widget in frame_matriz.winfo_children():  # Limpiar frame
        widget.destroy()
    matriz_entrada = crear_matriz(filas, columnas, frame_matriz)

