import numpy as np
import matplotlib.pyplot as plt

# Parámetros del sistema
alpha = 0.30  # tasa de reprobación por ciclo
beta = 0.8  # tasa de retención (1 - tasa de deserción)
gamma = 0.15  # tasa de crecimiento de nuevos ingresos por ciclo
epsilon = 0.50

def desertores_runge_kutta(reprobados_inicial, t0, t_final, h):
    desertores_lista = []
    reprobados = reprobados_inicial
    t = t0

    while t < t_final:
        desertores_lista.append(int(reprobados * (1 - beta)*(1*epsilon)))

        k1 = h * (-alpha * reprobados)
        k2 = h * (-alpha * (reprobados + k1 / 2))
        k3 = h * (-alpha * (reprobados + k2 / 2))
        k4 = h * (-alpha * (reprobados + k3))

        reprobados = reprobados + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        t = t + h

    return desertores_lista

def simular_ciclos(estudiantes_inicial, año_inicio, año_fin):
    años_simular = año_fin - año_inicio + 1
    ciclos = años_simular * 2

    estudiantes = [estudiantes_inicial]
    nuevos_ingresos_lista = []
    desertores_lista = []

    reprobados = 0  # Inicialmente no hay estudiantes reprobados

    for año in range(año_inicio, año_fin + 1):
        for ciclo in [1, 2]:
            # Nuevos ingresos
            nuevos_ingresos = int(estudiantes[-1] * gamma)
            estudiantes.append(estudiantes[-1] + nuevos_ingresos)
            nuevos_ingresos_lista.append(nuevos_ingresos)

            # Aprobados
            total = estudiantes[-1]
            aprobados = int(total * (1 - alpha))

            # Reprobados
            reprobados = int(total * alpha)

            # Desertores utilizando RK4
            desertores = desertores_runge_kutta(reprobados, 0, 1, 0.1)[-1]
            estudiantes.append(total - desertores)
            desertores_lista.append(desertores)

    return estudiantes, nuevos_ingresos_lista, desertores_lista

# Solicitar datos al usuario
estudiantes_inicial = int(input("Ingrese el número inicial de estudiantes: "))
año_inicio = int(input("Ingrese el año de inicio de la simulación: "))
año_fin = int(input("Ingrese el año final de la simulación: "))

# Realizar simulación
estudiantes, nuevos_ingresos, desertores = simular_ciclos(estudiantes_inicial, año_inicio, año_fin)


# Crear una única figura
fig, ax1 = plt.subplots(figsize=(15, 10))

# Gráfico principal de estudiantes
ax1.plot(range(len(estudiantes)), estudiantes, marker='o', color='blue', label='Estudiantes')
ax1.set_xlabel("Ciclo")
ax1.set_ylabel("Número de Estudiantes", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Añadir etiquetas de datos para estudiantes
for i, est in enumerate(estudiantes):
    ax1.annotate(f"{est}", (i, est), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

# Crear un segundo eje Y para nuevos ingresos y desertores
ax2 = ax1.twinx()

# Gráfico de nuevos ingresos y desertores
ax2.plot(range(1, len(estudiantes), 2), nuevos_ingresos, marker='s', color='green', label='Nuevos Ingresos')
ax2.plot(range(1, len(estudiantes), 2), desertores, marker='^', color='red', label='Desertores')
ax2.set_ylabel("Nuevos Ingresos / Desertores", color='green')
ax2.tick_params(axis='y', labelcolor='green')

# Añadir etiquetas de datos para nuevos ingresos y desertores
for i, (ing, des) in enumerate(zip(nuevos_ingresos, desertores)):
    ax2.annotate(f"+{ing}", (i*2+1, ing), textcoords="offset points", xytext=(0, 10), ha='center', color='green', fontsize=8)
    ax2.annotate(f"-{des}", (i*2+1, des), textcoords="offset points", xytext=(0, -15), ha='center', color='red', fontsize=8)

# Título y leyenda
plt.title(f"Simulación de Estudiantes, Nuevos Ingresos y Desertores ({año_inicio}-{año_fin})")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.grid(True)
plt.tight_layout()
plt.show()


# Imprimir resultados
print("\nResultados detallados:")
print(f"{año_inicio}-1 Inicio: {estudiantes[0]} estudiantes")

for i in range(1, len(estudiantes), 2):
    año = año_inicio + (i - 1) // 4
    ciclo = 2 if (i - 1) % 4 >= 2 else 1

    inicio_ciclo = estudiantes[i - 1]
    ingresados = nuevos_ingresos[i // 2]
    desertados = desertores[i // 2]
    fin_ciclo = estudiantes[i + 1]

    print(f"\n{año}-{ciclo}:")
    print(f"  Inicio del ciclo: {inicio_ciclo} estudiantes")
    print(f"  Ingresaron: {ingresados} estudiantes")
    print(f"  Desertaron: {desertados} estudiantes")
    print(f"  Fin del ciclo: {fin_ciclo} estudiantes")
    print(f"  Cambio neto: {fin_ciclo - inicio_ciclo} estudiantes")