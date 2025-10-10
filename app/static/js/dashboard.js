// Logout con confirmación SweetAlert2
document.getElementById('logout-btn').addEventListener('click', async (e) => {
  e.preventDefault();
  
  // Mostrar confirmación
  const result = await Swal.fire({
    title: '¿Cerrar sesión?',
    text: '¿Estás seguro de que quieres salir?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#1D6EB4',
    cancelButtonColor: '#666',
    confirmButtonText: 'Sí, salir',
    cancelButtonText: 'Cancelar'
  });

  // Si el usuario confirma
  if (result.isConfirmed) {
    try {
      const response = await fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Mostrar mensaje de despedida
        Swal.fire({
          icon: 'success',
          title: 'Sesión cerrada',
          text: 'Hasta pronto',
          showConfirmButton: false,
          timer: 1500
        }).then(() => {
          // Redirigir al login
          window.location.href = '/auth/';
        });
      } else {
        // Si hay error, redirigir de todas formas
        console.error('Error al cerrar sesión');
        window.location.href = '/auth/';
      }
    } catch (error) {
      console.error('Error:', error);
      // Mostrar error pero redirigir
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Hubo un problema al cerrar sesión',
        showConfirmButton: false,
        timer: 1500
      }).then(() => {
        window.location.href = '/auth/';
      });
    }
  }
});

// Función opcional para cargar estadísticas dinámicas
async function cargarEstadisticas() {
  try {
    const response = await fetch('/api/estadisticas', {
      credentials: 'include'
    });
    
    if (response.ok) {
      const data = await response.json();
      // Actualizar las estadísticas en la página
      console.log('Estadísticas:', data);
      
      // Ejemplo de actualización:
      // document.querySelector('.stat-card:nth-child(1) .stat-number').textContent = data.vehiculos;
    } else if (response.status === 401) {
      // Token expirado, redirigir al login
      window.location.href = '/auth/';
    }
  } catch (error) {
    console.error('Error cargando estadísticas:', error);
  }
}

// Cargar estadísticas al cargar la página (opcional, comentado por ahora)
// document.addEventListener('DOMContentLoaded', cargarEstadisticas);



