"""
Module 26: tree_walking_interpreter -- the naive way to "run" an AST:
walk it, directly, recursively, evaluating each node as you visit it.

No compilation step, no intermediate representation -- every single
time a loop body runs, this interpreter re-walks the SAME AST nodes
from scratch, re-dispatching on their type every time. That repeated
dispatch overhead is exactly what Module 27's bytecode VM exists to
eliminate, and this module's benchmark measures it directly.
"""

from ast_nodes import (
    AssignmentExpr, BinaryExpr, BlockStatement, BooleanLiteral, CallExpr,
    ExpressionStatement, FunctionDecl, Identifier, IfStatement, MemberExpr,
    NullLiteral, NumericLiteral, Program, ReturnStatement, StringLiteral,
    UnaryExpr, VarDecl, WhileStatement,
)


class Environment:
    """A real, nested lexical scope chain -- variable lookup walks
    outward through parent environments, exactly like real JS scoping."""

    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def define(self, name: str, value) -> None:
        self.vars[name] = value

    def get(self, name: str):
        env = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise NameError(f"{name} is not defined")

    def set(self, name: str, value) -> None:
        env = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return
            env = env.parent
        raise NameError(f"{name} is not defined (assignment target)")


class JSFunction:
    """A function value: the AST of its body, plus the environment it
    closed over at DEFINITION time -- real closure semantics."""

    def __init__(self, declaration: FunctionDecl, closure: Environment):
        self.declaration = declaration
        self.closure = closure


class ReturnSignal(Exception):
    """Used to unwind the Python call stack back out of a JS function
    call the instant a `return` statement executes -- the standard
    tree-walking-interpreter technique for non-local control flow."""

    def __init__(self, value):
        self.value = value


def execute_program(program: Program, env: Environment) -> None:
    for statement in program.body:
        execute_statement(statement, env)


def execute_statement(node, env: Environment):
    if isinstance(node, VarDecl):
        value = evaluate(node.init, env) if node.init is not None else None
        env.define(node.name, value)

    elif isinstance(node, FunctionDecl):
        env.define(node.name, JSFunction(node, env))

    elif isinstance(node, BlockStatement):
        # A real, deliberate simplification: this module does not give
        # blocks their own child scope (that's how JS `var` behaves,
        # not `let`/`const` -- noted explicitly in DECISIONS.md).
        for stmt in node.body:
            execute_statement(stmt, env)

    elif isinstance(node, IfStatement):
        if is_truthy(evaluate(node.test, env)):
            execute_statement(node.consequent, env)
        elif node.alternate is not None:
            execute_statement(node.alternate, env)

    elif isinstance(node, WhileStatement):
        while is_truthy(evaluate(node.test, env)):
            execute_statement(node.body, env)

    elif isinstance(node, ReturnStatement):
        value = evaluate(node.argument, env) if node.argument is not None else None
        raise ReturnSignal(value)

    elif isinstance(node, ExpressionStatement):
        evaluate(node.expression, env)

    else:
        raise TypeError(f"Unknown statement node: {node!r}")


def evaluate(node, env: Environment):
    if isinstance(node, NumericLiteral):
        return node.value
    if isinstance(node, StringLiteral):
        return node.value
    if isinstance(node, BooleanLiteral):
        return node.value
    if isinstance(node, NullLiteral):
        return None
    if isinstance(node, Identifier):
        return env.get(node.name)

    if isinstance(node, UnaryExpr):
        operand = evaluate(node.operand, env)
        if node.operator == "-":
            return -operand
        if node.operator == "+":
            return +operand
        if node.operator == "!":
            return not is_truthy(operand)
        raise TypeError(f"Unknown unary operator: {node.operator}")

    if isinstance(node, BinaryExpr):
        return evaluate_binary(node, env)

    if isinstance(node, AssignmentExpr):
        if node.operator == "=":
            value = evaluate(node.value, env)
        else:
            current = evaluate(node.target, env)
            rhs = evaluate(node.value, env)
            op = node.operator[0]  # '+=' -> '+', etc.
            value = apply_operator(op, current, rhs)
        if isinstance(node.target, Identifier):
            env.set(node.target.name, value)
        else:
            raise TypeError("Only identifier assignment targets are supported")
        return value

    if isinstance(node, CallExpr):
        callee = evaluate(node.callee, env)
        arguments = [evaluate(arg, env) for arg in node.arguments]
        return call_function(callee, arguments)

    if isinstance(node, MemberExpr):
        raise TypeError("Member access has no object model in this module's scope")

    raise TypeError(f"Unknown expression node: {node!r}")


def call_function(func, arguments: list):
    if not isinstance(func, JSFunction):
        raise TypeError(f"{func!r} is not a function")

    call_env = Environment(parent=func.closure)
    for name, value in zip(func.declaration.params, arguments):
        call_env.define(name, value)

    try:
        execute_statement(func.declaration.body, call_env)
    except ReturnSignal as signal:
        return signal.value
    return None  # fell off the end with no explicit return


def evaluate_binary(node: BinaryExpr, env: Environment):
    left = evaluate(node.left, env)
    right = evaluate(node.right, env)
    return apply_operator(node.operator, left, right)


def apply_operator(operator: str, left, right):
    if operator == "+":
        return left + right  # real JS behavior: string concatenation OR numeric addition
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        return left / right
    if operator == "%":
        return left % right
    if operator in ("==", "==="):
        return left == right
    if operator in ("!=", "!=="):
        return left != right
    if operator == "<":
        return left < right
    if operator == ">":
        return left > right
    if operator == "<=":
        return left <= right
    if operator == ">=":
        return left >= right
    if operator == "&&":
        return right if is_truthy(left) else left
    if operator == "||":
        return left if is_truthy(left) else right
    raise TypeError(f"Unknown binary operator: {operator}")


def is_truthy(value) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    return True
