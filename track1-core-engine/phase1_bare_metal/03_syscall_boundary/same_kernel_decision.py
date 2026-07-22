"""
Module 3: syscall_boundary -- the chokepoint proof.

nt_native_layer.py showed both API layers reach the same real file.
This script shows the sharper claim: when the kernel REFUSES a request,
both layers report the *same underlying decision*, just translated
into two different, layer-specific vocabularies --

    Win32 layer  : GetLastError() == ERROR_FILE_NOT_FOUND      (2)
    NT layer     : NTSTATUS      == STATUS_OBJECT_NAME_NOT_FOUND (0xC0000034)

These aren't two different decisions that happen to agree. Win32's
error is produced by RtlNtStatusToDosError() translating the NTSTATUS
the kernel actually returned -- i.e. the Win32 number is DERIVED FROM
the NT number. There is exactly one place the "does this file exist"
decision gets made, and it isn't in either API wrapper.
"""

import ctypes
import os

from ntdll_structs import (
    FILE_OPEN,
    FILE_SHARE_READ,
    FILE_SHARE_WRITE,
    FILE_SYNCHRONOUS_IO_NONALERT,
    FILE_NON_DIRECTORY_FILE,
    GENERIC_READ,
    OBJ_CASE_INSENSITIVE,
    STATUS_OBJECT_NAME_NOT_FOUND,
    SYNCHRONIZE,
    ERROR_FILE_NOT_FOUND,
    IO_STATUS_BLOCK,
    OBJECT_ATTRIBUTES,
    UNICODE_STRING,
    ntdll,
    to_nt_path,
)

kernel32 = ctypes.windll.kernel32
kernel32.CreateFileW.restype = ctypes.c_void_p

# IMPORTANT: Win32's dwCreationDisposition enum is a DIFFERENT numbering
# from the NT native CreateDisposition enum, despite both APIs meaning
# "only open if it already exists." Win32's OPEN_EXISTING is 3; the NT
# native FILE_OPEN (imported above, used for the ntdll call below) is 1.
# Reusing FILE_OPEN=1 here would actually mean Win32's CREATE_NEW, which
# *creates* the file if missing instead of failing -- a real bug we hit
# and caught by verifying output before writing docs (see DECISIONS.md).
OPEN_EXISTING = 3


def try_open_via_win32(missing_path: str) -> tuple[bool, int]:
    handle = kernel32.CreateFileW(missing_path, GENERIC_READ, FILE_SHARE_READ, None, OPEN_EXISTING, 0, None)
    INVALID_HANDLE_VALUE = 0xFFFFFFFFFFFFFFFF
    ok = handle != INVALID_HANDLE_VALUE
    err = kernel32.GetLastError()
    if ok:
        kernel32.CloseHandle(handle)
    return ok, err


def try_open_via_ntdll(missing_path: str) -> tuple[bool, int]:
    nt_path = to_nt_path(missing_path)
    path_buf = ctypes.create_unicode_buffer(nt_path)
    name = UNICODE_STRING()
    ntdll.RtlInitUnicodeString(ctypes.byref(name), path_buf)

    attrs = OBJECT_ATTRIBUTES()
    attrs.Length = ctypes.sizeof(OBJECT_ATTRIBUTES)
    attrs.ObjectName = ctypes.pointer(name)
    attrs.Attributes = OBJ_CASE_INSENSITIVE

    iosb = IO_STATUS_BLOCK()
    handle = ctypes.c_void_p()
    status = ntdll.NtCreateFile(
        ctypes.byref(handle),
        GENERIC_READ | SYNCHRONIZE,
        ctypes.byref(attrs),
        ctypes.byref(iosb),
        None,
        0,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        FILE_OPEN,
        FILE_SYNCHRONOUS_IO_NONALERT | FILE_NON_DIRECTORY_FILE,
        None,
        0,
    )
    ok = status == 0
    if ok:
        ntdll.NtClose(handle)
    return ok, status & 0xFFFFFFFF


def main() -> None:
    missing_path = os.path.abspath("this_file_does_not_exist_12345.txt")
    assert not os.path.exists(missing_path), "test path unexpectedly exists"

    print(f"Attempting to open a file that does not exist:\n  {missing_path}\n")

    win32_ok, win32_err = try_open_via_win32(missing_path)
    print("Win32 layer  (kernel32!CreateFileW):")
    print(f"    succeeded?  {win32_ok}")
    print(f"    GetLastError() = {win32_err} "
          f"{'(ERROR_FILE_NOT_FOUND)' if win32_err == ERROR_FILE_NOT_FOUND else ''}")

    nt_ok, nt_status = try_open_via_ntdll(missing_path)
    print("\nNT native layer (ntdll!NtCreateFile):")
    print(f"    succeeded?  {nt_ok}")
    print(f"    NTSTATUS = 0x{nt_status:08X} "
          f"{'(STATUS_OBJECT_NAME_NOT_FOUND)' if nt_status == STATUS_OBJECT_NAME_NOT_FOUND else ''}")

    print(
        "\nBoth layers refused -- for the SAME reason -- because both paths "
        "cross the identical syscall boundary underneath, where a single "
        "kernel decision was made once and reported twice, in two vocabularies."
    )

    if not (win32_err == ERROR_FILE_NOT_FOUND and nt_status == STATUS_OBJECT_NAME_NOT_FOUND):
        raise SystemExit("UNEXPECTED codes -- see DECISIONS.md troubleshooting notes")


if __name__ == "__main__":
    main()
