"""
Module 32: xss_csrf_on_toy_browser -- a real CSRF attack against a toy
bank server, using Module 29's real cookie-jar/SameSite logic to decide
whether the victim's session cookie actually gets attached.

The vulnerability modeled here is the classic CSRF shape: a hidden,
auto-submitting cross-site form makes the VICTIM'S OWN BROWSER send a
real, cookie-authenticated request to a target site the victim never
intended to visit right now.
"""

from cookie_jar import Cookie, CookieJar

BANK_HOST = "bank.example.com"
EVIL_HOST = "evil.com"


class ToyBankServer:
    """A toy server-side endpoint: transfers money IF a valid session
    cookie is attached to the request, no other checks at all -- the
    classic CSRF-vulnerable shape (no CSRF token, relying on cookies alone)."""

    def __init__(self):
        self.balance = 1000
        self.valid_session_tokens = {"victim-session-abc123"}

    def handle_transfer_request(self, attached_cookies: list, amount: int) -> str:
        session_cookie = next((c for c in attached_cookies if c.name == "session"), None)
        if session_cookie is None or session_cookie.value not in self.valid_session_tokens:
            return f"REJECTED: no valid session cookie attached -- transfer of ${amount} did NOT happen"
        self.balance -= amount
        return f"SUCCESS: transferred ${amount} to attacker. New balance: ${self.balance}"


def simulate_csrf_attack(session_same_site: str) -> None:
    jar = CookieJar()
    jar.set_cookie(Cookie(
        name="session", value="victim-session-abc123", domain=BANK_HOST,
        same_site=session_same_site, secure=(session_same_site == "None"),
    ))
    bank = ToyBankServer()

    print(f"Victim's session cookie set with SameSite={session_same_site!r}")
    print(f"Bank balance before attack: ${bank.balance}\n")

    print("Victim, while still logged into the bank, visits evil.com, which contains:")
    print(f'  <form action="https://{BANK_HOST}/transfer" method="POST" id="f">')
    print(f'    <input type="hidden" name="amount" value="500">')
    print(f"  </form><script>document.getElementById('f').submit()</script>\n")

    # The auto-submitting form is a real, top-level navigation (the
    # hidden form's target is the top frame) using POST -- exactly the
    # classic CSRF vector.
    attached = jar.cookies_for_request(
        requesting_page_host=EVIL_HOST,
        target_host=BANK_HOST,
        is_top_level_navigation=True,
        method="POST",
    )
    print(f"Cookies the browser actually attaches to this cross-site POST: "
          f"{[c.name for c in attached]}")

    result = bank.handle_transfer_request(attached, amount=500)
    print(f"Bank server's response: {result}")


if __name__ == "__main__":
    print("=== BEFORE: session cookie has SameSite=None (or historically, no restriction) ===\n")
    simulate_csrf_attack(session_same_site="None")

    print("\n" + "=" * 70 + "\n")

    print("=== AFTER: session cookie set with SameSite=Lax ===\n")
    simulate_csrf_attack(session_same_site="Lax")
