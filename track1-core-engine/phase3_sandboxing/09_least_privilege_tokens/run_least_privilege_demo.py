"""
Module 9: least_privilege_tokens -- the actual proof.

Creates one ordinary file, owned by this (Medium-integrity) process,
with completely normal permissions -- nothing special configured on
the file itself. Then runs the IDENTICAL probe script, against the
IDENTICAL file, under three different tokens:

  1. A Low-integrity token attempting to READ it
  2. A Low-integrity token attempting to WRITE to it
  3. A normal (Medium-integrity, same as this process) token attempting
     to WRITE to it, as a control

If least-privilege tokens genuinely restrict what a spawned process can
do -- even though it's still running as the exact same Windows user
account -- (2) must fail while (1) and (3) succeed. This is the real
mechanism Chromium's original Windows renderer sandbox relied on:
lowering integrity, not changing user accounts.
"""

import os
import sys

from low_integrity_token import make_token_at_integrity, run_with_token

TEST_FILE = os.path.abspath("parent_owned_file.txt")


def main() -> None:
    with open(TEST_FILE, "w") as f:
        f.write("data owned by the parent (Medium-integrity) process\n")
    print(f"[setup] created {TEST_FILE} with default permissions and integrity (Medium)\n", flush=True)

    # NOTE on flush=True everywhere below: the child processes spawned by
    # run_with_token() inherit the console directly and write to it
    # immediately. This script's OWN print() calls, when stdout isn't a
    # real interactive terminal (e.g. captured by another tool), are
    # block-buffered by default and would otherwise all appear AFTER
    # every child's output instead of interleaved in the real order
    # things happened -- a real ordering bug we hit while verifying this
    # module (see DECISIONS.md).
    print("=== Attempt 1: Low-integrity child, READ ===", flush=True)
    low_token = make_token_at_integrity("low")
    run_with_token(low_token, f'{sys.executable} probe_child.py "{TEST_FILE}" read')

    print("\n=== Attempt 2: Low-integrity child, WRITE ===", flush=True)
    low_token = make_token_at_integrity("low")  # fresh token per spawn
    run_with_token(low_token, f'{sys.executable} probe_child.py "{TEST_FILE}" write')

    print("\n=== Attempt 3 (control): Medium-integrity child, WRITE ===", flush=True)
    medium_token = make_token_at_integrity("medium")
    run_with_token(medium_token, f'{sys.executable} probe_child.py "{TEST_FILE}" write')

    print(
        "\n[analysis] Attempts 1 and 3 should say OK. Attempt 2 should say "
        "FAILED with PermissionError -- the SAME Windows user account, "
        "the SAME file, the SAME code, differing only in the token's "
        "integrity level.",
        flush=True,
    )

    os.remove(TEST_FILE)


if __name__ == "__main__":
    main()
