"""
Module 31: mixed_content_hsts -- a real toy HSTS store.

HSTS (HTTP Strict Transport Security) exists to close one specific
gap: the FIRST request to a site, before the browser has ever seen its
HTTPS response, could still be silently sent over plain HTTP -- and an
attacker sitting on the network path could intercept that first
plaintext request and never let the user reach the real HTTPS site at
all (an "SSL stripping" downgrade attack). HSTS's fix: once a browser
has seen a site declare itself HTTPS-only, EVERY future request to
that host is rewritten to HTTPS before a single packet leaves the
machine -- never sent in cleartext even once, never relying on a
redirect the attacker could also intercept.
"""

from dataclasses import dataclass


@dataclass
class HstsRecord:
    max_age: int
    include_subdomains: bool = False


class HstsStore:
    def __init__(self):
        self._records: dict = {}

    def record_header(self, hostname: str, header_value: str) -> None:
        """Parses a real `Strict-Transport-Security` response header,
        e.g. 'max-age=31536000; includeSubDomains'."""
        parts = [p.strip() for p in header_value.split(";")]
        max_age = 0
        include_subdomains = False
        for part in parts:
            if part.lower().startswith("max-age="):
                max_age = int(part.split("=", 1)[1])
            elif part.lower() == "includesubdomains":
                include_subdomains = True

        if max_age > 0:
            self._records[hostname.lower()] = HstsRecord(max_age, include_subdomains)
        else:
            # max-age=0 is real, specified HSTS behavior for CLEARING
            # a previously stored record.
            self._records.pop(hostname.lower(), None)

    def is_hsts_host(self, hostname: str) -> bool:
        hostname = hostname.lower()
        if hostname in self._records:
            return True
        # Check whether any ancestor domain recorded includeSubDomains.
        labels = hostname.split(".")
        for i in range(1, len(labels)):
            parent = ".".join(labels[i:])
            record = self._records.get(parent)
            if record and record.include_subdomains:
                return True
        return False

    def enforce(self, url: str) -> str:
        """Given a URL the browser is about to request, rewrite it to
        https:// BEFORE any network request is made, if this host (or
        an includeSubDomains-covered ancestor) is in the HSTS store."""
        if not url.startswith("http://"):
            return url
        hostname_and_rest = url[len("http://"):]
        hostname = hostname_and_rest.split("/", 1)[0].split(":", 1)[0]
        if self.is_hsts_host(hostname):
            return "https://" + hostname_and_rest
        return url
