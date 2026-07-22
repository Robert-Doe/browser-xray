"""
Module 29: cookies_samesite -- the real SameSite enforcement decision.

A cookie is attached to a request based on THREE things at once: does
the request's target match the cookie's site at all, is this a
top-level navigation or a subresource/XHR-style request, and what
SameSite value the cookie was set with. This is a real, precise
decision table -- not "Strict blocks cross-site, Lax and None don't."
"""

from dataclasses import dataclass

from same_site import is_same_site

VALID_SAME_SITE = {"Strict", "Lax", "None"}


@dataclass
class Cookie:
    name: str
    value: str
    domain: str          # the host that SET this cookie
    same_site: str = "Lax"   # real browsers default new cookies to Lax if unspecified
    secure: bool = False


class CookieJar:
    def __init__(self):
        self._cookies: list[Cookie] = []

    def set_cookie(self, cookie: Cookie) -> None:
        if cookie.same_site not in VALID_SAME_SITE:
            raise ValueError(f"invalid SameSite value: {cookie.same_site!r}")
        if cookie.same_site == "None" and not cookie.secure:
            # Real, specified browser rule: SameSite=None cookies MUST
            # also be marked Secure, or browsers reject them outright.
            raise ValueError("SameSite=None cookies must also be Secure")
        self._cookies.append(cookie)

    def cookies_for_request(
        self,
        requesting_page_host: str,
        target_host: str,
        *,
        is_top_level_navigation: bool,
        method: str = "GET",
        is_https: bool = True,
    ) -> list[Cookie]:
        """Decide which stored cookies (belonging to target_host) get
        attached to a request FROM a page at requesting_page_host TO
        target_host, given the real request context."""
        same_site_request = is_same_site(requesting_page_host, target_host)
        safe_method = method.upper() in ("GET", "HEAD")

        attached = []
        for cookie in self._cookies:
            if cookie.domain != target_host:
                continue
            if cookie.secure and not is_https:
                continue

            if same_site_request:
                attached.append(cookie)  # same-site: every SameSite value is sent
                continue

            # Cross-site from here on -- the real, precise per-value rules:
            if cookie.same_site == "None":
                attached.append(cookie)
            elif cookie.same_site == "Lax" and is_top_level_navigation and safe_method:
                attached.append(cookie)
            # SameSite=Strict: NEVER attached cross-site, no exceptions.
            # SameSite=Lax with a non-top-level or unsafe-method request: not attached either.

        return attached
