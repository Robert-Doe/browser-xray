/**
 * rings.ts, ported straight from
 * track1-core-engine/phase1_bare_metal/02_privilege_rings's real experiment
 * (ring_boundary_probe.py / privileged_instr_child.py): four real x86-64
 * instructions, hand-assembled to their actual opcode bytes, run from a
 * genuinely executable page. Two are unprivileged (legal at CPL 3). Two are
 * defined by the x86 architecture itself as privileged (legal only at
 * CPL 0), the CPU's own decode logic checks the Current Privilege Level
 * and raises #GP (General Protection fault) before the instruction takes
 * any effect, with no OS policy involved.
 */

export interface Instruction {
  name: string;
  opcode: string;
  bytes: number[];
  description: string;
  privileged: boolean;
}

export const INSTRUCTIONS: Instruction[] = [
  {
    name: 'NOP',
    opcode: '0x90',
    bytes: [0x90],
    description: 'No-op. Does nothing to CPU state. Legal at any ring.',
    privileged: false,
  },
  {
    name: 'RDTSC',
    opcode: '0x0F 0x31',
    bytes: [0x0f, 0x31],
    description: 'Read Time-Stamp Counter. Ring-3-legal by default (no CR4.TSD set).',
    privileged: false,
  },
  {
    name: 'CLI',
    opcode: '0xFA',
    bytes: [0xfa],
    description: 'Clear Interrupt Flag, disables maskable hardware interrupts machine-wide.',
    privileged: true,
  },
  {
    name: 'HLT',
    opcode: '0xF4',
    bytes: [0xf4],
    description: 'Halt the CPU until the next interrupt.',
    privileged: true,
  },
];

export type Ring = 0 | 1 | 2 | 3;

export interface ExecResult {
  status: 'OK' | 'FAULT';
  detail: string;
}

/**
 * Mirrors the real outcome table from ring_boundary_probe.py's actual run
 * (reproduced verbatim in the module's tutorial.html):
 *
 *   NOP    -> OK
 *   RDTSC  -> OK
 *   CLI    -> FAULT  <- exception: privileged instruction
 *   HLT    -> FAULT  <- exception: privileged instruction
 *
 * Ring 0 code is never actually exercised in the source module (it only
 * proves the Ring-3 side), but the CPU's CPL check is symmetric by
 * definition: a privileged instruction executed at CPL 0 is exactly what
 * it exists to allow.
 */
export function execute(instr: Instruction, ring: Ring): ExecResult {
  if (!instr.privileged) {
    return { status: 'OK', detail: 'runs normally, control falls through to RET' };
  }
  if (ring === 0) {
    return { status: 'OK', detail: 'CPL=0 permits this instruction; it executes as intended' };
  }
  return {
    status: 'FAULT',
    detail: `CPU decode checks CPL, sees ring ${ring} ≠ 0, raises #GP before the instruction has any effect (Windows reports STATUS_PRIVILEGED_INSTRUCTION)`,
  };
}
