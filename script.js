/**
 * NeuroDX Intranet - "Cerebro" Logic
 */

const API_BASE = 'http://localhost:8080/api';

function switchView(viewName) {
    const dashboardView = document.getElementById('dashboard-view');
    const adminView = document.getElementById('admin-view');
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => link.classList.remove('active'));

    if (viewName === 'dashboard') {
        dashboardView.style.display = 'block';
        adminView.style.display = 'none';
        navLinks[0].classList.add('active');
        loadDashboardData();
    } else if (viewName === 'admin') {
        dashboardView.style.display = 'none';
        adminView.style.display = 'block';
        navLinks[3].classList.add('active'); // "Administración" is the 4th link in new nav
        loadAdminData();
    }

    const activeView = viewName === 'dashboard' ? dashboardView : adminView;
    activeView.classList.remove('animate-fade');
    void activeView.offsetWidth;
    activeView.classList.add('animate-fade');
}

// Data Loading Functions
async function loadDashboardData() {
    try {
        const noticias = await fetch(`${API_BASE}/noticias`).then(r => r.json());
        renderNoticias(noticias);
    } catch (err) {
        console.error('Error loading dashboard data:', err);
    }
}

async function loadAdminData() {
    try {
        const [personal, logs] = await Promise.all([
            fetch(`${API_BASE}/personal`).then(r => r.json()),
            fetch(`${API_BASE}/logs`).then(r => r.json())
        ]);

        renderPersonal(personal);
        renderLogs(logs);
    } catch (err) {
        console.error('Error loading admin data:', err);
    }
}

// Rendering Functions
function renderNoticias(data) {
    const container = document.getElementById('noticias-container');
    if (!container) return;

    // We'll show up to 4 news items to match the design grid
    const images = [
        'https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=400',
        'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&q=80&w=400',
        'https://images.unsplash.com/photo-1454165833767-027ffea9e778?auto=format&fit=crop&q=80&w=400',
        'https://images.unsplash.com/photo-1522071823990-9512339540ac?auto=format&fit=crop&q=80&w=400'
    ];

    container.innerHTML = data.slice(0, 4).map((item, index) => `
        <div class="news-card">
            <div class="news-card-img" style="background-image: url('${images[index] || images[0]}');"></div>
            <div class="news-card-content">
                <h4 class="news-card-title">${item.titulo}</h4>
            </div>
        </div>
    `).join('');
}

function renderPersonal(data) {
    const container = document.getElementById('personal-table-body');
    if (!container) return;
    container.innerHTML = data.map(item => `
        <tr style="border-bottom: 1px solid var(--border);">
            <td style="padding: 1rem; display: flex; align-items: center; gap: 0.75rem;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: ${item.color_estado}; opacity: 0.8;"></div>
                <span style="font-weight: 500;">${item.nombre}</span>
            </td>
            <td style="padding: 1rem; color: var(--text-muted);">${item.especialidad}</td>
            <td style="padding: 1rem;"><span style="color: ${item.color_estado}; font-size: 0.85rem; font-weight: 600;">● ${item.estado}</span></td>
            <td style="padding: 1rem;"><i class="fas fa-edit" style="cursor: pointer; color: var(--text-muted);"></i></td>
        </tr>
    `).join('');
}

function renderLogs(data) {
    const container = document.getElementById('logs-container');
    if (!container) return;
    container.innerHTML = data.map(item => `
        <p style="margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(0,0,0,0.05);">
            <span style="font-weight: 600; color: var(--primary-purple);">${item.timestamp.split(' ')[1] || item.timestamp}</span> ${item.mensaje}
        </p>
    `).join('');
}

// Action Functions
async function addNewUser() {
    const nombre = prompt('Nombre del Médico:');
    const especialidad = prompt('Especialidad:');
    
    if (nombre && especialidad) {
        try {
            const res = await fetch(`${API_BASE}/personal`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, especialidad })
            });
            if (res.ok) {
                loadAdminData();
                alert('Médico agregado correctamente.');
            }
        } catch (err) {
            alert('Error al agregar médico.');
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('NeuroDX Cerebro Hub initialized.');
    switchView('dashboard');

    const searchInput = document.querySelector('.search-wrapper input');
    if (searchInput) {
        searchInput.addEventListener('focus', () => {
            document.querySelector('.search-wrapper').style.background = '#fff';
            document.querySelector('.search-wrapper').style.boxShadow = '0 0 0 2px var(--primary-purple)';
        });
        searchInput.addEventListener('blur', () => {
            document.querySelector('.search-wrapper').style.background = 'var(--bg-muted)';
            document.querySelector('.search-wrapper').style.boxShadow = 'none';
        });
    }
});
