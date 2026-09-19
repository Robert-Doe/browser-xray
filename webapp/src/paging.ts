/**
 * paging.ts — a real x86-64 4-level page-table address translation, ported
 * from what track1-core-engine/phase1_bare_metal/01_mem_addressing proves:
 *
 *   "A virtual address is a per-process, per-run illusion — never a fixed
 *   physical location. Process A's page tables might map 0x1F6330144B0 to
 *   physical frame X; Process B's completely separate page tables might
 *   map that same virtual number to physical frame Y, or to nothing at
 *   all." (module tutorial.html)
 *
 * Real x86-64 splits a 48-bit canonical virtual address into five fields —
 * this is the actual hardware layout the MMU walks on every memory access:
 *
 *   bits 47-39  PML4 index   (9 bits, 512 entries)
 *   bits 38-30  PDPT index   (9 bits, 512 entries)   "page-directory pointer table"
 *   bits 29-21  PD index     (9 bits, 512 entries)   "page directory"
 *   bits 20-12  PT index     (9 bits, 512 entries)   "page table"
 *   bits 11-0   offset       (12 bits -> 4096-byte pages)
 *
 * Each process gets its OWN four-level hierarchy (its own CR3 root). We
 * simulate that by seeding a deterministic-but-distinct frame allocator per
 * process, exactly capturing the module's point: identical indices, walked
 * through separate tables, land on different physical frames.
 */

export const PAGE_SIZE = 4096; // 0x1000, 12-bit offset

export interface VaFields {
  pml4: number;
  pdpt: number;
  pd: number;
  pt: number;
  offset: number;
}

/** Mirrors how the MMU decodes a virtual address's bit fields — hardware-fixed, same for every process. */
export function splitVirtualAddress(vaddr: bigint): VaFields {
  const mask9 = 0x1ffn;
  const mask12 = 0xfffn;
  return {
    pml4: Number((vaddr >> 39n) & mask9),
    pdpt: Number((vaddr >> 30n) & mask9),
    pd: Number((vaddr >> 21n) & mask9),
    pt: Number((vaddr >> 12n) & mask9),
    offset: Number(vaddr & mask12),
  };
}

/** Simple deterministic 32-bit mix (mulberry32-style) so a given (seed, path) always resolves the same way within one process, but differs across processes/seeds — standing in for "whatever CR3 happens to point to." */
function mix(a: number, b: number, c: number, d: number, e: number): number {
  let h = (a * 2654435761) ^ (b * 2246822519) ^ (c * 3266489917) ^ (d * 668265263) ^ (e * 374761393);
  h = Math.imul(h ^ (h >>> 15), 2246822519);
  h = Math.imul(h ^ (h >>> 13), 3266489917);
  h ^= h >>> 16;
  return h >>> 0;
}

export interface PageTableEntry {
  present: boolean;
  frame: number; // physical frame number (frame * PAGE_SIZE = physical base)
}

/**
 * walk() — simulates one process's private 4-level page-table walk.
 * `seed` stands in for that process's CR3 (the physical root of ITS OWN
 * tables) — two processes with different seeds have entirely separate
 * tables, even when asked to translate the identical virtual address.
 */
export function walk(seed: number, fields: VaFields): PageTableEntry {
  const h = mix(seed, fields.pml4, fields.pdpt, fields.pd, fields.pt);
  // ~2% of paths are deliberately left unmapped, to keep "page fault" a
  // real possible outcome rather than something we've quietly ruled out.
  const present = h % 50 !== 0;
  // Physical frame numbers on a modest simulated machine (up to ~1M frames
  // = 4GB of physical RAM), matching a realistic frame-number magnitude.
  const frame = h % 0xfffff;
  return { present, frame };
}

export function physicalAddress(entry: PageTableEntry, offset: number): bigint {
  return BigInt(entry.frame) * BigInt(PAGE_SIZE) + BigInt(offset);
}

export function hex(n: bigint | number, width = 0): string {
  const s = n.toString(16).toUpperCase();
  return '0x' + s.padStart(width, '0');
}
