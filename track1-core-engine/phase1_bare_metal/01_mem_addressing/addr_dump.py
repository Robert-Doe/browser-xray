"""
Module 1: mem_addressing
=========================
Prints the virtual address of live objects in THIS process, then asks
the OS itself (via the VirtualQuery Win32 API) what it knows about the
memory page that address lives on: its base, its size, and its access
permissions.

The point: your program never sees physical RAM. Every address below is
a virtual address that the CPU's MMU translates using this process's
own private page tables (see prerequisites/01_virtual_memory.html).
VirtualQuery is a syscall-backed query into those same page tables --
it can only ever describe pages that exist in the CALLING process's own
address space. Run this script twice in a row and the printed addresses
will very likely differ between runs: that's ASLR (Address Space Layout
Randomization) re-randomizing where the loader places things, proving
these numbers were never fixed physical locations to begin with.
"""

import ctypes
import ctypes.wintypes as wt
import sys


# --- Recreate the real Win32 MEMORY_BASIC_INFORMATION struct layout ---
# Field order and sizes must exactly match WinNT.h -- this is an EXTERNAL
# CONTRACT (Windows' own ABI), not a choice we get to make. Get one field
# wrong and every value after it reads garbage.
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wt.DWORD),
        ("__alignment1", wt.DWORD),   # struct padding on 64-bit; see DECISIONS.md
        ("RegionSize", ctypes.c_size_t),
        ("State", wt.DWORD),
        ("Protect", wt.DWORD),
        ("Type", wt.DWORD),
        ("__alignment2", wt.DWORD),   # trailing padding to 8-byte align RegionSize's follow-on
    ]


# Named constants from WinNT.h -- these numeric values are not our choice,
# they are Microsoft's ABI. We only choose to spell them out for readability.
PAGE_PROTECT = {
    0x01: "PAGE_NOACCESS",
    0x02: "PAGE_READONLY",
    0x04: "PAGE_READWRITE",
    0x08: "PAGE_WRITECOPY",
    0x10: "PAGE_EXECUTE",
    0x20: "PAGE_EXECUTE_READ",
    0x40: "PAGE_EXECUTE_READWRITE",
    0x80: "PAGE_EXECUTE_WRITECOPY",
    0x100: "PAGE_GUARD",
    0x200: "PAGE_NOCACHE",
    0x400: "PAGE_WRITECOMBINE",
}
MEM_STATE = {0x1000: "MEM_COMMIT", 0x2000: "MEM_RESERVE", 0x10000: "MEM_FREE"}
MEM_TYPE = {0x20000: "MEM_PRIVATE", 0x40000: "MEM_MAPPED", 0x1000000: "MEM_IMAGE"}

kernel32 = ctypes.windll.kernel32
kernel32.VirtualQuery.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(MEMORY_BASIC_INFORMATION),
    ctypes.c_size_t,
]
kernel32.VirtualQuery.restype = ctypes.c_size_t


def query_page(address: int) -> MEMORY_BASIC_INFORMATION:
    """Ask the OS what it knows about the page containing `address`."""
    mbi = MEMORY_BASIC_INFORMATION()
    written = kernel32.VirtualQuery(
        ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)
    )
    if written == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return mbi


def describe(label: str, address: int) -> None:
    mbi = query_page(address)
    protect = PAGE_PROTECT.get(mbi.Protect, hex(mbi.Protect))
    state = MEM_STATE.get(mbi.State, hex(mbi.State))
    mtype = MEM_TYPE.get(mbi.Type, hex(mbi.Type))
    print(f"{label}")
    print(f"    virtual address     : 0x{address:016X}")
    print(f"    page region base    : 0x{mbi.BaseAddress:016X}")
    print(f"    region size (bytes) : {mbi.RegionSize} (0x{mbi.RegionSize:X})")
    print(f"    protection          : {protect}")
    print(f"    state               : {state}")
    print(f"    type                : {mtype}")
    print()


def main() -> None:
    import os

    print(f"--- Process PID {os.getpid()} ---\n")

    # A local int. CPython caches small ints (-5..256), so we deliberately
    # use a large, non-cached value to guarantee a *fresh* heap allocation
    # rather than a shared interned object -- otherwise this "local
    # variable" would actually be a long-lived interpreter singleton and
    # prove nothing about THIS run's layout.
    local_int = 999_983 + 1
    describe("A fresh int object (heap-allocated this run):", id(local_int))

    # A list -- always heap-allocated, never interned.
    local_list = [1, 2, 3]
    describe("A list object (heap):", id(local_list))

    # A function object -- lives in a different region than plain data,
    # since code objects and their containing function objects are
    # allocated differently from simple heap data.
    def local_fn():
        pass

    describe("A function object:", id(local_fn))

    # The interpreter's own loaded module code (this file's compiled code
    # object) -- closer to "image" memory than heap memory.
    describe("This module's __name__ string object:", id(__name__))


if __name__ == "__main__":
    if sys.platform != "win32":
        raise SystemExit("This module targets Windows VirtualQuery; see DECISIONS.md")
    main()
