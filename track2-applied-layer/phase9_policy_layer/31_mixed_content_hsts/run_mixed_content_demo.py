"""
Module 31: mixed_content_hsts -- demonstration runner.
"""

from hsts_store import HstsStore
from mixed_content import check_subresource


def demo_hsts() -> None:
    print("=== HSTS: rewriting requests to HTTPS before any network request ===\n")
    store = HstsStore()
    store.record_header("example.com", "max-age=31536000; includeSubDomains")
    print("Recorded HSTS for example.com (includeSubDomains)\n")

    tests = [
        "http://example.com/login",
        "http://sub.example.com/page",
        "http://not-example.com/page",  # NOT a real subdomain -- must not match
    ]
    for url in tests:
        rewritten = store.enforce(url)
        changed = " (upgraded)" if rewritten != url else " (unchanged)"
        print(f"  requested: {url}")
        print(f"  actually sent: {rewritten}{changed}\n")


def demo_mixed_content() -> None:
    print("=== Mixed content: passive vs. active subresources on an HTTPS page ===\n")
    page = "https://example.com/dashboard"

    cases = [
        ("img", "http://example.com/logo.png"),
        ("script", "http://cdn.example.com/lib.js"),
        ("link", "http://cdn.example.com/theme.css"),
        ("video", "http://example.com/intro.mp4"),
    ]
    for tag, url in cases:
        result = check_subresource(page, tag, url)
        print(f"  <{tag} src=\"{url}\">")
        print(f"    -> {result.action.upper()}: {result.final_url}")
        print(f"    ({result.reason})\n")


if __name__ == "__main__":
    demo_hsts()
    demo_mixed_content()
