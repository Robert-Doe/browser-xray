"""
Module 5: process_creation -- the child side.

Claims the IDENTICAL virtual address the parent claimed (mem_pin.PINNED_ADDRESS),
reports what it finds there BEFORE writing anything (this is the key
check: if virtual memory were physically shared, we'd see the parent's
string here already), then writes its own, different string and confirms.
"""

from mem_pin import claim_pinned_address, read_pinned, write_pinned, PINNED_ADDRESS

CHILD_SECRET = b"CHILD_WROTE_THIS_VALUE_5678\x00"


def main() -> None:
    claim_pinned_address()
    print(f"[child] claimed the SAME virtual address as the parent: 0x{PINNED_ADDRESS:X}")

    before = read_pinned(len(CHILD_SECRET))
    print(f"[child] bytes found at that address BEFORE writing anything: {before!r}")

    write_pinned(CHILD_SECRET)
    after = read_pinned(len(CHILD_SECRET))
    print(f"[child] bytes at that address AFTER this process wrote to it: {after!r}")


if __name__ == "__main__":
    main()
