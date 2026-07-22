"""
Module 3: syscall_boundary -- shared struct/prototype declarations.

These three structs are the exact binary layout the NT native API
(ntdll.dll) expects -- an external contract we do not get to redesign.
Both scripts in this module import from here so the declaration lives
in exactly one place.
"""

import ctypes
import ctypes.wintypes as wt


class UNICODE_STRING(ctypes.Structure):
    """NT's native string type: explicit length + wide-char buffer,
    unlike a Win32 null-terminated LPCWSTR. Every NT native API that
    takes a name (a file path, an object name) takes one of these."""

    _fields_ = [
        ("Length", ctypes.c_ushort),
        ("MaximumLength", ctypes.c_ushort),
        ("Buffer", ctypes.c_wchar_p),
    ]


class OBJECT_ATTRIBUTES(ctypes.Structure):
    """Describes *what* is being opened and under what naming rules.
    Every NT object (file, key, event, section, ...) is opened through
    one of these, which is why it's shared infrastructure rather than
    something file-specific."""

    _fields_ = [
        ("Length", ctypes.c_ulong),
        ("RootDirectory", ctypes.c_void_p),
        ("ObjectName", ctypes.POINTER(UNICODE_STRING)),
        ("Attributes", ctypes.c_ulong),
        ("SecurityDescriptor", ctypes.c_void_p),
        ("SecurityQualityOfService", ctypes.c_void_p),
    ]


class IO_STATUS_BLOCK(ctypes.Structure):
    """Every NT I/O operation reports its result here. `Status` is
    logically a 32-bit NTSTATUS, but the real struct declares it as a
    union with a pointer-sized `PVOID` -- so we declare it as
    `c_void_p` to match the real size, and mask to the low 32 bits when
    reading it back as an NTSTATUS."""

    _fields_ = [
        ("Status", ctypes.c_void_p),
        ("Information", ctypes.c_void_p),
    ]


def nt_status(iosb: IO_STATUS_BLOCK) -> int:
    """Read IO_STATUS_BLOCK.Status as an unsigned 32-bit NTSTATUS."""
    raw = iosb.Status or 0
    return raw & 0xFFFFFFFF


ntdll = ctypes.WinDLL("ntdll.dll")

ntdll.RtlInitUnicodeString.argtypes = [
    ctypes.POINTER(UNICODE_STRING),
    ctypes.c_wchar_p,
]
ntdll.RtlInitUnicodeString.restype = None

ntdll.NtCreateFile.restype = ctypes.c_long
ntdll.NtCreateFile.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),   # FileHandle (out)
    wt.ULONG,                          # DesiredAccess
    ctypes.POINTER(OBJECT_ATTRIBUTES), # ObjectAttributes
    ctypes.POINTER(IO_STATUS_BLOCK),   # IoStatusBlock (out)
    ctypes.c_void_p,                   # AllocationSize (optional)
    wt.ULONG,                          # FileAttributes
    wt.ULONG,                          # ShareAccess
    wt.ULONG,                          # CreateDisposition
    wt.ULONG,                          # CreateOptions
    ctypes.c_void_p,                   # EaBuffer (optional)
    wt.ULONG,                          # EaLength
]

ntdll.NtReadFile.restype = ctypes.c_long
ntdll.NtReadFile.argtypes = [
    ctypes.c_void_p,                   # FileHandle
    ctypes.c_void_p,                   # Event (optional)
    ctypes.c_void_p,                   # ApcRoutine (optional)
    ctypes.c_void_p,                   # ApcContext (optional)
    ctypes.POINTER(IO_STATUS_BLOCK),   # IoStatusBlock (out)
    ctypes.c_void_p,                   # Buffer (out)
    wt.ULONG,                          # Length
    ctypes.c_void_p,                   # ByteOffset (optional)
    ctypes.c_void_p,                   # Key (optional)
]

ntdll.NtClose.argtypes = [ctypes.c_void_p]
ntdll.NtClose.restype = ctypes.c_long

# NTSTATUS values relevant to this module (from ntstatus.h -- Microsoft's
# constants, not ours).
STATUS_SUCCESS = 0x00000000
STATUS_OBJECT_NAME_NOT_FOUND = 0xC0000034

# Win32 GetLastError() codes (from winerror.h) for the same comparison.
ERROR_FILE_NOT_FOUND = 2

GENERIC_READ = 0x80000000
SYNCHRONIZE = 0x00100000
FILE_SHARE_READ = 0x1
FILE_SHARE_WRITE = 0x2
FILE_OPEN = 1
FILE_SYNCHRONOUS_IO_NONALERT = 0x20
FILE_NON_DIRECTORY_FILE = 0x40
OBJ_CASE_INSENSITIVE = 0x40


def to_nt_path(windows_path: str) -> str:
    """NT native paths use the \\??\\ prefix instead of a bare drive
    letter -- this is the NT object-manager namespace convention every
    native API call expects, distinct from the Win32 path convention
    kernel32 functions accept."""
    return "\\??\\" + windows_path
