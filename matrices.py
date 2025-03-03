import tkinter as tk
from tkinter import messagebox
import sympy as sp
import subprocess
import conexionfb
from conexionfb import iniciar_sesion

def crear_matriz(filas, columnas, frame, editable=True):
    #matriz grafica
    matriz = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            entrada = tk.Entry(frame, width=7, font=("Arial", 12))
            entrada.grid(row=i, column=j, padx=5, pady=5)
            if not editable:
                entrada.config(state="readonly", disabledbackground="white")
            fila.append(entrada)
        matriz.append(fila)
    return matriz

def obtener_matriz(matriz):
    #convierte matriz a sp
    try:
        return sp.Matrix([[sp.sympify(entry.get()) for entry in fila] for fila in matriz])
    except:
        messagebox.showerror("Error", "Valores inválidos en la matriz")
        return None

def mostrar_resultado(matriz_resultado):
   #matriz resuelta
    for widget in frame_resultado.winfo_children():
        widget.destroy()
    
    filas, columnas = matriz_resultado.shape
    resultado_entrada = crear_matriz(filas, columnas, frame_resultado, editable=False)
    
    for i in range(filas):
        for j in range(columnas):
            resultado_entrada[i][j].config(state="normal")
            resultado_entrada[i][j].insert(0, str(matriz_resultado[i, j]))
            resultado_entrada[i][j].config(state="readonly")

def calcular_operacion(operacion):
    matriz = obtener_matriz(matriz_entrada)
    if matriz is None:
        return
    
    try:
        if operacion == "Determinante":
            resultado = matriz.det()
            texto_resultado.config(text=f"Det: {resultado}", font=("Arial", 14))
            return
        elif operacion == "Inversa":
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

def abrir_calculadora(nombre_archivo,cerave):
    cerave.destroy()
    subprocess.Popen(["python", nombre_archivo]) 

def mostrar_menu():
    menu_window = tk.Toplevel(tk_matrices)
    menu_window.title("Menú")
    menu_window.geometry("300x200")
    menu_window.resizable(False, False)

    btn_iniciar_sesion = tk.Button(menu_window, text="Iniciar Sesión", command=iniciar_sesion)
    btn_iniciar_sesion.pack(pady=10)

    tk.Button(menu_window, text="Calculadora Científica", command=lambda: abrir_calculadora("calculadora_principal.py",tk_matrices)).pack(pady=10)
    tk.Button(menu_window, text="Calculadora Grafica", command=lambda: abrir_calculadora("calculo.py",tk_matrices)).pack(pady=10)
    tk.Button(menu_window, text="Conversión de Unidades", command=lambda: abrir_calculadora("fisica.py",tk_matrices)).pack(pady=10)
    tk.Button(menu_window, text="Calculadora Resistencias", command=lambda: abrir_calculadora("resistencias.py",tk_matrices)).pack(pady=10)

# Configuración de la interfaz
tk_matrices = tk.Tk()
tk_matrices.title("Calculadora de Matrices")

frame_entrada = tk.Frame(tk_matrices)
frame_entrada.grid(row=0, column=0, columnspan=2)

tk.Label(frame_entrada, text="Número de Filas:").grid(row=0, column=0)
tk.Label(frame_entrada, text="Número de Columnas:").grid(row=1, column=0)

entrada_filas = tk.Entry(frame_entrada, width=5)
entrada_filas.grid(row=0, column=1)
entrada_columnas = tk.Entry(frame_entrada, width=5)
entrada_columnas.grid(row=1, column=1)

def generar_matriz():
    global matriz_entrada
    filas = int(entrada_filas.get())
    columnas = int(entrada_columnas.get())
    for widget in frame_matriz.winfo_children():  # Limpiar frame
        widget.destroy()
    matriz_entrada = crear_matriz(filas, columnas, frame_matriz)

boton_generar = tk.Button(frame_entrada, text="Generar Matriz", command=generar_matriz)
boton_generar.grid(row=2, column=0, columnspan=2)

frame_matriz = tk.Frame(tk_matrices)
frame_matriz.grid(row=1, column=0, columnspan=2)

operaciones = ["Determinante", "Inversa", "Transpuesta", "Multiplicar por Escalar"]
frame_botones = tk.Frame(tk_matrices)
frame_botones.grid(row=2, column=0, columnspan=2, pady=10)

for i, op in enumerate(operaciones):
    boton = tk.Button(frame_botones, text=op, command=lambda op=op: calcular_operacion(op), font=("Arial", 12))
    boton.grid(row=i, column=0, columnspan=2, pady=5)

frame_escalar = tk.Frame(tk_matrices)
frame_escalar.grid(row=3, column=0, columnspan=2)
entrada_escalar = tk.Entry(frame_escalar, width=10)
entrada_escalar.grid(row=0, column=0)
tk.Label(frame_escalar, text="Escalar", font=("Arial", 12)).grid(row=0, column=1)

frame_resultado = tk.Frame(tk_matrices)
frame_resultado.grid(row=4, column=0, columnspan=2, pady=10)

texto_resultado = tk.Label(tk_matrices, text=" ", font=("Arial", 14))
texto_resultado.grid(row=5, column=0, columnspan=2)
botonmenu = tk.Button(tk_matrices,text="menu", command=mostrar_menu)
botonmenu.grid(row=6,column=0, columnspan=2)

tk_matrices.mainloop()
