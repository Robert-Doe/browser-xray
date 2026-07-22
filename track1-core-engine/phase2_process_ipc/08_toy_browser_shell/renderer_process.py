"""
Module 8: toy_browser_shell -- the RENDERER PROCESS.

Connects back to the Browser Process's listening socket, announces its
own PID, then services commands: "load_url" (simulate rendering a page
and report back a title) and "shutdown" (acknowledge and exit).

IMPORTANT HONESTY NOTE: this renderer does NOT actually parse HTML,
run CSS, or execute JavaScript yet -- that real machinery is what
Track 2, Phases 6-8 build, module by module, on top of this exact
process/IPC shell. Here, "rendering" is a deliberate stand-in so this
module's own claim (process + IPC shape) can be proven in isolation,
without needing a real parser to already exist.
"""

import os
import socket
import sys

from ipc_protocol import recv_message, send_message


def main() -> None:
    port = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", port))

    send_message(sock, {"type": "hello", "pid": os.getpid()})

    while True:
        message = recv_message(sock)

        if message["type"] == "load_url":
            url = message["url"]
            # Simulated render -- see module docstring.
            title = f"(toy render of {url})"
            send_message(
                sock,
                {"type": "loaded", "url": url, "title": title, "pid": os.getpid()},
            )

        elif message["type"] == "shutdown":
            send_message(sock, {"type": "shutdown_ack", "pid": os.getpid()})
            break

    sock.close()


if __name__ == "__main__":
    main()
