"""
Module 27: bytecode_vm -- executing compiled instructions.

The core loop below is the entire reason a bytecode VM is faster than
Module 26's tree-walker for the SAME program: instead of a chain of
`isinstance` checks re-run on every visit to every AST node, this is a
flat list index (`pc`), a dict/if-chain dispatch on a plain STRING
opcode, and a simple value stack. Every instruction here does the
minimum possible amount of work to advance the program by one step.

SCOPE SIMPLIFICATION (see DECISIONS.md): function calls recurse
through Python's own call stack (`run` calling itself), rather than
maintaining an explicit VM-level frame stack the way a production
bytecode VM would.
"""

from compiler import CodeObject


class Frame:
    def __init__(self, code: CodeObject, args: list):
        self.code = code
        self.locals = dict(zip(code.params, args))
        self.stack: list = []
        self.pc = 0


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


def apply_unary(operator: str, operand):
    if operator == "-":
        return -operand
    if operator == "+":
        return +operand
    if operator == "!":
        return not is_truthy(operand)
    raise TypeError(f"Unknown unary operator: {operator}")


def apply_binary(operator: str, left, right):
    if operator == "+":
        return left + right
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


def run(code: CodeObject, functions: dict, args: list = None):
    frame = Frame(code, args or [])
    return _execute_frame(frame, functions)


def run_program(code: CodeObject, functions: dict) -> dict:
    """Entry point for TOP-LEVEL script execution (not a function
    call) -- returns the frame's final locals so a caller can inspect
    top-level variables afterward, the VM equivalent of Module 26's
    `env.get(...)` after `execute_program`."""
    frame = Frame(code, [])
    _execute_frame(frame, functions)
    return frame.locals


def _execute_frame(frame: Frame, functions: dict):
    instructions = frame.code.instructions
    stack = frame.stack

    while frame.pc < len(instructions):
        instr = instructions[frame.pc]
        frame.pc += 1
        op = instr.op

        if op == "LOAD_CONST":
            stack.append(instr.arg)
        elif op == "LOAD_VAR":
            stack.append(frame.locals[instr.arg])
        elif op == "STORE_VAR":
            frame.locals[instr.arg] = stack.pop()
        elif op == "POP":
            stack.pop()
        elif op == "UNARY_OP":
            operand = stack.pop()
            stack.append(apply_unary(instr.arg, operand))
        elif op == "BINARY_OP":
            right = stack.pop()
            left = stack.pop()
            stack.append(apply_binary(instr.arg, left, right))
        elif op == "JUMP":
            frame.pc = instr.arg
        elif op == "JUMP_IF_FALSE":
            value = stack.pop()
            if not is_truthy(value):
                frame.pc = instr.arg
        elif op == "CALL":
            func_name, argc = instr.arg
            call_args = [stack.pop() for _ in range(argc)]
            call_args.reverse()
            func_code = functions[func_name]
            result = run(func_code, functions, call_args)
            stack.append(result)
        elif op == "RETURN":
            return stack.pop()
        else:
            raise TypeError(f"Unknown opcode: {op}")

    return None
