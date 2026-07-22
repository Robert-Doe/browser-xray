"""
Module 6: pipes_and_sockets -- named pipe CLIENT.

Connects to the exact pipe name pipe_server.py created. If that server
isn't there -- wrong name, or no server at all -- this fails outright
(see try_wrong_pipe_name.py), which is the whole point: there is no
implicit path between two processes, only ever this deliberately
agreed, kernel-mediated one.
"""

import sys

import win32file

PIPE_NAME = r"\\.\pipe\module6_demo_pipe"


def main() -> None:
    message = sys.argv[1] if len(sys.argv) > 1 else "hello from the client process"
    print(f"[client] connecting to {PIPE_NAME} ...")
    handle = win32file.CreateFile(
        PIPE_NAME,
        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        0, None,
        win32file.OPEN_EXISTING,
        0, None,
    )
    print("[client] connected.")

    win32file.WriteFile(handle, message.encode("utf-8"))
    print(f"[client] sent: {message!r}")

    hr, reply = win32file.ReadFile(handle, 4096)
    print(f"[client] received reply: {reply.decode('utf-8')!r}")

    win32file.CloseHandle(handle)


if __name__ == "__main__":
    main()
