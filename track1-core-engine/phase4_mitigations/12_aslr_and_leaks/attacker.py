"""
Module 12: aslr_and_leaks -- the attacker.

Given a target PID and an address to try (computed by the caller --
see run_aslr_defeat_demo.py for the two different ways that address
gets computed), attempts a real cross-process read (Module 11's exact
technique) and reports whether it landed on the real secret.
"""

import ctypes
import sys

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
EXPECTED_SECRET = b"REAL_SECRET_PAYLOAD_FOUND_ME"


def main() -> None:
    target_pid = int(sys.argv[1])
    guess_address = int(sys.argv[2], 16)

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, target_pid)
    if not handle:
        print(f"[attacker] OpenProcess failed, GetLastError={kernel32.GetLastError()}")
        return

    buffer = ctypes.create_string_buffer(32)
    bytes_read = ctypes.c_size_t(0)
    ok = kernel32.ReadProcessMemory(
        handle, ctypes.c_void_p(guess_address), buffer, 32, ctypes.byref(bytes_read)
    )

    if not ok:
        print(f"[attacker] tried 0x{guess_address:X} -- ReadProcessMemory FAILED "
              f"(GetLastError={kernel32.GetLastError()}); likely unmapped memory")
        return

    content = buffer.raw[: bytes_read.value]
    landed_on_secret = content.startswith(EXPECTED_SECRET)
    print(f"[attacker] tried 0x{guess_address:X} -- read succeeded: {content!r}")
    print(f"[attacker] landed on the real secret? {landed_on_secret}")


if __name__ == "__main__":
    main()
