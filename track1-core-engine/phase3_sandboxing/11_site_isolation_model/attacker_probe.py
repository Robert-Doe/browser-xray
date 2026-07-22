"""
Module 11: site_isolation_model -- stands in for "a compromised
Renderer Process for origin A, attempting to read origin B's memory."

Uses nothing but ordinary, documented, unprivileged Win32 APIs --
OpenProcess and ReadProcessMemory -- the exact tools any process can
legitimately try to use against any other process it knows the PID and
target address for. Whether this succeeds depends entirely on what the
OS decides to permit, not on anything clever this script does.
"""

import ctypes
import sys

PINNED_ADDRESS = 0x0000300000000000
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400


def main() -> None:
    target_pid = int(sys.argv[1])
    kernel32 = ctypes.windll.kernel32

    handle = kernel32.OpenProcess(
        PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, target_pid
    )
    err = kernel32.GetLastError()
    print(f"[attacker: origin A renderer] OpenProcess(PID {target_pid}) -> "
          f"handle={handle}, GetLastError={err}")

    if not handle:
        print("[attacker] cannot proceed -- no handle means no ReadProcessMemory is possible.")
        return

    buffer = ctypes.create_string_buffer(64)
    bytes_read = ctypes.c_size_t(0)
    ok = kernel32.ReadProcessMemory(
        handle, ctypes.c_void_p(PINNED_ADDRESS), buffer, 64, ctypes.byref(bytes_read)
    )
    if ok:
        print(f"[attacker] ReadProcessMemory SUCCEEDED: {buffer.raw[:bytes_read.value]!r}")
    else:
        print(f"[attacker] ReadProcessMemory FAILED, GetLastError={kernel32.GetLastError()}")


if __name__ == "__main__":
    main()
