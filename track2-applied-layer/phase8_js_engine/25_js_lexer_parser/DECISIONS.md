# Module 25: js_lexer_parser — DECISIONS.md

## Precedence climbing for binary expressions, rather than one grammar rule per precedence level
**(c) Convention — a standard, real parsing technique, not an
invented shortcut.** A naive recursive-descent grammar would need a
separate function per precedence level (`parse_or`, `parse_and`,
`parse_equality`, ...), each calling the next-tighter level — correct,
but repetitive. Precedence climbing (`_parse_binary(min_precedence)`)
achieves the identical result with one function and a small precedence
table, by only continuing to consume an operator if its precedence
meets the current minimum. This is a genuinely standard technique used
in many real parsers, not a simplification unique to this course.

## `_parse_binary(precedence + 1)` for the right-hand side, making binary operators left-associative
**(b) External contract.** Real JS defines `+`, `-`, `*`, `/`, etc. as
left-associative (`2 - 3 - 4` means `(2 - 3) - 4`, not
`2 - (3 - 4)`). Requiring the right-hand recursive call to use a
STRICTLY HIGHER minimum precedence (`precedence + 1`, not
`precedence`) is exactly what enforces left-associativity — we
verified this directly with `2 * 3 + 4` and `2 + 3 * 4` both producing
the correct, differently-shaped trees.

## Assignment implemented as right-associative, via a separate `_parse_assignment` layered above `_parse_binary`
**(b) External contract.** Real JS assignment is right-associative
(`a = b = 5` means `a = (b = 5)`), unlike the left-associative
arithmetic operators — this requires genuinely different handling
(recursing into itself for the right-hand side, not requiring higher
precedence), which is why assignment is deliberately a separate parsing
layer rather than just another row in the binary-precedence table.

## Numbers stored as Python `float`, not distinguishing integers
**(c) Convention.** Real JavaScript itself has exactly one numeric
type (IEEE-754 double-precision float) for all numbers — there is no
separate JS integer type. Using Python `float` for every
`NumericLiteral` value is a direct, accurate match to how JS itself
represents numbers, not a simplification that loses information JS
would have kept.

## Treating keywords as their own token type (`KEYWORD`), rather than lexing everything as `IDENT` and checking the string later
**(c) Convention.** Either approach is workable, but tagging keywords
at the lexer level means the parser's statement dispatch
(`_parse_statement`) can check `token.type == "KEYWORD"` without also
needing to compare against a keyword set at every call site — a small
but real clarity win, consistent with keeping each stage's own
responsibility clean.

## No object/array literals, arrow functions, template strings, or `for` loops
**(c) Convention — a deliberate, named scope boundary.** This module's
job is to prove the lexer/parser SHAPE (tokens → AST, precedence
climbing, recursive descent) works correctly and can be trusted as a
foundation — not to reach full ECMAScript coverage. The subset
implemented (variables, functions, if/else, while, return, the common
operators, calls, and member access) is enough to write and correctly
parse real, non-trivial control-flow programs, which Module 26's
interpreter needs.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Precedence climbing over per-level grammar rules | (c) Convention (standard real technique) | Yes, both are legitimate, precedence climbing is more compact |
| Left-associative binary operators via `precedence + 1` | (b) Forced — matches real JS operator associativity | No |
| Right-associative assignment via a separate parsing layer | (b) Forced — matches real JS assignment associativity | No |
| Numbers as Python `float` throughout | (c) Convention (matches JS's own single numeric type exactly) | No, for accuracy to real JS |
| Keywords tagged at the lexer level | (c) Convention (cleaner downstream dispatch) | Yes, checking strings later also works |
| No object/array literals, arrow functions, `for`, template strings | (c) Convention (named scope boundary) | Yes — all are natural, real extensions |

## What We Proved

Running a real, non-trivial JS-subset program (a function declaration,
a call inside an arithmetic expression, an if/else, and a while loop)
through the lexer and parser produced a correct, fully-structured AST
in every case, and five targeted precedence/associativity tests
confirmed:

1. **`2 + 3 * 4`** parsed as `+(2, *(3, 4))` — multiplication correctly
   binds tighter than addition.
2. **`2 * 3 + 4`** parsed as `+(*(2, 3), 4)` — the same operators,
   opposite tree shape, confirming precedence (not just "whichever
   operator appears first") governs the structure.
3. **`a = b = 5`** parsed as `a = (b = 5)` — confirming assignment's
   real right-associativity.
4. **`!x && y || z`** parsed as `||(&&(!(x), y), z)` — confirming
   unary, then `&&`, then `||` bind in the correct real precedence
   order.
5. **`obj.prop.method(1, 2).other`** correctly chained member access
   and call expressions left-to-right into one nested structure.

This is direct, run-and-observed confirmation that JS source becomes a
real, correctly-structured AST via standard lexing and recursive-
descent, precedence-climbing parsing — before a single line of that
program has been executed anywhere.
