"""
Module 22: style_computation -- local copy of Module 20's DOM node
types, extended with a `parent` reference and a `computed_style` slot.

The parent reference is new here specifically because style
computation needs to walk UP the tree (to match ancestor-dependent
selectors like "div p") -- Module 20 never needed that, since tree
CONSTRUCTION only ever needs to know the current insertion point, not
full bidirectional navigation.
"""

from dataclasses import dataclass, field


@dataclass
class Text:
    data: str
    parent: object = None


@dataclass
class Comment:
    data: str
    parent: object = None


@dataclass
class Element:
    tag: str
    attributes: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    parent: object = None
    computed_style: dict = field(default_factory=dict)

    def class_list(self) -> list:
        return self.attributes.get("class", "").split()

    def element_id(self) -> str:
        return self.attributes.get("id", "")


@dataclass
class Document:
    children: list = field(default_factory=list)


def render_tree(node, indent: int = 0) -> str:
    pad = "  " * indent
    lines = []
    if isinstance(node, Document):
        lines.append(f"{pad}#document")
        for child in node.children:
            lines.append(render_tree(child, indent + 1))
    elif isinstance(node, Element):
        attrs = "".join(f' {k}="{v}"' for k, v in node.attributes.items())
        lines.append(f"{pad}<{node.tag}{attrs}>")
        for child in node.children:
            lines.append(render_tree(child, indent + 1))
    elif isinstance(node, Text):
        lines.append(f"{pad}#text {node.data!r}")
    elif isinstance(node, Comment):
        lines.append(f"{pad}#comment {node.data!r}")
    return "\n".join(lines)
