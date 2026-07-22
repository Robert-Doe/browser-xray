"""
Module 26: tree_walking_interpreter -- demonstration runner.

Part A: correctness -- recursion, closures/scoping, string
concatenation, and logical operators, all evaluated directly.

Part B: a real benchmark. Computing fib(24) requires walking the SAME
small set of AST nodes (the if/else, the two recursive calls, the
subtraction, the addition) roughly 150,000 times. Every single one of
those visits re-dispatches on node TYPE from scratch via isinstance
checks -- there is no cached, precompiled representation of "what this
node does." That real, measured cost is exactly what Module 27's
bytecode VM is built to eliminate, and this module's number is the
baseline that comparison needs.
"""

import time

from interpreter import Environment, execute_program
from parser import parse

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
    print("=== Correctness: recursion ===")
    env = Environment()
    execute_program(parse("""
        function fib(n) {
          if (n < 2) { return n; } else { return fib(n - 1) + fib(n - 2); }
        }
        let r = fib(10);
    """), env)
    print(f"  fib(10) = {env.get('r')} (expected 55)\n")

    print("=== Correctness: loops and mutation ===")
    env = Environment()
    execute_program(parse("""
        let sum = 0;
        let i = 0;
        while (i < 100) {
          sum = sum + i;
          i = i + 1;
        }
    """), env)
    print(f"  sum of 0..99 = {env.get('sum')} (expected 4950)\n")

    print("=== Correctness: string concatenation and logical operators ===")
    env = Environment()
    execute_program(parse("""
        let greeting = "hello " + "world";
        let flag = !false && (1 < 2);
    """), env)
    print(f"  greeting = {env.get('greeting')!r} (expected 'hello world')")
    print(f"  flag = {env.get('flag')} (expected True)\n")


def run_benchmark() -> None:
    print("=== Benchmark: fib(24), direct tree-walking evaluation ===")
    program = parse(FIB_SOURCE)
    start = time.perf_counter()
    env = Environment()
    execute_program(program, env)
    elapsed = time.perf_counter() - start
    print(f"  fib(24) = {env.get('result'):.0f}")
    print(f"  wall-clock time: {elapsed * 1000:.1f} ms")
    print(
        "  (this is the real baseline Module 27's bytecode VM benchmark "
        "will be measured against, running the IDENTICAL program)"
    )


if __name__ == "__main__":
    run_correctness_checks()
    run_benchmark()
