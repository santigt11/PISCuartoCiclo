import time
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

from ControlAlerta import ErrorLogger, ErrorNotifier
from Subject import Subject
from alertDisplay import AlertDisplay
from RungeKuttaPrediccion import RungeKuttaPrediccion
from configBD import *

app = Flask(__name__)
app.secret_key = 'hola'

# Declaración de las variables globales
usuarioCorrecto = False
correoUsuario = None

# Ruta para mostrar el formulario de login
@app.route('/login')
def login():
    global usuarioCorrecto
    global correoUsuario
    usuarioCorrecto = False
    correoUsuario = None
    return render_template('login.html', usuarioCorrecto=usuarioCorrecto, correoUsuario=correoUsuario)

# Cerrar Sesion
@app.route('/signout')
def signout():
    global usuarioCorrecto
    global correoUsuario
    usuarioCorrecto = False
    correoUsuario = None
    return render_template('indexEstudiante.html', usuarioCorrecto=usuarioCorrecto, correoUsuario=correoUsuario)

@app.route('/signin', methods=['POST'])
def signin():
    global usuarioCorrecto  # Indicamos que vamos a usar la variable global
    global correoUsuario

    # Crear instancia de Subject
    subject = Subject()

    # Crear observadores y adjuntarlos al Subject
    error_logger = ErrorLogger()
    error_notifier = ErrorNotifier()
    alert_display = AlertDisplay()  # Nuevo observador para mostrar alertas
    subject.attach(error_logger)
    subject.attach(error_notifier)
    subject.attach(alert_display)

    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')

    # Validación de campos vacíos
    if not correo or not contrasena:
        error_message = 'Por favor, completa todos los campos.'
        subject.notify(error_message,"validation")  # Notificar a los observadores
        return render_template('login.html', error_message=error_message, usuarioCorrecto=usuarioCorrecto,
                               correoUsuario=correoUsuario)

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
            correoUsuario = correo
            break
    if usuarioCorrecto:
        return redirect(url_for('principal'))  # Redirige a otra vista si las credenciales son correctas
    else:
        error_message = 'Credenciales incorrectas. Intenta de nuevo.'
        subject.notify(error_message)  # Notificar a los observadores
        return render_template('login.html', error_message=error_message, usuarioCorrecto=usuarioCorrecto,
                               correoUsuario=correoUsuario)

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
@app.route('/')
def principal():
    return render_template('indexEstudiante.html', usuarioCorrecto=usuarioCorrecto, correoUsuario=correoUsuario)

@app.route('/acercaDe')
def informacion():
    return render_template('about.html', usuarioCorrecto=usuarioCorrecto, correoUsuario=correoUsuario)


# Add this new route
@app.route('/get_total_students/<int:year>', methods=['GET'])
def get_total_students(year):
    try:
        connection = connectionBD()
        cursor = connection.cursor(dictionary=True)

        # First, try to get the total from the anio table
        cursor.execute("SELECT totalEstudiantes FROM anio WHERE numAnio = %s", (year,))
        result = cursor.fetchone()

        if result:
            total = result['totalEstudiantes']
        else:
            # If not found in anio table, calculate from periodo table
            cursor.execute("""
                SELECT SUM(cantEstudiantesTotal) as total
                FROM periodo
                WHERE numAnio = %s
            """, (year,))
            result = cursor.fetchone()
            total = result['total'] if result and result['total'] is not None else 0

        return jsonify({'total': total})
    except mysql.connector.Error as error:
        print(f"Error al obtener el total de estudiantes: {error}")
        return jsonify({'error': str(error)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Ruta para calcular los datos con el método de Euler
@app.route('/calculate_rungeKutta', methods=['POST'])
def calculate_rungeKutta():
    data = request.get_json()
    año_inicio = int(data['año_inicio'])
    año_fin = int(data['año_fin'])
    opcion = data['opcion']
    factor = data['factor']
    estudiantes_inicial = int(data['estudiantes_inicial'])

    simulator = RungeKuttaPrediccion()
    estudiantes, nuevos_ingresos, desertores = simulator.simular_ciclos(estudiantes_inicial, año_inicio, año_fin,
                                                                        opcion, factor)

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
    global usuarioCorrecto
    global correoUsuario
    if usuarioCorrecto:
        return render_template('prediccion.html', usuarioCorrecto=usuarioCorrecto, correoUsuario=correoUsuario)
    else:
        return redirect(url_for('login'))

@app.route('/contacto')
def contacto():
    return render_template('contactDocente.html', usuarioCorrecto=usuarioCorrecto, correoUsuario=correoUsuario)



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
        sql = "INSERT INTO usuarios (id_Usuario, clave, correo, isAdmin) VALUES (%s, %s, %s, %s)"
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
        sql = "UPDATE usuarios SET clave = %s, correo = %s, isAdmin = %s WHERE id_Usuario = %s"
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

#Registrar Anio
def obtener_ultimo_numAnio():
    try:
        connection = connectionBD()
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(numAnio) FROM anio")
        resultado = cursor.fetchone()
        return 1 if resultado[0] is None else resultado[0] + 1
    except mysql.connector.Error as error:
        print(f"Error al obtener el último número de año: {error}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def crear_anio(totalEstudiantes, totalEgresados, totalDesertores, totalEstudiantesMatriculados):
    try:
        connection = connectionBD()
        cursor = connection.cursor()
        nuevo_numAnio = obtener_ultimo_numAnio()
        if nuevo_numAnio is None:
            return "Error al generar nuevo número de año"
        sql = "INSERT INTO anio (numAnio, totalEstudiantes, totalEgresados, totalDesertores) VALUES (%s, %s, %s, %s)"
        valores = (nuevo_numAnio, totalEstudiantes, totalEgresados, totalDesertores, totalEstudiantesMatriculados)
        cursor.execute(sql, valores)
        connection.commit()
        return f"Año creado exitosamente con número: {nuevo_numAnio}"
    except mysql.connector.Error as error:
        return f"Error al crear año: {error}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/anio', methods=['GET', 'POST'])
def crearAnio():
    if request.method == 'POST':
        totalEstudiantes = int(request.form['totalEstudiantes'])
        totalEgresados = int(request.form['totalEgresados'])
        totalDesertores = int(request.form['totalDesertores'])
        totalEstudiantesMatriculados = int(request.form['totalEstudiantesMatriculados'])
        resultado = crear_anio(totalEstudiantes, totalEgresados, totalDesertores, totalEstudiantesMatriculados)
        flash(resultado)
        return redirect(url_for('anioCreado'))
    return render_template('registrarAnio.html')

@app.route('/crear_Anio')
def anioCreado():
    return render_template('registrarAnio.html')

#Modificar Anio
@app.route('/modificarAnio', methods=['GET'])
def obtenerAnios():
    try:
        connection = connectionBD()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM anio")
        anios = cursor.fetchall()
        return render_template('modificarAnio.html', anios=anios)
    except mysql.connector.Error as error:
        print(f"Error al obtener los años: {error}")
        return "Error al obtener los años"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
@app.route('/actualizar_anio', methods=['POST'])
def actualizarAnio():
    numAnio = request.form['numAnio']
    totalEstudiantes = request.form['totalEstudiantes']
    totalEgresados = request.form['totalEgresados']
    totalDesertores = request.form['totalDesertores']
    totalEstudiantesMatriculados = request.form['totalEstudiantesMatriculados']

    try:
        connection = connectionBD()
        cursor = connection.cursor()
        sql = "UPDATE anio SET totalEstudiantes = %s, totalEgresados = %s, totalDesertores = %s = WHERE numAnio = %s"
        valores = (totalEstudiantes, totalEgresados, totalDesertores, totalEstudiantesMatriculados, numAnio)
        cursor.execute(sql, valores)
        connection.commit()
        flash("Año actualizado exitosamente")
    except mysql.connector.Error as error:
        flash(f"Error al actualizar año: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('obtenerAnios'))

#Registrar Periodo
def obtener_ultimo_numPeriodo(numAnio):
    try:
        connection = connectionBD()
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(numPeriodo) FROM periodo WHERE numAnio = %s", (numAnio,))
        resultado = cursor.fetchone()
        return 1 if resultado[0] is None else resultado[0] + 1
    except mysql.connector.Error as error:
        print(f"Error al obtener el último número de periodo: {error}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def crear_periodo(numAnio, cantEstudiantesHombre, cantEstudiantesMujer, cantEstudiantesEgresados, cantEstudiantesDesertores, cantEstudiantesMatriculados):
    try:
        connection = connectionBD()
        cursor = connection.cursor()
        nuevo_numPeriodo = obtener_ultimo_numPeriodo(numAnio)
        if nuevo_numPeriodo is None:
            return "Error al generar nuevo número de periodo"
        sql = "INSERT INTO periodo (numPeriodo, numAnio, cantEstudiantesHombre, cantEstudiantesMujer, cantEstudiantesEgresados, cantEstudiantesDesertores, cantEstudiantesTotal) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        valores = (nuevo_numPeriodo, numAnio, cantEstudiantesHombre, cantEstudiantesMujer, cantEstudiantesEgresados, cantEstudiantesDesertores, cantEstudiantesMatriculados)
        cursor.execute(sql, valores)
        connection.commit()
        return f"Periodo creado exitosamente con número: {nuevo_numPeriodo}"
    except mysql.connector.Error as error:
        return f"Error al crear periodo: {error}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/periodo', methods=['GET', 'POST'])
def crearPeriodo():
    if request.method == 'POST':
        numAnio = int(request.form['numAnio'])
        cantEstudiantesHombre = int(request.form['cantEstudiantesHombre'])
        cantEstudiantesMujer = int(request.form['cantEstudiantesMujer'])
        cantEstudiantesEgresados = int(request.form['cantEstudiantesEgresados'])
        cantEstudiantesDesertores = int(request.form['cantEstudiantesDesertores'])
        cantEstudiantesMatriculados = int(request.form['cantEstudiantesMatriculados'])
        resultado = crear_periodo(numAnio, cantEstudiantesHombre, cantEstudiantesMujer, cantEstudiantesEgresados, cantEstudiantesDesertores, cantEstudiantesMatriculados)
        flash(resultado)
        return redirect(url_for('periodoCreado'))
    
    # Obtener años ya registrados
    try:
        connection = connectionBD()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT numAnio FROM periodo ORDER BY numAnio")
        anios = cursor.fetchall()
    except mysql.connector.Error as error:
        flash(f"Error al obtener años: {error}")
        anios = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('registrarPeriodo.html', anios=anios)
    
@app.route('/crear_Periodo')
def periodoCreado():
    return render_template('registrarPeriodo.html')

#Modificar Periodo
@app.route('/modificarPeriodo', methods=['GET'])
def obtenerPeriodos():
    try:
        connection = connectionBD()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM periodo")
        periodos = cursor.fetchall()
        return render_template('modificarPeriodo.html', periodos=periodos)
    except mysql.connector.Error as error:
        print(f"Error al obtener los periodos: {error}")
        return "Error al obtener los periodos"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
@app.route('/actualizar_periodo', methods=['POST'])
def actualizarPeriodo():
    numPeriodo = request.form['numPeriodo']
    numAnio = request.form['numAnio']
    cantEstudiantesHombre = request.form['cantEstudiantesHombre']
    cantEstudiantesMujer = request.form['cantEstudiantesMujer']
    cantEstudiantesEgresados = request.form['cantEstudiantesEgresados']
    cantEstudiantesDesertores = request.form['cantEstudiantesDesertores']
    cantEstudiantesMatriculados = request.form['cantEstudiantesMatriculados']

    try:
        connection = connectionBD()
        cursor = connection.cursor()
        sql = "UPDATE periodo SET cantEstudiantesHombre = %s, cantEstudiantesMujer = %s, cantEstudiantesEgresados = %s, cantEstudiantesDesertores = %s, cantEstudiantesMatriculados = %s WHERE numPeriodo = %s AND numAnio = %s"
        valores = (cantEstudiantesHombre, cantEstudiantesMujer, cantEstudiantesEgresados, cantEstudiantesDesertores, cantEstudiantesMatriculados, numPeriodo, numAnio)
        cursor.execute(sql, valores)
        connection.commit()
        flash("Período actualizado exitosamente")
    except mysql.connector.Error as error:
        flash(f"Error al actualizar período: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('obtenerPeriodos'))


if __name__ == '__main__':
    app.run(debug=True, port=1000)
