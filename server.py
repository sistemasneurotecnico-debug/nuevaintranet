import http.server
import socketserver
import json
import sqlite3
import os
from urllib.parse import urlparse, parse_qs

PORT = 8080
DB_FILE = 'database.db'

class IntranetAPIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path.startswith('/api/'):
            self.handle_api_get(parsed_path)
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/personal':
            self.handle_add_personal()
        elif parsed_path.path == '/api/sync':
            self.handle_sync()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_api_get(self, parsed_path):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        endpoint = parsed_path.path.replace('/api/', '')
        
        try:
            if endpoint == 'personal':
                cursor.execute('SELECT * FROM personal')
                data = [dict(row) for row in cursor.fetchall()]
            elif endpoint == 'consultas':
                cursor.execute('SELECT * FROM consultas')
                data = [dict(row) for row in cursor.fetchall()]
            elif endpoint == 'noticias':
                cursor.execute('SELECT * FROM noticias')
                data = [dict(row) for row in cursor.fetchall()]
            elif endpoint == 'logs':
                cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10')
                data = [dict(row) for row in cursor.fetchall()]
            else:
                self.send_error(404, "Unknown API endpoint")
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_error(500, str(e))
        finally:
            conn.close()

    def handle_add_personal(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        user_data = json.loads(post_data)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO personal (nombre, especialidad, estado, color_estado) VALUES (?, ?, ?, ?)',
                           (user_data['nombre'], user_data['especialidad'], 'Activo', '#4ade80'))
            cursor.execute('INSERT INTO logs (mensaje) VALUES (?)', (f"Nuevo usuario agregado: {user_data['nombre']}",))
            conn.commit()
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
        except Exception as e:
            self.send_error(500, str(e))
        finally:
            conn.close()

    def handle_sync(self):
        # Simulate a sync operation by adding a log
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO logs (mensaje) VALUES (?)', ("Sincronización manual con WordPress ejecutada.",))
            conn.commit()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "synced"}).encode())
        except Exception as e:
            self.send_error(500, str(e))
        finally:
            conn.close()

    # Enable CORS for development
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), IntranetAPIHandler) as httpd:
        print(f"Servidor backend de NeuroDX corriendo en http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")
