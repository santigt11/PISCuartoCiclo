import numpy as np
import matplotlib.pyplot as plt

# Parámetros del sistema
alpha = 10.80  # tasa de reprobación
beta = 0.2     # tasa de recuperación
gamma = 0.3    # coeficiente de deserción por reprobación aumentado

# Funciones de derivadas
def dH_dt(H):
    return 0.01 * H

def dM_dt(M):
    return 0.01 * M

def dS_dt(H, M):
    return dH_dt(H) + dM_dt(M)

def dR_dt(S, R, H, M):
    return alpha * dS_dt(H, M) - beta * R

def dD_dt(R):
    return gamma * R

# Condiciones iniciales y configuración de tiempo
t0 = 0.0
tf = 5.0   # Tiempo final de simulación (por ejemplo, 10 años)
h = 0.1     # Tamaño del paso (por ejemplo, 0.1 años)

# Números iniciales de estudiantes y desertados
S0 = 1000.0  # Número total de estudiantes inicial
R0 = 0.0     # Número inicial de estudiantes reprobados
D0 = 0.0     # Número inicial de estudiantes desertados
H0 = 500.0   # Número inicial de hombres
M0 = 500.0   # Número inicial de mujeres

# Listas para almacenar los resultados
t_values = np.arange(t0, tf + h, h)  # Valores de tiempo desde t0 hasta tf con incremento h
S_values = np.zeros_like(t_values)
R_values = np.zeros_like(t_values)
D_values = np.zeros_like(t_values)
H_values = np.zeros_like(t_values)
M_values = np.zeros_like(t_values)

# Condiciones iniciales
S_values[0] = S0
R_values[0] = R0
D_values[0] = D0
H_values[0] = H0
M_values[0] = M0

# Método de Euler para integración numérica
for i in range(1, len(t_values)):
    H = H_values[i-1]
    M = M_values[i-1]
    S = S_values[i-1]
    R = R_values[i-1]
    D = D_values[i-1]

    dS = dS_dt(H, M)
    dR = dR_dt(S, R, H, M)
    dD = dD_dt(R)

    S_values[i] = S + h * dS
    R_values[i] = R + h * dR
    D_values[i] = D + h * dD
    H_values[i] = H + h * dH_dt(H)
    M_values[i] = M + h * dM_dt(M)

# Graficar resultados de S(t) y D(t)
plt.figure(figsize=(10, 6))
plt.plot(t_values, S_values, label="S(t) - Número Total de Estudiantes", color='blue')
plt.plot(t_values, D_values, label="D(t) - Estudiantes Desertados", color='red')
plt.xlabel("Tiempo (Años)")
plt.ylabel("Número de Estudiantes")
plt.title("Simulación de Estudiantes utilizando Método de Euler")
plt.legend()
plt.grid()
plt.show()
