"""
Module 20: dom_tree_builder -- turning a flat token stream into a tree.

The core idea this module proves: the tree is built INCREMENTALLY,
using a "stack of open elements" that tracks exactly where in the tree
new nodes currently get inserted -- and specific, real HTML5 rules
about which tags implicitly close other currently-open tags, entirely
independent of the tokenizer (Module 19), which has no concept of a
tree at all.

SCOPE SIMPLIFICATION (see DECISIONS.md): the real HTML5 tree
construction algorithm decides implicit closes using "scope" checks
that walk the ENTIRE open-elements stack against boundary elements.
This module checks only the IMMEDIATE top of the stack -- enough to
correctly demonstrate the real, well-known <p>/<p> and <li>/<li> auto-
close behavior, without reproducing the full scope algorithm.
"""

from dom_nodes import Comment, Document, Element, Text
from tokens import Character
from tokens import Comment as CommentToken
from tokens import EndOfFile, EndTag, StartTag

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img",
    "input", "link", "meta", "param", "source", "track", "wbr",
}

# Real HTML5 rule (simplified to immediate-parent checking -- see
# module docstring): opening tag X, while tag Y is the currently open
# element, implicitly closes Y first.
AUTO_CLOSE_ON_OPEN = {
    "p": {"p"},
    "li": {"li"},
}


def build_tree(tokens) -> Document:
    document = Document()
    stack: list = [document]  # top of stack = current insertion point

    def current():
        return stack[-1]

    for token in tokens:
        if isinstance(token, StartTag):
            top = stack[-1]
            if isinstance(top, Element) and top.tag in AUTO_CLOSE_ON_OPEN.get(token.name, ()):
                stack.pop()  # the real, observable "auto-close" behavior

            element = Element(tag=token.name, attributes=dict(token.attributes))
            current().children.append(element)
            if token.name not in VOID_ELEMENTS and not token.self_closing:
                stack.append(element)
            # Void/self-closing elements are appended as children but
            # never pushed -- by definition they cannot contain
            # anything, so there is no "inside" to insert into.

        elif isinstance(token, EndTag):
            # Scan DOWN the stack for a matching open element. If
            # found, close it AND everything still open above it --
            # real spec behavior: an ancestor's end tag implicitly
            # closes any of its still-open descendants too.
            for i in range(len(stack) - 1, 0, -1):
                node = stack[i]
                if isinstance(node, Element) and node.tag == token.name:
                    del stack[i:]
                    break
            # If no match exists anywhere in the stack, the end tag is
            # simply ignored -- also real, spec-accurate behavior, not
            # an error.

        elif isinstance(token, Character):
            current().children.append(Text(token.data))

        elif isinstance(token, CommentToken):
            current().children.append(Comment(token.data))

        elif isinstance(token, EndOfFile):
            break

    return document
