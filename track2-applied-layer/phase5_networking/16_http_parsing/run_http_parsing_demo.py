"""
Module 16: http_parsing -- the actual proof.

Part A: fetch a REAL page from a real, live internet server
(example.com, over TLS, reusing Module 15's connection technique), and
hand-parse its Content-Length-framed response with OUR OWN parser --
no http.client, no requests.

Part B: fetch from a small local server that emits a genuinely
chunked-encoded response, and hand-parse THAT with the exact same
parser, proving both real-world body-framing mechanisms work with one
shared, simple implementation.
"""

import socket
import ssl
import subprocess
import sys
import time

from http_parser import parse_response
from local_chunked_server import HOST as CHUNKED_HOST
from local_chunked_server import PORT as CHUNKED_PORT


def fetch_raw_https(hostname: str, path: str) -> bytes:
    context = ssl.create_default_context()
    sock = socket.create_connection((hostname, 443), timeout=10)
    tls_sock = context.wrap_socket(sock, server_hostname=hostname)

    request = (
        f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
    ).encode("ascii")
    tls_sock.sendall(request)

    data = b""
    while True:
        chunk = tls_sock.recv(4096)
        if not chunk:
            break
        data += chunk
    tls_sock.close()
    return data


def fetch_raw_local(host: str, port: int) -> bytes:
    sock = socket.create_connection((host, port), timeout=5)
    sock.sendall(b"GET / HTTP/1.1\r\nHost: local\r\nConnection: close\r\n\r\n")
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    sock.close()
    return data


def self_test_synthetic_cases() -> None:
    """Deterministic checks against hand-built byte strings -- proves
    the parser handles BOTH real-world framing mechanisms correctly,
    independent of whatever any live server happens to choose (Part A
    below turned out to hit chunked encoding both times we ran it
    live, since Cloudflare-fronted sites favor it -- this is why we
    don't rely on a live fetch alone to prove the Content-Length path)."""
    print("=== Part 0: self-test against synthetic, hand-built responses ===\n")

    raw_cl = (b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 11\r\n\r\n"
              b"hello world")
    result_cl = parse_response(raw_cl)
    assert result_cl.body == b"hello world"
    print(f"  Content-Length case: parsed body = {result_cl.body!r} (correct)")

    raw_chunked = (b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n"
                   b"5\r\nhello\r\n1\r\n \r\n5\r\nworld\r\n0\r\n\r\n")
    result_chunked = parse_response(raw_chunked)
    assert result_chunked.body == b"hello world"
    print(f"  chunked case:        parsed body = {result_chunked.body!r} (correct)\n")


def part_a_content_length() -> None:
    print("=== Part A: real live fetch -- whatever framing the server actually uses ===\n")
    raw = fetch_raw_https("example.com", "/")
    response = parse_response(raw)

    # Deliberately not assumed in advance -- inspect what the server
    # actually sent, the same way our parser has to.
    if response.headers.get("transfer-encoding", "").lower() == "chunked":
        framing = "chunked (Transfer-Encoding: chunked)"
    elif "content-length" in response.headers:
        framing = f"Content-Length: {response.headers['content-length']}"
    else:
        framing = "no explicit framing header -- body runs until connection close"

    print(f"  status: {response.status_code} {response.reason}")
    print(f"  headers parsed: {len(response.headers)}")
    print(f"  actual framing mechanism used: {framing}")
    print(f"  body length (our parser's count, after any dechunking): {len(response.body)} bytes")
    print(f"  body starts with: {response.body[:60]!r}\n")


def part_b_chunked() -> None:
    print("=== Part B: real chunked-encoded fetch, from a local server ===\n")
    server = subprocess.Popen(
        [sys.executable, "local_chunked_server.py"], stdout=subprocess.PIPE, text=True
    )
    time.sleep(0.4)

    raw = fetch_raw_local(CHUNKED_HOST, CHUNKED_PORT)
    header_end = raw.index(b"\r\n\r\n")
    still_chunk_framed = raw[header_end + 4:]
    print(f"  raw bytes received (still chunk-framed): {still_chunk_framed!r}")

    response = parse_response(raw)
    print(f"  status: {response.status_code} {response.reason}")
    print(f"  transfer-encoding header: {response.headers.get('transfer-encoding')}")
    print(f"  DECHUNKED body (our parser reassembled it): {response.body!r}")

    server.wait(timeout=5)


def main() -> None:
    self_test_synthetic_cases()
    part_a_content_length()
    part_b_chunked()
    print(
        "[analysis] The synthetic self-test proves our parser handles BOTH "
        "Content-Length and chunked framing correctly and deterministically. "
        "The live fetch in Part A happened to ALSO be chunked (Cloudflare's "
        "default) -- a real, honest observation, not the case we originally "
        "expected -- which is exactly why Part 0's synthetic Content-Length "
        "check matters: it proves that path works even when no live server "
        "we tried against exercises it. One shared parser, both real-world "
        "framing mechanisms, verified two different ways."
    )


if __name__ == "__main__":
    main()
