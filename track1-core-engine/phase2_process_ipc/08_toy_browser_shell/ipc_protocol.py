"""
Module 8: toy_browser_shell -- the wire protocol.

A tiny, length-prefixed JSON message protocol over a TCP socket
(Module 6's mechanism). Every message on the wire is:

    [ 4-byte big-endian length N ][ N bytes of UTF-8 JSON ]

This exact shape -- length prefix, then framed body -- is the same
basic idea real IPC systems (including Chromium's Mojo) use to know
where one message ends and the next begins on a byte-stream channel,
which has no message boundaries of its own (unlike Module 6's
message-mode named pipe). Every module in Track 2 that needs the
Browser Process <-> Renderer Process link reuses this exact protocol
rather than re-inventing message framing per module.
"""

import json
import socket
import struct

HEADER_FORMAT = "!I"  # big-endian ("network byte order"), unsigned 4-byte int
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def send_message(sock: socket.socket, message: dict) -> None:
    body = json.dumps(message).encode("utf-8")
    header = struct.pack(HEADER_FORMAT, len(body))
    sock.sendall(header + body)


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """TCP is a byte STREAM -- a single recv() call is not guaranteed to
    return exactly n bytes even if the sender sent exactly n. We must
    loop until we actually have everything we asked for."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(
                "socket closed while a message was still incomplete"
            )
        buf.extend(chunk)
    return bytes(buf)


def recv_message(sock: socket.socket) -> dict:
    header = _recv_exact(sock, HEADER_SIZE)
    (length,) = struct.unpack(HEADER_FORMAT, header)
    body = _recv_exact(sock, length)
    return json.loads(body.decode("utf-8"))
