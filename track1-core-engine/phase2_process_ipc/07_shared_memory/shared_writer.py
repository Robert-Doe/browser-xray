"""
Module 7: shared_memory -- the WRITER side.

Creates (or attaches to, if it already exists) a named, pagefile-backed
shared memory segment -- Windows' CreateFileMapping/MapViewOfFile under
the hood, wrapped by Python's mmap module via the `tagname` argument.
Unlike Module 6's pipes and sockets, there is no message being "sent"
here: once mapped, this memory is the SAME PHYSICAL PAGES in both
processes. A write here is instantly visible to anyone else mapping the
same name -- no copy, no kernel relay per write.

Stays alive (blocking on stdin) after writing, specifically so a
second process has time to attach to the segment before this one exits
and the OS reclaims it.
"""

import mmap
import sys

SIZE = 4096


def main() -> None:
    tagname = sys.argv[1] if len(sys.argv) > 1 else "Local\\module7_shared_demo"
    value = sys.argv[2] if len(sys.argv) > 2 else "written by shared_writer.py"

    print(f"[writer] mapping shared segment tagname={tagname!r}")
    segment = mmap.mmap(-1, SIZE, tagname=tagname)

    payload = value.encode("utf-8")
    segment[: len(payload)] = payload
    print(f"[writer] wrote: {payload!r}")

    print("[writer] waiting (blocked on stdin) so another process can attach...")
    sys.stdin.readline()  # unblocked by the orchestrator sending a newline

    # Re-read right before exiting -- if a reader wrote back into the
    # SAME shared segment while we were waiting, we should see it here,
    # with no message-passing of any kind involved.
    current = bytes(segment[:64]).split(b"\x00", 1)[0]
    print(f"[writer] final contents just before exit: {current!r}")

    segment.close()
    print("[writer] closed, exiting.")


if __name__ == "__main__":
    main()
