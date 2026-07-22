"""
Module 13: dep_nx_w_xor_x -- build-and-run orchestrator.

This module's actual proof lives in the two C programs
(dep_violation.c, dep_legitimate_jit.c) -- C is used here specifically
because the point being proven (what the CPU does when you jump into
non-executable memory) is a property of raw machine code execution
that a managed language's runtime would normally hide or prevent you
from ever attempting. This script is Python, consistent with the rest
of the course's tooling, and only compiles + runs the two C programs
and reports their real exit codes.
"""

import os
import subprocess

GCC_DIR = r"C:\msys64\mingw64\bin"
GCC = GCC_DIR + r"\gcc.exe"

STATUS_ACCESS_VIOLATION = 0xC0000005

# gcc.exe's own driver locates its helper executables (cc1.exe,
# collect2.exe, ld.exe) via PATH in this MSYS2 packaging -- invoking it
# by full path alone, without GCC_DIR also present on PATH, fails
# silently (returncode 1, no stderr). Verified directly; see
# DECISIONS.md.
_BUILD_ENV = dict(os.environ)
_BUILD_ENV["PATH"] = GCC_DIR + os.pathsep + _BUILD_ENV.get("PATH", "")


def build(source: str, output: str) -> None:
    print(f"Compiling {source} -> {output} ...")
    result = subprocess.run(
        [GCC, "-O0", "-o", output, source], capture_output=True, text=True, env=_BUILD_ENV
    )
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(f"compilation of {source} failed")
    print("  ok\n")


def run_and_report(exe: str) -> int:
    # CreateProcess (which subprocess.run uses on Windows) does not
    # search the current directory for a bare filename the way a shell
    # would -- an absolute path is required here, verified directly
    # after hitting FileNotFoundError with a bare relative name.
    result = subprocess.run([os.path.abspath(exe)], capture_output=True, text=True)
    print(result.stdout, end="")
    if result.returncode != 0:
        # Windows exit codes for a process killed by an unhandled
        # exception equal the exception's NTSTATUS, reported as a
        # signed 32-bit value by the OS.
        unsigned = result.returncode & 0xFFFFFFFF
        print(f"  process exit code: {result.returncode} (0x{unsigned:08X})")
        if unsigned == STATUS_ACCESS_VIOLATION:
            print("  -> STATUS_ACCESS_VIOLATION: the CPU refused to execute this page.")
    else:
        print(f"  process exit code: {result.returncode} (clean exit)")
    return result.returncode


def main() -> None:
    build("dep_violation.c", "dep_violation.exe")
    build("dep_legitimate_jit.c", "dep_legitimate_jit.exe")

    print("=== Running dep_violation.exe (heap memory, no execute permission) ===")
    code1 = run_and_report("dep_violation.exe")

    print("\n=== Running dep_legitimate_jit.exe (VirtualAlloc'd, PAGE_EXECUTE_READWRITE) ===")
    code2 = run_and_report("dep_legitimate_jit.exe")

    print(
        f"\n[analysis] Identical machine code bytes, identical logic to jump into "
        f"them. dep_violation.exe was killed by the CPU/OS "
        f"({'crashed as expected' if code1 != 0 else 'UNEXPECTEDLY SURVIVED'}). "
        f"dep_legitimate_jit.exe returned normally "
        f"({'as expected' if code2 == 0 else 'UNEXPECTEDLY FAILED'}). "
        f"The only difference between them was how the memory was obtained."
    )


if __name__ == "__main__":
    main()
