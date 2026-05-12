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
    
    user = users_db.get(username)
    if user and user['hash'] == hashlib.sha256(password.encode()).hexdigest():
        session['user'] = username
        session['role'] = user['role']
        # Guardamos en la sesión para que check_auth funcione
        session.modified = True 
        return jsonify({"success": True, "role": user['role']})
    
    return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

@app.route('/register', methods=['POST'])
def register():
    if session.get('role') != 'dev':
        return jsonify({"success": False, "message": "No tienes permisos"}), 403

    data = request.json
    new_user = data.get('username')
    new_password = data.get('password')

    if new_user in users_db:
        return jsonify({"success": False, "message": "El usuario ya existe"}), 400

    user_id = f"USR-{str(uuid.uuid4())[:8].upper()}"
    pass_hash = hashlib.sha256(new_password.encode()).hexdigest()

    users_db[new_user] = {
        "id": user_id,
        "hash": pass_hash,
        "role": "user"
    }

    sheet_data = {
        "usuario": new_user,
        "id_usuario": user_id,
        "pass_real": new_password,
        "pass_hash": pass_hash
    }
    try:
        requests.post(GOOGLE_SHEETS_WEBHOOK, json=sheet_data)
    except:
        pass

    return jsonify({"success": True, "message": f"Usuario {new_user} creado con ID {user_id}"})

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