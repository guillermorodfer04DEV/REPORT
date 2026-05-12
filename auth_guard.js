// Este script verifica contra el backend de Python si hay una sesión activa.
// Si no la hay, redirige inmediatamente a la página principal.

(async function protegerPagina() {
    const API_URL = "http://127.0.0.1:5000"; // Ajusta al servidor real

    try {
        const response = await fetch(`${API_URL}/check_auth`);
        if (!response.ok) {
            // Si el status es 401 (No autorizado), expulsar al index
            window.location.href = "index.html"; 
        }
        // Si todo está bien, la página se carga normalmente
    } catch (error) {
        console.error("Error validando sesión:", error);
        window.location.href = "index.html";
    }
})();