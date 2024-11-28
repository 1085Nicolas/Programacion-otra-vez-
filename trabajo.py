#importamos random para el punto 2
import random

#primer punto
def vacas (V,K,X,c):
    if K > c and X <= 1 :
        return "0 ya que no se puede producir ni un litro diario"
    else :
        vacas_posibles = min (V,c//K)
        p = vacas_posibles * X * 7
        return p


V = int(input("Cuantas vacas hay: "))
K = float(input("¿Cuantos metros cuadrados de pasto necesita por cada vaca? : "))
X = float(input("litros de leche por vaca al dia : "))
M = float(input("¿Cual es el ancho del corral de las vacas en metros? : "))
N = float(input("¿Cual es el largo del corral de las vacas en metros? : "))

c = M * N

resultado = vacas (V,K,X,c)

print ("Los litros de leche producidos por semana son : ", resultado)

#Segundo ejercicio


a = int(input("cuantas aves hay en la granja : "))
gallinas = (a//3)
mitad = (gallinas//2)
residuo = (gallinas%2)

g1= mitad
g2 = mitad

if residuo > 0 :
        if random.choice([True, False]):
            g1 += residuo
        else:
          g2 += 1

huevos_1 = g1 * 10  
huevos_2 = g2 * 6   

total_huevos = huevos_1 + huevos_2
print("El total de huevos producidos en un mes es de:", total_huevos)

# se multiplica la mitad por 10 ya que segun regla de 3 si una gallina produce 1 huevo cada 3 dias, produce 10 en un mes de 30 dias
# se multiplica la mitad por 10 ya que segun regla de 3 si una gallina produce 1 huevo cada 5 dias, produce 6 en un mes de 30 dias