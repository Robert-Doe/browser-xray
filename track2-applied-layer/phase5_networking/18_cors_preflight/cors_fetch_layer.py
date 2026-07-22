"""
Module 18: cors_preflight -- the client-side CORS logic.

Models what a browser's fetch() implementation actually does for a
cross-origin request:

  1. Same-origin? Skip all of this -- CORS is irrelevant, Module 17's
     default rules don't even apply, just fetch normally.
  2. Cross-origin AND the request is "non-simple" (a method other than
     GET/HEAD/POST, or a custom header)? Send an OPTIONS preflight
     FIRST, and only proceed if the server's preflight response
     explicitly grants this exact origin and method.
  3. Send the actual request. Regardless of what the preflight said,
     the ACTUAL response must ALSO carry a matching
     Access-Control-Allow-Origin header for the browser to hand the
     body back to script -- a preflight grant alone is not sufficient.
"""

import socket

from origin import origin_of, same_origin


class BlockedByCORS(Exception):
    pass


def _split_url(url: str) -> tuple[str, int, str]:
    parts = url.split("://", 1)[1]
    host_port, _, path = parts.partition("/")
    host, _, port_str = host_port.partition(":")
    port = int(port_str) if port_str else 80
    return host, port, "/" + path


def _raw_request(url: str, method: str, extra_headers: dict) -> tuple[int, dict, bytes]:
    host, port, path = _split_url(url)
    sock = socket.create_connection((host, port), timeout=5)

    header_lines = [f"{method} {path} HTTP/1.1", f"Host: {host}", "Connection: close"]
    for name, value in extra_headers.items():
        header_lines.append(f"{name}: {value}")
    request = ("\r\n".join(header_lines) + "\r\n\r\n").encode()
    sock.sendall(request)

    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    sock.close()

    header_end = data.index(b"\r\n\r\n")
    lines = data[:header_end].split(b"\r\n")
    status_code = int(lines[0].split(b" ")[1])
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(b":")
        headers[name.decode().strip().lower()] = value.decode().strip()
    body = data[header_end + 4 :]
    return status_code, headers, body


def _needs_preflight(method: str, custom_headers: dict) -> bool:
    return method not in ("GET", "HEAD", "POST") or bool(custom_headers)


def cors_enforced_fetch(
    requesting_page_url: str, target_url: str, method: str = "GET", custom_headers: dict | None = None
) -> bytes:
    custom_headers = custom_headers or {}
    requesting_origin = origin_of(requesting_page_url)
    target_origin = origin_of(target_url)

    if same_origin(requesting_origin, target_origin):
        _, _, body = _raw_request(target_url, method, custom_headers)
        return body

    if _needs_preflight(method, custom_headers):
        preflight_headers = {
            "Origin": str(requesting_origin),
            "Access-Control-Request-Method": method,
        }
        if custom_headers:
            preflight_headers["Access-Control-Request-Headers"] = ", ".join(custom_headers)

        status, headers, _ = _raw_request(target_url, "OPTIONS", preflight_headers)
        allow_origin = headers.get("access-control-allow-origin")
        allow_methods = headers.get("access-control-allow-methods", "")

        if allow_origin != str(requesting_origin) or method not in allow_methods:
            raise BlockedByCORS(
                f"preflight denied: server did not grant {method!r} from "
                f"{requesting_origin} (preflight status {status}, "
                f"Access-Control-Allow-Origin={allow_origin!r})"
            )

    actual_headers = dict(custom_headers)
    actual_headers["Origin"] = str(requesting_origin)
    _, headers, body = _raw_request(target_url, method, actual_headers)

    if headers.get("access-control-allow-origin") != str(requesting_origin):
        raise BlockedByCORS(
            f"actual response did not carry a matching Access-Control-Allow-Origin "
            f"for {requesting_origin} -- browser would withhold this body from script"
        )

    return body
