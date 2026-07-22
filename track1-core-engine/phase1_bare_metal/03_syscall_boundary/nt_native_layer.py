"""
Module 3: syscall_boundary -- bypass the friendly Win32 API entirely.

Every tutorial explains that CreateFileW (Win32) is a wrapper that
eventually calls NtCreateFile (the NT native API) in ntdll.dll, which
is what actually executes the `syscall` instruction into the kernel.
This script doesn't just claim that -- it calls NtCreateFile directly,
skipping kernel32 completely, and proves the file it opens is the exact
same real file a normal open() would reach: same bytes, same content.
That's only possible if both paths terminate at the same underlying
kernel object, via the same underlying syscall.
"""

import os

from ntdll_structs import (
    FILE_NON_DIRECTORY_FILE,
    FILE_OPEN,
    FILE_SHARE_READ,
    FILE_SHARE_WRITE,
    FILE_SYNCHRONOUS_IO_NONALERT,
    GENERIC_READ,
    OBJ_CASE_INSENSITIVE,
    STATUS_SUCCESS,
    SYNCHRONIZE,
    IO_STATUS_BLOCK,
    OBJECT_ATTRIBUTES,
    UNICODE_STRING,
    nt_status,
    ntdll,
    to_nt_path,
)
import ctypes


def open_and_read_via_ntdll(path: str, read_size: int = 256) -> bytes:
    nt_path = to_nt_path(path)
    path_buf = ctypes.create_unicode_buffer(nt_path)  # kept alive by this frame
    name = UNICODE_STRING()
    ntdll.RtlInitUnicodeString(ctypes.byref(name), path_buf)

    attrs = OBJECT_ATTRIBUTES()
    attrs.Length = ctypes.sizeof(OBJECT_ATTRIBUTES)
    attrs.RootDirectory = None
    attrs.ObjectName = ctypes.pointer(name)
    attrs.Attributes = OBJ_CASE_INSENSITIVE
    attrs.SecurityDescriptor = None
    attrs.SecurityQualityOfService = None

    open_iosb = IO_STATUS_BLOCK()
    handle = ctypes.c_void_p()

    status = ntdll.NtCreateFile(
        ctypes.byref(handle),
        GENERIC_READ | SYNCHRONIZE,
        ctypes.byref(attrs),
        ctypes.byref(open_iosb),
        None,
        0,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        FILE_OPEN,
        FILE_SYNCHRONOUS_IO_NONALERT | FILE_NON_DIRECTORY_FILE,
        None,
        0,
    )
    print(f"  NtCreateFile  -> NTSTATUS 0x{status & 0xFFFFFFFF:08X}"
          f" {'(STATUS_SUCCESS)' if status == STATUS_SUCCESS else ''}")
    if status != STATUS_SUCCESS:
        raise OSError(f"NtCreateFile failed: 0x{status & 0xFFFFFFFF:08X}")

    buf = ctypes.create_string_buffer(read_size)
    read_iosb = IO_STATUS_BLOCK()
    rstatus = ntdll.NtReadFile(
        handle, None, None, None, ctypes.byref(read_iosb), buf, read_size, None, None
    )
    print(f"  NtReadFile    -> NTSTATUS 0x{rstatus & 0xFFFFFFFF:08X}")
    bytes_read = int(read_iosb.Information or 0)
    ntdll.NtClose(handle)
    return buf.raw[:bytes_read]


def main() -> None:
    test_path = os.path.abspath("proof_file.txt")
    original_content = b"Written by ordinary Python open() -- kernel32 -> ntdll -> syscall.\n"

    with open(test_path, "wb") as f:
        f.write(original_content)
    print(f"Wrote {len(original_content)} bytes via Python's normal open()"
          f" (which itself goes through kernel32's CreateFileW).\n")

    print("Now reading the SAME file back, but skipping kernel32 entirely"
          " -- calling ntdll.dll's NtCreateFile / NtReadFile directly:")
    read_back = open_and_read_via_ntdll(test_path)

    print(f"\n  bytes read via raw NtCreateFile/NtReadFile: {read_back!r}")
    print(f"  identical to what we originally wrote?      "
          f"{read_back == original_content}")

    os.remove(test_path)

    if read_back != original_content:
        raise SystemExit("MISMATCH -- see DECISIONS.md troubleshooting notes")


if __name__ == "__main__":
    main()
