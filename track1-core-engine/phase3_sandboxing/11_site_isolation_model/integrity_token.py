"""
Module 11: site_isolation_model -- local copy of Module 9's
low-integrity token helper (see that module's tutorial for the full
explanation of WHY this technique works unprivileged). Duplicated here
deliberately so this module's directory stays runnable on its own,
matching every other module in this course -- see DECISIONS.md.
"""

import win32api
import win32con
import win32event
import win32process
import win32security
import ntsecuritycon

INTEGRITY_SIDS = {
    "low": "S-1-16-4096",
    "medium": "S-1-16-8192",
}
SE_GROUP_INTEGRITY = 0x00000020


def make_token_at_integrity(level: str):
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


def spawn_with_token(token, cmdline: str, timeout_ms: int = 5000) -> None:
    startup_info = win32process.STARTUPINFO()
    proc_handle, thread_handle, _pid, _tid = win32process.CreateProcessAsUser(
        token, None, cmdline, None, None, False, 0, None, None, startup_info
    )
    win32event.WaitForSingleObject(proc_handle, timeout_ms)
    win32api.CloseHandle(proc_handle)
    win32api.CloseHandle(thread_handle)
