"""
Module 20: dom_tree_builder -- the tree's node types.

A DOM tree is built from exactly these shapes: one root Document,
Element nodes (which can have children and attributes), Text nodes,
and Comment nodes. Nothing here is tokenizer-shaped anymore -- this is
genuinely a TREE, with parent/child relationships, not a flat stream.
"""

from dataclasses import dataclass, field


@dataclass
class Text:
    data: str


@dataclass
class Comment:
    data: str


@dataclass
class Element:
    tag: str
    attributes: dict = field(default_factory=dict)
    children: list = field(default_factory=list)


@dataclass
class Document:
    children: list = field(default_factory=list)


def render_tree(node, indent: int = 0) -> str:
    """A small pretty-printer -- not part of a real DOM API, but useful
    for actually SEEING the tree shape this module builds."""
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
