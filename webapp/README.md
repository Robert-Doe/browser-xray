# Browser X-Ray — Process & Memory Model Explorer (web demo)

An interactive port of two real mechanics from `track1-core-engine/phase1_bare_metal`:

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
