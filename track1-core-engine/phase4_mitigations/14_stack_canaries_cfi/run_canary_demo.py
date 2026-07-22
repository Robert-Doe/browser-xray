"""
Module 14: stack_canaries_cfi -- build-and-run orchestrator.

Compiles overflow_target.c TWICE -- once with GCC's stack protector
enabled, once with it explicitly disabled -- and runs each with a
short (harmless) and a long (overflowing) argument, reporting the real
exit codes.
"""

import os
import subprocess

GCC_DIR = r"C:\msys64\mingw64\bin"
GCC = GCC_DIR + r"\gcc.exe"

_BUILD_ENV = dict(os.environ)
_BUILD_ENV["PATH"] = GCC_DIR + os.pathsep + _BUILD_ENV.get("PATH", "")

STATUS_STACK_BUFFER_OVERRUN = 0xC0000409
STATUS_ACCESS_VIOLATION = 0xC0000005

SHORT_INPUT = "short"
LONG_INPUT = "A" * 40  # far past the vulnerable 16-byte buffer


def build(protector_flag: str, output: str) -> None:
    print(f"Compiling overflow_target.c ({protector_flag}) -> {output} ...")
    result = subprocess.run(
        [GCC, "-O0", protector_flag, "-o", output, "overflow_target.c"],
        capture_output=True, text=True, env=_BUILD_ENV,
    )
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(f"compilation failed for {output}")
    print("  ok\n")


def run_and_report(exe: str, arg: str) -> int:
    result = subprocess.run([os.path.abspath(exe), arg], capture_output=True, text=True)
    print(result.stdout, end="")
    print(result.stderr, end="")
    unsigned = result.returncode & 0xFFFFFFFF
    label = ""
    if unsigned == STATUS_STACK_BUFFER_OVERRUN:
        label = " -> STATUS_STACK_BUFFER_OVERRUN: the canary caught it before returning."
    elif unsigned == STATUS_ACCESS_VIOLATION:
        label = " -> STATUS_ACCESS_VIOLATION: it returned to a corrupted address."
    print(f"  exit code: {result.returncode} (0x{unsigned:08X}){label}\n")
    return result.returncode


def main() -> None:
    build("-fstack-protector-all", "overflow_protected.exe")
    build("-fno-stack-protector", "overflow_unprotected.exe")

    print("=== overflow_protected.exe, SHORT input (no overflow) ===")
    run_and_report("overflow_protected.exe", SHORT_INPUT)

    print("=== overflow_protected.exe, LONG input (overflows into the canary) ===")
    run_and_report("overflow_protected.exe", LONG_INPUT)

    print("=== overflow_unprotected.exe, LONG input (identical overflow, no canary) ===")
    run_and_report("overflow_unprotected.exe", LONG_INPUT)

    print(
        "[analysis] The protected build only fails when the overflow is real -- "
        "short input is untouched. Once genuinely overflowed, the protected build "
        "is killed cleanly at STATUS_STACK_BUFFER_OVERRUN, BEFORE the corrupted "
        "return address is ever used. The unprotected build, given the identical "
        "overflow, proceeds all the way to actually USING the corrupted return "
        "address -- crashing instead at STATUS_ACCESS_VIOLATION, which is what "
        "the canary exists to intercept earlier."
    )


if __name__ == "__main__":
    main()
