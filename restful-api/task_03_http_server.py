#!/usr/bin/python3
"""Simple API using http.server"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class SimpleAPIHandler(BaseHTTPRequestHandler):

    def _send_response(self, code=200, content_type="text/plain"):
        """Helper to send HTTP headers"""
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""

        if self.path == "/":
            self._send_response(200)
            self.wfile.write(b"Hello, this is a simple API!")

        elif self.path == "/data":
            self._send_response(200, "application/json")
            data = {
                "name": "John",
                "age": 30,
                "city": "New York"
            }
            self.wfile.write(json.dumps(data).encode())

        elif self.path == "/status":
            self._send_response(200, "application/json")
            self.wfile.write(json.dumps({"status": "OK"}).encode())

        elif self.path == "/info":
            self._send_response(200, "application/json")
            info = {
                "version": "1.0",
                "description": "A simple API built with http.server"
            }
            self.wfile.write(json.dumps(info).encode())

        else:
            self._send_response(404, "application/json")
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())


def run(server_class=HTTPServer, handler_class=SimpleAPIHandler, port=8000):
    """Start server"""
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
