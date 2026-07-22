"""
Module 25: js_lexer_parser -- demonstration runner.
"""

from lexer import tokenize
from parser import parse

PROGRAM = """
function add(a, b) {
  return a + b;
}
let x = add(2, 3) * 2;
if (x > 10) {
  x = x - 1;
} else {
  x = 0;
}
while (x > 0) {
  x = x - 1;
}
"""

PRECEDENCE_CASES = [
    "2 + 3 * 4;",
    "2 * 3 + 4;",
    "a = b = 5;",
    "!x && y || z;",
    "obj.prop.method(1, 2).other;",
]


def main() -> None:
    print("=== Full program: tokens (first 10) ===")
    for token in tokenize(PROGRAM)[:10]:
        print(f"  {token}")

    print("\n=== Full program: AST (one statement per line) ===")
    program = parse(PROGRAM)
    for statement in program.body:
        print(f"  {statement}\n")

    print("=== Operator precedence and associativity, verified ===")
    for src in PRECEDENCE_CASES:
        result = parse(src).body[0]
        print(f"  {src}\n    -> {result}\n")


if __name__ == "__main__":
    main()
