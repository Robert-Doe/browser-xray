"""
Module 6: pipes_and_sockets -- TCP socket SERVER (the portable alternative
to a Windows-specific named pipe).

A named pipe (pipe_server.py) only works between processes on the same
Windows machine, addressed by name. A TCP socket works the same way in
principle -- explicit setup on both ends, kernel-mediated -- but is
addressed by (host, port) instead of a name, and works across machines,
which is exactly why Chromium's own Mojo IPC can run either over local
OS primitives or, when needed, over a network-capable transport.
"""

import socket

HOST = "127.0.0.1"
PORT = 51837  # arbitrary, high, unlikely to collide with a running service


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        print(f"[server] listening on {HOST}:{PORT}")

        conn, addr = server_sock.accept()
        print(f"[server] client connected from {addr}")
        with conn:
            data = conn.recv(4096)
            message = data.decode("utf-8")
            print(f"[server] received: {message!r}")

            reply = f"[server acknowledges]: {message}".encode("utf-8")
            conn.sendall(reply)
            print(f"[server] sent reply: {reply!r}")

    print("[server] socket closed, exiting.")


if __name__ == "__main__":
    main()
