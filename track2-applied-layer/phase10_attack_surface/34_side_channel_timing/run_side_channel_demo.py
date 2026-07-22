"""
Module 34: side_channel_timing -- demonstration runner.

Framing: a script running on https://evil.com wants
https://api.example.com's secret session token. SOP (Module 17)
genuinely, correctly blocks it from ever reading api.example.com's
response body directly -- that channel is closed. But SOP was never
designed to hide response TIMING, and if api.example.com's token
verification takes measurably different time depending on how much of
a guess is correct, that's a real, exploitable leak SOP does nothing
about.
"""

import string
import time

from timing_side_channel import (
    constant_time_compare,
    naive_compare,
    recover_secret_via_timing,
)

SECRET_TOKEN = "X7f9Qz2A"
CHARSET = string.ascii_letters + string.digits


def main() -> None:
    print(f"api.example.com's real secret token (never sent to the attacker directly): {SECRET_TOKEN!r}\n")
    print(
        "The attacker script (on a different origin) never reads this value. SOP "
        "blocks that outright, exactly as Module 17 proved. Everything below uses "
        "ONLY the observed TIME each verification attempt takes.\n"
    )

    print("=== BEFORE: api.example.com uses a non-constant-time comparison ===\n")
    start = time.perf_counter()
    recovered = recover_secret_via_timing(naive_compare, SECRET_TOKEN, CHARSET)
    elapsed = time.perf_counter() - start
    print(f"  Attacker recovered, via timing alone: {recovered!r}")
    print(f"  Matches the real secret? {recovered == SECRET_TOKEN}")
    print(f"  (took {elapsed:.2f}s of real, measured guessing)\n")

    print("=== AFTER: api.example.com switches to a constant-time comparison ===\n")
    start = time.perf_counter()
    recovered = recover_secret_via_timing(constant_time_compare, SECRET_TOKEN, CHARSET)
    elapsed = time.perf_counter() - start
    print(f"  Attacker recovered, via the IDENTICAL timing attack: {recovered!r}")
    print(f"  Matches the real secret? {recovered == SECRET_TOKEN}")
    print(f"  (took {elapsed:.2f}s -- same attack, same effort, no usable signal left)\n")

    print(
        "[analysis] Same attacker, same technique, same number of guesses. The ONLY "
        "thing that changed was whether the verification function's timing depended "
        "on the secret at all -- proving the leak was never about SOP or site "
        "isolation failing (they didn't -- direct reads were never available), but "
        "about a timing channel neither of those policies were ever designed to close."
    )


if __name__ == "__main__":
    main()
