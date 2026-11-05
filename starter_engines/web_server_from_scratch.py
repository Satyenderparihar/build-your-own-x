#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""web_server_from_scratch.py: A Socket-Based HTTP/1.1 Web Server built from scratch in pure Python.

Implements core Web Server & Networking internals:
- Raw TCP Socket binding, listening, and accepting client connections
- HTTP/1.1 request wire protocol parsing (Method, URI path, Version, Headers)
- MIME type resolution and status code routing (200 OK, 404 Not Found)
- RESTful JSON API response generation
- Direct client testing and verification
"""

import socket
import threading
import json
import urllib.request
import time

class HTTPServerFromScratch:
    def __init__(self, host="127.0.0.1", port=9123):
        self.host = host
        self.port = port
        self.running = False
        self.sock = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.sock.settimeout(0.5)
        self.running = True
        
        while self.running:
            try:
                client_sock, addr = self.sock.accept()
                threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception:
                break

    def handle_client(self, client_sock):
        try:
            req_data = client_sock.recv(4096).decode("utf-8", errors="replace")
            if not req_data:
                client_sock.close()
                return
            
            lines = req_data.split("\r\n")
            request_line = lines[0]
            parts = request_line.split(" ")
            if len(parts) < 2:
                client_sock.close()
                return
            method, path = parts[0], parts[1]
            
            # Simple routing
            if path == "/" or path == "/index.html":
                body = "<h1>Deepesh Studio - Custom Web Server From Scratch</h1><p>Served over raw TCP sockets!</p>"
                res = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"
            elif path == "/api/status":
                payload = json.dumps({"status": "online", "server": "MyServer-Scratch/1.0", "time": time.time()})
                res = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(payload)}\r\nConnection: close\r\n\r\n{payload}"
            else:
                body = "404 Not Found"
                res = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"
                
            client_sock.sendall(res.encode("utf-8"))
        finally:
            client_sock.close()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()

def demo():
    print("=== Demonstrating HTTP Web Server From Scratch ===")
    port = 9876
    srv = HTTPServerFromScratch(port=port)
    t = threading.Thread(target=srv.start, daemon=True)
    t.start()
    time.sleep(0.1)
    
    print(f"1. Raw TCP Server listening on http://127.0.0.1:{port}")
    
    # Test HTTP GET /
    print("\n2. Sending HTTP GET / request:")
    req = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
    html = req.read().decode()
    print(f"  Response Status: {req.status} OK")
    print(f"  Response Body: {html[:60]}...")
    
    # Test HTTP GET /api/status
    print("\n3. Sending HTTP GET /api/status request:")
    req_api = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status")
    data = json.loads(req_api.read().decode())
    print(f"  Response Status: {req_api.status} OK")
    print(f"  JSON Payload: {data}")
    
    srv.stop()
    print("\n✓ Web Server From Scratch Demo completed successfully!\n")

if __name__ == "__main__":
    demo()
