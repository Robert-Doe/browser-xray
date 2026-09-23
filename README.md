# browser-xray

I got tired of repeating security claims I couldn't actually back up. "Site Isolation stops cross-origin memory reads." Sure, I'd read that a dozen times, in a dozen writeups, and I believed it the way you believe a fact you were told rather than one you found out for yourself. That gap bothered me enough that I built this: a real, working, toy browser stack, from the OS floor all the way up, so that every claim like that one is something I put two things in two processes and personally tried to break.

This is part of a bigger research program I'm running as a PhD security researcher. I've got several "build a browser from scratch" courses going at once, each one attacking the problem from a different angle. This is the one that starts a full layer lower than the others: at the OS process substrate that a browser's entire security model sits on top of. Everything else, the sandboxing, the site isolation, the exploit mitigations, is built out of that substrate, and I wanted a course that actually proved that instead of asserting it.

## The two things stacked on each other

A real browser's security model is really two systems, one riding on the other.

**Track 1, the Core Engine**, is the OS and process substrate. Address spaces, processes, IPC, sandboxing primitives, exploit mitigations. No browser code shows up yet, because this is the ground the browser stands on. A sentence like "Site Isolation prevents cross-origin memory reads" only means something once you've personally put two things in two processes and tried to read across that boundary and failed.

**Track 2, the Applied Layer**, is the browser engine and web security proper. Networking, HTML and CSS parsing, rendering, a JS engine, and the policies (SOP, CORS, cookies, CSP, HSTS) that only make sense once you already know which process boundary they're riding on. Track 2 leans on Track 1 constantly. You cannot reason correctly about Site Isolation, a sandbox escape, or a timing side channel without the process and IPC substrate sitting underneath it.

## Track 1, Core Engine: OS and process substrate

| # | Module | What it proves | Directory |
|---|--------|-----------------|-----------|
| 1 | Memory Addressing | A process's virtual address space is a translated illusion, not physical memory. The same virtual address in two processes maps to different physical RAM | [`track1-core-engine/phase1_bare_metal/01_mem_addressing/`](track1-core-engine/phase1_bare_metal/01_mem_addressing/) |
| 2 | Privilege Rings | User-mode code physically cannot execute a privileged instruction without trapping into the kernel | [`.../02_privilege_rings/`](track1-core-engine/phase1_bare_metal/02_privilege_rings/) |
| 3 | Syscall Boundary | Every "browser action" is a request that crosses into kernel code, traceable and interceptable | [`.../03_syscall_boundary/`](track1-core-engine/phase1_bare_metal/03_syscall_boundary/) |
| 4 | Process Anatomy | A process is a kernel-held data structure plus an address space plus threads, not "a running .exe" | [`.../04_process_anatomy/`](track1-core-engine/phase1_bare_metal/04_process_anatomy/) |
| 5 | Process Creation | Spawning a child process creates a genuinely distinct address space | [`.../05_process_creation/`](track1-core-engine/phase2_process_ipc/05_process_creation/) |
| 6 | Pipes and Sockets | Two isolated processes can only exchange data through an explicitly set up, kernel-mediated channel | [`.../06_pipes_and_sockets/`](track1-core-engine/phase2_process_ipc/06_pipes_and_sockets/) |
| 7 | Shared Memory | The one deliberate exception to process isolation has to be opted into by both sides | [`.../07_shared_memory/`](track1-core-engine/phase2_process_ipc/07_shared_memory/) |
| 8 | Toy Browser Shell | A browser can be correctly modeled as one Browser Process plus N Renderer Processes exchanging structured IPC. This is the seed of the toy browser | [`.../08_toy_browser_shell/`](track1-core-engine/phase2_process_ipc/08_toy_browser_shell/) |
| 9 | Least-Privilege Tokens | A process's OS-level permissions can be stripped after spawn, so a renderer literally cannot open a file its parent can | [`.../09_least_privilege_tokens/`](track1-core-engine/phase3_sandboxing/09_least_privilege_tokens/) |
| 10 | Syscall Filtering | A process can be blocked from making certain syscalls at all, even if compromised code inside it tries | [`.../10_syscall_filtering/`](track1-core-engine/phase3_sandboxing/10_syscall_filtering/) |
| 11 | Site Isolation Model | Putting two origins in two sandboxed OS processes makes cross-origin memory reads impossible without going through IPC | [`.../11_site_isolation_model/`](track1-core-engine/phase3_sandboxing/11_site_isolation_model/) |
| 12 | ASLR and Leaks | ASLR only raises exploit cost by randomizing addresses. It proves nothing once a single info leak exists | [`.../12_aslr_and_leaks/`](track1-core-engine/phase4_mitigations/12_aslr_and_leaks/) |
| 13 | DEP/NX (W^X) | W^X blocks code written into data memory from ever executing. Shown by triggering the fault, then the sanctioned alternative | [`.../13_dep_nx_w_xor_x/`](track1-core-engine/phase4_mitigations/13_dep_nx_w_xor_x/) |
| 14 | Stack Canaries and CFI | Canaries and CFI catch control-flow hijacks only at specific checkpoints, not universally | [`.../14_stack_canaries_cfi/`](track1-core-engine/phase4_mitigations/14_stack_canaries_cfi/) |

## Track 2, Applied Layer: browser engine and web security

| # | Module | What it proves | Directory |
|---|--------|-----------------|-----------|
| 15 | DNS/TCP/TLS Handshake | What "loading a URL" costs before a single byte of HTML arrives | [`.../15_dns_tcp_tls_handshake/`](track2-applied-layer/phase5_networking/15_dns_tcp_tls_handshake/) |
| 16 | HTTP Parsing | An HTTP response is structured text over a socket, hand-parseable with no framework magic | [`.../16_http_parsing/`](track2-applied-layer/phase5_networking/16_http_parsing/) |
| 17 | Origin Model / SOP | The browser, not the server, enforces that script from origin A cannot read a response from origin B | [`.../17_origin_model_sop/`](track2-applied-layer/phase5_networking/17_origin_model_sop/) |
| 18 | CORS Preflight | CORS is an opt-in relaxation of SOP through an extra validated round trip, not an independent mechanism | [`.../18_cors_preflight/`](track2-applied-layer/phase5_networking/18_cors_preflight/) |
| 19 | HTML Tokenizer | HTML parsing is a state machine with defined recovery behavior, not "reading tags" | [`.../19_html_tokenizer/`](track2-applied-layer/phase6_parsing_dom/19_html_tokenizer/) |
| 20 | DOM Tree Builder | The DOM is built incrementally from tokens under insertion-mode rules, not assembled all at once | [`.../20_dom_tree_builder/`](track2-applied-layer/phase6_parsing_dom/20_dom_tree_builder/) |
| 21 | CSS Parser / CSSOM | CSS becomes a separate object tree, parsed independently of the DOM and merged later | [`.../21_css_parser_cssom/`](track2-applied-layer/phase6_parsing_dom/21_css_parser_cssom/) |
| 22 | Style Computation | Every DOM node gets one fully resolved computed style through cascade and specificity before any pixel exists | [`.../22_style_computation/`](track2-applied-layer/phase7_rendering/22_style_computation/) |
| 23 | Layout / Box Model | Layout is a recursive geometry pass producing real x, y, width, and height boxes from styled nodes | [`.../23_layout_box_model/`](track2-applied-layer/phase7_rendering/23_layout_box_model/) |
| 24 | Paint and Composite | Paint (pixels) and composite (layers) are separate stages, which is why a compositor-only change skips layout and paint entirely | [`.../24_paint_and_composite/`](track2-applied-layer/phase7_rendering/24_paint_and_composite/) |
| 25 | JS Lexer/Parser | JS source becomes an AST before a single line executes | [`.../25_js_lexer_parser/`](track2-applied-layer/phase8_js_engine/25_js_lexer_parser/) |
| 26 | Tree-Walking Interpreter | The naive way to run JS is direct AST evaluation, and it is slow, measured here | [`.../26_tree_walking_interpreter/`](track2-applied-layer/phase8_js_engine/26_tree_walking_interpreter/) |
| 27 | Bytecode VM | A bytecode VM is a deliberate engineering response to interpreter overhead, measured against Module 26 | [`.../27_bytecode_vm/`](track2-applied-layer/phase8_js_engine/27_bytecode_vm/) |
| 28 | Event Loop / Microtasks | JS concurrency is single-threaded cooperative scheduling through task and microtask queues, not real parallelism | [`.../28_event_loop_microtasks/`](track2-applied-layer/phase8_js_engine/28_event_loop_microtasks/) |
| 29 | Cookies / SameSite | SameSite is an origin-adjacent boundary enforced by the browser on outgoing requests, set by a server-controlled flag | [`.../29_cookies_samesite/`](track2-applied-layer/phase9_policy_layer/29_cookies_samesite/) |
| 30 | CSP Enforcement | CSP is a browser-side allowlist checked before script or resource execution, not a server-side filter | [`.../30_csp_enforcement/`](track2-applied-layer/phase9_policy_layer/30_csp_enforcement/) |
| 31 | Mixed Content / HSTS | HSTS and mixed-content blocking exist specifically to stop a silent HTTPS to HTTP downgrade | [`.../31_mixed_content_hsts/`](track2-applied-layer/phase9_policy_layer/31_mixed_content_hsts/) |
| 32 | XSS/CSRF on the Toy Browser | A real XSS/CSRF payload succeeds against the toy browser until the specific policy module is wired in, then fails | [`.../32_xss_csrf_on_toy_browser/`](track2-applied-layer/phase10_attack_surface/32_xss_csrf_on_toy_browser/) |
| 33 | Clickjacking / UXSS | Clickjacking exploits the compositor and paint model, UXSS exploits a site-isolation gap, both demonstrated against this stack | [`.../33_clickjacking_uxss/`](track2-applied-layer/phase10_attack_surface/33_clickjacking_uxss/) |
| 34 | Side-Channel Timing | A non-weaponized timing side channel can leak cross-origin data even when SOP and site isolation block direct reads | [`.../34_side_channel_timing/`](track2-applied-layer/phase10_attack_surface/34_side_channel_timing/) |
| 35 | Sandbox Escape Chain | A full browser compromise needs multiple independently-built layers defeated together, tying both tracks into one attacker's-eye chain | [`.../35_sandbox_escape_chain/`](track2-applied-layer/phase10_attack_surface/35_sandbox_escape_chain/) |

## Cross-cutting lessons

Some ideas show up in genuinely different forms across several modules and never really belonged to just one of them. [`lessons/`](lessons/) pulls those out into their own concept clusters with fuller treatment: history, real-world alternative implementations, security implications, performance tradeoffs.

- [`01_ipc_across_the_stack`](lessons/01_ipc_across_the_stack/): Modules 6, 7, 8, 15, and 16, on how the same underlying IPC mechanism shows up as a raw OS primitive, then a custom application protocol, then a standardized internet protocol.
- [`02_browser_policy_stack`](lessons/02_browser_policy_stack/): Modules 17, 18, 29, 30, and 31, on how SOP, CORS, cookies, CSP, and HSTS interact and layer as defense in depth instead of standing alone.

## Tech stack

I used Python 3 as the primary language, mostly for speed of building and introspection over raw execution speed. It handles the IPC and the toy HTTP, DOM, CSS, and JS-engine modules along with the policy layer. C shows up only where a primitive has to be shown at the metal with nothing cushioning it, like `VirtualProtect`/`mprotect`, a raw shellcode-in-buffer demo for W^X in Module 13, and a stack-smashing target in Module 14.

Windows 11 native APIs (Job Objects, restricted tokens, integrity levels, `VirtualProtect`) are the primary platform target, because that's a real production sandbox model, and Chromium's actual Windows sandbox runs on exactly these primitives. WSL2/Linux shows up as a named comparison track for seccomp-bpf and namespaces, since most public Chromium sandbox-escape research is Linux or Android based, and I call out where the two diverge instead of quietly substituting one for the other.

Networking runs over real sockets and TLS through Python's `socket`/`ssl` stdlib. No fabricated protocol behavior anywhere. Verification is logs, hex dumps, and printed state rather than a GUI, and every module has a `SAFETY_NOTES.md` describing exactly what the demo does to the host and how to run it without causing yourself a bad afternoon.

What's deliberately out of scope: a spec-complete rendering engine, GPU compositing, a real V8-compatible JIT or optimizing compiler, a real cryptographic implementation (TLS runs through stdlib, I didn't reimplement it), mobile-browser specifics, weaponized exploit code, and any modification of actual Chromium source.

## Where this stands

All 35 modules across both tracks exist, each with a `tutorial.html`, a `DECISIONS.md`, a `SAFETY_NOTES.md`, and runnable Python (and for Modules 13 and 14, C) source, plus the two cross-cutting lesson clusters and the full prerequisites set. See [`ROADMAP.md`](ROADMAP.md) for the original phase-by-phase plan and [`GLOSSARY.md`](GLOSSARY.md) for every term, tagged with the module or prerequisite that introduces it first.

## How to explore or run it

Every module directory stands on its own:

- `tutorial.html`, the write-up: the concept, why it matters for browser security, and what the code demonstrates.
- `DECISIONS.md`, the design decisions and trade-offs behind that module's implementation.
- `SAFETY_NOTES.md`, what the module's code actually does on the host and how to run it without causing harm. This matters most in Track 1's process, sandboxing, and mitigation modules, which intentionally trigger faults, spawn low-privilege processes, or demonstrate exploit primitives.
- one or more `.py` files, occasionally a `.c` file, the runnable implementation.

Read the `SAFETY_NOTES.md` before you run anything. For a typical Python module:

```bash
cd track2-applied-layer/phase6_parsing_dom/19_html_tokenizer
python run_tokenizer_demo.py
```

For the small set of C modules (Track 1, Phase 4, the mitigations), compile first:

```bash
cd track1-core-engine/phase4_mitigations/13_dep_nx_w_xor_x
gcc dep_violation.c -o dep_violation
./dep_violation
```

Later modules generally depend on primitives that earlier ones already proved (Track 2 leans on Track 1's process and IPC substrate the whole way through, check each module's row in `ROADMAP.md` for its exact dependencies), so I'd read and run these in ascending order rather than picking one at random. If any of virtual memory, privilege rings, syscalls, processes and threads, handles and file descriptors, bytes/hex/endianness, IPC channels, or origins and URLs feels shaky, start with [`prerequisites/`](prerequisites/) first.
