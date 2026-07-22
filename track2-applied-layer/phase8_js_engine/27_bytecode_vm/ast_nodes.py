"""
Module 25: js_lexer_parser -- the AST node types.

An AST (Abstract Syntax Tree) is what the parser produces and nothing
more -- no execution happens anywhere in this module. Module 26 is the
first thing that ever looks at these nodes and DOES something with
them.
"""

from dataclasses import dataclass, field


@dataclass
class Program:
    body: list = field(default_factory=list)


@dataclass
class NumericLiteral:
    value: float


@dataclass
class StringLiteral:
    value: str


@dataclass
class BooleanLiteral:
    value: bool


@dataclass
class NullLiteral:
    pass


@dataclass
class Identifier:
    name: str


@dataclass
class BinaryExpr:
    operator: str
    left: object
    right: object


@dataclass
class UnaryExpr:
    operator: str
    operand: object


@dataclass
class AssignmentExpr:
    operator: str  # '=', '+=', etc.
    target: object  # Identifier or MemberExpr
    value: object


@dataclass
class CallExpr:
    callee: object
    arguments: list = field(default_factory=list)


@dataclass
class MemberExpr:
    obj: object
    property: str


@dataclass
class VarDecl:
    kind: str  # 'var' | 'let' | 'const'
    name: str
    init: object  # expression or None


@dataclass
class FunctionDecl:
    name: str
    params: list = field(default_factory=list)
    body: object = None  # BlockStatement


@dataclass
class BlockStatement:
    body: list = field(default_factory=list)


@dataclass
class IfStatement:
    test: object
    consequent: object
    alternate: object = None


@dataclass
class WhileStatement:
    test: object
    body: object = None


@dataclass
class ReturnStatement:
    argument: object = None


@dataclass
class ExpressionStatement:
    expression: object
