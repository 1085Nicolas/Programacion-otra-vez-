
import conexionfb


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

import sympy as sp
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk

# Función para crear matriz de entrada
def crear_matriz(filas, columnas, frame, editable=True):
    matriz = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            entrada = ctk.CTkEntry(frame, width=50, font=("Arial", 12))
            entrada.grid(row=i, column=j, padx=5, pady=5)
            if not editable:
                entrada.configure(state="readonly", fg_color="lightgray")
            fila.append(entrada)
        matriz.append(fila)
    return matriz

# Función para obtener la matriz de las entradas
def obtener_matriz(matriz_entrada):
    try:
        return sp.Matrix([[sp.sympify(entry.get()) for entry in fila] for fila in matriz_entrada])
    except:
        CTkMessagebox(title="Error", message="Valores inválidos en la matriz", icon="cancel")
        return None

# Función para mostrar el resultado
def mostrar_resultado(matriz_resultado, frame_resultado):
    for widget in frame_resultado.winfo_children():
        widget.destroy()

    filas, columnas = matriz_resultado.shape
    resultado_entrada = crear_matriz(filas, columnas, frame_resultado, editable=False)

    for i in range(filas):
        for j in range(columnas):
            resultado_entrada[i][j].configure(state="normal")
            resultado_entrada[i][j].insert(0, str(matriz_resultado[i, j]))
            resultado_entrada[i][j].configure(state="readonly")

# Función para realizar operaciones con la matriz
def calcular_operacion(operacion, interfaz):
    matriz = obtener_matriz(interfaz.matriz_entrada)
    if matriz is None:
        return
    
    try:
        if operacion == "Determinante":
            resultado = matriz.det()
            interfaz.texto_resultado.configure(text=f"Det: {resultado}")
            return
        elif operacion == "Inversa":
            if matriz.det() == 0:
                raise ValueError("La matriz no es invertible.")
            resultado = matriz.inv()
        elif operacion == "Transpuesta":
            resultado = matriz.T
        elif operacion == "Multiplicar por Escalar":
            escalar = sp.sympify(interfaz.entrada_escalar.get()) if interfaz.entrada_escalar.get() else 1
            resultado = matriz * escalar
        else:
            resultado = None

        if resultado is not None:
            mostrar_resultado(resultado, interfaz.frame_resultado)
    except Exception as e:
        CTkMessagebox(title="Error", message=f"Operación no válida: {e}", icon="cancel")

# Función para cambiar el modo de la interfaz
modo_actual = "dark"
def cambiarmodo():
    global modo_actual
    modo_actual = "light" if modo_actual == "dark" else "dark"
    ctk.set_appearance_mode(modo_actual)

# Función para generar la matriz en la interfaz
def generar_matriz(interfaz):
    try:
        filas = min(5, int(interfaz.entrada_filas.get()))
        columnas = min(5, int(interfaz.entrada_columnas.get()))
        if filas <= 0 or columnas <= 0:
            raise ValueError("Las filas y columnas deben ser mayores que 0.")
    except ValueError as e:
        CTkMessagebox(title="Error", message=f"Entrada no válida: {e}", icon="cancel")
        return

    for widget in interfaz.frame_matriz.winfo_children():
        widget.destroy()

    interfaz.matriz_entrada = crear_matriz(filas, columnas, interfaz.frame_matriz)
