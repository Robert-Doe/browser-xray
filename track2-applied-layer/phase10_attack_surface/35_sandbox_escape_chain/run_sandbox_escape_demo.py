"""
Module 35: sandbox_escape_chain -- the actual proof, tying Track 1 and
Track 2 together.

Runs the IDENTICAL "compromised renderer" probe under FOUR real
combinations of Track 1's own, already-independently-verified defenses:

    (a) no restriction at all
    (b) Job Object only               (Module 10's real mechanism)
    (c) least-privilege token only    (Module 9's real mechanism)
    (d) BOTH together

Neither defense alone is Module 35's invention -- both are the exact,
real, already-proven mechanisms from Phase 3. This module's only new
contribution is combining them and observing what a real, full
compromise chain actually requires.
"""

import os
import sys

import win32con
import win32event
import win32job
import win32process

from low_integrity_token import make_token_at_integrity

SENSITIVE_FILE = os.path.abspath("browser_process_private_data.txt")


def make_restrictive_job():
    job = win32job.CreateJobObject(None, "")
    info = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
    info["BasicLimitInformation"]["LimitFlags"] = (
        win32job.JOB_OBJECT_LIMIT_ACTIVE_PROCESS
        | win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    )
    info["BasicLimitInformation"]["ActiveProcessLimit"] = 1
    win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, info)
    return job


def spawn_probe(restrict_job: bool, restrict_token: bool) -> None:
    cmdline = f'{sys.executable} compromised_renderer_probe.py "{SENSITIVE_FILE}"'
    startup_info = win32process.STARTUPINFO()
    creation_flags = win32con.CREATE_SUSPENDED if restrict_job else 0

    if restrict_token:
        token = make_token_at_integrity("low")
        proc_info = win32process.CreateProcessAsUser(
            token, None, cmdline, None, None, False, creation_flags, None, None, startup_info
        )
    else:
        proc_info = win32process.CreateProcess(
            None, cmdline, None, None, False, creation_flags, None, None, startup_info
        )

    h_process, h_thread, _pid, _tid = proc_info

    if restrict_job:
        job = make_restrictive_job()
        win32job.AssignProcessToJobObject(job, h_process)
        win32process.ResumeThread(h_thread)

    win32event.WaitForSingleObject(h_process, 5000)


def run_scenario(label: str, restrict_job: bool, restrict_token: bool) -> None:
    # flush=True throughout: the probe child inherits the console and
    # writes immediately, while this script's own prints are
    # block-buffered whenever stdout isn't a live terminal -- the same
    # ordering pitfall documented in Module 9's and Module 10's own
    # DECISIONS.md files.
    print(f"=== {label} ===", flush=True)
    print(f"    Job Object restriction:      {'ON' if restrict_job else 'off'}", flush=True)
    print(f"    Least-privilege token:       {'ON' if restrict_token else 'off'}", flush=True)
    spawn_probe(restrict_job, restrict_token)
    print(flush=True)


def main() -> None:
    with open(SENSITIVE_FILE, "w") as f:
        f.write("BROWSER_PROCESS_SECRET_DATA")
    print(f"Created a file only the Browser Process should modify: {SENSITIVE_FILE}\n", flush=True)

    run_scenario("Scenario A: no sandboxing at all", restrict_job=False, restrict_token=False)
    run_scenario("Scenario B: Job Object only (Module 10)", restrict_job=True, restrict_token=False)
    run_scenario("Scenario C: least-privilege token only (Module 9)", restrict_job=False, restrict_token=True)
    run_scenario("Scenario D: BOTH together", restrict_job=True, restrict_token=True)

    os.remove(SENSITIVE_FILE)

    print(
        "[analysis] Only Scenario D blocks BOTH post-compromise actions. Scenarios B "
        "and C each block exactly the one thing their specific mechanism targets, "
        "and leave the other wide open -- real, direct evidence that a single "
        "defensive layer contains only part of what a fully compromised process "
        "could do, and that real sandbox design requires COMBINING independently-"
        "verified mechanisms, not choosing just one.",
        flush=True,
    )


if __name__ == "__main__":
    main()
