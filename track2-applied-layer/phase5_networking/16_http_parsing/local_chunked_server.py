"""
Module 16: http_parsing -- a tiny local server that emits a REAL,
genuinely wire-format chunked HTTP/1.1 response.

Real third-party services that use chunked encoding aren't reliably
available for a repeatable course exercise (services go down, change
behavior, rate-limit). Running our own minimal server means the
chunked-encoding demonstration is still a real client parsing real
bytes off a real socket -- just a socket we control, so the exercise
is reliable every time it's run.
"""

import socket

HOST = "127.0.0.1"
PORT = 51950


def build_chunked_response() -> bytes:
    chunks = [b"The quick ", b"brown fox ", b"jumps."]
    body = b""
    for chunk in chunks:
        size_hex = format(len(chunk), "x").encode("ascii")
        body += size_hex + b"\r\n" + chunk + b"\r\n"
    body += b"0\r\n\r\n"  # terminating zero-length chunk

    headers = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Connection: close\r\n"
        b"\r\n"
    )
    return headers + body


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        print(f"[chunked server] listening on {HOST}:{PORT}", flush=True)

        conn, _addr = server_sock.accept()
        with conn:
            conn.recv(4096)  # discard the request -- we always send the same response
            response = build_chunked_response()
            conn.sendall(response)
            print(f"[chunked server] sent a real chunked response ({len(response)} bytes)", flush=True)


if __name__ == "__main__":
    main()
