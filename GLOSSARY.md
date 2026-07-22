# GLOSSARY

Append-only. Alphabetical. Every term is tagged with the module that first
introduced it — if you hit a term you don't recognize in a later module,
it was defined here first; go back to that module's tutorial if you need
the full context, this file only gives the compressed definition.

**Format:** `**Term** — definition. *First seen: Module N (module_name).*`

---

**Address Space** — the full private range of virtual addresses a process
treats as its own; backed by that process's own page tables. *First seen:
Prerequisite 1 (Virtual Memory & Address Spaces).*

**ASLR (Address Space Layout Randomization)** — an OS mitigation that
randomizes the base addresses of a process's stack, heap, and loaded
modules on each run, so a memory-corruption bug alone isn't enough to
predict exploit-relevant addresses. *First seen: Prerequisite 1; proven
experimentally in Module 1 (mem_addressing).*

**CPL (Current Privilege Level)** — the CPU register value that records
which privilege ring currently-executing code is running in. *First seen:
Prerequisite 2 (Privilege Rings).*

**Endianness** — the byte order convention (little-endian or big-endian)
used to store a multi-byte value in memory. *First seen: Prerequisite 6
(Bytes, Hex, and Endianness).*

**Handle** — an opaque, per-process, kernel-issued reference to a system
resource (file, socket, process, etc.), carrying its own access rights
independent of the underlying object. *First seen: Prerequisite 5
(Handles & File Descriptors).*

**IPC (Inter-Process Communication)** — the general category of
kernel-mediated mechanisms (pipes, sockets, shared memory, Mojo, ...) that
let two isolated processes deliberately exchange data. *First seen:
Prerequisite 7 (IPC Channels).*

**id() (CPython)** — a built-in that returns an object's identity; in
CPython specifically (an implementation detail, not a language-spec
guarantee) this value is the object's real virtual memory address.
*First seen: Module 1 (mem_addressing).*

**MEM_COMMIT / MEM_RESERVE / MEM_FREE** — Win32 `VirtualQuery` "State"
values describing whether a virtual memory region is backed by real
storage (COMMIT), merely address-space-reserved (RESERVE), or unused
(FREE). *First seen: Module 1 (mem_addressing).*

**MEM_PRIVATE / MEM_MAPPED / MEM_IMAGE** — Win32 `VirtualQuery` "Type"
values describing whether a region is private process memory, a
memory-mapped file/section, or a loaded executable image. *First seen:
Module 1 (mem_addressing).*

**MEMORY_BASIC_INFORMATION** — the Win32 struct `VirtualQuery` fills in
to describe a memory region's base address, size, protection, state, and
type. *First seen: Module 1 (mem_addressing).*

**MMU (Memory Management Unit)** — the CPU hardware component that
translates virtual addresses to physical addresses on every memory
access, using the current process's page tables. *First seen:
Prerequisite 1 (Virtual Memory & Address Spaces).*

**Origin** — the (scheme, host, port) triple that is the unit of
identity the Same-Origin Policy compares. *First seen: Prerequisite 8
(Origins & URLs).*

**Page** — a fixed-size chunk (4 KB, typically) of virtual memory that
the OS maps to physical memory as a single unit, carrying its own
read/write/execute permission bits. *First seen: Prerequisite 1
(Virtual Memory & Address Spaces).*

**Page Table** — the per-process kernel data structure recording how
that process's virtual pages map to physical memory frames. *First
seen: Prerequisite 1 (Virtual Memory & Address Spaces).*

**PAGE_READWRITE / PAGE_EXECUTE / etc.** — Win32 `VirtualQuery`
"Protect" constants describing a memory page's access permissions.
*First seen: Module 1 (mem_addressing).*

**PCB (Process Control Block)** — the kernel-owned data structure
describing a process: its page table root, open handle table, security
context, and threads. *First seen: Prerequisite 4 (Processes vs.
Threads).*

**Privilege Ring** — a CPU-enforced execution mode; mainstream OSes use
Ring 0 (kernel mode) and Ring 3 (user mode). *First seen: Prerequisite 2
(Privilege Rings).*

**Process** — the OS's unit of isolation: one virtual address space, one
handle table, tracked by a PCB. *First seen: Prerequisite 4 (Processes
vs. Threads).*

**Same-Origin** — two URLs whose scheme, host, and port all match
exactly. *First seen: Prerequisite 8 (Origins & URLs).*

**Same-Site** — a looser match than same-origin, based on the
registrable domain (via the Public Suffix List); the basis for cookie
`SameSite` behavior. *First seen: Prerequisite 8 (Origins & URLs).*

**Syscall (System Call)** — the one sanctioned, kernel-controlled
transition point from Ring 3 into Ring 0, used for anything a process
does that affects the outside world. *First seen: Prerequisite 3
(System Calls).*

**Thread** — the OS's unit of execution: a register state and a stack,
sharing its parent process's address space and handles with any sibling
threads. *First seen: Prerequisite 4 (Processes vs. Threads).*

**Virtual Address** — a per-process, per-run address the CPU translates
via the MMU and page tables; never a physical RAM location itself.
*First seen: Prerequisite 1; proven experimentally in Module 1
(mem_addressing).*

**VirtualQuery** — the real Win32 API function that reports a memory
region's base, size, protection, state, and type for the calling
process's own address space. *First seen: Module 1 (mem_addressing).*

**#GP (General Protection Fault)** — the x86-64 CPU exception raised
when currently executing code attempts an operation its privilege level
doesn't permit, such as a Ring 3 process executing a privileged
instruction. *First seen: Module 2 (privilege_rings).*

**Privileged Instruction** — an x86-64 instruction (e.g. CLI, HLT) that
the ISA itself restricts to CPL 0 (Ring 0); executing one at Ring 3
raises a #GP fault immediately, before the instruction has any effect.
*First seen: Module 2 (privilege_rings).*

**SEH (Structured Exception Handling)** — Windows' mechanism for
delivering hardware and software exceptions to a process in a
catchable form; CPython's `ctypes` wraps foreign-function calls in an
SEH frame on Windows, turning hardware faults into ordinary Python
`OSError`s. *First seen: Module 2 (privilege_rings).*

**STATUS_PRIVILEGED_INSTRUCTION** — the Windows NTSTATUS code
(`0xC0000096`) reported when a process attempts to execute a
privileged CPU instruction outside Ring 0. *First seen: Module 2
(privilege_rings).*

**ERROR_FILE_NOT_FOUND** — the Win32 `GetLastError()` code (`2`)
reported when a requested file doesn't exist; produced by translating
the NT layer's `STATUS_OBJECT_NAME_NOT_FOUND` via
`RtlNtStatusToDosError()`. *First seen: Module 3 (syscall_boundary).*

**NT Native API** — the semi-private API exposed by `ntdll.dll`
(functions prefixed `Nt`/`Zt`, e.g. `NtCreateFile`) that sits directly
below the documented Win32 API and directly above the syscall
transition into the kernel. *First seen: Module 3 (syscall_boundary).*

**ntdll.dll** — the Windows DLL containing the NT Native API; the last
stop in user mode before a syscall instruction transitions into the
kernel. *First seen: Prerequisite 3 (System Calls); called directly in
Module 3 (syscall_boundary).*

**NTSTATUS** — the native Windows kernel status/error code type (a
signed 32-bit value, e.g. `STATUS_SUCCESS = 0x00000000`,
`STATUS_OBJECT_NAME_NOT_FOUND = 0xC0000034`), reported by NT native API
calls. *First seen: Module 3 (syscall_boundary).*

**OBJECT_ATTRIBUTES** — the NT native struct describing what object is
being opened (its name, root directory, and naming attributes),
required by nearly every NT native "open" call. *First seen: Module 3
(syscall_boundary).*

**UNICODE_STRING** — NT's native string type: an explicit
length-prefixed wide-character string, distinct from a Win32
null-terminated `LPCWSTR`. *First seen: Module 3 (syscall_boundary).*

**Win32 API** — the documented, public application-facing Windows API
(e.g. `kernel32.dll`'s `CreateFileW`), implemented as a wrapper over
the NT Native API. *First seen: Prerequisite 3 (System Calls); directly
exercised in Module 3 (syscall_boundary).*

**Integrity Level** — a Windows security-token property (`Untrusted`,
`Low`, `Medium`, `High`, `System`, ...) mainly used to prevent
lower-integrity processes from writing to or manipulating
higher-integrity ones; distinct from Administrator group membership.
*First seen: Module 4 (process_anatomy).*

**OpenProcess** — the Win32 API call that requests a handle to a
different process, with an explicitly named access mask the kernel
checks before granting it. *First seen: Module 4 (process_anatomy).*

**Pseudo-Handle** — a special constant handle value (e.g. from
`GetCurrentProcess()`) that always refers to "the calling process
itself," requiring no access check, unlike a real handle obtained via
`OpenProcess()`. *First seen: Module 4 (process_anatomy).*

**SID (Security Identifier)** — a variable-length structure uniquely
identifying a security principal (a user, group, or in this course's
usage, an integrity level); commonly rendered as a string like
`S-1-16-8192`. *First seen: Module 4 (process_anatomy).*

**Token (Access Token)** — the kernel object representing a process's
(or thread's) security context: its identity, group memberships,
privileges, and integrity level, consulted on every access check
involving that process. *First seen: Module 4 (process_anatomy);
central to Module 9 (least_privilege_tokens).*

**Toolhelp32 Snapshot** — a Win32 mechanism (`CreateToolhelp32Snapshot`)
that captures a point-in-time list of all processes, threads, or
modules system-wide, since Windows provides no direct "count threads
for PID X" query. *First seen: Module 4 (process_anatomy).*

**CreateProcess** — the underlying Windows API (wrapped by Python's
`subprocess`) that spawns a new process with its own fresh, empty
address space. *First seen: Module 5 (process_creation).*

**Pinned Address** — a specific virtual address deliberately requested
via `VirtualAlloc`'s non-NULL `lpAddress` parameter, which either
succeeds at exactly that address or fails outright. *First seen:
Module 5 (process_creation).*

**Zero-Initialization** — the documented Windows guarantee that freshly
`MEM_COMMIT`ted memory pages start filled with zero bytes, never
leftover data from other processes. *First seen: Module 5
(process_creation).*

**Named Pipe** — a Windows IPC mechanism addressed by a string name
(e.g. `\\.\pipe\example`), opened by a client the same way a file is
opened, requiring a server to have already created it. *First seen:
Module 6 (pipes_and_sockets).*

**Loopback Address (127.0.0.1)** — the IP address a machine uses to
address itself; a socket bound only to it is reachable solely from
processes on the same machine, never from the network. *First seen:
Module 6 (pipes_and_sockets).*

**Mojo** — Chromium's own cross-platform IPC system, used for
communication between the Browser Process and Renderer/GPU/utility
processes; built on platform-specific transports (e.g. named pipes on
Windows, Unix domain sockets on POSIX). *First seen: Module 6
(pipes_and_sockets); central to Module 8 (toy_browser_shell).*

**TCP Socket** — a kernel-mediated, connection-oriented IPC channel
addressed by a (host, port) pair, usable both locally and across a
network. *First seen: Module 6 (pipes_and_sockets).*

**CreateFileMapping / MapViewOfFile** — the Win32 API pair that creates
a shared, pagefile- or file-backed memory section and maps it into a
process's address space; wrapped by Python's `mmap` module when given a
`tagname`. *First seen: Module 7 (shared_memory).*

**Local\\ / Global\\ Namespace** — Windows kernel-object naming
prefixes; `Local\` scopes a named object (pipe, shared section, etc.)
to the current login session, `Global\` makes it visible system-wide
and typically requires elevated privilege. *First seen: Module 7
(shared_memory).*

**Shared Memory** — an IPC mechanism where two or more processes map
the identical physical pages into their own address spaces, so writes
by one are immediately visible to the other with no copy — the
deliberate, narrower exception to process isolation. *First seen:
Prerequisite 7 (IPC Channels); built directly in Module 7
(shared_memory).*

**Browser Process** — the single, privileged coordinating process in a
multi-process browser architecture; owns spawning and orchestrating
Renderer Processes and communicates with them only via IPC. *First
seen: Module 8 (toy_browser_shell).*

**Length-Prefixed Framing** — a wire-protocol technique where each
message is preceded by a fixed-size field stating its byte length, so a
receiver reading a byte stream (which has no message boundaries of its
own) knows exactly where one message ends and the next begins. *First
seen: Module 8 (toy_browser_shell).*

**Renderer Process** — a process spawned by the Browser Process to
handle the (in this course, initially simulated) work of turning a URL
into a rendered page; deliberately isolated from the Browser Process
and other renderers via process boundaries. *First seen: Module 8
(toy_browser_shell).*

**CreateProcessAsUser** — the Win32 API that spawns a process running
under an explicitly supplied token rather than the caller's default
one; normally privileged, but exempted from that privilege check when
the supplied token is a duplicate of the caller's own. *First seen:
Module 9 (least_privilege_tokens).*

**Mandatory Integrity Control (MIC)** — Windows' integrity-level-based
access control layer; by default enforces "no write up" (a
lower-integrity process cannot write to a higher-integrity object) but
does *not* by default enforce "no read up." *First seen: Module 4
(process_anatomy); its read/write asymmetry proven directly in Module 9
(least_privilege_tokens).*

**No Write Up** — Mandatory Integrity Control's default policy: a
process cannot write to an object labeled at a higher integrity level
than its own token. *First seen: Module 9 (least_privilege_tokens).*

**SeRelabelPrivilege** — the Windows privilege required to RAISE a
token's integrity level; ordinary user tokens do not hold it, which is
why lowering integrity (no privilege required) is a one-way,
safe-by-default operation. *First seen: Module 9
(least_privilege_tokens).*

**Job Object** — a Windows kernel object that groups processes under
shared, kernel-enforced limits (process count, memory, CPU time, UI
restrictions); child processes join their parent's job automatically by
default. *First seen: Module 10 (syscall_filtering).*

**Win32k System Call Disable** — a documented Windows process
mitigation policy intended to block a process from making any Win32k.sys
(GUI subsystem) syscalls; attempted but not successfully verified
working in this course's environment — see Module 10's DECISIONS.md for
the full account. *First seen: Module 10 (syscall_filtering).*

**No Read Up (process/thread objects)** — Windows' Mandatory Integrity
Control default policy specifically for process and thread kernel
objects: a lower-integrity process cannot open a higher-integrity
process/thread with read access, unlike generic objects such as files,
which allow read-up by default. *First seen: Module 11
(site_isolation_model).*

**ReadProcessMemory** — the Win32 API that reads bytes from another
process's virtual memory, given a handle with sufficient access rights;
whether it succeeds depends entirely on the OS's access-control
decision at handle-acquisition time, not on anything the calling code
does. *First seen: Module 11 (site_isolation_model).*

**Site Isolation** — Chromium's security architecture assigning
different web origins to different, separately sandboxed OS processes;
its real guarantee depends on process separation combined with a
genuine privilege/trust difference between origins' processes, not
process separation alone. *First seen: Prerequisite 4; its precise
mechanism proven in Module 11 (site_isolation_model).*

**ERROR_PARTIAL_COPY** — the Windows error code (299) returned by
`ReadProcessMemory` when the requested address range is only partially
(or not at all) mapped in the target process — a common real signature
of a guessed address landing outside valid memory. *First seen: Module
12 (aslr_and_leaks).*

**Information Leak (Info Leak)** — a bug or behavior that reveals a
memory address (or other secret) to an attacker; the general
precondition for defeating ASLR, since a leaked address combined with a
known fixed offset reveals every other address the offset relates it
to. *First seen: Module 12 (aslr_and_leaks).*

**DEP (Data Execution Prevention)** — Windows' name for CPU-enforced
NX (No-eXecute) protection: memory pages not explicitly marked
executable cannot have their contents run as code, enforced by the CPU
itself at the moment of instruction fetch. *First seen: Prerequisite 1;
proven directly in Module 13 (dep_nx_w_xor_x).*

**NX Bit (No-eXecute)** — the hardware page-table permission bit
(present on essentially all mainstream CPUs since ~2004) that DEP/W^X
is built on; without it, execute-permission enforcement would have no
hardware mechanism to rely on. *First seen: Module 13 (dep_nx_w_xor_x).*

**STATUS_ACCESS_VIOLATION** — the Windows NTSTATUS code (`0xC0000005`)
reported when a process is terminated for an invalid memory access,
including attempting to execute a non-executable page. *First seen:
Module 13 (dep_nx_w_xor_x).*

**W^X (Write XOR Execute)** — the stricter security discipline of never
leaving a memory page both writable and executable at the same time;
the pattern hardened JIT compilers follow by flipping a page's
permissions between writable and executable rather than granting both
simultaneously. *First seen: Module 13 (dep_nx_w_xor_x).*

**CFI (Control Flow Integrity)** — a broader class of mitigation that
validates indirect calls/returns land on legitimate targets at the
point of the jump itself, catching control-flow hijacks that a stack
canary (checked only at one function's return) would miss entirely —
e.g. corrupted heap function pointers or C++ vtable pointers. *First
seen: Module 14 (stack_canaries_cfi).*

**Stack Canary** — a random value the compiler places on the stack
between local buffers and the saved return address, checked
immediately before a function returns; a mismatch indicates a
buffer overflow occurred and the process is terminated before the
(possibly corrupted) return address is used. *First seen: Module 14
(stack_canaries_cfi).*

**STATUS_STACK_BUFFER_OVERRUN** — the Windows NTSTATUS code
(`0xC0000409`) reported when a stack canary check fails, distinct from
the generic `STATUS_ACCESS_VIOLATION` an unmitigated overflow produces
on return. *First seen: Module 14 (stack_canaries_cfi).*

**Cipher Suite** — the combination of cryptographic algorithms (key
exchange, bulk encryption, integrity check) a TLS connection negotiates
to use, e.g. `TLS_AES_256_GCM_SHA384`. *First seen: Module 15
(dns_tcp_tls_handshake).*

**Ephemeral Port** — a temporary, OS-assigned local port number used
for the client side of an outbound connection, drawn from a pool of
high-numbered ports so many simultaneous connections don't collide.
*First seen: Module 15 (dns_tcp_tls_handshake).*

**TLS (Transport Layer Security)** — the protocol that authenticates a
server's identity and encrypts/integrity-protects data in transit;
verifies WHO you're talking to and that the data wasn't tampered with —
says nothing about whether the content itself is safe or trustworthy.
*First seen: Prerequisite 8 (implicit in "https"); proven directly in
Module 15 (dns_tcp_tls_handshake).*

**Chunked Transfer Encoding** — an HTTP/1.1 body-framing mechanism
where the body is sent as a series of hex-length-prefixed pieces
("chunks"), terminated by a zero-length chunk — used when the total
body size isn't known in advance. *First seen: Module 16
(http_parsing).*

**Content-Length** — an HTTP header stating the exact byte size of the
response body, letting a client know precisely how many bytes to read
after the headers. *First seen: Module 16 (http_parsing).*

**HTTP Request/Response Smuggling** — a vulnerability class arising
when two systems in a chain (e.g. a proxy and an origin server)
disagree about where one HTTP message ends and the next begins, often
due to conflicting Content-Length/Transfer-Encoding headers — letting
an attacker hide a message the second system processes but the first
never inspected. *First seen: Module 16 (http_parsing).*

**Same-Origin Policy (SOP)** — the browser-enforced default rule that
script running on one origin cannot read the response of a request to
a different origin; enforced on the client side, after the network
request has already completed — it does not prevent the request itself
from being sent. *First seen: Prerequisite 8; proven directly in
Module 17 (origin_model_sop).*

**CORS (Cross-Origin Resource Sharing)** — a server-controlled,
opt-in relaxation of the Same-Origin Policy, granted per-origin via
`Access-Control-*` response headers; for "non-simple" requests, the
browser sends a preflight OPTIONS request first to ask permission
before risking a real, possibly side-effecting request. *First seen:
Module 18 (cors_preflight).*

**Preflight Request** — an automatic `OPTIONS` request a browser sends
before a non-simple cross-origin request, declaring the intended
method and headers; the real request is only sent if the server's
preflight response explicitly grants it. *First seen: Module 18
(cors_preflight).*

**Simple Request** — an HTTP request (GET/HEAD/POST with only a small
allowlist of headers) that skips CORS preflight; the response-side
`Access-Control-Allow-Origin` check still applies even though the
preflight step is skipped. *First seen: Module 18 (cors_preflight).*

**Bogus Comment** — the HTML5 tokenizer's specified recovery path for
malformed markup after `<?` or an invalid tag/end-tag name: the
remaining content up to the next `>` is swallowed into a Comment token
rather than causing a parse failure. *First seen: Module 19
(html_tokenizer).*

**Parse Error (HTML5 spec sense)** — a label for malformed input in the
HTML5 tokenization/parsing spec that is always paired with an exact,
defined recovery action; processing never stops because of one. *First
seen: Module 19 (html_tokenizer).*

**Tokenizer** — the component that converts a raw character stream
into a flat sequence of tokens (start tags, end tags, comments,
character data) via an explicit state machine, without building any
tree structure. *First seen: Module 19 (html_tokenizer).*

**Adoption Agency Algorithm** — the real HTML5 spec's sophisticated
procedure for handling misnested formatting elements (e.g.
`<b><i>text</b></i>`), which can reconstruct and duplicate elements to
preserve likely author intent; more sophisticated than simple
stack-unwinding. *First seen: Module 20 (dom_tree_builder).*

**Stack of Open Elements** — the core data structure of HTML5 tree
construction: elements are pushed when opened and popped when closed
(or implicitly closed), with the top of the stack always representing
the current insertion point for new nodes. *First seen: Module 20
(dom_tree_builder).*

**CSSOM (CSS Object Model)** — the tree of parsed CSS rules and
declarations, built entirely independently of the DOM, with no
awareness of any specific HTML document until style computation later
matches selectors against it. *First seen: Module 21
(css_parser_cssom).*

**Forward-Compatible Parsing** — CSS's deliberate design property that
an unrecognized construct (a malformed declaration, an unknown at-rule)
is safely skipped rather than aborting the entire stylesheet — allowing
old parsers to survive newer CSS features they don't understand yet.
*First seen: Module 21 (css_parser_cssom).*

**!important** — a CSS declaration modifier that lets it override rules
that would otherwise win the cascade based on specificity or source
order. *First seen: Module 21 (css_parser_cssom).*

**Cascade** — the algorithm that resolves conflicting CSS declarations
targeting the same element and property into one final value, in
strict priority order: `!important` beats specificity, specificity
beats source order. *First seen: Module 22 (style_computation).*

**Computed Style** — the final, resolved set of property values a
browser assigns to a DOM element after running the cascade against
every matching CSS rule. *First seen: Module 22 (style_computation).*

**Specificity** — a selector's weight in the cascade, calculated as an
`(IDs, classes, types)` tuple compared lexicographically — any number
of type selectors never outweighs one class selector, and any number
of classes never outweighs one ID selector. *First seen: Module 22
(style_computation).*

**Block Flow / Block-Level Layout** — the default CSS layout mode
where each element stacks vertically below the previous sibling and
fills its parent's available width unless given an explicit width.
*First seen: Module 23 (layout_box_model).*

**Box-Sizing (content-box vs. border-box)** — the CSS property
controlling whether a declared `width`/`height` describes content only
(`content-box`, CSS's default — padding/border add on top) or the
total box including padding and border (`border-box` — content shrinks
to fit). *First seen: Module 23 (layout_box_model).*

**Layout / Box Model** — the pipeline stage that computes real
geometry (x, y, width, height) for every element from its computed
style, recursively, based on its parent's available space and its
children's own computed geometry. *First seen: Module 23
(layout_box_model).*

**Compositor Layer** — a separately-managed painted surface (bitmap)
that can be repositioned, scaled, or faded by the GPU without
re-running layout or paint; triggered by specific CSS properties like
`transform`, `opacity` animations, or `will-change`. *First seen:
Module 24 (paint_and_composite).*

**Paint** — the pipeline stage that reads an element's visual computed
style and records what color/pixels go where in its own local box
coordinates; distinct from composite, which positions already-painted
content. *First seen: Module 24 (paint_and_composite).*

**Composite** — the pipeline stage that arranges already-painted
content into layers and positions them for final display; can run
independently of layout and paint for compositor-only property changes
like `transform`. *First seen: Module 24 (paint_and_composite).*

**AST (Abstract Syntax Tree)** — the tree-structured representation of
parsed source code, with no execution semantics attached; the output
of parsing and the input to interpretation/compilation. *First seen:
Module 25 (js_lexer_parser).*

**Precedence Climbing** — a compact recursive-descent technique for
parsing binary expressions correctly, using a single function and a
precedence table rather than one grammar rule per precedence level.
*First seen: Module 25 (js_lexer_parser).*

**Recursive Descent (Parsing)** — a parsing technique where each
grammar rule is implemented as a function that may call other
rule-functions recursively, mirroring the grammar's own structure.
*First seen: Module 25 (js_lexer_parser).*

**Closure** — a function value bundled with a reference to the lexical
scope (`Environment`) active at the moment it was defined, letting it
access those variables later even after that defining scope's own code
has finished running. *First seen: Module 26
(tree_walking_interpreter).*

**Environment (Scope Chain)** — a linked chain of variable scopes;
looking up a name checks the current scope, then walks outward through
parent scopes until found. *First seen: Module 26
(tree_walking_interpreter).*

**Tree-Walking Interpreter** — the simplest way to execute an AST:
recursively visit each node and evaluate it directly, re-dispatching on
node type every single visit, with no intermediate compiled
representation. *First seen: Module 26 (tree_walking_interpreter).*

**Bytecode** — a flat, precompiled sequence of small instructions
(opcodes + arguments) produced once from an AST, executed by a VM loop
that indexes into the array via a program counter rather than
re-walking tree structure. *First seen: Module 27 (bytecode_vm).*

**Opcode** — the part of a bytecode instruction identifying which
operation to perform (e.g. `LOAD_CONST`, `BINARY_OP`), as distinct from
its argument/operand. *First seen: Module 27 (bytecode_vm).*

**Program Counter (PC)** — the index into a flat instruction list
indicating which instruction executes next; advanced by one after each
instruction, or set directly by jump instructions. *First seen: Module
27 (bytecode_vm).*

**Event Loop** — the single-threaded scheduling mechanism that runs
queued callbacks one at a time, fully draining the microtask queue
after each macrotask (and after the initial synchronous script),
rather than executing anything in true parallel. *First seen: Module
28 (event_loop_microtasks).*

**Macrotask** — a queued unit of work (e.g. `setTimeout`, I/O
callbacks, UI events) that runs one at a time, with the microtask
queue fully drained after each one completes. *First seen: Module 28
(event_loop_microtasks).*

**Microtask** — a queued unit of work (e.g. `Promise.then`,
`queueMicrotask`) that is run to full queue exhaustion — including
microtasks queued by other microtasks mid-drain — before the next
macrotask is allowed to run. *First seen: Module 28
(event_loop_microtasks).*

**Public Suffix List (PSL)** — the list of domain suffixes (e.g.
`.com`, `.co.uk`) that are NOT themselves registrable, used to
correctly compute a hostname's registrable domain for same-site
comparisons. *First seen: Module 29 (cookies_samesite).*

**Registrable Domain** — the smallest domain a person could actually
register (one label plus a public suffix, e.g. `example.com` or
`example.co.uk`); the basis for same-site comparisons. *First seen:
Prerequisite 8; computed directly in Module 29 (cookies_samesite).*

**SameSite (cookie attribute)** — a cookie attribute (`Strict`, `Lax`,
or `None`) controlling whether it's sent on cross-site requests;
enforcement depends on both cross-site status and request context
(top-level navigation vs. subresource, safe vs. unsafe method). *First
seen: Module 29 (cookies_samesite).*

**CSP (Content Security Policy)** — a browser-enforced, opt-in
allowlist (declared via an HTTP header) restricting which sources a
page may load scripts, styles, and other resources from; checked
before a resource would load or execute, not as an after-the-fact
filter. Real, primary use case: neutralizing an XSS payload's ability
to run even after an injection has already occurred. *First seen:
Module 30 (csp_enforcement).*

**'unsafe-inline'** — a CSP `script-src`/`style-src` keyword that
permits ALL inline scripts/styles on a page; a real, common
migration-era compromise, distinct from the more precise
nonce/hash-based allowlisting real CSP also supports. *First seen:
Module 30 (csp_enforcement).*

**HSTS (HTTP Strict Transport Security)** — a browser-enforced policy,
learned from a `Strict-Transport-Security` response header, that
rewrites future `http://` requests to a host to `https://` before any
network request is made — preventing SSL-stripping downgrade attacks
after the first successful HTTPS visit. *First seen: Module 31
(mixed_content_hsts).*

**HSTS Preload List** — a hardcoded list, shipped inside the browser
itself, of domains treated as HTTPS-only from their very first-ever
request — closing the "trust on first use" gap ordinary
header-learned HSTS has. *First seen: Module 31 (mixed_content_hsts).*

**Mixed Content** — a resource loaded over plain HTTP on an otherwise
HTTPS page; modern browsers auto-upgrade passive content (images,
audio, video) to HTTPS and block active content (scripts, stylesheets,
frames) outright, reflecting the real difference in what a network
attacker could do with each. *First seen: Module 31
(mixed_content_hsts).*

**CSRF (Cross-Site Request Forgery)** — an attack where a cross-site
page causes the victim's own browser to send a real, cookie-
authenticated request to a target site, exploiting the fact that
cookies (unless SameSite-restricted) are attached regardless of which
page triggered the request. *First seen: Module 32
(xss_csrf_on_toy_browser).*

**XSS (Cross-Site Scripting)** — an attack where attacker-controlled
input is inserted into a page's HTML without escaping, becoming a real
executable script in the page's own DOM and origin. *First seen:
Module 32 (xss_csrf_on_toy_browser).*

**Clickjacking** — an attack exploiting the real separation between
compositing (visual opacity) and input hit-testing (click routing,
based purely on topmost layer/z-index): a nearly-invisible element is
positioned to receive clicks the user believes are going to a
different, visible element underneath. *First seen: Module 33
(clickjacking_uxss).*

**frame-ancestors** — a CSP directive (successor to `X-Frame-Options`)
letting a page declare which origins may embed it in a frame at all,
checked before the framing succeeds — the real defense against
clickjacking. *First seen: Module 33 (clickjacking_uxss).*

**UXSS (Universal Cross-Site Scripting)** — a categorically more severe
vulnerability class than ordinary XSS: a bug in the BROWSER ENGINE's
own origin-enforcement code (not any individual website) that lets
script from one origin access another origin's window/document
directly — unfixable by any website's own configuration, since the
flaw sits below where site-level defenses like CSP operate. *First
seen: Module 33 (clickjacking_uxss).*

**Constant-Time Comparison** — a comparison implementation that always
performs the same amount of work regardless of where (or whether) a
mismatch occurs, closing off timing side-channels that an early-exit
comparison would otherwise leak through. *First seen: Module 34
(side_channel_timing).*

**Timing Side-Channel** — an information leak where a secret can be
inferred purely from how LONG an operation takes, independent of
whether the operation's actual output/content is ever readable;
neither the Same-Origin Policy nor site isolation were designed to hide
timing, only content. *First seen: Module 34 (side_channel_timing).*

**Defense in Depth** — the security principle that multiple,
independent, individually-limited defensive mechanisms, layered
together, produce meaningfully stronger protection than any single
mechanism alone, since an attacker must defeat all of them
simultaneously rather than just one. *First seen: Module 35
(sandbox_escape_chain), proven directly via a real 2×2 combined-defense
matrix.*
