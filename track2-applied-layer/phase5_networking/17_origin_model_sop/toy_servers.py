"""
Module 17: origin_model_sop -- two local "websites" standing in for
two different real origins.

Two loopback servers on two different ports. Port is part of the
origin tuple (Prerequisite 8) -- so these genuinely count as two
different origins, the same way https://bank.example and
https://attacker.example would, without this module needing real
domain names or certificates to make the point.
"""

import socket
import threading

ORIGIN_A_PORT = 51960  # stands in for the "attacker"/requesting page's own origin
ORIGIN_B_PORT = 51961  # stands in for the "victim" origin holding sensitive data


def _serve_forever(port: int, body: bytes) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", port))
        server_sock.listen(1)
        while True:
            conn, _addr = server_sock.accept()
            with conn:
                conn.recv(4096)
                response = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                    b"Connection: close\r\n\r\n" + body
                )
                conn.sendall(response)


def start_origin_servers() -> tuple[str, str]:
    """Starts both toy origin servers as background threads (they run
    for the lifetime of the calling process) and returns their base
    URLs."""
    threading.Thread(
        target=_serve_forever, args=(ORIGIN_A_PORT, b"public content from origin A"), daemon=True
    ).start()
    threading.Thread(
        target=_serve_forever, args=(ORIGIN_B_PORT, b"PRIVATE_SESSION_DATA_FOR_ORIGIN_B_ONLY"), daemon=True
    ).start()
    return f"http://127.0.0.1:{ORIGIN_A_PORT}/", f"http://127.0.0.1:{ORIGIN_B_PORT}/"
