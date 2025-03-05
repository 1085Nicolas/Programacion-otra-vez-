import funciones_principales
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

# Diccionario calculadora cientifica y grafica

def crear_diccionario_funciones(entry,etiqueta,cientifica_obj):
    return {
        "D/R": lambda: funciones_principales.agregar_a_pantalla(entry, "D/R"),
        "AYUDA": lambda: funciones_principales.agregar_a_pantalla(entry, "AYUDA"),
        "Cl/Os": lambda: Cientifica.cambiar_tema(),
        "HISTORIAL": lambda: conexionfb.mostrar_historial_calculadora(entry),
        "MENU": lambda: cientifica_obj.abrir_menu_principal(),
        "SALIR": lambda: funciones_principales.cerrar_aplicacion(cientifica_obj),
        "Σ": lambda: funciones_principales.agregar_a_pantalla(entry, "Σ "),
        "Π": lambda: funciones_principales.agregar_a_pantalla(entry, "Π "),
        "lim": lambda: funciones_principales.agregar_a_pantalla(entry, "lim("),
        "d/dx": lambda: funciones_principales.agregar_a_pantalla(entry, "d/dx "),
        "∫": lambda: funciones_principales.agregar_a_pantalla(entry, "∫"),
        "GRAFICA": lambda: funciones_principales.graficar_funcion(entry),
        "x": lambda: funciones_principales.agregar_a_pantalla(entry, "x"),
        "y": lambda: funciones_principales.agregar_a_pantalla(entry, "y"),
        "z": lambda: funciones_principales.agregar_a_pantalla(entry, "z"),
        "π": lambda: funciones_principales.agregar_a_pantalla(entry, "π"),
        "e": lambda: funciones_principales.agregar_a_pantalla(entry, "e"),
        "x⁻¹": lambda: funciones_principales.agregar_a_pantalla(entry, "⁻¹"),
        "^": lambda: funciones_principales.agregar_a_pantalla(entry, "^"),
        "x²": lambda: funciones_principales.agregar_a_pantalla(entry, "²"),
        "x³": lambda: funciones_principales.agregar_a_pantalla(entry, "³"),
        "ⁿ√a": lambda: funciones_principales.agregar_a_pantalla(entry, "√"),
        "√": lambda: funciones_principales.agregar_a_pantalla(entry, " √"),
        "∛": lambda: funciones_principales.agregar_a_pantalla(entry, "∛"),
        "arcsin": lambda: funciones_principales.agregar_a_pantalla(entry, "arcsn("),
        "arcos": lambda: funciones_principales.agregar_a_pantalla(entry, "arccs("),
        "arctan": lambda: funciones_principales.agregar_a_pantalla(entry, "arctn("),
        "log": lambda: funciones_principales.agregar_a_pantalla(entry, "lg("),
        "ln": lambda: funciones_principales.agregar_a_pantalla(entry, "ln("),
        "logx(a)": lambda: funciones_principales.agregar_a_pantalla(entry, "log("),
        "sin": lambda: funciones_principales.agregar_a_pantalla(entry, "sin("),
        "cos": lambda: funciones_principales.agregar_a_pantalla(entry, "cos("),
        "tan": lambda: funciones_principales.agregar_a_pantalla(entry, "tan("),
        "cot": lambda: funciones_principales.agregar_a_pantalla(entry, "cot("),
        "sec": lambda: funciones_principales.agregar_a_pantalla(entry, "sec("),
        "csc": lambda: funciones_principales.agregar_a_pantalla(entry, "csc("),
        "(": lambda: funciones_principales.agregar_a_pantalla(entry, "("),
        ")": lambda: funciones_principales.agregar_a_pantalla(entry, ")"),
        "x!": lambda: funciones_principales.agregar_a_pantalla(entry, "!"),
        "%": lambda: funciones_principales.agregar_a_pantalla(entry, "%"),
        "° ' ''": lambda: funciones_principales.convertir_grados_decimal(etiqueta),
        "S⭤ D": lambda: funciones_principales.convertir_fraccion_decimal(etiqueta),
    }

opernp = {
    "sin": "np.sin", "cos": "np.cos", "tan": "np.tan",
    "cot": "1/np.tan", "sec": "1/np.cos", "csc": "1/np.sin",
    "arcsn": "np.arcsin", "arccs": "np.arccos", "arctn": "np.arctan"
    , "²": "**2", "³": "**3", "^": "**", "⁻¹": "**-1",
    "ln": "np.log", "lg": "np.log10",
    "π": "np.pi", "e": "np.e","%": "/100"
}

opersp = { 
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "cot": lambda x: 1/sp.tan(x), "sec": lambda x: 1/sp.cos(x), "csc": lambda x: 1/sp.sin(x),
    "arcsn": sp.asin, "arccs": sp.acos, "arctn": sp.atan,
    "ln": sp.ln, "lg": sp.log,  
    "π": sp.pi, "e": sp.E, "²": "**2", "³": "**3", "^": "**", "⁻¹": "**-1"
}


def crear_diccionario(entry,etiqueta):
    return {
        "7": lambda: funciones_principales.agregar_a_pantalla(entry, "7"),
        "8": lambda: funciones_principales.agregar_a_pantalla(entry, "8"),
        "9": lambda: funciones_principales.agregar_a_pantalla(entry, "9"),
        "DEL": lambda: funciones_principales.delete_last(entry),
        "AC": lambda: funciones_principales.clear_all(entry,etiqueta),
        "4": lambda: funciones_principales.agregar_a_pantalla(entry, "4"),
        "5": lambda: funciones_principales.agregar_a_pantalla(entry, "5"),
        "6": lambda: funciones_principales.agregar_a_pantalla(entry, "6"),
        "X": lambda: funciones_principales.agregar_a_pantalla(entry, "*"),
        "/": lambda: funciones_principales.agregar_a_pantalla(entry, "/"),
        "1": lambda: funciones_principales.agregar_a_pantalla(entry, "1"),
        "2": lambda: funciones_principales.agregar_a_pantalla(entry, "2"),
        "3": lambda: funciones_principales.agregar_a_pantalla(entry, "3"),
        "+": lambda: funciones_principales.agregar_a_pantalla(entry, "+"),
        "-": lambda: funciones_principales.agregar_a_pantalla(entry, "-"),
        "0": lambda: funciones_principales.agregar_a_pantalla(entry, "0"),
        ".": lambda: funciones_principales.agregar_a_pantalla(entry, "."),
        "+/-": lambda: funciones_principales.toggle_sign(entry),
        "Ans": lambda: funciones_principales.insert_answer(entry,etiqueta),
        "=": lambda: funciones_principales.calcular(entry.get(),etiqueta,entry),
    }

## Diccionarios calculadora de unidades

def crear_diccionario_unidades(entry,etiqueta):
    return {
        "AYUDA": lambda: None,
        "Cl/0s": lambda: funciones_principales.agregar_a_pantalla(entry, "MENU") ,
        "MENU": lambda: funciones_principales.agregar_a_pantalla(entry, "MENU"),
        "SALIR": lambda: funciones_principales.cerrar_aplicacion(unidades),
        "9": lambda: funciones_principales.agregar_a_pantalla(entry, "9"),
        "8": lambda: funciones_principales.agregar_a_pantalla(entry, "8"),
        "7": lambda: funciones_principales.agregar_a_pantalla(entry, "7"),
        "Historial": lambda: funciones_principales.agregar_a_pantalla(entry, "7"),
        "6": lambda: funciones_principales.agregar_a_pantalla(entry, "6"),
        "5": lambda: funciones_principales.agregar_a_pantalla(entry, "5"),
        "4": lambda: funciones_principales.agregar_a_pantalla(entry, "4"),
        "AC": lambda: funciones_principales.clear_all(entry,etiqueta),
        "3": lambda: funciones_principales.agregar_a_pantalla(entry, "3"),
        "2": lambda: funciones_principales.agregar_a_pantalla(entry, "2"),
        "1": lambda: funciones_principales.agregar_a_pantalla(entry, "1"),
        "DEL": lambda: funciones_principales.delete_last(entry),
        "0": lambda: funciones_principales.agregar_a_pantalla(entry, "0"),
        ".": lambda: funciones_principales.agregar_a_pantalla(entry, "."),
        "+/-": lambda: funciones_principales.toggle_sign(entry),

    }

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

## Calculadora Codigo Color Resistencias

# Diccionarios de opciones y colores para las bandas de resistencia

opciones = ["negro", "marron", "rojo", "naranja", "amarillo", "verde", "azul", "violeta", "gris", "blanco"]
colores = {
    "negro": "black", "marron": "brown", "rojo": "red", "naranja": "orange", "amarillo": "yellow",
    "verde": "green", "azul": "blue", "violeta": "purple", "gris": "gray", "blanco": "white"
}
valores = {
    "negro": 0, "marron": 1, "rojo": 2, "naranja": 3, "amarillo": 4,
    "verde": 5, "azul": 6, "violeta": 7, "gris": 8, "blanco": 9
}

# Diccionario de opciones y colores para la banda 4 (tolerancia dorado/plateado)
opciones_banda4 = ["dorado", "plateado"]
colores_banda4 = {
    "dorado": "gold", "plateado": "silver"
}
tolerancias = {
    "dorado": "± 5%", "plateado": "± 10%"
}

## Matrices No Usa Diccionarios