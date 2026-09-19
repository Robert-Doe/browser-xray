import './style.css';
import { splitVirtualAddress, walk, physicalAddress, hex, PAGE_SIZE } from './paging';
import { INSTRUCTIONS, execute, Ring } from './rings';

const app = document.getElementById('app')!;

app.innerHTML = `
  <div class="topbar">
    <div class="brand">Browser X-Ray</div>
    <div class="links">
      <a href="https://github.com/Robert-Doe/browser-xray" target="_blank" rel="noopener">GitHub</a>
      <a href="https://robertdoe.com">&larr; robertdoe.com</a>
    </div>
  </div>
  <div class="hero">
    <h1>Process &amp; Memory Model Explorer</h1>
    <p class="tagline">
      Real mechanics from the course, ported to TypeScript: a live
      <code>x86-64</code> 4-level page-table walk proving virtual addresses
      are a per-process illusion, and the Ring 0 / Ring 3 hardware boundary
      that real x86 instructions cannot cross without a fault.
    </p>
  </div>
  <main>
    <div class="tabs" id="tabs"></div>
    <div id="tab-content"></div>
  </main>
  <footer>
    Ported from <a href="https://github.com/Robert-Doe/browser-xray" target="_blank" rel="noopener">Robert-Doe/browser-xray</a>,
    track1-core-engine &mdash; real bit layouts, real opcodes, real fault semantics.
  </footer>
`;

const tabsEl = document.getElementById('tabs')!;
const contentEl = document.getElementById('tab-content')!;

type TabId = 'paging' | 'rings';
let activeTab: TabId = 'paging';

const tabs: { id: TabId; label: string }[] = [
  { id: 'paging', label: 'Address Translation' },
  { id: 'rings', label: 'Privilege Rings' },
];

function renderTabs(): void {
  tabsEl.innerHTML = tabs
    .map((t) => `<button class="tab-btn ${t.id === activeTab ? 'active' : ''}" data-tab="${t.id}">${t.label}</button>`)
    .join('');
  tabsEl.querySelectorAll<HTMLButtonElement>('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      activeTab = btn.dataset.tab as TabId;
      renderAll();
    });
  });
}

function renderAll(): void {
  renderTabs();
  if (activeTab === 'paging') renderPagingTab();
  else renderRingsTab();
}

renderAll();

// ---------------------------------------------------------------------------
// Tab 1: virtual-to-physical address translation, two processes
// ---------------------------------------------------------------------------

const PROC_A_SEED = 0xa11ce001;
const PROC_B_SEED = 0xb0b00b02;
const PROC_A_PID = 4812;
const PROC_B_PID = 5936;

const PRESET_ADDRS = ['0x00001F6330144B0', '0x00007FFE12340000', '0x0000000140001000'];

function renderPagingTab(): void {
  contentEl.innerHTML = `
    <div class="card">
      <h2>Same virtual address, two processes, two page tables</h2>
      <p class="desc">
        This is the real proof from Module 1 (<code>mem_addressing</code>):
        a virtual address only ever means something relative to the
        page tables of the process reading it. Real x86-64 hardware splits
        every 48-bit virtual address into five fields the MMU walks on
        every access &mdash; a 9-bit index into each of four table levels,
        plus a 12-bit in-page offset (4096-byte pages). Enter one virtual
        address; each process below resolves it through its <em>own</em>
        table hierarchy (its own <code>CR3</code>).
      </p>
      <label style="display:flex;flex-direction:column;gap:6px;font-size:12px;color:var(--text-dim);max-width:320px">
        Virtual address (hex)
        <input id="va-input" type="text" value="${PRESET_ADDRS[0]}" spellcheck="false" />
      </label>
      <div class="btn-row">
        <button class="btn" id="translate-btn">Translate</button>
        ${PRESET_ADDRS.map((a) => `<button class="btn secondary preset-btn" data-addr="${a}">${a}</button>`).join('')}
      </div>
    </div>
    <div id="va-fields-card"></div>
    <div class="two-pane" id="proc-panels"></div>
    <div id="verdict-card"></div>
  `;

  const input = document.getElementById('va-input') as HTMLInputElement;

  function run() {
    let raw = input.value.trim();
    if (!raw) return;
    let big: bigint;
    try {
      big = BigInt(raw.startsWith('0x') || raw.startsWith('0X') ? raw : '0x' + raw);
    } catch {
      contentEl.querySelector('#verdict-card')!.innerHTML = `<div class="card"><p class="desc" style="color:var(--danger)">Not a valid hex address.</p></div>`;
      return;
    }
    // Keep it within the 48-bit canonical range real x86-64 uses.
    big = big & 0xffffffffffffn;

    const fields = splitVirtualAddress(big);

    document.getElementById('va-fields-card')!.outerHTML = `
      <div class="card" id="va-fields-card">
        <h2 style="font-size:15px">Bit-field breakdown of ${hex(big)}</h2>
        <p class="desc">This split is identical for every process &mdash; it's fixed by the MMU hardware, not by any OS policy.</p>
        <div class="bit-breakdown">
          <div class="seg"><span class="lbl">PML4[47:39]</span><span class="num">${fields.pml4}</span></div>
          <div class="seg"><span class="lbl">PDPT[38:30]</span><span class="num">${fields.pdpt}</span></div>
          <div class="seg"><span class="lbl">PD[29:21]</span><span class="num">${fields.pd}</span></div>
          <div class="seg"><span class="lbl">PT[20:12]</span><span class="num">${fields.pt}</span></div>
          <div class="seg"><span class="lbl">offset[11:0]</span><span class="num">${hex(fields.offset)}</span></div>
        </div>
      </div>
    `;

    const panels = document.getElementById('proc-panels')!;
    const a = walk(PROC_A_SEED, fields);
    const b = walk(PROC_B_SEED, fields);
    const physA = a.present ? physicalAddress(a, fields.offset) : null;
    const physB = b.present ? physicalAddress(b, fields.offset) : null;

    panels.innerHTML = [
      { label: 'Process A', pid: PROC_A_PID, entry: a, phys: physA },
      { label: 'Process B', pid: PROC_B_PID, entry: b, phys: physB },
    ]
      .map(
        (p) => `
        <div class="process-panel">
          <div class="pid">PID ${p.pid} &middot; own CR3 root &middot; own 4-level tables</div>
          <h3>${p.label}</h3>
          <table class="byte-table">
            <tr><th>PTE.present</th><td>${p.entry.present ? '1' : '0'}</td></tr>
            <tr><th>PTE.frame</th><td>${p.entry.present ? hex(p.entry.frame) : '&mdash;'}</td></tr>
          </table>
          ${
            p.phys !== null
              ? `<div class="result-addr">${hex(p.phys)}</div><p class="desc" style="margin:4px 0 0">physical address = frame &times; ${PAGE_SIZE} + offset</p>`
              : `<div class="result-addr" style="color:var(--danger)">#PF page fault</div><p class="desc" style="margin:4px 0 0">not present in this process's tables</p>`
          }
        </div>`
      )
      .join('');

    const verdict = document.getElementById('verdict-card')!;
    if (physA !== null && physB !== null) {
      const same = physA === physB;
      verdict.innerHTML = `
        <div class="verdict ${same ? 'same' : 'diff'}">
          ${
            same
              ? 'Coincidence: both processes happened to land on the same physical frame for this address (rare, but possible). Try another address to see the normal case.'
              : `Confirmed: the identical virtual address <code>${hex(big)}</code> resolves to <strong>different physical RAM</strong> in each process. Nothing about the number itself pins it to a location &mdash; only that process's own page tables do.`
          }
        </div>`;
    } else {
      verdict.innerHTML = `
        <div class="verdict diff">
          At least one process has no mapping for this address at all &mdash; a real, valid outcome. Isolation cuts both ways: a process can't even discover whether another process has something mapped there.
        </div>`;
    }
  }

  document.getElementById('translate-btn')!.addEventListener('click', run);
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') run(); });
  contentEl.querySelectorAll<HTMLButtonElement>('.preset-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      input.value = btn.dataset.addr!;
      run();
    });
  });

  run();
}

// ---------------------------------------------------------------------------
// Tab 2: privilege rings
// ---------------------------------------------------------------------------

let selectedRing: Ring = 3;

function ringSvg(): string {
  const rings: { r: number; ring: Ring; fill: string }[] = [
    { r: 150, ring: 3, fill: '#2a2a2e' },
    { r: 112, ring: 2, fill: '#3a2f14' },
    { r: 75, ring: 1, fill: '#4a3a10' },
    { r: 38, ring: 0, fill: '#d4a017' },
  ];
  const cx = 160, cy = 160;
  return `
    <svg class="ring-svg" width="320" height="320" viewBox="0 0 320 320">
      ${rings
        .map(
          (r) => `<circle cx="${cx}" cy="${cy}" r="${r.r}" fill="${r.ring === selectedRing ? r.fill : '#1c1c20'}"
            stroke="${r.ring === selectedRing ? 'var(--accent)' : 'var(--border)'}" stroke-width="${r.ring === selectedRing ? 2.5 : 1}"
            data-ring="${r.ring}" />`
        )
        .join('')}
      <text x="${cx}" y="${cy + 5}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="20" font-weight="700" fill="var(--text)">R${selectedRing}</text>
      ${rings
        .map((r, i) => {
          const labelY = cy - r.r + 16;
          return `<text x="${cx}" y="${labelY}" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="${r.ring === selectedRing ? 'var(--text)' : 'var(--text-dim)'}">Ring ${r.ring}${i === 0 ? ' (user mode)' : i === 3 ? ' (kernel)' : ''}</text>`;
        })
        .join('')}
    </svg>
  `;
}

function renderRingsTab(): void {
  contentEl.innerHTML = `
    <div class="card">
      <h2>The privilege boundary is enforced by the CPU, not the OS</h2>
      <p class="desc">
        Real x86 defines four privilege rings (CPL 0&ndash;3); commodity OSes
        (Windows, Linux, macOS) only ever use Ring 0 (kernel) and Ring 3
        (user mode / a browser renderer process). Click a ring, then watch
        which of these four <strong>real, hand-assembled x86 instructions</strong>
        the CPU's own decode logic allows to run &mdash; from Module 2
        (<code>privilege_rings</code>)'s actual experiment.
      </p>
      <div class="ring-layout">
        <div class="ring-diagram" id="ring-diagram"></div>
        <div class="ring-info">
          <p class="desc">
            Selected: <strong style="color:var(--text)">Ring ${selectedRing}</strong>
            ${selectedRing === 0 ? ' &mdash; kernel mode. Full instruction set, unrestricted memory access.' : ''}
            ${selectedRing === 3 ? ' &mdash; user mode. Where every browser renderer process runs; no privileged instruction executes here.' : ''}
            ${selectedRing === 1 || selectedRing === 2 ? ' &mdash; architecturally real, but unused by every mainstream OS (no CPL check below treats these specially here).' : ''}
          </p>
          <div class="instr-list" id="instr-list"></div>
        </div>
      </div>
    </div>
  `;

  function drawDiagram() {
    document.getElementById('ring-diagram')!.innerHTML = ringSvg();
    document.querySelectorAll<SVGCircleElement>('.ring-svg circle').forEach((c) => {
      c.addEventListener('click', () => {
        selectedRing = Number(c.dataset.ring) as Ring;
        renderRingsTab();
      });
    });
  }

  function drawInstructions() {
    const cpl: Ring = selectedRing === 1 || selectedRing === 2 ? 3 : selectedRing;
    document.getElementById('instr-list')!.innerHTML = INSTRUCTIONS.map((instr) => {
      const result = execute(instr, cpl);
      return `
        <div class="instr-row">
          <div style="min-width:70px">
            <div class="name">${instr.name}</div>
            <div class="opcode">${instr.opcode}</div>
          </div>
          <div class="note">${instr.description}</div>
          <span class="badge ${result.status === 'OK' ? 'ok' : 'fault'}" title="${result.detail}">${result.status}</span>
        </div>`;
    }).join('');
  }

  drawDiagram();
  drawInstructions();
}
