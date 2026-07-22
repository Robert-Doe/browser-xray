"""
Module 12: aslr_and_leaks -- the "vulnerable" toy target.

Allocates a memory region at an OS-CHOSEN address (NOT pinned this
time -- ASLR gets to do its real job). Writes a "secret" at a FIXED
OFFSET from the region's base (representing something like a function
pointer table, a saved return address, or any other fixed-layout
target a real exploit would aim for). Then -- simulating a real,
common bug class (a debug/diagnostic feature that echoes back more
than it should) -- prints the region's BASE address as a "diagnostic
pointer," while deliberately never printing the secret's own address.

The offset between the diagnostic pointer and the secret is FIXED and
public knowledge (it's baked into this file, which an attacker could
obtain by reverse-engineering the target binary once) -- only the base
address itself is secret, and only because ASLR randomizes it fresh
each run.
"""

import ctypes
import os
import sys
import time

kernel32 = ctypes.windll.kernel32
kernel32.VirtualAlloc.restype = ctypes.c_void_p
kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong, ctypes.c_ulong]

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04
REGION_SIZE = 0x3000

# Public knowledge (an attacker could learn this from the binary itself,
# without ever running it) -- the FIXED distance from the diagnostic
# pointer to the actual secret.
SECRET_OFFSET = 0x2000
SECRET_VALUE = b"REAL_SECRET_PAYLOAD_FOUND_ME\x00"


def main() -> None:
    # lpAddress=None (NULL) -- unlike Modules 5 and 11, we deliberately
    # let Windows choose the address, so ASLR is actually in play.
    base = kernel32.VirtualAlloc(None, REGION_SIZE, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
    if not base:
        raise ctypes.WinError(ctypes.get_last_error())

    secret_address = base + SECRET_OFFSET
    ctypes.memmove(secret_address, SECRET_VALUE, len(SECRET_VALUE))

    pid = os.getpid()
    print(f"PID={pid}")
    # The bug: this diagnostic line reveals a real, live pointer. It
    # does NOT reveal the secret's address directly -- but combined
    # with the fixed, public SECRET_OFFSET, it doesn't need to.
    print(f"DIAGNOSTIC_POINTER=0x{base:X}")
    sys.stdout.flush()

    hold_seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
    time.sleep(hold_seconds)


if __name__ == "__main__":
    main()
