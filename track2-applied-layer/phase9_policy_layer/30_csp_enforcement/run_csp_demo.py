"""
Module 30: csp_enforcement -- demonstration runner.

Simulates a page's script loader processing a real list of <script>
tags against a real, parsed CSP policy -- proving the check happens
BEFORE any script would execute: a blocked script never reaches an
"executed" list at all, the same way a browser never runs one CSP
refuses to load.
"""

from csp_enforcement import check_script, origin_of
from csp_parser import parse_csp

CSP_HEADER = "script-src 'self' https://cdn.trusted.com; style-src 'self' 'unsafe-inline'"

PAGE_URL = "https://example.com/index.html"

# Each entry: (label, src_or_None, inline_code_or_None)
SCRIPT_TAGS = [
    ("<script>alert(document.cookie)</script> (inline, e.g. injected via XSS)", None, "alert(document.cookie)"),
    ('<script src="/app.js"> (same-origin, first-party code)', "https://example.com/app.js", None),
    ('<script src="https://cdn.trusted.com/lib.js"> (explicitly allowed CDN)',
     "https://cdn.trusted.com/lib.js", None),
    ('<script src="https://evil.com/inject.js"> (unlisted third party)',
     "https://evil.com/inject.js", None),
]


def main() -> None:
    policy = parse_csp(CSP_HEADER)
    page_origin = origin_of(PAGE_URL)

    print(f"Page: {PAGE_URL}")
    print(f"CSP header: {CSP_HEADER}")
    print(f"Parsed policy: {policy}\n")

    executed = []
    blocked = []

    for label, src, inline in SCRIPT_TAGS:
        allowed, reason = check_script(policy, page_origin, src=src, inline_code=inline)
        print(f"{label}")
        print(f"    {reason}")
        if allowed:
            executed.append(label)
        else:
            blocked.append(label)
        print()

    print(f"Scripts that reached execution: {len(executed)}")
    for label in executed:
        print(f"    - {label}")
    print(f"\nScripts BLOCKED before ever executing: {len(blocked)}")
    for label in blocked:
        print(f"    - {label}")


if __name__ == "__main__":
    main()
