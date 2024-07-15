import numpy as np
import matplotlib.pyplot as plt

# Parámetros del sistema
alpha = 0.20  # tasa de reprobación por ciclo
beta = 0.8  # tasa de retención (1 - tasa de deserción)
gamma = 0.10  # tasa de crecimiento de nuevos ingresos por ciclo

def desertores_runge_kutta(reprobados_inicial, t0, t_final, h,opcion):

    desertores_lista = []
    reprobados = reprobados_inicial
    t = t0

    if opcion=="hombres":
        alpha1 = 1.80  # tasa de reprobación por ciclo
        beta1 = 0.8  # tasa de retención (1 - tasa de deserción)
        while t < t_final:
            desertores_lista.append(int(reprobados * (1 - beta1)))

            k1 = h * (-alpha1 * reprobados)
            k2 = h * (-alpha1 * (reprobados + k1 / 2))
            k3 = h * (-alpha1 * (reprobados + k2 / 2))
            k4 = h * (-alpha1 * (reprobados + k3))

            reprobados = reprobados + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            t = t + h
    elif opcion=="mujeres":
        alpha2 = 1.60  # tasa de reprobación por ciclo
        beta2 = 0.8  # tasa de retención (1 - tasa de deserción)
        while t < t_final:
            desertores_lista.append(int(reprobados * (1 - beta2)))
            k1 = h * (-alpha2 * reprobados)
            k2 = h * (-alpha2 * (reprobados + k1 / 2))
            k3 = h * (-alpha2 * (reprobados + k2 / 2))
            k4 = h * (-alpha2 * (reprobados + k3))

            reprobados = reprobados + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            t = t + h
    elif opcion=="general":
        while t < t_final:
            desertores_lista.append(int(reprobados * (1 - beta)))

            k1 = h * (-alpha * reprobados)
            k2 = h * (-alpha * (reprobados + k1 / 2))
            k3 = h * (-alpha * (reprobados + k2 / 2))
            k4 = h * (-alpha * (reprobados + k3))

            reprobados = reprobados + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            t = t + h

    return desertores_lista
def aprobados_runge_kutta(total_estudiantes, t0, t_final, h,opcion):

    if opcion=="hombres":
        delta = 0.30  # tasa de aprobación para la nueva ecuación
        aprobados_lista = []
        hombres = total_estudiantes // 2  # Dividimos el total de estudiantes entre 2
        t = t0

        while t < t_final:
            # Nueva ecuación diferencial: dA = hombres * delta
            k1 = h * (hombres * delta)
            k2 = h * ((hombres + k1 / 2) * delta)
            k3 = h * ((hombres + k2 / 2) * delta)
            k4 = h * ((hombres + k3) * delta)

            aprobados = hombres + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            aprobados_lista.append(int(aprobados))

            t = t + h
    elif opcion=="mujeres":
        delta=0.20
        aprobados_lista = []
        mujeres = total_estudiantes // 2  # Dividimos el total de estudiantes entre 2
        t = t0

        while t < t_final:
            # Nueva ecuación diferencial: dA = hombres * delta
            k1 = h * (mujeres * delta)
            k2 = h * ((mujeres + k1 / 2) * delta)
            k3 = h * ((mujeres + k2 / 2) * delta)
            k4 = h * ((mujeres + k3) * delta)

            aprobados = mujeres + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            aprobados_lista.append(int(aprobados))

            t = t + h
    return aprobados_lista


def simular_ciclos(estudiantes_inicial, año_inicio, año_fin,opcion):
    años_simular = año_fin - año_inicio + 1
    ciclos = años_simular * 2

    estudiantes = [estudiantes_inicial]
    nuevos_ingresos_lista = []
    desertores_lista = []

    reprobados = 0  # Inicialmente no hay estudiantes reprobados

    for año in range(año_inicio, año_fin + 1):
        for ciclo in [1, 2]:
            # Nuevos ingresos
            if opcion=="hombres":
                gamma1 = 0.06  # tasa de crecimiento de nuevos ingresos por ciclo
                nuevos_ingresos = int(estudiantes[-1] * gamma1)
                estudiantes.append(estudiantes[-1] + nuevos_ingresos)
                nuevos_ingresos_lista.append(nuevos_ingresos)
                total = estudiantes[-1]
                aprobados = aprobados_runge_kutta(total, 0, 1, 0.1,"hombres")[-1]
                reprobados = total - aprobados

                # Calcular desertores
                desertores = desertores_runge_kutta(reprobados, 0, 1, 0.1,"hombres")[-1]
                estudiantes.append(total - desertores)
                desertores_lista.append(desertores)
            elif opcion=="mujeres":
                gamma2 = 0.04  # tasa de crecimiento de nuevos ingresos por ciclo
                nuevos_ingresos = int(estudiantes[-1] * gamma2)
                estudiantes.append(estudiantes[-1] + nuevos_ingresos)
                nuevos_ingresos_lista.append(nuevos_ingresos)
                total = estudiantes[-1]
                aprobados = aprobados_runge_kutta(total, 0, 1, 0.1,"mujeres")[-1]
                reprobados = total - aprobados
                desertores = desertores_runge_kutta(reprobados, 0, 1, 0.1,"mujeres")[-1]
                estudiantes.append(total - desertores)
                desertores_lista.append(desertores)
            elif opcion=="general":
                nuevos_ingresos = int(estudiantes[-1] * gamma)
                estudiantes.append(estudiantes[-1] + nuevos_ingresos)
                nuevos_ingresos_lista.append(nuevos_ingresos)
                # Aprobados
                total = estudiantes[-1]
                aprobados = int(total * (1 - alpha))

                # Reprobados
                reprobados = int(total * alpha)

            # Desertores utilizando RK4
                desertores = desertores_runge_kutta(reprobados, 0, 1, 0.1,"general")[-1]
                estudiantes.append(total - desertores)
                desertores_lista.append(desertores)

    return estudiantes, nuevos_ingresos_lista, desertores_lista

while(True):
    opcion=input("Seleccione la prediccion que desea realizar(hombres/mujeres/general): ")
    estudiantes_inicial = int(input("Ingrese el número inicial de estudiantes: "))
    año_inicio = int(input("Ingrese el año de inicio de la simulación: "))
    año_fin = int(input("Ingrese el año final de la simulación: "))
    # Realizar simulación
    estudiantes, nuevos_ingresos, desertores = simular_ciclos(estudiantes_inicial, año_inicio, año_fin, opcion)

    # Graficar resultados
    if opcion == "hombres":
        plt.figure(figsize=(15, 8))
        plt.plot(range(len(estudiantes)), estudiantes, marker='o')
        plt.xlabel("Ciclo")
        plt.ylabel("Número de Estudiantes")
        plt.title(f"Simulación de Estudiantes Hombres ({año_inicio}-{año_fin})")
        plt.grid(True)

        # Añadir etiquetas de datos
        for i, est in enumerate(estudiantes):
            plt.annotate(f"{est}", (i, est), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.tight_layout()
        plt.show()
    elif opcion == "mujeres":
        plt.figure(figsize=(15, 8))
        plt.plot(range(len(estudiantes)), estudiantes, marker='o')
        plt.xlabel("Ciclo")
        plt.ylabel("Número de Estudiantes")
        plt.title(f"Simulación de Estudiantes Mujeres ({año_inicio}-{año_fin})")
        plt.grid(True)

        # Añadir etiquetas de datos
        for i, est in enumerate(estudiantes):
            plt.annotate(f"{est}", (i, est), textcoords="offset points", xytext=(0, 10), ha='center')

        plt.tight_layout()
        plt.show()

    elif opcion == "general":
        plt.figure(figsize=(15, 8))
        plt.plot(range(len(estudiantes)), estudiantes, marker='o')
        plt.xlabel("Ciclo")
        plt.ylabel("Número de Estudiantes")
        plt.title(f"Simulación de Estudiantes ({año_inicio}-{año_fin})")
        plt.grid(True)
        # Añadir etiquetas de datos
        for i, est in enumerate(estudiantes):
            plt.annotate(f"{est}", (i, est), textcoords="offset points", xytext=(0, 10), ha='center')
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
        if opcion == "hombres":
            print(f"\n{año}-{ciclo}:")
            print(f"  Inicio del periodo: {inicio_ciclo} estudiantes")
            print(f"  Ingresaron: {ingresados} hombres")
            print(f"  Desertaron: {desertados} hombres")
            print(f"  Fin del periodo: {fin_ciclo} estudiantes")
            print(f"  Cambio neto: {fin_ciclo - inicio_ciclo} hombres")
        elif opcion == "mujeres":
            print(f"\n{año}-{ciclo}:")
            print(f"  Inicio del periodo: {inicio_ciclo} estudiantes")
            print(f"  Ingresaron: {ingresados} mujeres")
            print(f"  Desertaron: {desertados} mujeres")
            print(f"  Fin del periodo: {fin_ciclo} estudiantes")
            print(f"  Cambio neto: {fin_ciclo - inicio_ciclo}  mujeres")
        elif opcion == "general":
            print(f"\n{año}-{ciclo}:")
            print(f"  Inicio del periodo: {inicio_ciclo} estudiantes")
            print(f"  Ingresaron: {ingresados} estudiantes")
            print(f"  Desertaron: {desertados} estudiantes")
            print(f"  Fin del ciclo: {fin_ciclo} estudiantes")
            print(f"  Cambio neto: {fin_ciclo - inicio_ciclo} estudiantes")
    confirmar = input("¿Desea realizar otra predicción? (Si/No): ")
    if confirmar.lower() != "si":
        break
    print("Programa finalizado.")