(async function protegerPagina() {
    // 1. Corregimos la URL base (sin el /login al final)
    const API_URL = 'https://guillermodev.pythonanywhere.com';

function mostrarInterfaz(username, role) {
    document.getElementById('loginModal').style.display = 'none';
    
    // Configurar Badge
    document.getElementById('userBadge').style.display = 'block';
    document.getElementById('userNameDisplay').innerText = username;
    document.getElementById('userDevTag').style.display = (role === 'dev') ? 'inline-block' : 'none';
    
    // Guardar el nombre para que otras páginas (como reporte.html) lo usen
    localStorage.setItem('tecno_current_user', username);
    localStorage.setItem('tecno_current_role', role);

    cargarMenu(role);
}

function cargarMenu(role) {
    const container = document.getElementById('gridContainer');
    container.innerHTML = "";

    // Cargar botones normales
    configBotones.forEach(btn => {
        const item = document.createElement('a');
        item.href = btn.link;
        item.className = 'btn-nav';
        item.innerHTML = `<img src="${btn.icono}"><span>${btn.nombre}</span>`;
        container.appendChild(item);
    });

    // Cargar botón Dev SIEMPRE que sea dev
    if(role === 'dev') {
        const devBtn = document.createElement('div');
        devBtn.id = 'devPanelBtn';
        devBtn.className = 'btn-nav accent';
        devBtn.style.cursor = 'pointer';
        devBtn.innerHTML = `<i>⚙️</i><span>Crear Usuario</span>`;
        devBtn.onclick = () => document.getElementById('createUserModal').style.display = 'flex';
        container.appendChild(devBtn);
    }
}

// Validación inicial al abrir la página
async function verificarSesion() {
    try {
        const resp = await fetch(`${API_URL}/check_auth`, {credentials: 'include'});
        const data = await resp.json();
        if(data.authenticated) {
            mostrarInterfaz(data.user, data.role);
        } else {
            document.getElementById('loginModal').style.display = 'flex';
            document.getElementById('userBadge').style.display = 'none';
        }
    } catch(e) {
        document.getElementById('loginModal').style.display = 'flex';
    }
}

// Al loguearse
async function login() {
    const u = document.getElementById('userIn').value;
    const p = document.getElementById('passIn').value;
    
    try {
        const resp = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p}),
            credentials: 'include'
        });
        const data = await resp.json();
        if(data.success) {
            mostrarInterfaz(u, data.role); // Usamos el nombre que introdujo
        } else {
            alert("Error: " + data.message);
        }
    } catch(e) { alert("Error de conexión"); }
}

// Cerrar sesión
async function cerrarSesion() {
    await fetch(`${API_URL}/logout`, { method: 'POST', credentials: 'include' });
    localStorage.removeItem('tecno_current_user');
    localStorage.removeItem('tecno_current_role');
    location.reload(); // Recarga la página para devolverte al login
}

// Cambiar contraseña
function abrirCambioClave() {
    document.getElementById('userMenuModal').style.display = 'none';
    document.getElementById('changePassModal').style.display = 'flex';
}

async function cambiarPassword() {
    const curr = document.getElementById('currentPass').value;
    const newP = document.getElementById('newPass').value;
    if(!curr || !newP) return alert("Llena ambos campos");

    try {
        const resp = await fetch(`${API_URL}/change_password`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({current_password: curr, new_password: newP}),
            credentials: 'include'
        });
        const data = await resp.json();
        if(data.success) {
            alert("Contraseña cambiada con éxito.");
            document.getElementById('changePassModal').style.display = 'none';
            document.getElementById('currentPass').value = '';
            document.getElementById('newPass').value = '';
        } else {
            alert("Error: " + data.message);
        }
    } catch(e) { alert("Error de conexión"); }
}

// Ejecutamos la verificación al cargar
window.onload = verificarSesion;
})();