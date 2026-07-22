"""
Module 16: http_parsing -- a real, hand-rolled HTTP/1.1 response parser.

No http.client, no requests, no framework of any kind -- an HTTP
response is just bytes with a well-defined, plain-text structure:

    STATUS LINE \r\n
    Header-Name: value \r\n
    Header-Name: value \r\n
    \r\n
    <body, framed EITHER by Content-Length OR by chunked encoding>

This module hand-parses both of the two real body-framing mechanisms
an HTTP/1.1 response actually uses -- a server MUST tell the client
which one applies (via the Content-Length or Transfer-Encoding
header), because without one of them, the client has no way to know
where the body ends, short of the connection simply closing.
"""

from dataclasses import dataclass


@dataclass
class HttpResponse:
    version: str
    status_code: int
    reason: str
    headers: dict
    body: bytes


def _parse_status_line(line: bytes) -> tuple[str, int, str]:
    parts = line.split(b" ", 2)
    version = parts[0].decode("ascii")
    status_code = int(parts[1])
    reason = parts[2].decode("ascii", errors="replace") if len(parts) > 2 else ""
    return version, status_code, reason


def _parse_headers(header_lines: list[bytes]) -> dict:
    headers = {}
    for line in header_lines:
        if not line:
            continue
        name, _, value = line.partition(b":")
        # HTTP header names are case-insensitive by spec -- normalizing
        # to lowercase here is what lets callers reliably look up
        # "content-length" regardless of how the server capitalized it.
        headers[name.decode("ascii").strip().lower()] = value.decode("ascii", errors="replace").strip()
    return headers


def dechunk(chunked_body: bytes) -> bytes:
    """Reverse HTTP/1.1 chunked transfer encoding: each chunk is a
    hex length, \\r\\n, that many bytes, \\r\\n, repeating until a
    zero-length chunk marks the end."""
    result = bytearray()
    pos = 0
    while True:
        line_end = chunked_body.index(b"\r\n", pos)
        size_field = chunked_body[pos:line_end].split(b";", 1)[0]  # ignore chunk extensions
        size = int(size_field, 16)
        pos = line_end + 2
        if size == 0:
            break
        result.extend(chunked_body[pos : pos + size])
        pos += size + 2  # skip the chunk's trailing \r\n
    return bytes(result)


def parse_response(raw: bytes) -> HttpResponse:
    header_end = raw.index(b"\r\n\r\n")
    header_block = raw[:header_end]
    remainder = raw[header_end + 4 :]

    lines = header_block.split(b"\r\n")
    version, status_code, reason = _parse_status_line(lines[0])
    headers = _parse_headers(lines[1:])

    transfer_encoding = headers.get("transfer-encoding", "").lower()
    if transfer_encoding == "chunked":
        body = dechunk(remainder)
    elif "content-length" in headers:
        content_length = int(headers["content-length"])
        body = remainder[:content_length]
    else:
        # No framing header at all -- by spec, the body is "everything
        # until the connection closes." We've already read everything
        # available, so the remainder IS the whole body.
        body = remainder

    return HttpResponse(version, status_code, reason, headers, body)
