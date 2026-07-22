"""
Module 25: js_lexer_parser -- a real recursive-descent parser with
precedence climbing for expressions.

This is the standard, real technique essentially every hand-written
parser (including real JS engines' parsers) uses for expressions:
binary operators are parsed via a loop that only continues consuming
an operator if its precedence is high enough, which is what makes
`2 + 3 * 4` naturally parse as `2 + (3 * 4)` without needing separate,
hardcoded grammar rules per precedence level written out by hand.
"""

from ast_nodes import (
    AssignmentExpr, BinaryExpr, BlockStatement, BooleanLiteral, CallExpr,
    ExpressionStatement, FunctionDecl, Identifier, IfStatement, MemberExpr,
    NullLiteral, NumericLiteral, Program, ReturnStatement, StringLiteral,
    UnaryExpr, VarDecl, WhileStatement,
)
from lexer import tokenize

BINARY_PRECEDENCE = {
    "||": 1,
    "&&": 2,
    "==": 3, "!=": 3, "===": 3, "!==": 3,
    "<": 4, ">": 4, "<=": 4, ">=": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6, "%": 6,
}
ASSIGNMENT_OPS = {"=", "+=", "-=", "*=", "/="}


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def _peek(self):
        return self.tokens[self.pos]

    def _advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _expect(self, type_: str, value=None):
        token = self._advance()
        if token.type != type_ or (value is not None and token.value != value):
            raise SyntaxError(f"Expected {type_} {value!r}, got {token.type} {token.value!r}")
        return token

    def _at(self, type_: str, value=None) -> bool:
        token = self._peek()
        return token.type == type_ and (value is None or token.value == value)

    # --- program / statements ---

    def parse_program(self) -> Program:
        body = []
        while not self._at("EOF"):
            body.append(self._parse_statement())
        return Program(body)

    def _parse_statement(self):
        if self._at("KEYWORD", "var") or self._at("KEYWORD", "let") or self._at("KEYWORD", "const"):
            return self._parse_var_decl()
        if self._at("KEYWORD", "function"):
            return self._parse_function_decl()
        if self._at("KEYWORD", "if"):
            return self._parse_if()
        if self._at("KEYWORD", "while"):
            return self._parse_while()
        if self._at("KEYWORD", "return"):
            return self._parse_return()
        if self._at("OP", "{"):
            return self._parse_block()
        return self._parse_expression_statement()

    def _parse_var_decl(self) -> VarDecl:
        kind = self._advance().value
        name = self._expect("IDENT").value
        init = None
        if self._at("OP", "="):
            self._advance()
            init = self._parse_expression()
        if self._at("OP", ";"):
            self._advance()
        return VarDecl(kind=kind, name=name, init=init)

    def _parse_function_decl(self) -> FunctionDecl:
        self._advance()  # 'function'
        name = self._expect("IDENT").value
        self._expect("OP", "(")
        params = []
        if not self._at("OP", ")"):
            params.append(self._expect("IDENT").value)
            while self._at("OP", ","):
                self._advance()
                params.append(self._expect("IDENT").value)
        self._expect("OP", ")")
        body = self._parse_block()
        return FunctionDecl(name=name, params=params, body=body)

    def _parse_block(self) -> BlockStatement:
        self._expect("OP", "{")
        body = []
        while not self._at("OP", "}"):
            body.append(self._parse_statement())
        self._expect("OP", "}")
        return BlockStatement(body)

    def _parse_if(self) -> IfStatement:
        self._advance()  # 'if'
        self._expect("OP", "(")
        test = self._parse_expression()
        self._expect("OP", ")")
        consequent = self._parse_statement()
        alternate = None
        if self._at("KEYWORD", "else"):
            self._advance()
            alternate = self._parse_statement()
        return IfStatement(test=test, consequent=consequent, alternate=alternate)

    def _parse_while(self) -> WhileStatement:
        self._advance()  # 'while'
        self._expect("OP", "(")
        test = self._parse_expression()
        self._expect("OP", ")")
        body = self._parse_statement()
        return WhileStatement(test=test, body=body)

    def _parse_return(self) -> ReturnStatement:
        self._advance()  # 'return'
        argument = None
        if not self._at("OP", ";"):
            argument = self._parse_expression()
        if self._at("OP", ";"):
            self._advance()
        return ReturnStatement(argument=argument)

    def _parse_expression_statement(self) -> ExpressionStatement:
        expr = self._parse_expression()
        if self._at("OP", ";"):
            self._advance()
        return ExpressionStatement(expr)

    # --- expressions (precedence climbing) ---

    def _parse_expression(self):
        return self._parse_assignment()

    def _parse_assignment(self):
        left = self._parse_binary(1)
        if self._peek().type == "OP" and self._peek().value in ASSIGNMENT_OPS:
            operator = self._advance().value
            value = self._parse_assignment()  # right-associative
            return AssignmentExpr(operator=operator, target=left, value=value)
        return left

    def _parse_binary(self, min_precedence: int):
        left = self._parse_unary()
        while True:
            token = self._peek()
            if token.type != "OP" or token.value not in BINARY_PRECEDENCE:
                break
            precedence = BINARY_PRECEDENCE[token.value]
            if precedence < min_precedence:
                break
            operator = self._advance().value
            right = self._parse_binary(precedence + 1)  # left-associative: next level requires HIGHER precedence
            left = BinaryExpr(operator=operator, left=left, right=right)
        return left

    def _parse_unary(self):
        if self._at("OP", "!") or self._at("OP", "-") or self._at("OP", "+"):
            operator = self._advance().value
            operand = self._parse_unary()
            return UnaryExpr(operator=operator, operand=operand)
        return self._parse_call_member()

    def _parse_call_member(self):
        expr = self._parse_primary()
        while True:
            if self._at("OP", "("):
                self._advance()
                arguments = []
                if not self._at("OP", ")"):
                    arguments.append(self._parse_assignment())
                    while self._at("OP", ","):
                        self._advance()
                        arguments.append(self._parse_assignment())
                self._expect("OP", ")")
                expr = CallExpr(callee=expr, arguments=arguments)
            elif self._at("OP", "."):
                self._advance()
                prop = self._expect("IDENT").value
                expr = MemberExpr(obj=expr, property=prop)
            else:
                break
        return expr

    def _parse_primary(self):
        token = self._peek()
        if token.type == "NUMBER":
            self._advance()
            return NumericLiteral(float(token.value))
        if token.type == "STRING":
            self._advance()
            return StringLiteral(token.value)
        if token.type == "KEYWORD" and token.value in ("true", "false"):
            self._advance()
            return BooleanLiteral(token.value == "true")
        if token.type == "KEYWORD" and token.value == "null":
            self._advance()
            return NullLiteral()
        if token.type == "IDENT":
            self._advance()
            return Identifier(token.value)
        if token.type == "OP" and token.value == "(":
            self._advance()
            expr = self._parse_expression()
            self._expect("OP", ")")
            return expr
        raise SyntaxError(f"Unexpected token {token.type} {token.value!r}")


def parse(source: str) -> Program:
    return Parser(tokenize(source)).parse_program()
