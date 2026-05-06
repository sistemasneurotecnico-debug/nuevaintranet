import os
import sqlite3
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'neurodx_secret_key_ultra_secure'

DB_PATH = 'database.db'
PLUGINS_DIR = 'plugins'

if not os.path.exists(PLUGINS_DIR):
    os.makedirs(PLUGINS_DIR)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Authentication Wrapper ---
def login_required(role=None):
    def wrapper(f):
        def wrapped_f(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('No tienes permisos para acceder a esta sección.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        wrapped_f.__name__ = f.__name__
        return wrapped_f
    return wrapper

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    noticias = conn.execute('SELECT * FROM noticias').fetchall()
    consultas = conn.execute('SELECT * FROM consultas').fetchall()
    personal = conn.execute('SELECT * FROM personal').fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                           noticias=noticias, 
                           consultas=consultas, 
                           personal=personal,
                           user=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        # Simple password check for demo (can be upgraded to hash check)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['nombre'] = user['nombre_completo']
            
            flash(f'Bienvenido, {user["nombre_completo"]}', 'success')
            return redirect(url_for('admin' if user['role'] == 'admin' else 'index'))
        else:
            flash('Credenciales incorrectas.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Admin Panel (Escritorio) ---

@app.route('/admin')
@login_required(role='admin')
def admin():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    logs = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10').fetchall()
    conn.close()
    
    # Scan for plugins
    plugins = []
    for f in os.listdir(PLUGINS_DIR):
        if f.endswith('.py') or f.endswith('.php'):
            plugins.append({
                'name': f,
                'type': 'PHP' if f.endswith('.php') else 'Python',
                'status': 'Activo'
            })
            
    return render_template('admin.html', usuarios=usuarios, logs=logs, plugins=plugins, user=session)

@app.route('/admin/user/add', methods=['POST'])
@login_required(role='admin')
def add_user():
    username = request.form['username']
    password = request.form['password']
    nombre = request.form['nombre']
    role = request.form['role']
    
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO usuarios (username, password, nombre_completo, role) VALUES (?, ?, ?, ?)',
                     (username, password, nombre, role))
        conn.commit()
        conn.close()
        flash('Usuario añadido correctamente.', 'success')
    except sqlite3.IntegrityError:
        flash('El nombre de usuario ya existe.', 'error')
        
    return redirect(url_for('admin'))

# --- Plugin Execution Simulation ---
@app.route('/admin/plugin/run/<filename>')
@login_required(role='admin')
def run_plugin(filename):
    path = os.path.join(PLUGINS_DIR, filename)
    if not os.path.exists(path):
        return "Plugin no encontrado", 404
        
    if filename.endswith('.php'):
        try:
            result = subprocess.check_output(['php', path], stderr=subprocess.STDOUT, text=True)
            return f"<h3>Resultado del Plugin PHP:</h3><pre>{result}</pre>"
        except Exception as e:
            return f"Error ejecutando PHP (¿Está instalado?): {str(e)}", 500
    elif filename.endswith('.py'):
        # Safety warning: Running arbitrary code is dangerous
        return f"Ejecutando plugin Python: {filename} (Simulado por seguridad)"
        
    return "Tipo de archivo no soportado", 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
