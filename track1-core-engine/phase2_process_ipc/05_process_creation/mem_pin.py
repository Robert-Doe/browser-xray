"""
Module 5: process_creation -- shared helper.

Wraps VirtualAlloc with an explicit lpAddress argument. Passing a
non-NULL lpAddress asks Windows to reserve+commit memory at THAT EXACT
virtual address rather than letting the OS pick one -- if that address
range is already in use in this process, the call fails outright rather
than silently picking a different address. This lets two independent
processes each request the identical numeric virtual address on
purpose, which is exactly the setup this module's experiment needs.
"""

import ctypes
import ctypes.wintypes as wt

kernel32 = ctypes.windll.kernel32
kernel32.VirtualAlloc.restype = ctypes.c_void_p
kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, wt.DWORD]

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04

# A high, deliberately unusual address (32 TB) chosen specifically
# because ordinary process startup (loader, heap, stack, DLLs) never
# lands anywhere near it -- making an exact-address request reliably
# succeed. See DECISIONS.md for why this specific value.
PINNED_ADDRESS = 0x0000200000000000
PINNED_SIZE = 4096


def claim_pinned_address() -> int:
    """Commit memory at the exact PINNED_ADDRESS in the CALLING
    process. Raises if the OS could not grant that exact address."""
    got = kernel32.VirtualAlloc(
        ctypes.c_void_p(PINNED_ADDRESS), PINNED_SIZE, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    )
    if not got:
        raise ctypes.WinError(ctypes.get_last_error())
    if got != PINNED_ADDRESS:
        raise RuntimeError(
            f"OS granted a different address (0x{got:X}) than requested "
            f"(0x{PINNED_ADDRESS:X}) -- see DECISIONS.md troubleshooting."
        )
    return got


def read_pinned(length: int = 32) -> bytes:
    return ctypes.string_at(PINNED_ADDRESS, length)


def write_pinned(data: bytes) -> None:
    ctypes.memmove(PINNED_ADDRESS, data, len(data))
