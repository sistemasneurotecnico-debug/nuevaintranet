import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Tabla Personal
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        especialidad TEXT NOT NULL,
        estado TEXT NOT NULL,
        color_estado TEXT NOT NULL
    )
    ''')

    # Tabla Usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nombre_completo TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'employee'
    )
    ''')

    # Tabla Consultas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente TEXT NOT NULL,
        hora TEXT NOT NULL
    )
    ''')

    # Tabla Noticias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS noticias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        contenido TEXT NOT NULL,
        icon TEXT NOT NULL
    )
    ''')

    # Tabla Logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        mensaje TEXT NOT NULL
    )
    ''')

    # Datos iniciales (si las tablas están vacías)
    cursor.execute('SELECT COUNT(*) FROM personal')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO personal (nombre, especialidad, estado, color_estado) VALUES (?, ?, ?, ?)', [
            ('Dr. Alexander Thorne', 'Neurocirugía', 'Activo', '#4ade80'),
            ('Dra. Elena Vance', 'Neurología Clínica', 'En Consulta', '#facc15')
        ])

    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO usuarios (username, password, nombre_completo, role) VALUES (?, ?, ?, ?)', [
            ('admin', 'admin123', 'Administrador NeuroDX', 'admin'),
            ('user', 'user123', 'Empleado de Planta', 'employee')
        ])

    cursor.execute('SELECT COUNT(*) FROM consultas')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO consultas (paciente, hora) VALUES (?, ?)', [
            ('Paciente #4402', '09:30 AM'),
            ('Paciente #4405', '11:00 AM')
        ])

    cursor.execute('SELECT COUNT(*) FROM noticias')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO noticias (titulo, contenido, icon) VALUES (?, ?, ?)', [
            ('Nuevo Ala de Neuro-Imagen', 'La inauguración será este viernes. Contamos con tecnología de resonancia magnética de 7 Teslas.', 'fa-hospital-user'),
            ('Reconocimiento Internacional', 'NeuroDX ha sido galardonado por sus aportes a la tele-cirugía robótica.', 'fa-award')
        ])

    cursor.execute('SELECT COUNT(*) FROM logs')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO logs (mensaje) VALUES (?)', [
            ('Intento de acceso exitoso - Usuario: admin_neuro',),
            ('Actualización de base de datos de pacientes completada.',),
            ('Backup automático generado en servidor remoto.',)
        ])

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

if __name__ == '__main__':
    init_db()
