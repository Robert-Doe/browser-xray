"""
Module 18: cors_preflight -- the actual proof.

One toy server (cors_server.py) enforces a real policy: it only grants
cross-origin access to ONE specific partner origin. We hit it with a
non-simple request (a PUT with a custom header, guaranteeing a real
preflight per the spec's own rules) from TWO different requesting
origins: one that matches the server's allowlist, one that doesn't.
"""

import time

from cors_fetch_layer import BlockedByCORS, cors_enforced_fetch
from cors_server import ALLOWED_ORIGIN, start_cors_server

DISALLOWED_ORIGIN = "http://127.0.0.1:51970/"  # NOT on the server's allowlist


def main() -> None:
    target_url = start_cors_server()
    time.sleep(0.3)

    print(f"Server's CORS policy allows exactly one origin: {ALLOWED_ORIGIN}\n")

    print("=== Part A: request from the ALLOWED partner origin ===")
    body = cors_enforced_fetch(
        requesting_page_url=ALLOWED_ORIGIN,
        target_url=target_url,
        method="PUT",
        custom_headers={"X-Custom-Auth": "token123"},
    )
    print(f"  preflight (OPTIONS) sent, then the real PUT -- both granted.")
    print(f"  response body exposed to script: {body!r}\n")

    print("=== Part B: IDENTICAL request from a DIFFERENT, disallowed origin ===")
    try:
        cors_enforced_fetch(
            requesting_page_url=DISALLOWED_ORIGIN,
            target_url=target_url,
            method="PUT",
            custom_headers={"X-Custom-Auth": "token123"},
        )
        print("  UNEXPECTED: request was not blocked")
    except BlockedByCORS as e:
        print(f"  BLOCKED at the preflight step, as expected: {e}\n")

    print("=== Part C: same-origin request (no CORS machinery involved at all) ===")
    body = cors_enforced_fetch(requesting_page_url=target_url, target_url=target_url, method="GET")
    print(f"  no preflight needed -- same origin. body: {body!r}\n")

    print(
        "[analysis] The ONLY difference between Part A and Part B was the "
        "requesting page's own origin, sent in the Origin header. The "
        "server's policy is the single source of truth for who's allowed; "
        "the preflight is how the browser asks BEFORE risking a real, "
        "possibly side-effecting PUT request, rather than finding out only "
        "after the fact."
    )


if __name__ == "__main__":
    main()
