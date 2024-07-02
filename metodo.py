import numpy as np
import matplotlib.pyplot as plt


def sistema_ecuaciones(t, y):
    # y[0]: total de estudiantes
    # y[1]: número de hombres
    # y[2]: número de mujeres
    # y[3]: número total de estudiantes que han desertado
    # y[4]: número de estudiantes que han desertado por factor económico

    tasa_ingreso = 100  # estudiantes por unidad de tiempo
    tasa_desercion_total = 0.1  # fracción de estudiantes que desertan por unidad de tiempo
    tasa_desercion_economica = 0.06  # fracción de estudiantes que desertan por factores económicos
    proporcion_hombres = 0.55  # proporción de hombres en los nuevos ingresos

    dy = np.zeros(5)

    # Cambio en el total de estudiantes
    dy[0] = tasa_ingreso - tasa_desercion_total * y[0]

    # Cambio en el número de hombres
    dy[1] = proporcion_hombres * tasa_ingreso - tasa_desercion_total * y[1]

    # Cambio en el número de mujeres
    dy[2] = (1 - proporcion_hombres) * tasa_ingreso - tasa_desercion_total * y[2]

    # Cambio en el número total de desertores
    dy[3] = tasa_desercion_total * y[0]

    # Cambio en el número de desertores por factor económico
    dy[4] = tasa_desercion_economica * y[0]

    return dy


def runge_kutta_4(f, t0, y0, t_final, h):
    t = np.arange(t0, t_final + h, h)
    n = len(t)
    y = np.zeros((n, len(y0)))
    y[0] = y0

    for i in range(1, n):
        k1 = h * f(t[i - 1], y[i - 1])
        k2 = h * f(t[i - 1] + 0.5 * h, y[i - 1] + 0.5 * k1)
        k3 = h * f(t[i - 1] + 0.5 * h, y[i - 1] + 0.5 * k2)
        k4 = h * f(t[i - 1] + h, y[i - 1] + k3)

        y[i] = y[i - 1] + (k1 + 2 * k2 + 2 * k3 + k4) / 6

    return t, y


# Parámetros iniciales
t0 = 0
y0 = [1000, 550, 450, 0, 0]  # [total, hombres, mujeres, desertores_totales, desertores_economicos]
t_final = 50
h = 0.1

# Resolver el sistema de ecuaciones
t, y = runge_kutta_4(sistema_ecuaciones, t0, y0, t_final, h)

# Graficar los resultados
plt.figure(figsize=(12, 8))
plt.plot(t, y[:, 4], 'r-', label='Desertores por factor económico')
plt.title('Deserción estudiantil por factor económico')
plt.xlabel('Tiempo')
plt.ylabel('Número de estudiantes')
plt.legend()
plt.grid(True)
plt.show()