// tickets.js - Gestión de tickets activos

document.addEventListener('DOMContentLoaded', () => {
    cargarTicketsActivos();
    
    // Auto-refrescar cada 30 segundos
    setInterval(cargarTicketsActivos, 30000);
});

// ========== CARGAR TICKETS ACTIVOS ==========
async function cargarTicketsActivos() {
    try {
        const response = await fetch('/api/tickets/activos');
        
        if (!response.ok) {
            throw new Error('Error al cargar tickets');
        }
        
        const tickets = await response.json();
        mostrarTickets(tickets);
        actualizarEstadisticas(tickets);
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron cargar los tickets'
        });
    }
}

// ========== MOSTRAR TICKETS EN LA TABLA ==========
function mostrarTickets(tickets) {
    const tbody = document.getElementById('tbody-tickets');
    
    if (tickets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="no-data">No hay vehículos en el estacionamiento</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    tickets.forEach(ticket => {
        const row = crearFilaTicket(ticket);
        tbody.appendChild(row);
    });
}

// ========== CREAR FILA DE TICKET ==========
function crearFilaTicket(ticket) {
    const tr = document.createElement('tr');
    
    // Usar tiempo transcurrido calculado por el backend
    const tiempoTranscurrido = ticket.tiempo_transcurrido 
        ? ticket.tiempo_transcurrido.texto 
        : 'Calculando...';
    
    // Formatear hora de entrada
    const entrada = new Date(ticket.fecha_entrada);
    const horaEntrada = entrada.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
    
    // Icono según tipo
    const iconosTipo = {
        'regular': 'fa-car',
        'moto': 'fa-motorcycle',
        'discapacitado': 'fa-wheelchair'
    };
    const icono = iconosTipo[ticket.tipo_vehiculo] || 'fa-car';
    
    tr.innerHTML = `
        <td><strong>#${ticket.id}</strong></td>
        <td><strong>${ticket.placa}</strong></td>
        <td>
            <span class="badge-espacio">${ticket.espacio ? ticket.espacio.numero : 'N/A'}</span>
        </td>
        <td>
            <i class="fas ${icono}"></i>
            ${capitalizarPrimeraLetra(ticket.tipo_vehiculo)}
        </td>
        <td>${horaEntrada}</td>
        <td><strong>${tiempoTranscurrido}</strong></td>
        <td>
            <button class="btn-icon btn-salida" onclick="registrarSalida(${ticket.id})" title="Registrar Salida">
                <i class="fas fa-sign-out-alt"></i> Salida
            </button>
        </td>
    `;
    
    return tr;
}

// ========== REGISTRAR SALIDA ==========
async function registrarSalida(ticketId) {
    try {
        // Confirmar
        const result = await Swal.fire({
            title: '¿Registrar salida?',
            text: 'Se calculará el tiempo y el monto a cobrar',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sí, registrar salida',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#2486DB'
        });
        
        if (!result.isConfirmed) {
            return;
        }
        
        // Mostrar loading
        Swal.fire({
            title: 'Calculando...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/api/tickets/${ticketId}/salida`, {
            method: 'POST'
        });
        
        const result2 = await response.json();
        
        if (!response.ok) {
            throw new Error(result2.error || 'Error al registrar salida');
        }
        
        // Usar formato de moneda dominicana
        const montoFormateado = result2.monto_formateado || `RD$${result2.monto.toFixed(2)}`;
        
        // Mostrar resumen con formato mejorado
        Swal.fire({
            icon: 'success',
            title: '¡Salida Registrada!',
            html: `
                <div style="text-align: left; padding: 1rem;">
                    <p><strong>Placa:</strong> ${result2.ticket.placa}</p>
                    <p><strong>Tiempo de estancia:</strong> ${result2.tiempo_estancia_horas} horas</p>
                    
                    <div style="background: linear-gradient(135deg, #f0f8ff 0%, #e6f2ff 100%); 
                                padding: 1.5rem; 
                                border-radius: 12px; 
                                margin: 1.5rem 0; 
                                border-left: 4px solid #2486DB;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <h2 style="color: #2486DB; 
                                   margin: 0 0 0.5rem 0; 
                                   text-align: center; 
                                   font-size: 3rem;
                                   font-weight: bold;">
                            ${montoFormateado}
                        </h2>
                        <p style="text-align: center; 
                                  color: #666; 
                                  margin: 0; 
                                  font-size: 0.95rem;
                                  font-weight: 500;">
                            Pesos Dominicanos
                        </p>
                    </div>
                    
                    <p style="text-align: center; 
                              color: #28a745; 
                              font-weight: 600;
                              margin: 0;">
                        <i class="fas fa-check-circle"></i> Monto a cobrar
                    </p>
                </div>
            `,
            confirmButtonText: 'Aceptar',
            confirmButtonColor: '#2486DB',
            width: '500px'
        });
        
        // Recargar tickets
        cargarTicketsActivos();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== ACTUALIZAR ESTADÍSTICAS ==========
function actualizarEstadisticas(tickets) {
    document.getElementById('stat-total-tickets').textContent = tickets.length;
}

// ========== UTILIDADES ==========
function capitalizarPrimeraLetra(texto) {
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}

