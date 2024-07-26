import mysql.connector
from configBD import connectionBD
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

app = Flask(__name__)
app.secret_key = 'hola'

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

@app.route('/', methods=['GET', 'POST'])
def crearUsuario():
    if request.method == 'POST':
        clave = request.form['clave']
        correo = request.form['correo']
        isDocente = 1 if 'isDocente' in request.form else 0
        resultado = crear_usuario(clave, correo, isDocente)
        flash(resultado)
        return redirect(url_for('crearUsuario'))
    return render_template('usuario.html')

if __name__ == '__main__':
    app.run(debug=True, port=1000)