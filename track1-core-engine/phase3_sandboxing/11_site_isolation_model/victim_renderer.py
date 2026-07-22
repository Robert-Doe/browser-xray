"""
Module 11: site_isolation_model -- stands in for "the Renderer Process
for origin B," holding something origin-specific and sensitive in its
own memory (imagine a session token, or decrypted page content only
origin B should ever see).

Pins a known, fixed virtual address (Module 5's technique) so an
"attacker" process can be handed the exact address to try reading --
this module is not about address-guessing, it's about whether reading
a KNOWN address in another process is even possible at all.
"""

import ctypes
import os
import time

kernel32 = ctypes.windll.kernel32
kernel32.VirtualAlloc.restype = ctypes.c_void_p
kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong, ctypes.c_ulong]

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04
PINNED_ADDRESS = 0x0000300000000000
SECRET = b"ORIGIN_B_SESSION_TOKEN_SECRET\x00"


def main() -> None:
    got = kernel32.VirtualAlloc(
        ctypes.c_void_p(PINNED_ADDRESS), 4096, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    )
    if got != PINNED_ADDRESS:
        raise RuntimeError(f"expected 0x{PINNED_ADDRESS:X}, got {got}")

    ctypes.memmove(PINNED_ADDRESS, SECRET, len(SECRET))
    print(
        f"[victim: origin B renderer] PID {os.getpid()} holding a secret "
        f"at 0x{PINNED_ADDRESS:X}",
        flush=True,
    )

    time.sleep(3)  # stay alive long enough for the attacker probe to try
    print("[victim: origin B renderer] exiting", flush=True)


if __name__ == "__main__":
    main()
