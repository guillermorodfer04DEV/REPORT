(async function protegerPagina() {
    // 1. Corregimos la URL base (sin el /login al final)
    const API_URL = "https://guillermodev.pythonanywhere.com"; 

    try {
        // 2. Agregamos credentials: 'include' para que el navegador envíe la cookie de sesión
        const response = await fetch(`${API_URL}/check_auth`, {
            method: 'GET',
            credentials: 'include' 
        });

        if (!response.ok) {
            // Si el servidor responde 401, volvemos al inicio
            window.location.href = "index.html"; 
        }
    } catch (error) {
        console.error("Error validando sesión:", error);
        window.location.href = "index.html";
    }
})();