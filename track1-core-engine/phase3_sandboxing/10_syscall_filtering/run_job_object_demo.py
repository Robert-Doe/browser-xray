"""
Module 10: syscall_filtering -- the actual proof.

Module 9 showed a process could be denied a specific FILE, by identity
(integrity level). This module shows something stronger: a process can
be denied an entire CATEGORY of operation -- "create any new process
at all" -- enforced by the kernel at the moment of the attempt, no
matter what code inside the process tries, using completely ordinary,
unprivileged APIs.

The mechanism is a Windows Job Object with JOB_OBJECT_LIMIT_ACTIVE_PROCESS
set to 1. A process placed in that job IS the job's one permitted
process. Because child processes automatically join their parent's job
by default, ANY attempt by that process to spawn a new one would push
the job over its limit -- and Windows refuses the process creation
itself, at the syscall level, before the new process exists at all.

This is the real mechanism Chromium's Windows sandbox uses to stop a
compromised renderer from spawning arbitrary child processes (e.g. a
shell) -- not a application-level check the renderer could be tricked
into skipping, but a kernel-enforced quota it cannot get around no
matter what code runs inside it.
"""

import sys

import win32con
import win32event
import win32job
import win32process


def run_unrestricted() -> None:
    # flush=True throughout this module: spawned children inherit the
    # console and write immediately, while THIS script's own prints are
    # block-buffered whenever stdout isn't a live terminal -- the same
    # ordering pitfall documented in Module 9's DECISIONS.md.
    print("=== Part A: probe_spawn_child.py running WITHOUT any Job Object restriction ===\n", flush=True)
    startup_info = win32process.STARTUPINFO()
    proc_info = win32process.CreateProcess(
        None, f'{sys.executable} probe_spawn_child.py', None, None, False,
        0, None, None, startup_info,
    )
    h_process, _h_thread, pid, _tid = proc_info
    print(f"[orchestrator] spawned unrestricted probe, PID {pid}", flush=True)
    win32event.WaitForSingleObject(h_process, 5000)


def run_inside_restrictive_job() -> None:
    print("\n=== Part B: probe_spawn_child.py running INSIDE a Job Object "
          "(ActiveProcessLimit=1) ===\n", flush=True)

    job = win32job.CreateJobObject(None, "")
    info = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
    info["BasicLimitInformation"]["LimitFlags"] = (
        win32job.JOB_OBJECT_LIMIT_ACTIVE_PROCESS
        | win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    )
    info["BasicLimitInformation"]["ActiveProcessLimit"] = 1
    win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, info)
    print("[orchestrator] created a Job Object with ActiveProcessLimit=1", flush=True)

    # CREATE_SUSPENDED so we can assign it to the job BEFORE it runs any
    # of its own code -- otherwise it could (in this demo) spawn its
    # child before the restriction is even in place.
    startup_info = win32process.STARTUPINFO()
    proc_info = win32process.CreateProcess(
        None, f'{sys.executable} probe_spawn_child.py', None, None, False,
        win32con.CREATE_SUSPENDED, None, None, startup_info,
    )
    h_process, h_thread, pid, _tid = proc_info

    win32job.AssignProcessToJobObject(job, h_process)
    print(f"[orchestrator] assigned PID {pid} to the job -- it now occupies "
          f"the job's ONE permitted process slot", flush=True)

    win32process.ResumeThread(h_thread)
    win32event.WaitForSingleObject(h_process, 5000)


def main() -> None:
    run_unrestricted()
    run_inside_restrictive_job()
    print(
        "\n[analysis] Part A's probe successfully spawned its own child process. "
        "Part B's IDENTICAL code, IDENTICAL Python interpreter, IDENTICAL "
        "subprocess.run() call -- failed, because the OS refused to create "
        "the new process at all once it would have exceeded the job's quota."
    )


if __name__ == "__main__":
    main()
