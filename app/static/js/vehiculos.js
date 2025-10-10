// vehiculos.js - Ingreso rápido de vehículos

document.addEventListener('DOMContentLoaded', () => {
    cargarDisponibilidad();
    
    // Event listener para formulario
    document.getElementById('form-ingreso-rapido')?.addEventListener('submit', ingresarVehiculoRapido);
});

// ========== INGRESAR VEHÍCULO RÁPIDO ==========
async function ingresarVehiculoRapido(e) {
    e.preventDefault();
    
    const placa = document.getElementById('input-placa').value.trim().toUpperCase();
    const tipoVehiculo = document.getElementById('select-tipo-vehiculo').value;
    
    if (!placa) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Debes ingresar una placa'
        });
        return;
    }
    
    try {
        // Mostrar loading
        Swal.fire({
            title: 'Asignando espacio...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch('/api/tickets/ingresar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                placa: placa,
                tipo_vehiculo: tipoVehiculo
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al ingresar vehículo');
        }
        
        // Éxito
        Swal.fire({
            icon: 'success',
            title: '¡Vehículo Ingresado!',
            html: `
                <div style="text-align: center;">
                    <h2 style="color: #2486DB; margin: 1rem 0;">${result.espacio.numero}</h2>
                    <p><strong>Placa:</strong> ${placa}</p>
                    <p><strong>Tipo:</strong> ${tipoVehiculo}</p>
                    <p><strong>Sección:</strong> ${result.espacio.seccion}</p>
                </div>
            `,
            confirmButtonText: 'Aceptar',
            confirmButtonColor: '#2486DB'
        });
        
        // Limpiar formulario
        document.getElementById('input-placa').value = '';
        document.getElementById('select-tipo-vehiculo').value = 'regular';
        
        // Actualizar disponibilidad
        cargarDisponibilidad();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== CARGAR DISPONIBILIDAD ==========
async function cargarDisponibilidad() {
    try {
        const response = await fetch('/api/espacios/estadisticas');
        const stats = await response.json();
        
        // Actualizar contadores
        document.getElementById('disponibles-regular').textContent = stats.disponibles || 0;
        
        // Si tienes separado por tipo, úsalo
        // document.getElementById('disponibles-moto').textContent = ...
        // document.getElementById('disponibles-discapacitado').textContent = ...
        
    } catch (error) {
        console.error('Error:', error);
    }
}

