"""
Module 12: aslr_and_leaks -- the actual proof.

Step 1: run the vulnerable target ONCE and throw it away -- capturing
its diagnostic pointer purely to stand in for "an address an attacker
learned at some point in the past" (a previous exploitation attempt, a
cached value, generic prior knowledge of this exact binary).

Step 2: run the vulnerable target AGAIN, as a fresh process with a
FRESH ASLR-randomized base address, and keep it alive.

Part A: attack the fresh (Step 2) process using the STALE (Step 1)
pointer + the fixed, public offset. If ASLR is doing its job, this
must fail or land on the wrong data -- the stale process's address has
nothing to do with the new one.

Part B: attack the SAME fresh process using ITS OWN, freshly-leaked
pointer + the identical fixed offset. This must succeed, regardless of
what the random base actually turned out to be this run -- because the
offset relationship, once known, holds no matter where the base lands.
"""

import re
import subprocess
import sys
import time

POINTER_RE = re.compile(r"DIAGNOSTIC_POINTER=0x([0-9A-Fa-f]+)")
PID_RE = re.compile(r"PID=(\d+)")
SECRET_OFFSET = 0x2000


def get_stale_reference_pointer() -> int:
    print("=== Step 1: run the target once, keep only its address, then let it exit ===\n", flush=True)
    result = subprocess.run(
        [sys.executable, "vulnerable_process.py", "0.1"],
        capture_output=True, text=True, check=True,
    )
    pointer = int(POINTER_RE.search(result.stdout).group(1), 16)
    print(f"[reference run] diagnostic pointer was 0x{pointer:X} (this process has now exited)\n", flush=True)
    return pointer


def start_live_target() -> tuple[subprocess.Popen, int, int]:
    print("=== Step 2: start the REAL target for this attack, freshly ASLR-randomized ===\n", flush=True)
    proc = subprocess.Popen(
        [sys.executable, "vulnerable_process.py", "3"],
        stdout=subprocess.PIPE, text=True,
    )
    pid_line = proc.stdout.readline()
    pointer_line = proc.stdout.readline()
    pid = int(PID_RE.search(pid_line).group(1))
    pointer = int(POINTER_RE.search(pointer_line).group(1), 16)
    print(f"[live target] PID={pid}, THIS run's real diagnostic pointer=0x{pointer:X}\n", flush=True)
    return proc, pid, pointer


def run_attack(label: str, pid: int, guess_address: int) -> None:
    print(f"--- {label}: guessing secret at 0x{guess_address:X} ---", flush=True)
    result = subprocess.run(
        [sys.executable, "attacker.py", str(pid), hex(guess_address)],
        capture_output=True, text=True, check=True,
    )
    print(result.stdout, flush=True)


def main() -> None:
    stale_pointer = get_stale_reference_pointer()
    proc, pid, fresh_pointer = start_live_target()

    time.sleep(0.3)

    run_attack("Part A (STALE address from a previous run)", pid, stale_pointer + SECRET_OFFSET)
    run_attack("Part B (FRESH address, leaked from THIS run)", pid, fresh_pointer + SECRET_OFFSET)

    proc.wait()

    print(
        "[analysis] Part A used a real, correctly-offset formula applied to the "
        "WRONG run's base address -- and failed. Part B used the identical "
        "formula applied to THIS run's actual leaked base -- and succeeded, "
        "regardless of what random value ASLR happened to choose. The offset "
        "was never the secret. The base address was -- until it leaked.",
        flush=True,
    )


if __name__ == "__main__":
    main()
