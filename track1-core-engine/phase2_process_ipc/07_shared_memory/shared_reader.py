"""
Module 7: shared_memory -- the READER side.

Attaches to a named shared segment by tagname and reads whatever is
there RIGHT NOW. If the tagname matches an already-live segment
(writer still holding it open), this sees the writer's actual bytes --
no copy was sent to it, it's looking at the same physical memory. If
the tagname does NOT match anything currently live, Windows silently
hands back a brand-new, private, zero-filled segment instead of
raising an error -- a real, important asymmetry from Module 6's pipes
and sockets, which fail loudly when there's no match.
"""

import mmap
import sys

SIZE = 4096


def main() -> None:
    tagname = sys.argv[1] if len(sys.argv) > 1 else "Local\\module7_shared_demo"
    write_back = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"[reader] mapping shared segment tagname={tagname!r}")
    segment = mmap.mmap(-1, SIZE, tagname=tagname)

    current = bytes(segment[:64]).split(b"\x00", 1)[0]
    print(f"[reader] bytes found immediately upon mapping: {current!r}")

    if write_back:
        payload = write_back.encode("utf-8")
        segment[: len(payload)] = payload
        print(f"[reader] wrote back: {payload!r}")

    segment.close()


if __name__ == "__main__":
    main()
