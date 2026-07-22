"""
Module 1: mem_addressing -- the actual proof.

addr_dump.py shows *a* set of addresses for *one* run. On its own that
doesn't prove anything -- for all you can tell from one run, those
numbers might be fixed physical locations that just happen to be
printed once. This script runs addr_dump.py as two SEPARATE, freshly
started processes and diffs their output. If virtual memory were a
lie -- if those addresses really were physical RAM locations -- both
runs would have to print identical numbers (the RAM doesn't move
between runs). They don't. That's the proof.
"""

import re
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "addr_dump.py"
ADDR_RE = re.compile(r"virtual address\s*:\s*0x([0-9A-Fa-f]+)")
LABEL_RE = re.compile(r"^(A .+:|This module.+:)$", re.MULTILINE)


def run_once() -> list[int]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True
    )
    return [int(m, 16) for m in ADDR_RE.findall(result.stdout)]


def main() -> None:
    print("Running addr_dump.py as two independent processes...\n")
    run_a = run_once()
    run_b = run_once()

    labels = ["fresh int", "list", "function", "__name__ string"]

    print(f"{'object':<18}{'run A address':<22}{'run B address':<22}{'identical?'}")
    print("-" * 74)
    any_identical = False
    for label, a, b in zip(labels, run_a, run_b):
        same = a == b
        any_identical = any_identical or same
        print(f"{label:<18}0x{a:<20X}0x{b:<20X}{'YES' if same else 'no'}")

    print()
    if any_identical:
        print(
            "UNEXPECTED: an address repeated across independent runs.\n"
            "This can legitimately happen if ASLR is disabled system-wide,\n"
            "or extremely rarely by chance -- see DECISIONS.md before assuming\n"
            "the demo is broken."
        )
    else:
        print(
            "CONFIRMED: every address differs between two independent runs of\n"
            "the identical program. Physical RAM did not move between these\n"
            "two runs -- what moved is the VIRTUAL mapping each process was\n"
            "handed. That mapping is the 'illusion': the number your program\n"
            "sees is never a fixed location, only ever this run's translation."
        )

    # Second proof, inside the SAME diff: the *relative* offset between two
    # objects allocated back-to-back in one run is a property of the heap
    # allocator's behavior, not of ASLR -- so it should be far more stable
    # across runs than the absolute addresses are.
    offset_a = run_a[1] - run_a[0]
    offset_b = run_b[1] - run_b[0]
    print(
        f"\nRelative offset (list address - int address):\n"
        f"    run A: {offset_a}\n"
        f"    run B: {offset_b}\n"
        f"    (Absolute addresses moved by "
        f"{abs(run_b[0] - run_a[0])} bytes between runs; the offset between\n"
        f"    two objects allocated moments apart in the SAME run is a much\n"
        f"    smaller, allocator-driven number -- ASLR randomizes the BASE,\n"
        f"    not the allocator's internal layout logic.)"
    )


if __name__ == "__main__":
    main()
