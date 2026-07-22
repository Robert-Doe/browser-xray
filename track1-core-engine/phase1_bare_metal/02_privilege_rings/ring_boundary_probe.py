"""
Module 2: privilege_rings -- the real experiment.

Runs four different real x86-64 instructions, each freshly assembled by
hand into machine code and executed directly from an OS-granted
executable page. Two are ordinary, unprivileged instructions any Ring 3
program is allowed to run. Two are instructions the x86 architecture
itself defines as privileged -- legal only at CPL 0 (Ring 0). This
process never leaves Ring 3. If privilege rings are a real hardware
boundary and not just an OS convention, the two privileged instructions
must fault every single time, with no code of ours "catching" or
preventing it -- the CPU refuses before our instruction even completes.
"""

import ctypes
import ctypes.wintypes as wt

kernel32 = ctypes.windll.kernel32

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
PAGE_EXECUTE_READWRITE = 0x40

kernel32.VirtualAlloc.restype = ctypes.c_void_p
kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, wt.DWORD]
kernel32.VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_size_t, wt.DWORD]

# Raw machine code for each instruction under test, followed by RET
# (0xC3) so that if the CPU *does* allow it, control returns cleanly to
# Python instead of running off into unrelated memory.
INSTRUCTIONS = {
    "NOP  (no-op -- Ring 3 legal)": bytes([0x90, 0xC3]),
    "RDTSC (read timestamp counter -- Ring 3 legal by default)": bytes(
        [0x0F, 0x31, 0xC3]
    ),
    "CLI  (clear interrupt flag -- PRIVILEGED, Ring 0 only)": bytes([0xFA, 0xC3]),
    "HLT  (halt the CPU -- PRIVILEGED, Ring 0 only)": bytes([0xF4, 0xC3]),
}


def run_code(code: bytes) -> tuple[str, str | None]:
    """Execute raw machine code in a fresh executable page. Returns
    ("OK", None) if the CPU ran it and returned normally, or
    ("FAULT", <message>) if the CPU raised a hardware exception that
    ctypes' Windows SEH wrapper converted into a Python OSError."""
    addr = kernel32.VirtualAlloc(
        None, len(code), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE
    )
    if not addr:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        ctypes.memmove(addr, code, len(code))
        func = ctypes.CFUNCTYPE(None)(addr)
        func()
        return "OK", None
    except OSError as e:
        # ctypes on Windows wraps every foreign-function call in a real
        # SEH (Structured Exception Handling) frame specifically so a
        # hardware fault during that call becomes a catchable Python
        # exception instead of tearing down the whole interpreter.
        return "FAULT", str(e)
    finally:
        kernel32.VirtualFree(addr, 0, MEM_RELEASE)


def main() -> None:
    print(f"{'instruction':<62}{'result'}")
    print("-" * 90)
    for label, code in INSTRUCTIONS.items():
        status, detail = run_code(code)
        line = f"{label:<62}{status}"
        if detail:
            line += f"   <- {detail}"
        print(line)


if __name__ == "__main__":
    main()
