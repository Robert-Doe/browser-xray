"""
Module 10: syscall_filtering -- the "compromised renderer" stand-in.

Stands in for what a compromised renderer process might try first:
spawning a new process (in a real attack, often a shell). Uses nothing
but ordinary, unprivileged `subprocess.run` -- no special API, no
attempt to bypass anything. Whether this succeeds or fails is decided
entirely by whatever Job Object (if any) the OS placed this process
into before it ever got to run this line.
"""

import subprocess
import sys


def main() -> None:
    try:
        result = subprocess.run(
            [sys.executable, "-c", "print('a new process ran')"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        print(f"spawn attempt SUCCEEDED: child said {result.stdout.strip()!r}")
    except OSError as e:
        print(f"spawn attempt BLOCKED by the OS: {e}")


if __name__ == "__main__":
    main()
