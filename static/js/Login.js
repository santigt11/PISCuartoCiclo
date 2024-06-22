let signUp = document.getElementById("signUp");
let signIn = document.getElementById("signIn");
let nameInput = document.getElementById("nameInput");
let title = document.getElementById("title");
let loginForm = document.getElementById("loginForm");

signIn.onclick = function () {
    nameInput.style.maxHeight = "0";
    title.innerHTML = "Login";
    signUp.classList.add("disable");
    signIn.classList.remove("disable");
};

// Login.js
loginForm.addEventListener("submit", function(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    let correo = document.getElementById("correo").value;
    let contrasena = document.getElementById("contrasena").value;

    // Validación de campos vacíos
    if (correo.trim() === '' || contrasena.trim() === '') {
        showErrorMessage("Por favor, completa todos los campos.");
        return; // Detener la ejecución si hay campos vacíos
    }

    // Envío del formulario si todos los campos están completos
    let data = new FormData();
    data.append('correo', correo);
    data.append('contrasena', contrasena);

    fetch('/signin', {
        method: 'POST',
        body: data
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            showAlert(data.message, 'success');
            window.location.href = "/inicio";  // Redirigir a la página principal si las credenciales son correctas
        } else {
            showErrorMessage(data.message); // Mostrar mensaje de error del servidor si las credenciales son incorrectas
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert("Error al intentar iniciar sesión. Inténtalo de nuevo más tarde.", 'error');

    });

});
function showErrorMessage(message) {
    errorContainer.innerHTML = `<div class="message error-message">${message}</div>`;
    attemptContainer.innerHTML = '';
};



