import time

import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, render_template, request, redirect, url_for

from RungeKuttaSimulator import RungeKuttaSimulator
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

def contarUsuarios():
    conexion_MySQL = connectionBD()
    mycursos = conexion_MySQL.cursor(dictionary=True)
    querySQL = "SELECT COUNT(*) FROM PIS.Estudiantes"
    mycursos.execute(querySQL)
    count = mycursos.fetchone()
    mycursos.close()
    return count

# Ruta para la página principal
@app.route('/inicio')
def principal():
    return render_template('indexEstudiante.html')


@app.route('/acercaDe')
def informacion():
    return render_template('about.html')

# Ruta para calcular los datos con el método de Euler
@app.route('/calculate_rungeKutta', methods=['POST'])
def calculate_rungeKutta():
    data = request.get_json()
    estudiantes_inicial = int(data['estudiantes_inicial'])
    año_inicio = int(data['año_inicio'])
    año_fin = int(data['año_fin'])
    opcion = data['opcion']

    simulator = RungeKuttaSimulator()
    estudiantes, nuevos_ingresos, desertores = simulator.simular_ciclos(estudiantes_inicial, año_inicio, año_fin, opcion)

    años = list(range(año_inicio, año_fin + 1))

    response_data = {
        'estudiantes': estudiantes,
        'nuevos_ingresos': nuevos_ingresos,
        'desertores': desertores,
        'años': años
    }

    return jsonify(response_data)

# Ruta para la página de predicción
@app.route('/prediccion')
def prediccion():
    return render_template('prediccion.html')

@app.route('/contacto')
def contacto():
    return render_template('contactDocente.html')

if __name__ == '__main__':
    app.run(debug=True, port=1000)
