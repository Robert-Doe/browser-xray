"""
Module 4: process_anatomy -- what a process actually IS.

"A process" is not "a running .exe" -- that's the file on disk, which
is just a template. A process is a live, kernel-tracked bundle of:
  - identity + bookkeeping (a PID, a PCB the kernel maintains)
  - a private virtual address space (Prerequisite 1)
  - a handle table (Prerequisite 5)
  - a security context (a token -- who this process is allowed to act as)
  - one or more threads (Prerequisite 4) actually executing code in it

This script queries every one of those pieces for THIS process, live,
through real Windows APIs -- proving each is a genuine, separately
queryable kernel-tracked property, not something we're asserting exists.
"""

import ctypes
import ctypes.wintypes as wt
import os

import win32api
import win32con
import win32process
import win32security
import ntsecuritycon

kernel32 = ctypes.windll.kernel32
kernel32.GetProcessHandleCount.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
kernel32.GetProcessHandleCount.restype = wt.BOOL


class THREADENTRY32(ctypes.Structure):
    """Toolhelp32's snapshot record for one thread system-wide -- we
    filter by th32OwnerProcessID to find threads belonging to us."""

    _fields_ = [
        ("dwSize", wt.DWORD),
        ("cntUsage", wt.DWORD),
        ("th32ThreadID", wt.DWORD),
        ("th32OwnerProcessID", wt.DWORD),
        ("tpBasePri", ctypes.c_long),
        ("tpDeltaPri", ctypes.c_long),
        ("dwFlags", wt.DWORD),
    ]


TH32CS_SNAPTHREAD = 0x00000004


def count_threads(pid: int) -> int:
    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if snap == -1:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        entry = THREADENTRY32()
        entry.dwSize = ctypes.sizeof(THREADENTRY32)
        count = 0
        ok = kernel32.Thread32First(snap, ctypes.byref(entry))
        while ok:
            if entry.th32OwnerProcessID == pid:
                count += 1
            ok = kernel32.Thread32Next(snap, ctypes.byref(entry))
        return count
    finally:
        kernel32.CloseHandle(snap)


def handle_count(process_handle) -> int:
    count = ctypes.c_ulong()
    if not kernel32.GetProcessHandleCount(int(process_handle), ctypes.byref(count)):
        raise ctypes.WinError(ctypes.get_last_error())
    return count.value


def integrity_level(process_handle) -> tuple[str, int]:
    token = win32security.OpenProcessToken(process_handle, win32con.TOKEN_QUERY)
    sid, _attrs = win32security.GetTokenInformation(token, ntsecuritycon.TokenIntegrityLevel)
    sid_str = win32security.ConvertSidToStringSid(sid)
    rid = int(sid_str.rsplit("-", 1)[1])
    names = {
        0x0000: "Untrusted",
        0x1000: "Low",
        0x2000: "Medium",
        0x2100: "Medium High",
        0x3000: "High",
        0x4000: "System",
        0x5000: "Protected Process",
    }
    return names.get(rid, f"Unknown (RID {rid})"), rid


def dump_this_process() -> None:
    pid = win32api.GetCurrentProcessId()
    handle = win32api.GetCurrentProcess()

    mem = win32process.GetProcessMemoryInfo(handle)
    threads = count_threads(pid)
    handles = handle_count(handle)
    level_name, level_rid = integrity_level(handle)

    print(f"PID (process identity, kernel-assigned)      : {pid}")
    print(f"Threads currently executing in this process  : {threads}")
    print(f"Open kernel handles owned by this process     : {handles}")
    print(f"Working set (physical RAM currently used)     : {mem['WorkingSetSize']:,} bytes")
    print(f"Page faults so far                             : {mem['PageFaultCount']:,}")
    print(f"Security context (token integrity level)       : {level_name} (RID 0x{level_rid:04X})")
    print(f"Virtual address space                          : private to this PID "
          f"(see Module 1 -- id() addresses only mean something here)")


if __name__ == "__main__":
    print(f"--- Anatomy of THIS process (PID {os.getpid()}) ---\n")
    dump_this_process()
