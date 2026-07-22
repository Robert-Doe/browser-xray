"""
Module 29: cookies_samesite -- demonstration runner.

One target site (bank.example.com) sets three cookies -- one per
SameSite value. We then simulate four different real request contexts
FROM a different, cross-site page (evil.com), plus one same-site
request from a related subdomain, and show exactly which cookies get
attached each time.
"""

from cookie_jar import Cookie, CookieJar

TARGET = "bank.example.com"
CROSS_SITE_PAGE = "evil.com"
SAME_SITE_PAGE = "app.bank.example.com"  # different HOST, but same registrable domain (example.com)


def main() -> None:
    jar = CookieJar()
    jar.set_cookie(Cookie(name="strict_session", value="s1", domain=TARGET, same_site="Strict"))
    jar.set_cookie(Cookie(name="lax_session", value="s2", domain=TARGET, same_site="Lax"))
    jar.set_cookie(Cookie(name="none_session", value="s3", domain=TARGET, same_site="None", secure=True))

    scenarios = [
        ("Same-site request (app.bank.example.com -> bank.example.com), top-level GET",
         SAME_SITE_PAGE, True, "GET"),
        ("Cross-site TOP-LEVEL navigation (evil.com -> bank.example.com), GET",
         CROSS_SITE_PAGE, True, "GET"),
        ("Cross-site SUBRESOURCE/XHR request (evil.com -> bank.example.com), GET",
         CROSS_SITE_PAGE, False, "GET"),
        ("Cross-site TOP-LEVEL navigation via POST (e.g. an auto-submitting form)",
         CROSS_SITE_PAGE, True, "POST"),
    ]

    for label, requesting_host, is_top_level, method in scenarios:
        attached = jar.cookies_for_request(
            requesting_page_host=requesting_host,
            target_host=TARGET,
            is_top_level_navigation=is_top_level,
            method=method,
        )
        names = sorted(c.name for c in attached)
        print(f"{label}")
        print(f"    cookies attached: {names}\n")


if __name__ == "__main__":
    main()
