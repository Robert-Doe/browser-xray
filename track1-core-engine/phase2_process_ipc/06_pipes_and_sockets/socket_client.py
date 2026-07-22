"""
Module 6: pipes_and_sockets -- TCP socket CLIENT.
"""

import socket
import sys

HOST = "127.0.0.1"
PORT = 51837


def main() -> None:
    message = sys.argv[1] if len(sys.argv) > 1 else "hello over TCP"
    print(f"[client] connecting to {HOST}:{PORT} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print("[client] connected.")

        sock.sendall(message.encode("utf-8"))
        print(f"[client] sent: {message!r}")

        reply = sock.recv(4096)
        print(f"[client] received reply: {reply.decode('utf-8')!r}")


if __name__ == "__main__":
    main()
