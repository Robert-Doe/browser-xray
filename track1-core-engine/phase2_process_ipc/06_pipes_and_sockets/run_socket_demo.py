"""
Module 6: pipes_and_sockets -- orchestrates the TCP socket experiment.

Same structure as run_pipe_demo.py: Part A shows a real, deliberately
established channel working. Part B shows a connection attempt to a
port NOTHING is listening on being refused outright -- proving the
"no channel = no path" claim holds for sockets exactly as it did for
named pipes, despite the very different addressing scheme.
"""

import socket
import subprocess
import sys
import time

from socket_server import HOST, PORT

WRONG_PORT = 51838  # nothing listens here


def part_a_real_channel() -> None:
    print("=== Part A: a real, deliberately established TCP channel ===\n")
    server = subprocess.Popen(
        [sys.executable, "socket_server.py"], stdout=subprocess.PIPE, text=True
    )
    time.sleep(0.5)  # give the server time to bind + listen

    client = subprocess.run(
        [sys.executable, "socket_client.py", "hello over TCP"],
        capture_output=True,
        text=True,
        check=True,
    )
    print(client.stdout)

    server_out, _ = server.communicate(timeout=5)
    print(server_out)


def part_b_no_channel_exists() -> None:
    print(f"=== Part B: attempting to reach {HOST}:{WRONG_PORT} -- nothing is listening ===\n")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        try:
            sock.connect((HOST, WRONG_PORT))
            print("[client] UNEXPECTED: connection succeeded with no server present.")
        except ConnectionRefusedError as e:
            # The common case: nothing is listening, and the loopback
            # stack immediately answers the SYN with a TCP RST -- an
            # explicit, fast refusal.
            print(f"[client] connection actively refused by the kernel: {e}")
        except (TimeoutError, socket.timeout) as e:
            # Also a valid "no channel" outcome: on some machines a
            # local firewall/security product silently drops the SYN
            # instead of answering with RST, so the client sees a
            # timeout rather than an immediate refusal. Either way, no
            # data ever crossed -- see DECISIONS.md for why we treat
            # both as confirming the same underlying claim.
            print(f"[client] connection timed out waiting for a response "
                  f"(no RST received -- likely filtered rather than actively "
                  f"refused, but still: no channel, no data crossed): {e}")


def main() -> None:
    part_a_real_channel()
    part_b_no_channel_exists()


if __name__ == "__main__":
    main()
