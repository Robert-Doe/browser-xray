"""
Module 27: bytecode_vm -- compiling an AST into a flat instruction
list, ONCE, instead of re-interpreting the tree on every visit.

This is the real, deliberate engineering step real JS engines take
(V8's "Ignition" is exactly a bytecode interpreter of this shape):
walk the AST a single time, emitting a small, fixed vocabulary of
instructions, so that RUNNING the program afterward becomes a tight
loop over a flat array with integer/string opcode dispatch -- never
re-walking the tree or re-asking "what kind of node is this" again.
"""

from dataclasses import dataclass, field

from ast_nodes import (
    AssignmentExpr, BinaryExpr, BlockStatement, BooleanLiteral, CallExpr,
    ExpressionStatement, FunctionDecl, Identifier, IfStatement, NullLiteral,
    NumericLiteral, Program, ReturnStatement, StringLiteral, UnaryExpr,
    VarDecl, WhileStatement,
)


@dataclass
class Instr:
    op: str
    arg: object = None


@dataclass
class CodeObject:
    instructions: list
    params: list = field(default_factory=list)
    name: str = "<script>"


class Compiler:
    def __init__(self):
        self.functions: dict = {}

    def compile_program(self, program: Program) -> CodeObject:
        instructions = []
        for stmt in program.body:
            self._compile_statement(stmt, instructions)
        return CodeObject(instructions=instructions, params=[], name="<script>")

    def _compile_statement(self, node, out: list) -> None:
        if isinstance(node, VarDecl):
            if node.init is not None:
                self._compile_expr(node.init, out)
            else:
                out.append(Instr("LOAD_CONST", None))
            out.append(Instr("STORE_VAR", node.name))

        elif isinstance(node, FunctionDecl):
            body_instrs = []
            for stmt in node.body.body:
                self._compile_statement(stmt, body_instrs)
            body_instrs.append(Instr("LOAD_CONST", None))
            body_instrs.append(Instr("RETURN"))
            self.functions[node.name] = CodeObject(
                instructions=body_instrs, params=list(node.params), name=node.name
            )

        elif isinstance(node, BlockStatement):
            for stmt in node.body:
                self._compile_statement(stmt, out)

        elif isinstance(node, IfStatement):
            self._compile_expr(node.test, out)
            jump_to_else = Instr("JUMP_IF_FALSE", None)
            out.append(jump_to_else)
            self._compile_statement(node.consequent, out)
            if node.alternate is not None:
                jump_to_end = Instr("JUMP", None)
                out.append(jump_to_end)
                jump_to_else.arg = len(out)
                self._compile_statement(node.alternate, out)
                jump_to_end.arg = len(out)
            else:
                jump_to_else.arg = len(out)

        elif isinstance(node, WhileStatement):
            loop_start = len(out)
            self._compile_expr(node.test, out)
            jump_to_end = Instr("JUMP_IF_FALSE", None)
            out.append(jump_to_end)
            self._compile_statement(node.body, out)
            out.append(Instr("JUMP", loop_start))
            jump_to_end.arg = len(out)

        elif isinstance(node, ReturnStatement):
            if node.argument is not None:
                self._compile_expr(node.argument, out)
            else:
                out.append(Instr("LOAD_CONST", None))
            out.append(Instr("RETURN"))

        elif isinstance(node, ExpressionStatement):
            self._compile_expr(node.expression, out)
            out.append(Instr("POP"))

        else:
            raise TypeError(f"Cannot compile statement: {node!r}")

    def _compile_expr(self, node, out: list) -> None:
        if isinstance(node, NumericLiteral):
            out.append(Instr("LOAD_CONST", node.value))
        elif isinstance(node, StringLiteral):
            out.append(Instr("LOAD_CONST", node.value))
        elif isinstance(node, BooleanLiteral):
            out.append(Instr("LOAD_CONST", node.value))
        elif isinstance(node, NullLiteral):
            out.append(Instr("LOAD_CONST", None))
        elif isinstance(node, Identifier):
            out.append(Instr("LOAD_VAR", node.name))
        elif isinstance(node, UnaryExpr):
            self._compile_expr(node.operand, out)
            out.append(Instr("UNARY_OP", node.operator))
        elif isinstance(node, BinaryExpr):
            # SCOPE SIMPLIFICATION (see DECISIONS.md): && and || are
            # compiled as plain binary ops here, NOT short-circuited
            # via jumps the way a real bytecode compiler would.
            self._compile_expr(node.left, out)
            self._compile_expr(node.right, out)
            out.append(Instr("BINARY_OP", node.operator))
        elif isinstance(node, AssignmentExpr):
            if node.operator == "=":
                self._compile_expr(node.value, out)
            else:
                out.append(Instr("LOAD_VAR", node.target.name))
                self._compile_expr(node.value, out)
                out.append(Instr("BINARY_OP", node.operator[0]))
            out.append(Instr("STORE_VAR", node.target.name))
            out.append(Instr("LOAD_VAR", node.target.name))  # assignment is itself an expression
        elif isinstance(node, CallExpr):
            for arg in node.arguments:
                self._compile_expr(arg, out)
            out.append(Instr("CALL", (node.callee.name, len(node.arguments))))
        else:
            raise TypeError(f"Cannot compile expression: {node!r}")


def compile_source(source: str):
    from parser import parse

    compiler = Compiler()
    top_level = compiler.compile_program(parse(source))
    return top_level, compiler.functions
