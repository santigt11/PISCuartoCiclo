import random1
def generar_numero_aleatorio(minimo=30, maximo=30):

    if minimo > maximo:
        raise ValueError("El valor mínimo debe ser menor o igual al valor máximo")
    return random.randint(minimo, maximo)

def generar_numero_aleatorio_Egresados(minimo=3, maximo=7):
    if minimo > maximo:
        raise ValueError("El valor mínimo debe ser menor o igual al valor máximo")
    return random.randint(minimo, maximo)
