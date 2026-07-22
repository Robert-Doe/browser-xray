"""
Module 30: csp_enforcement -- the real enforcement decision.

CSP's core idea: for each resource TYPE (scripts, styles, ...), the
page declares an explicit allowlist of sources. Anything not on that
list is refused -- checked BEFORE the browser would otherwise load or
execute it, never after the fact as a content filter.
"""

from urllib.parse import urlsplit


def origin_of(url: str) -> str:
    parts = urlsplit(url)
    port = parts.port or (443 if parts.scheme == "https" else 80)
    return f"{parts.scheme}://{parts.hostname}:{port}"


def is_source_allowed(sources: list, page_origin: str, target_url: str = None, is_inline: bool = False) -> bool:
    if not sources or "'none'" in sources:
        return False

    if is_inline:
        # SCOPE SIMPLIFICATION (see DECISIONS.md): real CSP also supports
        # nonces ('nonce-xxxx') and hashes ('sha256-xxxx') to allow SPECIFIC
        # inline scripts without allowing all of them. This module only
        # implements the blanket 'unsafe-inline' keyword.
        return "'unsafe-inline'" in sources

    target_origin = origin_of(target_url)
    target_parts = urlsplit(target_url)
    target_origin_no_port = f"{target_parts.scheme}://{target_parts.hostname}"

    for source in sources:
        if source == "'self'":
            if target_origin == page_origin:
                return True
            continue
        # CSP source expressions are commonly written WITHOUT an
        # explicit port (e.g. "https://cdn.trusted.com" implicitly
        # means the scheme's default port) -- comparing both the
        # full origin and the no-port form covers that real case.
        if source.rstrip("/") in (target_origin, target_origin_no_port):
            return True
    return False


def check_script(policy: dict, page_origin: str, src: str = None, inline_code: str = None):
    """Returns (allowed, reason). Exactly one of src/inline_code is set."""
    if "script-src" in policy:
        sources = policy["script-src"]
    elif "default-src" in policy:
        sources = policy["default-src"]
    else:
        # Real, important distinction: NEITHER directive being present
        # (e.g. no CSP header was sent at all) means scripts are
        # UNRESTRICTED by default -- a different case from a directive
        # being present with an empty/'none' list, which DOES restrict.
        # Collapsing these two cases was a real bug caught while
        # building Module 32's XSS demo against this exact function
        # (see that module's DECISIONS.md).
        label = "inline script" if inline_code is not None else f"script from {origin_of(src)}"
        return True, f"{label} ALLOWED -- no script-src or default-src directive present at all"

    is_inline = inline_code is not None
    allowed = is_source_allowed(sources, page_origin, target_url=src, is_inline=is_inline)

    if is_inline:
        label = "inline script"
    else:
        label = f"script from {origin_of(src)}"

    if allowed:
        return True, f"{label} ALLOWED by script-src {sources}"
    return False, f"{label} BLOCKED -- not permitted by script-src {sources}"
