// Toggle para mostrar/ocultar contraseña
const togglePassword = document.getElementById('togglePassword');
const password = document.getElementById('password');

if (togglePassword) {
  togglePassword.addEventListener('click', function () {
    const icon = this.querySelector('i');
    if (password.type === 'password') {
      password.type = 'text';
      icon.classList.remove('fa-eye');
      icon.classList.add('fa-eye-slash');
    } else {
      password.type = 'password';
      icon.classList.remove('fa-eye-slash');
      icon.classList.add('fa-eye');
    }
  });
}

// Manejo del formulario de login
document.getElementById('login-form').addEventListener('submit', async function(e) {
  e.preventDefault();

  const usuario = document.getElementById('usuario').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include', // Importante para enviar cookies
      body: JSON.stringify({
        nombre_usuario: usuario,
        password: password
      })
    });

    const data = await response.json();

    if (response.ok) {
      // Mostrar mensaje de éxito
      Swal.fire({
        icon: 'success',
        title: '¡Login exitoso!',
        text: `Bienvenido ${data.usuario}`,
        showConfirmButton: false,
        timer: 1500
      }).then(() => {
        // Redirigir al dashboard
        window.location.href = '/dashboard';
      });
    } else {
      // Mostrar error
      Swal.fire({
        icon: 'error',
        title: 'Error de autenticación',
        text: data.error || 'Usuario o contraseña incorrectos'
      });
    }
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: 'No se pudo conectar con el servidor'
    });
    console.error('Error:', error);
  }
});


