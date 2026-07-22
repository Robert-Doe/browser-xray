"""
Module 33: clickjacking_uxss -- Part B: UXSS (Universal XSS).

Regular XSS (Module 32) exploits a bug in ONE specific site's own
input handling. UXSS is categorically different and more severe: it
exploits a bug in the BROWSER ENGINE's own origin-checking -- meaning
it can let a script from ANY origin reach into ANY other origin's
window, entirely independent of whether either site has any bug of
its own at all. This module models the exact gap: a missing origin
check on cross-window access, reusing Module 17's real same-origin
comparison as the enforcement gate.
"""

from dataclasses import dataclass, field


@dataclass
class ToyWindow:
    origin: str
    document_text: str
    secret_data: str = ""


def origin_of(url: str) -> str:
    scheme, rest = url.split("://", 1)
    host = rest.split("/", 1)[0]
    return f"{scheme}://{host}"


def same_origin(a: str, b: str) -> bool:
    return a == b


def access_other_window(requesting_origin: str, target_window: ToyWindow, enforce_origin_check: bool):
    """Models a browser engine's own internal decision about whether
    script running in one window may reach into another window's
    document -- real browsers MUST enforce this on every single such
    access, with no exceptions, or the result is a UXSS bug."""
    if enforce_origin_check and not same_origin(requesting_origin, target_window.origin):
        raise PermissionError(
            f"blocked: {requesting_origin} is not same-origin with {target_window.origin}"
        )
    return target_window.document_text


def main() -> None:
    victim_window = ToyWindow(
        origin="https://webmail.example",
        document_text="<div id='inbox'>...</div><input id='authToken' value='SECRET_AUTH_TOKEN_XYZ'>",
        secret_data="SECRET_AUTH_TOKEN_XYZ",
    )
    attacker_origin = "https://evil.com"

    print("=== BEFORE: a (hypothetical) browser engine bug skips the origin check ===\n")
    print(f"Attacker script running on {attacker_origin} calls into the browser engine")
    print(f"asking for webmail.example's window.document directly...\n")
    leaked = access_other_window(attacker_origin, victim_window, enforce_origin_check=False)
    print(f"  Engine returned: {leaked!r}")
    print("  The attacker's script, from a COMPLETELY UNRELATED origin, just read the")
    print("  victim's actual document content directly -- this is UNIVERSAL XSS: it has")
    print("  nothing to do with any bug on webmail.example's own part.\n")

    print("=== AFTER: the engine enforces a real origin check on every cross-window access ===\n")
    try:
        access_other_window(attacker_origin, victim_window, enforce_origin_check=True)
        print("  UNEXPECTED: access succeeded")
    except PermissionError as e:
        print(f"  BLOCKED, as expected: {e}")


if __name__ == "__main__":
    main()
