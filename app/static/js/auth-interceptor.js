// auth-interceptor.js - Manejo global de expiración de sesión

// Interceptar todas las peticiones fetch para detectar 401
const originalFetch = window.fetch;
window.fetch = function(...args) {
    return originalFetch.apply(this, args)
        .then(response => {
            // Si es 401 (no autorizado), mostrar mensaje y redirigir
            if (response.status === 401) {
                handleSessionExpired();
                // Retornar una promesa rechazada para que el código que llamó a fetch maneje el error
                return Promise.reject(new Error('Sesión expirada'));
            }
            return response;
        })
        .catch(error => {
            // Re-lanzar el error para que el código original lo maneje
            throw error;
        });
};

// Función para manejar sesión expirada
function handleSessionExpired() {
    // Evitar mostrar múltiples alertas
    if (window.sessionExpiredShown) {
        return;
    }
    window.sessionExpiredShown = true;
    
    Swal.fire({
        icon: 'warning',
        title: 'Sesión Expirada',
        text: 'Tu sesión ha expirado por inactividad. Serás redirigido al login.',
        confirmButtonText: 'Ir al Login',
        confirmButtonColor: '#2486DB',
        allowOutsideClick: false,
        allowEscapeKey: false
    }).then(() => {
        // Redirigir al login
        window.location.href = '/auth/';
    });
}

// También interceptar XMLHttpRequest (por si acaso)
const originalXHROpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(...args) {
    this.addEventListener('load', function() {
        if (this.status === 401) {
            handleSessionExpired();
        }
    });
    return originalXHROpen.apply(this, args);
};
