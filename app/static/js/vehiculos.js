// vehiculos.js - Ingreso rápido de vehículos

document.addEventListener('DOMContentLoaded', () => {
    cargarDisponibilidad();
    
    // Auto-convertir placa a mayúsculas mientras escribes
    const inputPlaca = document.getElementById('input-placa');
    if (inputPlaca) {
        inputPlaca.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });
    }
    
    // Event listener para formulario
    document.getElementById('form-ingreso-rapido')?.addEventListener('submit', ingresarVehiculoRapido);
    
    // Event listener para cambio de tipo de vehículo
    document.getElementById('select-tipo-vehiculo')?.addEventListener('change', actualizarDisponibilidad);
});

// Variable global para almacenar espacios por tipo
let espaciosPorTipo = {};

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
                    <h2 style="color: #2486DB; margin: 1rem 0; font-size: 3rem;">${result.espacio.numero}</h2>
                    <p><strong>Placa:</strong> ${placa}</p>
                    <p><strong>Tipo:</strong> ${capitalizarPrimeraLetra(tipoVehiculo)}</p>
                    <p><strong>Sección:</strong> ${result.espacio.seccion}</p>
                    <p style="margin-top: 1rem; color: #666;">
                        <i class="fas fa-ticket-alt"></i> Ticket #${result.ticket.id}
                    </p>
                </div>
            `,
            confirmButtonText: 'Aceptar',
            confirmButtonColor: '#2486DB'
        });
        
        // Limpiar formulario
        document.getElementById('input-placa').value = '';
        document.getElementById('select-tipo-vehiculo').value = 'regular';
        
        // Focus en input
        document.getElementById('input-placa').focus();
        
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
        const response = await fetch('/api/espacios/disponibles-por-tipo');
        
        if (response.ok) {
            espaciosPorTipo = await response.json();
            actualizarDisponibilidad();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== ACTUALIZAR DISPONIBILIDAD ==========
function actualizarDisponibilidad() {
    // Actualizar cada tipo de espacio
    const regularElement = document.getElementById('disponibles-regular');
    const motoElement = document.getElementById('disponibles-moto');
    const discapacitadoElement = document.getElementById('disponibles-discapacitado');
    
    if (regularElement) {
        regularElement.textContent = espaciosPorTipo.regular || 0;
    }
    if (motoElement) {
        motoElement.textContent = espaciosPorTipo.moto || 0;
    }
    if (discapacitadoElement) {
        discapacitadoElement.textContent = espaciosPorTipo.discapacitado || 0;
    }
}

// ========== UTILIDADES ==========
function capitalizarPrimeraLetra(texto) {
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}


