import time

import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, render_template, request, redirect, url_for
from configBD import *

app = Flask(__name__)


# Ruta para mostrar el formulario de login
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signin', methods=['POST'])
def signin():
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')

    # Validación de campos vacíos
    if not correo or not contrasena:
        error_message = 'Por favor, completa todos los campos.'
        time.sleep(1)  # Espera de 1 segundos antes de continuar

        return render_template('login.html', error_message=error_message)

    # Lógica de validación (simplificada)
    conexion_MySQL = connectionBD()
    mycursos = conexion_MySQL.cursor(dictionary=True)
    querySQL = "SELECT * FROM PIS.usuarios ORDER BY id_usuario"
    mycursos.execute(querySQL)
    lista_usuarios = mycursos.fetchall()
    mycursos.close()

    usuarioCorrecto = False
    for usuario in lista_usuarios:
        if usuario['correo'] == correo and usuario['clave'] == contrasena:
            usuarioCorrecto = True
            break
        else:
            print ("entra a usuario correcto pero falso")
    if usuarioCorrecto:
        return redirect(url_for('principal'))  # Redirige a otra vista si las credenciales son correctas
    else:
        error_message = 'Credenciales incorrectas. Intenta de nuevo.'
        return render_template('login.html', error_message=error_message)
# Ruta para la página principal
@app.route('/inicio')
def principal():
    return render_template('indexEstudiante.html')


@app.route('/acercaDe')
def informacion():
    return render_template('about.html')

# Constantes para el método de Euler
alpha = 10.80  # Tasa de reprobación
beta = 0.2     # Tasa de recuperación
gamma = 0.3    # Coeficiente de deserción por reprobación aumentado

# Funciones de derivadas para el método de Euler
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

# Ruta para calcular los datos con el método de Euler
@app.route('/calculate_euler', methods=['POST'])
def calculate_euler():
    data = request.get_json()
    t0 = float(data['t0'])
    t_final = float(data['t_final'])

    # Condiciones iniciales y configuración de tiempo
    h = 1  # Tamaño del paso (constante)
    t_values = np.arange(t0, t_final + h, h)  # Valores de tiempo desde t0 hasta tf con incremento h
    S0 = 1000.0  # Número total de estudiantes inicial
    R0 = 0.0     # Número inicial de estudiantes reprobados
    D0 = 0.0     # Número inicial de estudiantes desertados
    H0 = 500.0   # Número inicial de hombres
    M0 = 500.0   # Número inicial de mujeres

    # Listas para almacenar los resultados
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

    # Preparar los datos para ser enviados al cliente
    response_data = {
        't': t_values.tolist(),
        'S': S_values.tolist(),
        'D': D_values.tolist()
    }

    return jsonify(response_data)

# Ruta para la página de predicción
@app.route('/prediccion')
def prediccion():
    return render_template('prediccion.html')


if __name__ == '__main__':
    app.run(debug=True, port=1000)
