"""
Module 6: pipes_and_sockets -- orchestrates the named-pipe experiment.

Part A: spawn the server, then the client, as two SEPARATE processes,
and show a real message crossing the deliberately-established channel.

Part B: prove the negative -- attempt to connect to a pipe name no
server ever created, and show the kernel refuses the connection
outright. No channel was set up, so no data can cross, no matter how
correctly-formed the connection attempt is.
"""

import subprocess
import sys
import time

import pywintypes
import win32file

PIPE_NAME = r"\\.\pipe\module6_demo_pipe"
WRONG_PIPE_NAME = r"\\.\pipe\module6_demo_pipe_NO_SERVER_HERE"


def part_a_real_channel() -> None:
    print("=== Part A: a real, deliberately established channel ===\n")
    server = subprocess.Popen(
        [sys.executable, "pipe_server.py"], stdout=subprocess.PIPE, text=True
    )
    time.sleep(0.5)  # give CreateNamedPipe + ConnectNamedPipe time to start listening

    client = subprocess.run(
        [sys.executable, "pipe_client.py", "hello from the client process"],
        capture_output=True,
        text=True,
        check=True,
    )
    print(client.stdout)

    server_out, _ = server.communicate(timeout=5)
    print(server_out)


def part_b_no_channel_exists() -> None:
    print("=== Part B: attempting to reach a pipe NO SERVER ever created ===\n")
    print(f"[client] connecting to {WRONG_PIPE_NAME} (nothing is listening here) ...")
    try:
        win32file.CreateFile(
            WRONG_PIPE_NAME,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None,
        )
        print("[client] UNEXPECTED: connection succeeded with no server present.")
    except pywintypes.error as e:
        print(f"[client] connection refused by the kernel, as expected:")
        print(f"    winerror={e.winerror}, funcname={e.funcname!r}, strerror={e.strerror!r}")


def main() -> None:
    part_a_real_channel()
    part_b_no_channel_exists()


if __name__ == "__main__":
    main()
