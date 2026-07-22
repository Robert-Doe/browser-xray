"""
Module 4: process_anatomy -- inspecting a DIFFERENT process.

process_anatomy.py inspected the calling process itself, using a
"pseudo handle" (GetCurrentProcess()) that always just means "me."
Inspecting a genuinely different process is a different, harder
operation: you must call OpenProcess() and explicitly name which
rights you want, and the kernel decides whether to grant them based on
your own process's security context versus the target's. This script
spawns a real child process and inspects it from the OUTSIDE, proving
that "process anatomy" isn't self-knowledge each process has about
itself -- it's kernel-tracked data any sufficiently-privileged process
can query about ANY process, given the right handle.
"""

import subprocess
import sys
import time

import win32api
import win32con
import win32process

from process_anatomy import count_threads, handle_count, integrity_level


def main() -> None:
    # A trivial, long-enough-lived child so we have time to inspect it
    # before it exits.
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3)"])
    time.sleep(0.3)  # let it fully start up before we query it

    print(f"Spawned child process, PID {child.pid}\n")

    # We do NOT have a handle to this process yet -- child.pid is just a
    # number (see Prerequisite 5: a PID is not a handle). We must
    # explicitly ask the kernel for one, naming the exact rights we want.
    access = (
        win32con.PROCESS_QUERY_INFORMATION
        | win32con.PROCESS_VM_READ
    )
    handle = win32api.OpenProcess(access, False, child.pid)
    print(f"OpenProcess granted a handle with rights: "
          f"PROCESS_QUERY_INFORMATION | PROCESS_VM_READ\n")

    mem = win32process.GetProcessMemoryInfo(handle)
    threads = count_threads(child.pid)
    handles = handle_count(handle)
    level_name, level_rid = integrity_level(handle)

    print(f"--- Anatomy of the CHILD process (PID {child.pid}), seen from outside ---")
    print(f"Threads                     : {threads}")
    print(f"Open kernel handles         : {handles}")
    print(f"Working set                 : {mem['WorkingSetSize']:,} bytes")
    print(f"Security context (integrity): {level_name} (RID 0x{level_rid:04X})")

    win32api.CloseHandle(handle)
    child.wait()

    print(
        "\nEverything above came from the SAME kernel-tracked structures "
        "process_anatomy.py read about itself -- the only difference was "
        "needing an explicit OpenProcess() handle, with explicit rights, "
        "to reach across the process boundary at all."
    )


if __name__ == "__main__":
    main()
