from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Ruta para mostrar el formulario de login
@app.route('/')
def login():
    return render_template('login.html')

# Ruta para procesar el formulario de login
@app.route('/signin', methods=['POST'])
def signin():
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')

    # Verificar las credenciales aquí...

    if correo == 'abelmoral13@gmail.com' and contrasena == '123':
        # Credenciales válidas, redirigir al usuario a la página principal
        return redirect(url_for('principal'))
    else:
        # Credenciales inválidas, volver al formulario de login con un mensaje de error
        return render_template('login.html', error='Credenciales incorrectas')


# Ruta para la página principal
@app.route('/inicio')
def principal():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
