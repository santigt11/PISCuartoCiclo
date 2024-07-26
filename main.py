import time

import numpy as np
from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from flask import Flask, render_template, request, redirect, url_for

from RungeKuttaSimulator import RungeKuttaSimulator
from configBD import *

app = Flask(__name__)
app.secret_key = 'hola'

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
    querySQL = "SELECT COUNT(*) AS total FROM PIS.Estudiantes"
    mycursos.execute(querySQL)
    return list(mycursos.fetchone().values())[0]

@app.route('/obtener_estudiantes', methods=['GET'])
def obtener_estudiantes():
    total_estudiantes = contarUsuarios()
    return jsonify({'total': total_estudiantes})

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



#Administrar
def obtener_ultimo_id():
    try:
        connection = connectionBD()
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(id_Usuario) FROM usuarios")
        resultado = cursor.fetchone()
        return 1 if resultado[0] is None else resultado[0] + 1
    except mysql.connector.Error as error:
        print(f"Error al obtener el último ID: {error}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def crear_usuario(clave, correo, isDocente):
    try:
        connection = connectionBD()
        cursor = connection.cursor()
        nuevo_id = obtener_ultimo_id()
        if nuevo_id is None:
            return "Error al generar nuevo ID"
        sql = "INSERT INTO usuarios (id_Usuario, clave, correo, isDocente) VALUES (%s, %s, %s, %s)"
        valores = (nuevo_id, clave, correo, isDocente)
        cursor.execute(sql, valores)
        connection.commit()
        return f"Usuario creado exitosamente con ID: {nuevo_id}"
    except mysql.connector.Error as error:
        return f"Error al crear usuario: {error}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/administrar', methods=['GET', 'POST'])
def crearUsuario():
    if request.method == 'POST':
        clave = request.form['clave']
        correo = request.form['correo']
        isDocente = 1 if 'isDocente' in request.form else 0
        resultado = crear_usuario(clave, correo, isDocente)
        flash(resultado)
        return redirect(url_for('usuarioCreado'))
    return render_template('registrarUsuario.html')

@app.route('/crear_Usuario')
def usuarioCreado():
    return render_template('registrarUsuario.html')

#Obtengo los usuarios
@app.route('/modificar', methods=['GET'])
def obtenerUsuarios():
    try:
        connection = connectionBD()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        return render_template('modificarUsuario.html', usuarios=usuarios)
    except mysql.connector.Error as error:
        print(f"Error al obtener los usuarios: {error}")
        return "Error al obtener los usuarios"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
@app.route('/actualizar_usuario', methods=['POST'])
def actualizarUsuario():
    id_usuario = request.form['id_usuario']
    clave = request.form['clave']
    correo = request.form['correo']
    isDocente = 1 if 'isDocente' in request.form else 0

    try:
        connection = connectionBD()
        cursor = connection.cursor()
        sql = "UPDATE usuarios SET clave = %s, correo = %s, isDocente = %s WHERE id_Usuario = %s"
        valores = (clave, correo, isDocente, id_usuario)
        cursor.execute(sql, valores)
        connection.commit()
        flash("Usuario actualizado exitosamente")
    except mysql.connector.Error as error:
        flash(f"Error al actualizar usuario: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('obtenerUsuarios'))


if __name__ == '__main__':
    app.run(debug=True, port=1000)
