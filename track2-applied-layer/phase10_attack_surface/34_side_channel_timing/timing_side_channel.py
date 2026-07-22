"""
Module 34: side_channel_timing -- a real, measurable, non-weaponized
timing side-channel.

THE CORE POINT: Module 17's Same-Origin Policy blocks a cross-origin
script from reading a RESPONSE BODY. It says nothing about how LONG
that response took to arrive -- timing is not "content" in the sense
SOP protects. If the time a server takes to answer depends, even
slightly, on a secret value, an attacker who can never read that
secret directly can still recover it by measuring timing alone, one
guess at a time.

THE VULNERABLE PATTERN (`naive_compare`): a non-constant-time string
comparison -- the single most common REAL root cause of real-world
timing side-channel vulnerabilities in token/password verification
code. It returns as soon as it finds a mismatched character, so a
guess with a correct 3-character prefix genuinely takes measurably
longer to reject than a guess that's wrong from the very first
character.

THE FIX (`constant_time_compare`): always does the exact same amount
of work regardless of where (or whether) a mismatch occurs -- the real,
standard defense (e.g. Python's own `hmac.compare_digest`).
"""

import time

PER_CHARACTER_DELAY = 0.0002  # models real per-character verification cost (e.g. a hash step)


def naive_compare(guess: str, secret: str) -> bool:
    """VULNERABLE: exits the instant a mismatch is found."""
    if len(guess) != len(secret):
        return False
    for i in range(len(secret)):
        if guess[i] != secret[i]:
            return False
        time.sleep(PER_CHARACTER_DELAY)
    return True


def constant_time_compare(guess: str, secret: str) -> bool:
    """FIXED: always performs the same per-character work for every
    character, every time, regardless of where (or whether) a mismatch
    occurs -- no early exit, so no timing signal to measure."""
    if len(guess) != len(secret):
        return False
    result_diff = 0
    for i in range(len(secret)):
        result_diff |= ord(guess[i]) ^ ord(secret[i])
        time.sleep(PER_CHARACTER_DELAY)
    return result_diff == 0


def _time_guess(compare_fn, guess: str, secret: str, reps: int = 3) -> float:
    """Measures wall-clock time for one guess, taking the MINIMUM over
    several repetitions -- a real, standard technique for reducing
    noise from OS scheduling jitter when timing-attacking a real system."""
    best = float("inf")
    for _ in range(reps):
        start = time.perf_counter()
        compare_fn(guess, secret)
        best = min(best, time.perf_counter() - start)
    return best


def recover_secret_via_timing(compare_fn, secret: str, charset: str) -> str:
    """The actual attack: recovers `secret` ONE CHARACTER AT A TIME,
    using ONLY timing measurements of `compare_fn` -- never reading
    `secret` directly at any point."""
    recovered = ""
    for position in range(len(secret)):
        best_char, best_time = None, -1.0
        for candidate in charset:
            guess = recovered + candidate + "A" * (len(secret) - position - 1)
            elapsed = _time_guess(compare_fn, guess, secret)
            if elapsed > best_time:
                best_time, best_char = elapsed, candidate
        recovered += best_char
    return recovered
