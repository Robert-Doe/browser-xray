"""
Module 6: pipes_and_sockets -- named pipe SERVER.

Creates a Windows named pipe at a specific, fixed name and waits for
exactly one client to connect. Until a client connects to THIS EXACT
NAME, no data can cross -- there is no ambient channel between this
process and anything else. This is the kernel-mediated channel
Prerequisite 7 describes, made concrete.
"""

import win32pipe
import win32file

PIPE_NAME = r"\\.\pipe\module6_demo_pipe"


def main() -> None:
    print(f"[server] creating named pipe: {PIPE_NAME}")
    pipe = win32pipe.CreateNamedPipe(
        PIPE_NAME,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1,        # max instances
        65536,    # out buffer size
        65536,    # in buffer size
        0,        # default timeout
        None,     # default security attributes
    )

    print("[server] waiting for a client to connect (blocks until it does)...")
    win32pipe.ConnectNamedPipe(pipe, None)
    print("[server] client connected.")

    hr, data = win32file.ReadFile(pipe, 4096)
    message = data.decode("utf-8")
    print(f"[server] received from client: {message!r}")

    reply = f"[server acknowledges]: {message}".encode("utf-8")
    win32file.WriteFile(pipe, reply)
    print(f"[server] sent reply: {reply!r}")

    win32file.FlushFileBuffers(pipe)
    win32pipe.DisconnectNamedPipe(pipe)
    win32file.CloseHandle(pipe)
    print("[server] closed the pipe, exiting.")


if __name__ == "__main__":
    main()
