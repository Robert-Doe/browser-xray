"""
Module 17: origin_model_sop -- two fetch functions, same network layer
underneath, differing only in whether the ORIGIN CHECK exists at all.

naive_fetch(): does exactly what a raw socket/HTTP client (Module 16)
does -- sends the request, returns whatever comes back. No concept of
"origin" exists anywhere in it.

sop_enforced_fetch(): performs the IDENTICAL network request -- the
bytes leave the machine and the target server responds, exactly as
before -- but only hands the response BODY back to the calling code if
the requesting page's origin matches the target's origin. This models
a real, important, and often-missed nuance: the Same-Origin Policy
does not stop the network request from happening. It stops the
SCRIPT from being allowed to read what came back.
"""

import socket

from http_helpers import parse_response
from origin import origin_of, same_origin


def _raw_get(url: str) -> bytes:
    parts = url.split("://", 1)[1]
    host_port, _, path = parts.partition("/")
    host, _, port_str = host_port.partition(":")
    port = int(port_str) if port_str else 80
    path = "/" + path

    sock = socket.create_connection((host, port), timeout=5)
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
    sock.sendall(request)
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    sock.close()
    return data


def naive_fetch(target_url: str) -> bytes:
    """No origin awareness whatsoever -- returns the response body to
    whoever called it, unconditionally. This is what happens if
    nothing in the stack enforces SOP at all."""
    raw = _raw_get(target_url)
    return parse_response(raw).body


class BlockedBySameOriginPolicy(Exception):
    pass


def sop_enforced_fetch(requesting_page_url: str, target_url: str) -> bytes:
    """The SAME network request as naive_fetch -- but the response
    body is only returned to the caller if the requesting page's
    origin matches the target's origin."""
    requesting_origin = origin_of(requesting_page_url)
    target_origin = origin_of(target_url)

    raw = _raw_get(target_url)  # the network request happens regardless
    response = parse_response(raw)

    if not same_origin(requesting_origin, target_origin):
        raise BlockedBySameOriginPolicy(
            f"script running on {requesting_origin} may not read a response "
            f"from {target_origin} -- request WAS sent and a real response "
            f"WAS received over the network; the browser is withholding it "
            f"from script, not preventing the request itself"
        )

    return response.body
