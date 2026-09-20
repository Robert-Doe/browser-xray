# Browser X-Ray — Tag to Byte, From Scratch (web demo)

An interactive port of real mechanics spanning both tracks of the course —
the OS substrate a browser stands on, and the applied byte-to-DOM pipeline
built on top of it — plus a Module Library surfacing all 35 modules and 8
prerequisites in the course, not just the ones with a live demo.

**Address Translation** (Module 1, `01_mem_addressing`) — a genuine x86-64
4-level page-table walk (PML4 → PDPT → PD → PT → 12-bit offset, 4096-byte
pages) implemented in TypeScript. Enter one virtual address and watch two
simulated processes, each with its own table hierarchy, resolve it to
*different* physical frames (or to a page fault) — the actual proof the
module's `prove_aslr_illusion.py` makes: a virtual address is only ever
meaningful relative to the page tables of the process reading it.

**Privilege Rings** (Module 2, `02_privilege_rings`) — a Ring 0–3 diagram
wired to the four real, hand-assembled x86 instructions from
`ring_boundary_probe.py`/`privileged_instr_child.py`: `NOP` (`0x90`),
`RDTSC` (`0x0F 0x31`), `CLI` (`0xFA`), and `HLT` (`0xF4`). Selecting Ring 3
reproduces the module's actual outcome — the two privileged instructions
fault (`#GP`) before they take effect, exactly as `CLI`/`HLT` do when
Windows reports `STATUS_PRIVILEGED_INSTRUCTION` for the real experiment.

**Bytes → HTTP** (Module 16, `http_parsing`) — a real, hand-rolled HTTP/1.1
response parser ported from `http_parser.py`: no `fetch()`, no framework.
Edit a raw response (or pick a Content-Length or chunked-encoding example)
and watch it parsed byte-for-byte, with a genuine hex+ASCII dump of the
exact bytes being parsed.

**HTML → DOM** (Modules 19 and 20, `html_tokenizer` / `dom_tree_builder`) —
the real character-at-a-time tokenizer state machine (named states
matching the WHATWG spec's own names) feeding a real "stack of open
elements" tree constructor, both ported from their Python originals. Six
examples exercise the real spec-accurate recovery paths the course tests:
a stray `<` becoming a literal character, `<?xml?>` becoming a bogus
comment, and unclosed `<p>`/`<li>` auto-closing the previous one — the
resulting DOM tree is drawn as a real SVG diagram (`d3-hierarchy`), not
indented text.

**The Module Library** (below the four tabs) — every one of the course's
35 modules (2 tracks, 10 phases) and 8 prerequisites, browsable by track
and phase. Each module shows its real source files, its real
`DECISIONS.md` reasoning, and verified doc links — generated directly from
the course repo by `scripts/generate-library.mjs`, never hand-transcribed.
Six modules (marked with a dot in the nav) also have the live demos above;
the rest get the same real-code-and-reasoning treatment without a runnable
demo, since many (process sandboxing, syscall filtering, ASLR/DEP/CFI,
site isolation) require actual OS-level privileges a static webpage can't
exercise honestly.

## Local development

```bash
cd webapp
npm install
npm run dev
```

## Build

```bash
npm run build
```

Output goes to `webapp/dist/`.

## Static hosting

Deploy on Vercel, Netlify, or Cloudflare Pages with:

- Root directory: `webapp`
- Build command: `npm run build`
- Output directory: `dist`

No backend, no server-side code — it's a fully static site.
