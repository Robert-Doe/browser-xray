"""
Module 8: toy_browser_shell -- the BROWSER PROCESS.

This is the seed every later Track 2 module builds on: ONE privileged
Browser Process that spawns ONE Renderer Process per tab (Module 5's
proof: each is a genuinely separate process/address space) and talks
to each over its own dedicated IPC channel (Module 6's mechanism,
Module 8's message protocol) -- never sharing memory with them
(Module 7's boundary, deliberately not crossed here).

This models the real, foundational shape of Chromium's multi-process
architecture: a Browser Process that owns privileged operations
(spawning, orchestrating tabs) and Renderer Processes that do the
(here, simulated) work of turning a URL into a rendered page.
"""

import os
import socket
import subprocess
import sys

from ipc_protocol import recv_message, send_message

PORT = 51900


class Tab:
    def __init__(self, tab_id: int, url: str, proc: subprocess.Popen, conn: socket.socket, renderer_pid: int):
        self.tab_id = tab_id
        self.url = url
        self.proc = proc
        self.conn = conn
        self.renderer_pid = renderer_pid


def main() -> None:
    urls = sys.argv[1:] or ["https://example.com", "https://example.org", "https://example.net"]
    browser_pid = os.getpid()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", PORT))
    server.listen(len(urls))

    print(f"[browser] Browser Process PID {browser_pid} listening on port {PORT}")
    print(f"[browser] opening {len(urls)} tab(s), one Renderer Process each\n")

    tabs: list[Tab] = []
    for tab_id, url in enumerate(urls):
        proc = subprocess.Popen([sys.executable, "renderer_process.py", str(PORT)])
        conn, _addr = server.accept()
        hello = recv_message(conn)
        renderer_pid = hello["pid"]
        print(
            f"[browser] tab {tab_id}: spawned Renderer Process PID {renderer_pid} "
            f"for {url}  (genuinely separate from Browser PID {browser_pid}: "
            f"{renderer_pid != browser_pid})"
        )
        tabs.append(Tab(tab_id, url, proc, conn, renderer_pid))

    print()
    for tab in tabs:
        send_message(tab.conn, {"type": "load_url", "url": tab.url})
        response = recv_message(tab.conn)
        print(
            f"[browser] tab {tab.tab_id} loaded by renderer PID {response['pid']}: "
            f"title={response['title']!r}"
        )

    print()
    for tab in tabs:
        send_message(tab.conn, {"type": "shutdown"})
        recv_message(tab.conn)  # shutdown_ack
        tab.conn.close()
        tab.proc.wait(timeout=5)
        print(f"[browser] tab {tab.tab_id} renderer (PID {tab.renderer_pid}) shut down cleanly")

    server.close()
    print(f"\n[browser] all {len(tabs)} tabs closed. Browser Process (PID {browser_pid}) exiting.")


if __name__ == "__main__":
    main()
