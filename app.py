from flask import Flask, request, jsonify, session
import hashlib
import uuid
import requests
from flask_cors import CORS 

app = Flask(__name__)

# MODIFICACIÓN NECESARIA: Permitir credenciales para que la sesión funcione
CORS(app, supports_credentials=True) 

app.secret_key = 'SECURITY_KEY_LOL'

# Configuración de seguridad para Cookies en la nube
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True
)

GOOGLE_SHEETS_WEBHOOK = "https://script.google.com/macros/s/AKfycbxIy5MkktHy7xHajr2SH2aFagGLUTtpQG6NHSbqspE7pSnRINcPED9v1q4LaYLf3diq/exec"

users_db = {
    "admin": {
        "id": "USR-0000",
        "hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "dev"
    }
}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    pw_hash = hashlib.sha256(password.encode()).hexdigest()

    # Mantenemos el admin original como un "Plan B" por si Google Sheets está vacío o falla
    user_local = users_db.get(username)
    if user_local and user_local['hash'] == pw_hash:
        session['user'] = username
        session['role'] = user_local['role']
        session.modified = True
        return jsonify({"success": True, "role": session['role']})

    # Verificamos contra Google Sheets
    try:
        resp = requests.get(GOOGLE_SHEETS_WEBHOOK)
        usuarios_sheets = resp.json()
        
        for row in usuarios_sheets:
            if row.get('usuario') == username and row.get('pass_hash') == pw_hash:
                session['user'] = username
                session['role'] = row.get('role', 'user')
                session.modified = True
                return jsonify({"success": True, "role": session['role']})
                
        return jsonify({"success": False, "message": "Credenciales inválidas"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": "Error al conectar con la base de datos de usuarios"}), 500

@app.route('/register', methods=['POST'])
def register():
    if session.get('role') != 'dev':
        return jsonify({"success": False, "message": "No tienes permisos"}), 403

    data = request.json
    new_user = data.get('username')
    new_password = data.get('password')
    estado = data.get('estado', 'No definido')
    is_admin = data.get('is_admin', False)
    
    role = "dev" if is_admin else "user"
    user_id = f"USR-{str(uuid.uuid4())[:8].upper()}"
    pass_hash = hashlib.sha256(new_password.encode()).hexdigest()

    # Enviar a Google Sheets con la nueva estructura
    sheet_data = {
        "usuario": new_user,
        "id_usuario": user_id,
        "pass_real": new_password,
        "pass_hash": pass_hash,
        "estado": estado,
        "role": role
    }
    
    try:
        requests.post(GOOGLE_SHEETS_WEBHOOK, json=sheet_data)
        return jsonify({"success": True, "message": f"Usuario {new_user} creado con éxito"})
    except:
        return jsonify({"success": False, "message": "Error guardando en Google Sheets"}), 500

@app.route('/check_auth', methods=['GET'])
def check_auth():
    if 'user' in session:
        return jsonify({"authenticated": True, "user": session['user'], "role": session['role']})
    return jsonify({"authenticated": False}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

# En PythonAnywhere esto no se usa, pero lo dejamos para tu local
if __name__ == '__main__':
    app.run(debug=True, port=5000)