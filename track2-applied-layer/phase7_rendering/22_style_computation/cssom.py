"""
Module 21: css_parser_cssom -- the CSSOM's node types.

Deliberately NOT the same shapes as Module 20's DOM nodes -- CSS is
parsed into its OWN, independent object model. A CSSRule doesn't know
or care what element it might eventually apply to; that matching only
happens later (Module 22), once both trees already exist separately.
"""

from dataclasses import dataclass, field


@dataclass
class Declaration:
    property: str
    value: str
    important: bool = False


@dataclass
class CSSRule:
    selectors: list = field(default_factory=list)  # raw selector strings, comma-split
    declarations: list = field(default_factory=list)


def render_cssom(rules) -> str:
    lines = []
    for rule in rules:
        lines.append(", ".join(rule.selectors) + " {")
        for decl in rule.declarations:
            bang = " !important" if decl.important else ""
            lines.append(f"    {decl.property}: {decl.value}{bang};")
        lines.append("}")
    return "\n".join(lines)
