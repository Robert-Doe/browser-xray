"""
Module 35: sandbox_escape_chain -- the "compromised renderer."

Stands in for a renderer process AFTER an attacker has already
achieved code execution inside it (via some real memory-safety bug --
Module 14 built and proved a genuine one; we do not re-detonate it
here, see DECISIONS.md). This script is deliberately ordinary,
unprivileged Python code attempting two concrete, realistic
post-compromise goals:

  1. Spawn a new process (standing in for launching a shell) -- the
     kind of action Module 10's Job Object restriction targets.
  2. TAMPER WITH (append to) a file belonging to the privileged
     Browser Process -- the kind of action Module 9's least-privilege
     token targets. This is deliberately a WRITE, not a read: Module 9
     already proved, directly, that Windows' default Mandatory
     Integrity Control blocks WRITE-up but does NOT block read-up on
     ordinary file objects -- so a read-based test here would not
     actually exercise the token defense at all. Using a write keeps
     this module's evidence consistent with, not contradicting,
     Module 9's own already-verified finding.

Whether either succeeds is decided ENTIRELY by what restrictions (if
any) the process was launched under -- this script itself contains no
awareness of sandboxing at all, exactly like real attacker-controlled
code wouldn't.
"""

import subprocess
import sys


def try_spawn_process() -> str:
    try:
        subprocess.run(
            [sys.executable, "-c", "print('a new process ran')"],
            capture_output=True, text=True, timeout=5, check=True,
        )
        return "SUCCEEDED"
    except OSError as e:
        return f"BLOCKED (OSError: {e})"


def try_tamper_with_file(path: str) -> str:
    try:
        with open(path, "a") as f:
            f.write("\nTAMPERED_BY_COMPROMISED_RENDERER")
        return "SUCCEEDED (file modified)"
    except PermissionError as e:
        return f"BLOCKED (PermissionError: {e})"


def main() -> None:
    sensitive_file = sys.argv[1]
    print(f"spawn_new_process: {try_spawn_process()}", flush=True)
    print(f"tamper_with_browser_process_file: {try_tamper_with_file(sensitive_file)}", flush=True)


if __name__ == "__main__":
    main()
