import time

from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Ruta para mostrar el formulario de login
@app.route('/')
def login():
    return render_template('login.html')

# Ruta para procesar el formulario de login
#@app.route('/signin', methods=['POST'])
#def signin():
#    correo = request.form.get('correo')
#    contrasena = request.form.get('contrasena')

    # Verificar las credenciales aquí...

   # if correo == 'abelmoral13@gmail.com' and contrasena == '123':
        # Credenciales válidas, redirigir al usuario a la página principal
    #    return redirect(url_for('principal'))
    #else:
        # Credenciales inválidas, mostrar el mensaje de error en el formulario de login
     #   return render_template('error.html', mostrar_error=True)

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
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
