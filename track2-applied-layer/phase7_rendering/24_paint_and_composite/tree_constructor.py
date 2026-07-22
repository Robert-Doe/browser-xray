"""
Module 22: style_computation -- local copy of Module 20's tree
constructor, extended to set each node's `parent` reference as it's
inserted (needed for ancestor-matching selectors -- see dom_nodes.py).
See Module 20 for the full explanation of the auto-close mechanism.
"""

from dom_nodes import Comment, Document, Element, Text
from tokens import Character
from tokens import Comment as CommentToken
from tokens import EndOfFile, EndTag, StartTag

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img",
    "input", "link", "meta", "param", "source", "track", "wbr",
}

AUTO_CLOSE_ON_OPEN = {
    "p": {"p"},
    "li": {"li"},
}


def build_tree(tokens) -> Document:
    document = Document()
    stack: list = [document]

    def current():
        return stack[-1]

    for token in tokens:
        if isinstance(token, StartTag):
            top = stack[-1]
            if isinstance(top, Element) and top.tag in AUTO_CLOSE_ON_OPEN.get(token.name, ()):
                stack.pop()

            element = Element(tag=token.name, attributes=dict(token.attributes), parent=current())
            current().children.append(element)
            if token.name not in VOID_ELEMENTS and not token.self_closing:
                stack.append(element)

        elif isinstance(token, EndTag):
            for i in range(len(stack) - 1, 0, -1):
                node = stack[i]
                if isinstance(node, Element) and node.tag == token.name:
                    del stack[i:]
                    break

        elif isinstance(token, Character):
            current().children.append(Text(token.data, parent=current()))

        elif isinstance(token, CommentToken):
            current().children.append(Comment(token.data, parent=current()))

        elif isinstance(token, EndOfFile):
            break

    return document
