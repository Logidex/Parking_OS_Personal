// dashboard.js - Gestión del dashboard principal

document.addEventListener('DOMContentLoaded', () => {
    // Solo cargar estadísticas si estamos en el dashboard
    if (window.location.pathname === '/dashboard') {
        cargarEstadisticas();
        cargarActividadReciente();
        cargarOcupacionPorTipo();
        
        // Auto-refrescar cada 30 segundos
        setInterval(() => {
            cargarEstadisticas();
            cargarActividadReciente();
            cargarOcupacionPorTipo();
        }, 30000);
    }
});

// ========== CARGAR ESTADÍSTICAS ==========
async function cargarEstadisticas() {
    try {
        const response = await fetch('/api/dashboard/estadisticas');
        
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
    // Actualizar tarjetas de estadísticas
    const statCards = document.querySelectorAll('.stat-card');
    
    if (statCards.length >= 4) {
        // Total Vehículos
        statCards[0].querySelector('.stat-number').textContent = stats.total_vehiculos;
        
        // Espacios Ocupados
        statCards[1].querySelector('.stat-number').textContent = 
            `${stats.espacios_ocupados} / ${stats.total_espacios}`;
        statCards[1].querySelector('.stat-number').innerHTML += 
            `<br><small style="font-size: 0.8rem; color: #666;">${stats.porcentaje_ocupacion}% ocupación</small>`;
        
        // Tickets Activos
        statCards[2].querySelector('.stat-number').textContent = stats.tickets_activos;
        
        // Ingresos Hoy
        statCards[3].querySelector('.stat-number').textContent = stats.ingresos_hoy_formateado;
        statCards[3].querySelector('.stat-number').innerHTML += 
            `<br><small style="font-size: 0.8rem; color: #666;">${stats.transacciones_hoy} transacciones</small>`;
    }
}

// ========== CARGAR ACTIVIDAD RECIENTE ==========
async function cargarActividadReciente() {
    try {
        const response = await fetch('/api/dashboard/actividad-reciente');
        
        if (!response.ok) {
            throw new Error('Error al cargar actividad');
        }
        
        const actividades = await response.json();
        mostrarActividadReciente(actividades);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== MOSTRAR ACTIVIDAD RECIENTE ==========
function mostrarActividadReciente(actividades) {
    const tbody = document.querySelector('.recent-activity tbody');
    
    if (!tbody) return;
    
    if (actividades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="no-data">No hay actividad reciente</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    actividades.forEach(actividad => {
        const row = crearFilaActividad(actividad);
        tbody.appendChild(row);
    });
}

// ========== CREAR FILA DE ACTIVIDAD ==========
function crearFilaActividad(actividad) {
    const tr = document.createElement('tr');
    
    // Formatear hora
    const fecha = new Date(actividad.fecha_entrada);
    const hora = fecha.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // Acción y estado según el tipo
    let accion, estadoBadge;
    
    if (actividad.estado === 'activo') {
        accion = `Ingresó (${actividad.tiempo_transcurrido || 'Ahora'})`;
        estadoBadge = '<span class="badge badge-success">Activo</span>';
    } else {
        accion = `Salió - ${actividad.monto_formateado || 'N/A'}`;
        estadoBadge = '<span class="badge badge-secondary">Finalizado</span>';
    }
    
    // Icono según tipo de vehículo
    const iconos = {
        'regular': 'fa-car',
        'moto': 'fa-motorcycle',
        'discapacitado': 'fa-wheelchair'
    };
    const icono = iconos[actividad.tipo_vehiculo] || 'fa-car';
    
    tr.innerHTML = `
        <td>${hora}</td>
        <td>
            <i class="fas ${icono}"></i>
            <strong>${actividad.placa}</strong>
            ${actividad.espacio ? `<br><small>Espacio ${actividad.espacio}</small>` : ''}
        </td>
        <td>${accion}</td>
        <td>${estadoBadge}</td>
    `;
    
    return tr;
}

// ========== CARGAR OCUPACIÓN POR TIPO ==========
async function cargarOcupacionPorTipo() {
    try {
        const response = await fetch('/api/dashboard/ocupacion-por-tipo');
        
        if (!response.ok) {
            throw new Error('Error al cargar ocupación');
        }
        
        const ocupacion = await response.json();
        mostrarOcupacionPorTipo(ocupacion);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== MOSTRAR OCUPACIÓN POR TIPO ==========
function mostrarOcupacionPorTipo(ocupacion) {
    const container = document.getElementById('ocupacion-por-tipo');
    
    if (!container) return;
    
    container.innerHTML = `
        <div class="ocupacion-card">
            <h4>🚗 Regulares</h4>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${ocupacion.regular.porcentaje}%; background: #2486DB;"></div>
            </div>
            <p>${ocupacion.regular.ocupados} / ${ocupacion.regular.total} ocupados (${ocupacion.regular.porcentaje}%)</p>
        </div>
        
        <div class="ocupacion-card">
            <h4>🏍️ Motos</h4>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${ocupacion.moto.porcentaje}%; background: #28a745;"></div>
            </div>
            <p>${ocupacion.moto.ocupados} / ${ocupacion.moto.total} ocupados (${ocupacion.moto.porcentaje}%)</p>
        </div>
        
        <div class="ocupacion-card">
            <h4>♿ Discapacitados</h4>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${ocupacion.discapacitado.porcentaje}%; background: #ffc107;"></div>
            </div>
            <p>${ocupacion.discapacitado.ocupados} / ${ocupacion.discapacitado.total} ocupados (${ocupacion.discapacitado.porcentaje}%)</p>
        </div>
    `;
}




