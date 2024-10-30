import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Type
import uuid

class SimpleRequestHandler(BaseHTTPRequestHandler):

    user_list = [{
        'id': str(uuid.uuid4()),
        'first_name': 'Michal',
        'last_name': 'Mucha',
        'role': 'instructor'
    }]
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/team":
            response = {
                "team_members": self.user_list
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()

            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        content_length: int = int(self.headers['Content-Length'])
        post_data: bytes = self.rfile.read(content_length)
        received_data: dict = json.loads(post_data.decode())

        new_member = {
            'id': str(uuid.uuid4()),
            'first_name': received_data.get('first_name'),
            'last_name': received_data.get('last_name'),
            'role': received_data.get('role')
        }
        self.user_list.append(new_member)
        response: dict = {
            "message": "New team member added successfully",
            "team_members": self.user_list
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_DELETE(self) -> None:
        path_parts = self.path.split('/')
        if len(path_parts) == 3 and path_parts[1] == "team":
            member_id = path_parts[2]

            user_to_remove = next((user for user in self.user_list if user['id'] == member_id), None)
            if user_to_remove:
                self.user_list.remove(user_to_remove)
                response = {
                    "message": "User deleted successfully",
                    "team_members": self.user_list
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