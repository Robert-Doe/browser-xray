"""
Module 5: process_creation -- the actual proof.

1. This (parent) process claims a specific, unusual virtual address and
   writes a known string into it.
2. It spawns a genuinely separate child process, which claims THE EXACT
   SAME numeric virtual address and writes a DIFFERENT string into it.
3. The parent then re-reads its own copy at that same address.

If process creation did not actually create a separate address space --
if "spawning a process" were closer to starting a new thread that
happens to share memory -- the child's write would have overwritten (or
the child would have seen) the parent's data, because they used the
identical virtual address. What we're about to observe is proof that
none of that happens: two numerically identical addresses, two
completely independent physical realities behind them.
"""

import subprocess
import sys

from mem_pin import claim_pinned_address, read_pinned, write_pinned, PINNED_ADDRESS

PARENT_SECRET = b"PARENT_WROTE_THIS_VALUE_1234\x00"


def main() -> None:
    claim_pinned_address()
    print(f"[parent] claimed virtual address 0x{PINNED_ADDRESS:X}")

    write_pinned(PARENT_SECRET)
    print(f"[parent] wrote: {PARENT_SECRET!r}\n")

    print("[parent] spawning a genuinely separate child process, which will")
    print("[parent] claim the EXACT SAME virtual address and write its own value...\n")

    result = subprocess.run(
        [sys.executable, "child_writes_same_address.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    print(result.stdout)

    still_there = read_pinned(len(PARENT_SECRET))
    print(f"[parent] re-reading MY OWN copy at 0x{PINNED_ADDRESS:X} after the "
          f"child ran and wrote to 'the same' address:")
    print(f"[parent] bytes found: {still_there!r}")
    print(f"[parent] unchanged from what I originally wrote? {still_there == PARENT_SECRET}")

    if still_there != PARENT_SECRET:
        raise SystemExit(
            "UNEXPECTED: the child's write affected the parent's memory. "
            "See DECISIONS.md -- this would mean process isolation failed, "
            "which should not be possible on a normal Windows installation."
        )


if __name__ == "__main__":
    main()
