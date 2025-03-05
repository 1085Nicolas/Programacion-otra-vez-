import customtkinter as ctk
import tkinter as tk
import diccionarios
import sympy as sp
import funciones_otras_calculadoras
import funciones_principales 
import diccionarios

# Configurar ventana principal
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

ctk.set_appearance_mode("dark")  

class Cientifica(ctk.CTk):  
    def __init__(self):
        super().__init__()

        self.title("Calculadora Científica")
        self.geometry("414x595")
        self.resizable(False, False)

        self.modo_oscuro = True  

        self.resultado = ctk.CTkLabel(self, text="", font=("Arial", 20), width=380, justify="right")
        self.resultado.pack(pady=3, padx=10)

        self.entrada = ctk.CTkEntry(self, font=("Arial", 20), width=380, justify="right")
        self.entrada.pack(pady=10, padx=10)

        self.colores = {
            "morado": ("#A14FCF", "#6A0DAD"),
            "naranja": ("#F5B041", "#E67E22"),
            "verde": ("#58D68D", "#27AE60"),
            "gris": ("#AAB7B8", "#5D6D7E"),
            "azul": ("#5DADE2", "#2980B9")
        }

        self.frame_funciones = ctk.CTkFrame(self)
        self.frame_funciones.pack()

        self.botones_funciones = diccionarios.crear_diccionario_funciones(self.entrada, self.resultado,self)
        self.crear_botones(self.botones_funciones, self.frame_funciones, "funcion", 6)  

        self.frame_numeros = ctk.CTkFrame(self)
        self.frame_numeros.pack(pady=8)

        self.botones_numeros = diccionarios.crear_diccionario(self.entrada, self.resultado)
        self.crear_botones(self.botones_numeros, self.frame_numeros, "numero", 5)  
    def abrir_menu_principal(self):
        self.destroy()

        # Abrimos el menú principal
        from menu import MainMenu
        main_menu = MainMenu()
        main_menu.mainloop()

    def crear_botones(self, botones, frame, tipo="funcion", botones_por_fila=6):
        botones_morados = ["D/R", "AYUDA", "HISTORIAL", "Cl/Os", "MENU", "SALIR"]
        botones_naranjas = ["GRAFICA", "="]
        botones_azules = ["+", "-", "X", "/","DEL","Ans","AC"]

        contador = 0
        for texto, funcion in botones.items():
            if texto in botones_morados:
                color_fondo = self.colores["morado"][1] if self.modo_oscuro else self.colores["morado"][0]
            elif texto in botones_naranjas:
                color_fondo = self.colores["naranja"][1] if self.modo_oscuro else self.colores["naranja"][0]
            elif texto in botones_azules:
                color_fondo = self.colores["azul"][1] if self.modo_oscuro else self.colores["azul"][0]
            elif tipo == "numero":
                color_fondo = self.colores["gris"][1] if self.modo_oscuro else self.colores["gris"][0]
            else:
                color_fondo = self.colores["verde"][1] if self.modo_oscuro else self.colores["verde"][0]

            button = ctk.CTkButton(
                master=frame,
                text=texto,
                width=60,
                height=40,
                fg_color=color_fondo,
                command=self.cambiar_tema if texto == "Cl/Os" else funcion  # Corregí el nombre
            )
            button.grid(row=contador // botones_por_fila, column=contador % botones_por_fila, padx=2, pady=2, sticky="nsew")
            contador += 1  

    def cambiar_tema(self):
        self.modo_oscuro = not self.modo_oscuro
        nuevo_modo = "dark" if self.modo_oscuro else "light"
        ctk.set_appearance_mode(nuevo_modo)
        self.actualizar_colores()

    def actualizar_colores(self):
        for widget in self.frame_funciones.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                texto = widget.cget("text")
                if texto in ["D/R", "AYUDA", "HISTORIAL", "Cl/Os", "MENU", "SALIR"]:
                    nuevo_color = self.colores["morado"][1] if self.modo_oscuro else self.colores["morado"][0]
                elif texto in ["GRAFICA", "="]:
                    nuevo_color = self.colores["naranja"][1] if self.modo_oscuro else self.colores["naranja"][0]
                elif texto in ["+", "-", "X", "/"]:
                    nuevo_color = self.colores["azul"][1] if self.modo_oscuro else self.colores["azul"][0]
                else:
                    nuevo_color = self.colores["verde"][1] if self.modo_oscuro else self.colores["verde"][0]
                widget.configure(fg_color=nuevo_color)

        for widget in self.frame_numeros.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                nuevo_color = self.colores["gris"][1] if self.modo_oscuro else self.colores["gris"][0]
                widget.configure(fg_color=nuevo_color)


#fisica.bind("<Key>", manejar_teclado) 

from funciones_otras_calculadoras import calcular_resistencia, seleccionar_color
from diccionarios import opciones, colores, valores, opciones_banda4, colores_banda4, tolerancias
import customtkinter as ctk

class InterfazResistencia:
    def __init__(self, ventana_principal):
        self.ventana_principal = ventana_principal  # Guarda una referencia a la ventana principal
        self.ventana = ctk.CTk()
        self.ventana.geometry("600x300")  # Tamaño inicial
        self.ventana.resizable(True, True)  # Permite redimensionar tanto en ancho como en alto
        self.banda1 = tk.StringVar(value="negro")
        self.banda2 = tk.StringVar(value="negro")
        self.banda3 = tk.StringVar(value="negro")
        self.banda4 = tk.StringVar(value="dorado")  # Usamos dorado como valor por defecto para la banda 4

        self.crear_interfaz_resistencia()

    def crear_interfaz_resistencia(self):
        self.ventana.title("Calculadora de Resistencias 4 Bandas")

        # Título
        titulo = ctk.CTkLabel(self.ventana, text="Calculadora de Resistencias 4 Bandas", font=("Arial", 20))
        titulo.grid(row=0, column=0, columnspan=4, pady=10)

        # Crear botones para cada banda
        self.banda1_button = ctk.CTkButton(self.ventana, text="Banda 1", fg_color=colores[self.banda1.get()], font=("Arial", 14),
                                          command=lambda: seleccionar_color(self.banda1, opciones, self.banda1_button, colores))
        self.banda2_button = ctk.CTkButton(self.ventana, text="Banda 2", fg_color=colores[self.banda2.get()], font=("Arial", 14),
                                          command=lambda: seleccionar_color(self.banda2, opciones, self.banda2_button, colores))
        self.banda3_button = ctk.CTkButton(self.ventana, text="Banda 3", fg_color=colores[self.banda3.get()], font=("Arial", 14),
                                          command=lambda: seleccionar_color(self.banda3, opciones, self.banda3_button, colores))
        self.banda4_button = ctk.CTkButton(self.ventana, text="Banda 4", fg_color=colores_banda4[self.banda4.get()], font=("Arial", 14),
                                          command=lambda: seleccionar_color(self.banda4, opciones_banda4, self.banda4_button, colores_banda4))

        # Colocar los botones en la interfaz
        self.banda1_button.grid(row=1, column=0, padx=5, pady=5)
        self.banda2_button.grid(row=1, column=1, padx=5, pady=5)
        self.banda3_button.grid(row=1, column=2, padx=5, pady=5)
        self.banda4_button.grid(row=1, column=3, padx=5, pady=5)

        # Crear un botón para calcular la resistencia
        calcular_btn = ctk.CTkButton(self.ventana, text="Calcular", font=("Arial", 14), command=lambda: calcular_resistencia(self.banda1, self.banda2, self.banda3, self.banda4,self.resultado))
        calcular_btn.grid(row=2, column=0, columnspan=4, pady=10)

        # Mostrar el resultado de la resistencia calculada
        self.resultado = ctk.CTkLabel(self.ventana, text="Resistencia: ", font=("Arial", 16))
        self.resultado.grid(row=3, column=0, columnspan=4, pady=10)

        # Botón para volver al menú principal
        botonmenu = ctk.CTkButton(self.ventana, text="Menú", font=("Arial", 14), command=self.volver_menu)
        botonmenu.grid(row=4, column=1, pady=10)

        # Botón para cambiar entre el modo dark/light
        botonmodo = ctk.CTkButton(self.ventana, text="Cl/Os", font=("Arial", 14), command=self.cambiar_tema)
        botonmodo.grid(row=4, column=2, pady=10)

        # Ejecutar la ventana
        self.ventana.mainloop()

    def volver_menu(self):
        # Cerrar la ventana actual (calculadora) y mostrar el menú principal
        self.ventana.destroy()
        self.ventana_principal.deiconify()  # Muestra la ventana principal (menú)

    def cambiar_tema(self):
        # Cambiar entre tema oscuro y claro
        if ctk.get_appearance_mode() == "dark":
            ctk.set_appearance_mode("light")  # Cambiar a modo claro
        else:
            ctk.set_appearance_mode("dark") 


from funciones_otras_calculadoras import calcular_operacion, generar_matriz, cambiarmodo
import customtkinter as ctk

class Interfaz:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Calculadora de Matrices")
        self.ventana.geometry("482x440")
        self.ventana.resizable(False, False)  # Aumentar el tamaño de la ventana

        # Frame izquierdo para los botones de operaciones
        self.frame_botones = ctk.CTkFrame(self.ventana)
        self.frame_botones.grid(row=1, column=0, padx=10, pady=10)

        # Botones de operaciones
        self.operaciones = ["Determinante", "Inversa", "Transpuesta", "Multiplicar por Escalar"]
        for i, op in enumerate(self.operaciones):
            boton = ctk.CTkButton(self.frame_botones, text=op, command=lambda op=op: calcular_operacion(op), font=("Arial", 12))
            boton.grid(row=i, column=0, padx=5, pady=5)

        # Campo de entrada para escalar
        self.entrada_escalar = ctk.CTkEntry(self.frame_botones, width=10)
        self.entrada_escalar.grid(row=4, column=0)

        # Frame derecho para la creación de matrices
        self.frame_entrada = ctk.CTkFrame(self.ventana)
        self.frame_entrada.grid(row=0, column=0, padx=0, pady=0)

        # Entradas para filas y columnas
        ctk.CTkLabel(self.frame_entrada, text="Número de Filas:").grid(row=1, column=0)
        ctk.CTkLabel(self.frame_entrada, text="Número de Columnas:").grid(row=2, column=0)

        # Botones para cambiar el tema
        self.menuboton = ctk.CTkButton(self.frame_entrada, text="Menú", font=("Arial", 12), width=6, height=15, command=self.volver_menu_principal)
        self.modoboton = ctk.CTkButton(self.frame_entrada, text="Cl/Os", font=("Arial", 12), width=6, height=6, command=cambiarmodo)
        self.menuboton.grid(row=0, column=0)
        self.modoboton.grid(row=0, column=1)

        # Entradas para filas y columnas
        self.entrada_filas = ctk.CTkEntry(self.frame_entrada, width=10)
        self.entrada_filas.grid(row=1, column=1)
        self.entrada_columnas = ctk.CTkEntry(self.frame_entrada, width=10)
        self.entrada_columnas.grid(row=2, column=1)

        # Botón para generar matriz
        self.boton_generar = ctk.CTkButton(self.frame_entrada, text="Generar Matriz", command=generar_matriz)
        self.boton_generar.grid(row=3, column=0, columnspan=2, pady=10)

        # Frame para la matriz de entrada
        self.frame_matriz = ctk.CTkFrame(self.ventana)
        self.frame_matriz.grid(row=0, column=1, padx=0, pady=5)

        # Frame para mostrar el resultado
        self.frame_resultado = ctk.CTkFrame(self.ventana)
        self.frame_resultado.grid(row=1, column=1, columnspan=2, pady=0)

        # Etiqueta para mostrar el texto del resultado
        self.texto_resultado = ctk.CTkLabel(self.ventana, text=" ", font=("Arial", 14))
        self.texto_resultado.grid(row=3, column=0, columnspan=2, pady=5)

    def volver_menu_principal(self):
        # Este método oculta la calculadora y muestra el menú principal
        self.ventana.withdraw()  # Oculta la ventana actual
        from menu import MainMenu  # Asegúrate de que el menú esté importado
        main_menu = MainMenu()  # Crear una instancia del menú
        main_menu.deiconify()  # Mostrar el menú
        main_menu.mainloop()  # Iniciar el ciclo principal del menú


##interfaz de conversion de unidades 

from diccionarios import crear_diccionario_unidades
from funciones_otras_calculadoras import convertir

class Fisica:
    def __init__(self, unidades):
        # Crear la ventana principal
        self.fisica = ctk.CTk()
        self.fisica.title("Conversor de Unidades")
        self.fisica.geometry("300x630")
        
        # Crear la etiqueta de resultado
        self.etiqueta_resultado = ctk.CTkLabel(self.fisica, text="Resultado", font=("Arial", 16))
        self.etiqueta_resultado.pack(pady=20)

        # Crear Entry para ingresar números
        self.entrada_valor = ctk.CTkEntry(self.fisica, width=200, font=("Arial", 14))
        self.entrada_valor.pack(pady=10)

        # Menú de categorías
        self.categoria_var = tk.StringVar(value="Longitud")
        self.menu_categoria = ctk.CTkOptionMenu(self.fisica, variable=self.categoria_var, values=list(unidades.keys()))
        self.menu_categoria.pack(pady=10)

        # Menú de unidades origen
        self.unidad_origen_var = tk.StringVar(value="metros")
        self.menu_origen = ctk.CTkOptionMenu(self.fisica, variable=self.unidad_origen_var, values=list(unidades[self.categoria_var.get()].keys()))
        self.menu_origen.pack(pady=10)

        # Menú de unidades destino
        self.unidad_destino_var = tk.StringVar(value="kilómetros")
        self.menu_destino = ctk.CTkOptionMenu(self.fisica, variable=self.unidad_destino_var, values=list(unidades[self.categoria_var.get()].keys()))
        self.menu_destino.pack(pady=10)

        # Función para actualizar los menús de unidades según la categoría seleccionada
        self.categoria_var.trace("w", self.actualizar_unidades)

        # Crear el Frame para los botones
        self.frame_botonera = ctk.CTkFrame(self.fisica)
        self.frame_botonera.pack(pady=10)

        # Función para crear los botones
        self.crear_botones(self.frame_botonera, self.entrada_valor, self.etiqueta_resultado)

    def actualizar_unidades(self, *args):
        categoria = self.categoria_var.get()
        opciones = list(unidades[categoria].keys())
        
        self.unidad_origen_var.set(opciones[0])
        self.unidad_destino_var.set(opciones[1])

        self.menu_origen["menu"].delete(0, "end")
        self.menu_destino["menu"].delete(0, "end")

        for unidad in opciones:
            self.menu_origen["menu"].add_command(label=unidad, command=tk._setit(self.unidad_origen_var, unidad))
            self.menu_destino["menu"].add_command(label=unidad, command=tk._setit(self.unidad_destino_var, unidad))

    def crear_botones(self, frame, entry, etiqueta):
        botones = crear_diccionario_unidades(entry, etiqueta)
        
        # Contador para las filas y columnas
        fila = 0
        columna = 0
        
        for texto, comando in botones.items():
            if texto != "Cl/Os" and texto != "HISTORIAL":  # Evitar botones innecesarios
                boton = ctk.CTkButton(frame, text=texto, width=60, height=60, command=comando)
                boton.grid(row=fila, column=columna, padx=5, pady=5)
                
                # Actualizar el contador para las filas y columnas
                columna += 1
                if columna > 3:  # Si hay más de 5 columnas, mover a la siguiente fila
                    columna = 0
                    fila += 1

        boton_igual = ctk.CTkButton(frame, text="=", width=60, height=60, command=lambda: self.convertir(entry, etiqueta))
        boton_igual.grid(row=4, column=3, padx=5, pady=5)

    def convertir(self, entry, etiqueta_resultado):
        valor = entry.get()
        if valor:
            valor = float(valor)
            convertir(unidades, self.categoria_var, self.unidad_origen_var, self.unidad_destino_var, valor, etiqueta_resultado)
        else:
            etiqueta_resultado.configure(text="Ingrese un número válido")

    def run(self):
        self.fisica.mainloop()

# Crear y ejecutar la interfaz
if __name__ == "__main__":
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

    fisica_app = Fisica(unidades)
    fisica_app.run()
