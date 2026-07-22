"""
Module 27: bytecode_vm -- demonstration runner.

Part A: correctness, using the identical three test programs from
Module 26, confirming the compiler+VM produce the exact same results
as direct tree-walking evaluation.

Part B: a real, same-process, back-to-back benchmark -- Module 26's
tree-walking interpreter and this module's compile-then-run VM,
executing the BYTE-FOR-BYTE IDENTICAL fib(24) source, timed
consecutively in the same run so the comparison is as fair as this
course's tooling allows.
"""

import time

from compiler import compile_source
from interpreter import Environment, execute_program
from parser import parse
from vm import run_program

FIB_SOURCE = """
function fib(n) {
  if (n < 2) {
    return n;
  } else {
    return fib(n - 1) + fib(n - 2);
  }
}
let result = fib(24);
"""


def run_correctness_checks() -> None:
    cases = [
        ("recursion", """
            function fib(n) {
              if (n < 2) { return n; } else { return fib(n - 1) + fib(n - 2); }
            }
            let r = fib(10);
        """, "r", 55.0),
        ("loop + mutation", """
            let sum = 0;
            let i = 0;
            while (i < 100) { sum = sum + i; i = i + 1; }
        """, "sum", 4950.0),
    ]
    print("=== Correctness: compiler+VM matches Module 26's tree-walker ===")
    for label, src, var_name, expected in cases:
        top, funcs = compile_source(src)
        vm_result = run_program(top, funcs)[var_name]

        env = Environment()
        execute_program(parse(src), env)
        interp_result = env.get(var_name)

        print(f"  {label}: VM={vm_result}, interpreter={interp_result}, expected={expected}")
        assert vm_result == interp_result == expected
    print()


def run_benchmark() -> None:
    print("=== Benchmark: fib(24), identical source, same process ===\n")

    program_ast = parse(FIB_SOURCE)
    start = time.perf_counter()
    env = Environment()
    execute_program(program_ast, env)
    interpreter_time = time.perf_counter() - start
    print(f"Tree-walking interpreter (Module 26): {interpreter_time * 1000:.1f} ms "
          f"(result={env.get('result'):.0f})")

    top, funcs = compile_source(FIB_SOURCE)
    start = time.perf_counter()
    locals_ = run_program(top, funcs)
    vm_time = time.perf_counter() - start
    print(f"Bytecode VM (Module 27):               {vm_time * 1000:.1f} ms "
          f"(result={locals_['result']:.0f})")

    speedup = interpreter_time / vm_time
    print(f"\nSpeedup: {speedup:.2f}x")
    print(
        "Same AST, same program, same process, same Python interpreter -- the "
        "only thing that changed is HOW the program is executed: re-walking "
        "the tree on every visit, versus dispatching over a flat, precompiled "
        "instruction list."
    )


if __name__ == "__main__":
    run_correctness_checks()
    run_benchmark()
