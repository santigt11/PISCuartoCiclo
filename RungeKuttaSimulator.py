import numpy as np
import matplotlib.pyplot as plt

class RungeKuttaSimulator:
    def __init__(self):
        self.alpha = 0.20  # tasa de reprobación por ciclo
        self.beta = 0.8  # tasa de retención (1 - tasa de deserción)
        self.gamma = 0.10  # tasa de crecimiento de nuevos ingresos por ciclo

    def desertores_runge_kutta(self, reprobados_inicial, t0, t_final, h, opcion):
        desertores_lista = []
        reprobados = reprobados_inicial
        t = t0

        if opcion == "hombres":
            alpha1, beta1 = 1.80, 0.8
        elif opcion == "mujeres":
            alpha1, beta1 = 1.60, 0.8
        else:
            alpha1, beta1 = self.alpha, self.beta

        while t < t_final:
            desertores_lista.append(int(reprobados * (1 - beta1)))
            k1 = h * (-alpha1 * reprobados)
            k2 = h * (-alpha1 * (reprobados + k1 / 2))
            k3 = h * (-alpha1 * (reprobados + k2 / 2))
            k4 = h * (-alpha1 * (reprobados + k3))
            reprobados = reprobados + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            t = t + h

        return desertores_lista

    def aprobados_runge_kutta(self, total_estudiantes, t0, t_final, h, opcion):
        if opcion == "hombres":
            delta = 0.30
        elif opcion == "mujeres":
            delta = 0.20
        else:
            return []  # No se calcula para opción general

        aprobados_lista = []
        estudiantes = total_estudiantes // 2
        t = t0

        while t < t_final:
            k1 = h * (estudiantes * delta)
            k2 = h * ((estudiantes + k1 / 2) * delta)
            k3 = h * ((estudiantes + k2 / 2) * delta)
            k4 = h * ((estudiantes + k3) * delta)
            aprobados = estudiantes + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            aprobados_lista.append(int(aprobados))
            t = t + h

        return aprobados_lista

    def simular_ciclos(self, estudiantes_inicial, año_inicio, año_fin, opcion):
        estudiantes = [estudiantes_inicial]
        nuevos_ingresos_lista = []
        desertores_lista = []

        for año in range(año_inicio, año_fin + 1):
            for ciclo in [1, 2]:
                if opcion == "hombres":
                    gamma1 = 0.06
                elif opcion == "mujeres":
                    gamma1 = 0.04
                else:
                    gamma1 = self.gamma

                nuevos_ingresos = int(estudiantes[-1] * gamma1)
                estudiantes.append(estudiantes[-1] + nuevos_ingresos)
                nuevos_ingresos_lista.append(nuevos_ingresos)
                total = estudiantes[-1]

                if opcion != "general":
                    aprobados = self.aprobados_runge_kutta(total, 0, 1, 0.1, opcion)[-1]
                    reprobados = total - aprobados
                else:
                    reprobados = int(total * self.alpha)

                desertores = self.desertores_runge_kutta(reprobados, 0, 1, 0.1, opcion)[-1]
                estudiantes.append(total - desertores)
                desertores_lista.append(desertores)

        return estudiantes, nuevos_ingresos_lista, desertores_lista