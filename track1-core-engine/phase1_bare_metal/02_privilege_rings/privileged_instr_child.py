"""
Module 2: privilege_rings -- the child under test.

This process allocates a genuinely executable page, writes ONE real x86-64
machine instruction into it -- CLI (opcode 0xFA), "clear interrupt flag" --
and jumps into it. CLI is defined by the x86 architecture itself as a
privileged instruction: only code running at CPL 0 (Ring 0 / kernel mode)
is permitted to execute it. This process runs entirely in Ring 3 (user
mode) -- there is no way to reach Ring 0 by simply calling a function.

Expect this process to die. That is the entire point: the CPU should raise
a #GP (general protection) fault the instant CLI executes, Windows should
turn that into the STATUS_PRIVILEGED_INSTRUCTION exception, and since we
install no handler for it, the OS terminates this process and reports that
NTSTATUS as its exit code. run_and_decode.py (the parent) reads that exit
code back and proves the fault actually happened, for the reason claimed.
"""

import ctypes
import ctypes.wintypes as wt

kernel32 = ctypes.windll.kernel32

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_EXECUTE_READWRITE = 0x40

kernel32.VirtualAlloc.restype = ctypes.c_void_p
kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, wt.DWORD]

# CLI ; RET -- the RET is never reached; CLI faults first. We deliberately
# mark this page PAGE_EXECUTE_READWRITE (not the DEP-violating scenario --
# that's Module 13's separate, later point). The only thing under test
# here is whether a *privileged instruction* can run at Ring 3, given a
# page the OS has fully permitted us to execute from.
CODE = bytes([0xFA, 0xC3])

addr = kernel32.VirtualAlloc(
    None, len(CODE), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE
)
if not addr:
    raise ctypes.WinError(ctypes.get_last_error())

ctypes.memmove(addr, CODE, len(CODE))

func_type = ctypes.CFUNCTYPE(None)
run_cli = func_type(addr)

print("About to execute CLI (a privileged instruction) at Ring 3...", flush=True)
run_cli()  # <-- the process should never survive past this line

# If we ever reach here, something is fundamentally wrong with the premise
# of this module -- privilege rings would not be a real hardware boundary.
print("UNREACHABLE: CLI executed successfully at Ring 3.", flush=True)
