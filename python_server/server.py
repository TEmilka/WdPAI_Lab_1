import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Type
import uuid
import psycopg2
import os
import time

DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_NAME = os.environ.get('DB_NAME', 'baza_lab2')
DB_USER = os.environ.get('DB_USER', 'emilia.trybala')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'emilka2024')

def add_default_user(cursor):
    cursor.execute("SELECT * FROM users WHERE id = %s;", ('123e4567-e89b-12d3-a456-426614174000',))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (id, first_name, last_name, role) VALUES (%s, %s, %s, %s);",
                       ('123e4567-e89b-12d3-a456-426614174000', 'Michał', 'Mucha', 'Instruktor'))
        conn.commit()
        print("Dodano domyślnego użytkownika Michała Muchę.")

def connect_to_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Połączono z bazą danych")
            return conn
        except psycopg2.OperationalError:
            print("Błąd połączenia z bazą danych, ponawianie za 5 sekund...")
            time.sleep(5)

conn = connect_to_db()
cursor = conn.cursor()
add_default_user(cursor)

class SimpleRequestHandler(BaseHTTPRequestHandler):

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def get_team_members(self):
        try:
            cursor.execute("SELECT * FROM users;")
            rows = cursor.fetchall()
            return [{
                'id': str(row[0]),
                'first_name': row[1],
                'last_name': row[2],
                'role': row[3]
            } for row in rows]
        except Exception as e:
            return {"error": str(e)}

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        try:
            users = self.get_team_members()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()

            self.wfile.write(json.dumps({"users": users}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_POST(self) -> None:
        content_length: int = int(self.headers['Content-Length'])
        post_data: bytes = self.rfile.read(content_length)
        received_data: dict = json.loads(post_data.decode())

        new_user_id = str(uuid.uuid4())

        try:
            cursor.execute("INSERT INTO users (id, first_name, last_name, role) VALUES (%s, %s, %s, %s);",
                           (new_user_id, received_data.get('first_name'), received_data.get('last_name'),
                            received_data.get('role')))
            conn.commit()

            users = self.get_team_members()

            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"users": users}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_DELETE(self) -> None:
        path_parts = self.path.split('/')
        if len(path_parts) == 2:
            user_id = path_parts[1]

            try:
                cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    users = self.get_team_members()
                    response = {
                        "message": "User deleted successfully",
                        "team_members": users
                    }

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    response = {"error": "User not found"}
                    self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(400)
            self.send_cors_headers()
            self.end_headers()


def run(
        server_class: Type[HTTPServer] = HTTPServer,
        handler_class: Type[BaseHTTPRequestHandler] = SimpleRequestHandler,
        port: int = 8000
) -> None:
    server_address: tuple = ('', port)
    httpd: HTTPServer = server_class(server_address, handler_class)
    print(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
