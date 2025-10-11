// transacciones.js - Gestión del historial de transacciones

document.addEventListener('DOMContentLoaded', () => {
    cargarTransacciones();
    cargarEstadisticas();
});

// ========== CARGAR TRANSACCIONES ==========
async function cargarTransacciones() {
    try {
        const response = await fetch('/api/transacciones');
        
        if (!response.ok) {
            throw new Error('Error al cargar transacciones');
        }
        
        const transacciones = await response.json();
        mostrarTransacciones(transacciones);
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron cargar las transacciones'
        });
    }
}

// ========== MOSTRAR TRANSACCIONES EN LA TABLA ==========
function mostrarTransacciones(transacciones) {
    const tbody = document.querySelector('tbody');
    
    if (transacciones.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No hay transacciones registradas</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    transacciones.forEach(transaccion => {
        const row = crearFilaTransaccion(transaccion);
        tbody.appendChild(row);
    });
}

// ========== CREAR FILA DE TRANSACCIÓN ==========
function crearFilaTransaccion(transaccion) {
    const tr = document.createElement('tr');
    
    // Formatear fecha de salida
    const salida = new Date(transaccion.fecha_salida);
    const fechaFormateada = salida.toLocaleDateString('es-DO', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // Tiempo de estancia
    const tiempoEstancia = transaccion.tiempo_estancia 
        ? transaccion.tiempo_estancia.texto 
        : 'N/A';
    
    // Método de pago con icono
    const metodosIconos = {
        'efectivo': '<i class="fas fa-money-bill-wave" style="color: #28a745;"></i> Efectivo',
        'tarjeta': '<i class="fas fa-credit-card" style="color: #007bff;"></i> Tarjeta'
    };
    const metodoPago = metodosIconos[transaccion.metodo_pago] || transaccion.metodo_pago;
    
    // Monto
    const monto = transaccion.monto_formateado || `RD$${transaccion.monto.toFixed(2)}`;
    
    tr.innerHTML = `
        <td><strong>#${transaccion.id}</strong></td>
        <td>${fechaFormateada}</td>
        <td>
            <strong>${transaccion.placa}</strong>
            <br>
            <small style="color: #666;">
                ${capitalizarPrimeraLetra(transaccion.tipo_vehiculo)} - 
                Espacio ${transaccion.espacio ? transaccion.espacio.numero : 'N/A'}
            </small>
        </td>
        <td>${tiempoEstancia}</td>
        <td><strong style="color: #28a745;">${monto}</strong></td>
        <td>${metodoPago}</td>
    `;
    
    return tr;
}

// ========== CARGAR ESTADÍSTICAS ==========
async function cargarEstadisticas() {
    try {
        const response = await fetch('/api/transacciones/estadisticas');
        
        if (!response.ok) {
            throw new Error('Error al cargar estadísticas');
        }
        
        const stats = await response.json();
        mostrarEstadisticas(stats);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== MOSTRAR ESTADÍSTICAS ==========
function mostrarEstadisticas(stats) {
    // Buscar o crear contenedor de estadísticas
    const statsContainer = document.getElementById('stats-container');
    
    if (statsContainer) {
        statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <i class="fas fa-receipt"></i>
                    <div class="stat-content">
                        <h3>${stats.total_transacciones}</h3>
                        <p>Transacciones</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <i class="fas fa-dollar-sign"></i>
                    <div class="stat-content">
                        <h3>${stats.total_recaudado_formateado}</h3>
                        <p>Total Recaudado</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <i class="fas fa-money-bill-wave"></i>
                    <div class="stat-content">
                        <h3>${stats.metodos_pago.efectivo}</h3>
                        <p>Pagos en Efectivo</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <i class="fas fa-credit-card"></i>
                    <div class="stat-content">
                        <h3>${stats.metodos_pago.tarjeta}</h3>
                        <p>Pagos con Tarjeta</p>
                    </div>
                </div>
            </div>
        `;
    }
}

// ========== UTILIDADES ==========
function capitalizarPrimeraLetra(texto) {
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}
