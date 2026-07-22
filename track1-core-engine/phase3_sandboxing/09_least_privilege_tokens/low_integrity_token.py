"""
Module 9: least_privilege_tokens -- shared helper.

Builds a LOW-integrity copy of this process's own security token, and
spawns a child process running under it. This is the real technique
Windows' own Protected Mode Internet Explorer and Chromium's original
Windows sandbox both used: you don't need to BE an administrator or a
service to hand a child process fewer rights than you have -- lowering
your own token's integrity level is always permitted (only RAISING it
requires special privilege), and Windows makes a specific allowance for
CreateProcessAsUser when the token is a duplicate of your OWN token,
which is why this works from an ordinary, non-elevated process.
"""

import win32api
import win32con
import win32event
import win32process
import win32security
import ntsecuritycon

# Mandatory Integrity Control SIDs (Microsoft-defined, not our choice).
INTEGRITY_SIDS = {
    "untrusted": "S-1-16-0",
    "low": "S-1-16-4096",
    "medium": "S-1-16-8192",
    "high": "S-1-16-12288",
}

# SE_GROUP_INTEGRITY -- not exposed as a win32con constant in this
# pywin32 build; verified directly (see DECISIONS.md) and hardcoded
# from WinNT.h.
SE_GROUP_INTEGRITY = 0x00000020


def make_token_at_integrity(level: str):
    """Duplicate the calling process's own primary token, then lower
    (never raise) its integrity level to `level`."""
    current = win32api.GetCurrentProcess()
    original_token = win32security.OpenProcessToken(current, win32con.TOKEN_ALL_ACCESS)

    duplicate = win32security.DuplicateTokenEx(
        original_token,
        win32security.SecurityImpersonation,
        win32con.TOKEN_ALL_ACCESS,
        win32security.TokenPrimary,
        None,
    )

    sid = win32security.ConvertStringSidToSid(INTEGRITY_SIDS[level])
    win32security.SetTokenInformation(
        duplicate, ntsecuritycon.TokenIntegrityLevel, (sid, SE_GROUP_INTEGRITY)
    )
    return duplicate


def run_with_token(token, cmdline: str, timeout_ms: int = 5000) -> int:
    """Spawn `cmdline` running under `token`, wait for it to exit, and
    return its exit code. The child's own stdout/stderr are inherited
    (not captured) so its printed output appears directly."""
    startup_info = win32process.STARTUPINFO()
    proc_handle, thread_handle, pid, tid = win32process.CreateProcessAsUser(
        token, None, cmdline, None, None, False, 0, None, None, startup_info
    )
    win32event.WaitForSingleObject(proc_handle, timeout_ms)
    exit_code = win32process.GetExitCodeProcess(proc_handle)
    win32api.CloseHandle(proc_handle)
    win32api.CloseHandle(thread_handle)
    return exit_code
