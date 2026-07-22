# Module 3: syscall_boundary — DECISIONS.md

## `ntdll_structs.py`

### `UNICODE_STRING`, `OBJECT_ATTRIBUTES`, `IO_STATUS_BLOCK` field layouts
**(b) External contract.** These three structs must match the real NT
native API ABI exactly, the same way Module 1's
`MEMORY_BASIC_INFORMATION` had to. They are not documented in the
public Win32 SDK headers the way Win32 structs are — the NT native API
is intentionally semi-private, and its layouts are known through
Microsoft's own WDK (Windows Driver Kit) headers and long-standing,
consistent reverse-engineering by the systems community. We are relying
on that documented-elsewhere layout, not inventing it.

### `IO_STATUS_BLOCK.Status` declared as `c_void_p`, not `c_ulong`
**(a) Forced by the platform ABI.** The real struct declares this field
as a union of `NTSTATUS` (4 bytes) and `PVOID` (8 bytes on x64) — the
union's actual size is 8 bytes because the compiler must reserve enough
space for the larger member. Declaring it as `c_ulong` (4 bytes) would
shift every subsequent read of the struct's memory by 4 bytes on a
64-bit build. We read it back and mask to the low 32 bits
(`nt_status()`) precisely because we know only that portion holds the
real NTSTATUS.

### `to_nt_path()` prepending `\??\`
**(b) External contract.** The NT object manager namespace uses a
different path convention than the Win32 API's drive-letter paths.
`\??\C:\...` is the documented, standard way to address a DOS-style
path through the NT native namespace (the `\??` portion is itself an
NT object-manager symbolic-link directory that maps drive letters to
their real device paths). We didn't choose this prefix — it's how the
NT namespace has always worked.

### `GENERIC_READ | SYNCHRONIZE` as `DesiredAccess`, plus
`FILE_SYNCHRONOUS_IO_NONALERT`
**(b) External contract, with a (c) convention layered on top.**
Calling `NtCreateFile` directly means we're responsible for requesting
`SYNCHRONIZE` access and specifying `FILE_SYNCHRONOUS_IO_NONALERT`
ourselves — kernel32's `CreateFileW` normally does this bookkeeping for
you invisibly. Omitting it produces a handle that behaves
asynchronously by default and made `NtReadFile` return
`STATUS_PENDING` instead of completing inline during initial testing;
adding these flags was necessary, not stylistic, to get synchronous
read semantics matching what `ReadFile` gives you for free.

---

## `nt_native_layer.py`

### Writing the test file with plain `open()`, then reading it back only
through `NtReadFile`
**(c) Convention — this is the module's core teaching move.** Using
two genuinely different code paths (Python's buffered `open()`, which
eventually calls kernel32's `CreateFileW`, versus a direct `NtCreateFile`
call) for write and read respectively is what makes "these reach the
same underlying file" a falsifiable claim instead of an assertion.

---

## `same_kernel_decision.py`

### The `OPEN_EXISTING` vs `FILE_OPEN` bug we actually hit
**(b) External contract — documented here because it bit us for real.**
Win32's `dwCreationDisposition` enum (`CREATE_NEW=1, CREATE_ALWAYS=2,
OPEN_EXISTING=3, OPEN_ALWAYS=4, TRUNCATE_EXISTING=5`) and the NT native
`CreateDisposition` enum (`FILE_SUPERSEDE=0, FILE_OPEN=1,
FILE_CREATE=2, FILE_OPEN_IF=3, FILE_OVERWRITE=4, FILE_OVERWRITE_IF=5`)
are **two separate, differently-numbered contracts that happen to share
some English words**. Our first draft of `try_open_via_win32()`
mistakenly passed the NT constant `FILE_OPEN` (value `1`) as Win32's
`dwCreationDisposition` — which Win32 reads as `CREATE_NEW` (also
value `1`), meaning "create the file if it doesn't exist." The result:
the "open a missing file" test silently *created* the missing file and
reported success, defeating the entire experiment. We caught this only
by actually running the script and finding a leftover file on disk, not
by inspection. **Fixed** by declaring `OPEN_EXISTING = 3` explicitly for
the Win32 call, with a comment explaining why the two enums cannot be
shared. This is left in this document deliberately: it's a real,
concrete example of exactly the point the module makes — the two API
layers are not the same vocabulary, and assuming otherwise is a genuine,
easy-to-make mistake, not a hypothetical one.

### Asserting `not os.path.exists(missing_path)` before the test
**(c) Convention, defense specifically motivated by the bug above.**
After being burned once by a disposition mix-up silently creating the
target file, we added an explicit precondition check so a similar
future mistake fails loudly (an `AssertionError`) instead of silently
producing a misleading "both layers succeeded" result.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Struct layouts match the real NT ABI | (b) Forced — undocumented-but-known contract | No |
| `IO_STATUS_BLOCK.Status` sized as pointer, masked to 32 bits | (a) Forced — struct union ABI | No |
| `\??\` path prefix | (b) Forced — NT namespace convention | No |
| Explicit `SYNCHRONIZE` + `FILE_SYNCHRONOUS_IO_NONALERT` | (b) Forced, once you bypass kernel32's default bookkeeping | No, once native calls are used |
| Write via `open()`, read via raw `NtReadFile` | (c) Convention — the module's teaching payload | N/A |
| `OPEN_EXISTING` (Win32) vs `FILE_OPEN` (NT) kept as separate named constants | (b) Forced — two distinct enums | No — conflating them is the bug we hit |
| Precondition assertion on the missing-file test | (c) Convention (defensive, motivated by a real bug) | Yes |

## What We Proved

1. **`nt_native_layer.py`**: a file written through Python's ordinary
   `open()` — which itself routes through kernel32's `CreateFileW` —
   was read back byte-for-byte identical through a direct
   `ntdll!NtCreateFile` + `NtReadFile` call that never touches
   kernel32 at all. The only way both paths can reach identical bytes
   is if they terminate at the same underlying kernel file object,
   confirming the layered model (your code → Win32 API → ntdll.dll →
   NT kernel) from Prerequisite 3 is real, not just a conceptual
   diagram.
2. **`same_kernel_decision.py`**: attempting to open a nonexistent file
   through both layers produced `GetLastError() == 2
   (ERROR_FILE_NOT_FOUND)` via Win32 and `NTSTATUS == 0xC0000034
   (STATUS_OBJECT_NAME_NOT_FOUND)` via the NT native layer — two
   differently-numbered codes representing the exact same underlying
   kernel refusal, confirming there is one shared decision point below
   both APIs, not two independent checks that happen to agree.
