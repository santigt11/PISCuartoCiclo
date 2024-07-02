import time

import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify

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
    if correo == 'abel@mora' and contrasena == '123':
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

@app.route('/modelo')
def matematica():
    return render_template('service.html')
@app.route('/prediccion')
def prediccion():
    return render_template('prediccion.html')
#Sistema de ecuaciones
# Función para el sistema de ecuaciones
def sistema_ecuaciones(t, y):
    tasa_ingreso = 100  # estudiantes por unidad de tiempo
    tasa_desercion_total = 0.1  # fracción de estudiantes que desertan por unidad de tiempo
    tasa_desercion_economica = 0.06  # fracción de estudiantes que desertan por factores económicos
    proporcion_hombres = 0.55  # proporción de hombres en los nuevos ingresos

    dy = np.zeros(5)
    dy[0] = tasa_ingreso - tasa_desercion_total * y[0]
    dy[1] = proporcion_hombres * tasa_ingreso - tasa_desercion_total * y[1]
    dy[2] = (1 - proporcion_hombres) * tasa_ingreso - tasa_desercion_total * y[2]
    dy[3] = tasa_desercion_total * y[0]
    dy[4] = tasa_desercion_economica * y[0]

    return dy

# Función para el método de Runge-Kutta de cuarto orden
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

# Ruta para calcular los datos con el método de Runge-Kutta
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    t0 = float(data['t0'])
    y0 = list(map(float, data['y0']))
    t_final = float(data['t_final'])
    h = float(data['h'])

    t, y = runge_kutta_4(sistema_ecuaciones, t0, y0, t_final, h)

    # Preparar los datos para ser enviados al cliente
    response_data = {
        't': t.tolist(),
        'y': y[:, 4].tolist()  # Selecciona la columna correspondiente a 'y4' para los resultados
    }

    return jsonify(response_data)



if __name__ == '__main__':
    app.run(debug=True)
