import time

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


if __name__ == '__main__':
    app.run(debug=True)
