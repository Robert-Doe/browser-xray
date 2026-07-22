"""
Module 17: origin_model_sop -- the origin tuple, precisely.

An origin is exactly (scheme, host, port) -- nothing more, nothing
less (see Prerequisite 8). This module implements that comparison
directly from a URL string, using only Python's standard library URL
parser to split out the pieces -- the COMPARISON logic (what counts as
"same") is what we write ourselves, since that's the actual policy.
"""

from dataclasses import dataclass
from urllib.parse import urlsplit

DEFAULT_PORTS = {"http": 80, "https": 443}


@dataclass(frozen=True)
class Origin:
    scheme: str
    host: str
    port: int

    def __str__(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"


def origin_of(url: str) -> Origin:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = parts.hostname.lower() if parts.hostname else ""
    port = parts.port if parts.port is not None else DEFAULT_PORTS.get(scheme)
    return Origin(scheme, host, port)


def same_origin(a: Origin, b: Origin) -> bool:
    """The entire Same-Origin Policy comparison: all three parts must
    match EXACTLY. No fuzzy matching, no 'close enough' on subdomains,
    no ignoring the port."""
    return (a.scheme, a.host, a.port) == (b.scheme, b.host, b.port)
