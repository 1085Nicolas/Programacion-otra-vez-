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