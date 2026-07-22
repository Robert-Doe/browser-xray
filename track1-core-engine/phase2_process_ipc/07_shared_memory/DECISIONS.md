# Module 7: shared_memory — DECISIONS.md

## `shared_writer.py` / `shared_reader.py`

### `mmap.mmap(-1, SIZE, tagname=...)` instead of raw `ctypes` calls to
`CreateFileMapping`/`MapViewOfFile`
**(c) Convention.** Python's standard-library `mmap` module wraps
exactly these two Win32 APIs when given a `tagname` and a file
descriptor of `-1` (meaning "back this by the system paging file, not
a real file"). Modules 1–3 deliberately used raw `ctypes` to expose
every ABI detail; here, the struct-level detail isn't this module's
teaching point (the *sharing behavior* is), so using the well-tested
standard-library wrapper is the right call — while still being honest
that it's calling the identical underlying OS mechanism, not something
Python invented.

### Blocking the writer on `sys.stdin.readline()` rather than a fixed sleep
**(c) Convention.** A fixed sleep (used pragmatically in Modules 4 and
6 for startup timing) would work here too, but a named shared segment
backed only by the paging file is reclaimed once **no process** still
holds a handle to it — so the writer must reliably still be alive when
the reader attaches, for as long as the reader needs. Blocking on
stdin, unblocked explicitly by the orchestrator once the reader has
finished, removes the timing guess entirely for the "stay alive long
enough" half of the problem (a short `sleep` is still used before the
*reader* starts, to give the writer time to finish creating the
segment in the first place).

### Splitting on `\x00` when reading back the segment's contents
**(c) Convention.** The segment is a fixed 4096-byte buffer; only a
prefix of it is meaningfully written in any given run. Splitting on the
first null byte is a simple, explicit way to show "here is the actual
message," rather than printing 4096 mostly-zero bytes and asking the
reader to visually parse it.

## `run_shared_memory_demo.py`

### Building Part B (mismatched tagnames) as a *silent* divergence, not an error case
**(b) External contract — a verified, not assumed, Windows behavior.**
Our first instinct, based on Module 6's pipes-and-sockets pattern, was
to expect a mismatched name to fail the way `OPEN_EXISTING` fails for
pipes. Testing it directly (see `06 Run It`) showed the opposite:
`CreateFileMapping` (via `mmap`'s `tagname`) **creates** a new, private,
zero-filled section if the name doesn't already exist, rather than
failing. This is a real, load-bearing difference in this module's
teaching point, not a design choice we made — we designed Part B
specifically to surface and demonstrate this contract once we'd
confirmed it, rather than assuming pipes/sockets and shared memory fail
the same way.

### `"Local\\module7_shared_demo"` as the tag namespace prefix
**(b) External contract.** The `Local\` prefix places the shared
section in the caller's own Windows session namespace, as opposed to
`Global\`, which requires elevated privileges and is visible across all
sessions on the machine (relevant on multi-user/Terminal Services
systems). Using `Local\` is the appropriate, least-privileged choice
for two processes in the same user session, which is exactly this
module's scenario.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| `mmap` module over raw `ctypes` | (c) Convention (focus on sharing behavior, not ABI) | Yes — Modules 1–3's raw-ctypes style also works here |
| Writer blocks on stdin, not a fixed sleep | (c) Convention (removes a race condition class) | Yes, a longer fixed sleep could substitute, less reliably |
| Part B demonstrates silent divergence, not a thrown error | (b) Forced — verified real `CreateFileMapping` behavior | No — this is what the OS actually does |
| `Local\` namespace prefix | (b) Forced/appropriate — matches this module's same-session scenario | Technically yes (`Global\`), but requires elevation and wider exposure |

## What We Proved

1. **Part A**: a reader process, mapping the same named segment a
   writer had already created and written to, saw the writer's exact
   bytes *the instant it mapped the segment* — no message was sent, no
   IPC call carried the data; it was already there because both
   processes were looking at the same physical memory. The reader then
   wrote its own value back, and the still-running writer process saw
   that change too, on its own next read — proving genuine, live,
   bidirectional sharing distinct from Module 6's one-shot
   message-passing.
2. **Part B**: a reader using a slightly different tagname than the
   writer received **no error** and **no data** — just its own private,
   zero-filled segment, with the mismatch never surfaced anywhere. This
   is real, captured evidence of a genuine, easy-to-miss risk unique to
   shared memory: getting the agreed name wrong doesn't fail loudly the
   way a wrong pipe name or port does (Module 6) — it fails silently,
   by simply not sharing anything, which is a materially different (and
   more dangerous, in production systems) kind of bug to have.
