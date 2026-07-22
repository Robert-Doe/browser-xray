"""
Module 11: site_isolation_model -- the actual proof, and its honest
limits.

Part A: an "origin B" renderer holds a secret at a known address. An
UNRESTRICTED "origin A" renderer -- same user, same (Medium) integrity,
no sandboxing applied -- uses only ordinary, documented Win32 APIs
(OpenProcess + ReadProcessMemory) to reach across the process boundary
and read it.

If Part A succeeds, that is important and easy to miss: Module 5's
proof that a process can't ACCIDENTALLY see another's memory does NOT
mean a DELIBERATE, sufficiently-privileged process can't reach across
on purpose using entirely legitimate OS APIs. Process separation alone
is not the same claim as "cannot be read."

Part B: the identical attack, except the "origin A" renderer now runs
under a Module-9-style LOW-integrity token, while "origin B" stays at
the OS default (Medium). This time, OpenProcess itself is refused.

The real, precise claim Site Isolation depends on is Part B's
combination -- process separation PLUS a real privilege/trust
difference between origins' renderer processes -- not process
separation alone.
"""

import subprocess
import sys
import time

from integrity_token import make_token_at_integrity, spawn_with_token


def part_a_same_privilege_cross_read() -> None:
    print("=== Part A: unrestricted, same-integrity cross-process read ===\n", flush=True)
    victim = subprocess.Popen([sys.executable, "victim_renderer.py"])
    time.sleep(0.5)

    result = subprocess.run(
        [sys.executable, "attacker_probe.py", str(victim.pid)],
        capture_output=True, text=True, check=True,
    )
    print(result.stdout, flush=True)
    victim.wait()


def part_b_integrity_separated_cross_read() -> None:
    print("\n=== Part B: attacker forced to LOW integrity, victim stays Medium ===\n", flush=True)
    victim = subprocess.Popen([sys.executable, "victim_renderer.py"])
    time.sleep(0.5)

    low_token = make_token_at_integrity("low")
    cmdline = f"{sys.executable} attacker_probe.py {victim.pid}"
    spawn_with_token(low_token, cmdline)

    victim.wait()


def main() -> None:
    part_a_same_privilege_cross_read()
    part_b_integrity_separated_cross_read()
    print(
        "\n[analysis] Part A's cross-process read SUCCEEDED using only ordinary "
        "OS APIs -- process separation (Module 5) alone did not stop a "
        "deliberate, same-privilege attempt. Part B's IDENTICAL attempt "
        "FAILED at OpenProcess itself once the attacker ran at lower "
        "integrity than the victim -- confirming Site Isolation's real "
        "guarantee depends on process separation COMBINED WITH a genuine "
        "privilege/trust difference between origins, not on process "
        "separation by itself.",
        flush=True,
    )


if __name__ == "__main__":
    main()
