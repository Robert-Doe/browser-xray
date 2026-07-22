"""
Module 18: cors_preflight -- local copy of Module 17's origin tuple
logic (see that module for the full explanation). Duplicated here for
this module's own directory self-containment.
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
    return (a.scheme, a.host, a.port) == (b.scheme, b.host, b.port)
