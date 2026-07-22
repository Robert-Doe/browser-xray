"""
Module 18: cors_preflight -- a toy server that actually implements a
CORS policy: it allows cross-origin access from exactly ONE named
partner origin, and no other.

Real logic, not a stub: this server parses the incoming request's
Origin header and method, decides whether to grant access, and
responds with the real Access-Control-* headers a real CORS-compliant
server would send -- including handling OPTIONS preflight requests
distinctly from actual requests, per the real spec's two-step dance.
"""

import socket
import threading

PORT = 51972
ALLOWED_ORIGIN = "http://127.0.0.1:51999"  # the one origin this server trusts
BODY = b"cross-origin-accessible data (if your origin is allowed)"


def _parse_request(raw: bytes) -> dict:
    lines = raw.split(b"\r\n")
    method, path, _ = lines[0].split(b" ")
    headers = {}
    for line in lines[1:]:
        if not line:
            break
        name, _, value = line.partition(b":")
        headers[name.decode().strip().lower()] = value.decode().strip()
    return {"method": method.decode(), "path": path.decode(), "headers": headers}


def _handle(conn: socket.socket) -> None:
    with conn:
        raw = conn.recv(8192)
        if not raw:
            return
        request = _parse_request(raw)
        origin = request["headers"].get("origin")
        allowed = origin == ALLOWED_ORIGIN

        if request["method"] == "OPTIONS":
            # This is a PREFLIGHT request -- the browser asking
            # permission BEFORE sending the real one. No body, just a
            # policy answer.
            requested_method = request["headers"].get("access-control-request-method", "")
            lines = [b"HTTP/1.1 204 No Content"]
            if allowed:
                lines.append(f"Access-Control-Allow-Origin: {origin}".encode())
                lines.append(f"Access-Control-Allow-Methods: {requested_method}".encode())
                lines.append(b"Access-Control-Allow-Headers: X-Custom-Auth")
            lines.append(b"Connection: close")
            lines.append(b"\r\n")
            conn.sendall(b"\r\n".join(lines))
            return

        # The ACTUAL request (GET/PUT/etc.) -- always processed and
        # answered, regardless of CORS policy. Whether the browser
        # exposes this response to the calling script is a decision
        # made on the CLIENT side, based on whether the header below
        # is present and matches.
        header_lines = [
            b"HTTP/1.1 200 OK",
            b"Content-Type: text/plain",
            f"Content-Length: {len(BODY)}".encode(),
        ]
        if allowed:
            header_lines.append(f"Access-Control-Allow-Origin: {origin}".encode())
        header_lines.append(b"Connection: close")
        response = b"\r\n".join(header_lines) + b"\r\n\r\n" + BODY
        conn.sendall(response)


def _serve_forever() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", PORT))
        server_sock.listen(5)
        while True:
            conn, _addr = server_sock.accept()
            _handle(conn)


def start_cors_server() -> str:
    threading.Thread(target=_serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{PORT}/"
