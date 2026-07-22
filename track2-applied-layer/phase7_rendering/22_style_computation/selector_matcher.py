"""
Module 22: style_computation -- giving selector TEXT (Module 21 kept
it as raw strings) actual meaning: does this selector match this DOM
element, and how SPECIFIC is it.

SCOPE (see DECISIONS.md): supports type/class/ID/universal selectors,
combined into one compound (e.g. "div.card#main"), plus the descendant
combinator (whitespace-separated compounds, e.g. "div p"). Child (>),
sibling (+ / ~), attribute, and pseudo-class/element selectors are all
out of scope.
"""

import re
from dataclasses import dataclass

from dom_nodes import Element

_COMPOUND_RE = re.compile(r"([.#]?[A-Za-z0-9_-]+|\*)")


@dataclass(frozen=True)
class Specificity:
    ids: int
    classes: int
    types: int

    def as_tuple(self) -> tuple:
        return (self.ids, self.classes, self.types)


def _parse_compound(compound: str) -> dict:
    """'div.card#main' -> {'type': 'div', 'classes': ['card'], 'id': 'main'}"""
    parsed = {"type": None, "classes": [], "id": None}
    for piece in _COMPOUND_RE.findall(compound):
        if piece == "*":
            continue
        elif piece.startswith("#"):
            parsed["id"] = piece[1:]
        elif piece.startswith("."):
            parsed["classes"].append(piece[1:])
        else:
            parsed["type"] = piece
    return parsed


def _compound_matches(element: Element, compound: str) -> bool:
    parsed = _parse_compound(compound)
    if parsed["type"] is not None and element.tag != parsed["type"]:
        return False
    if parsed["id"] is not None and element.element_id() != parsed["id"]:
        return False
    for cls in parsed["classes"]:
        if cls not in element.class_list():
            return False
    return True


def matches_selector(element: Element, selector: str) -> bool:
    """Descendant-combinator matching: the RIGHTMOST compound must
    match the element itself; each compound to its left must match
    SOME ancestor, in order, walking up the tree."""
    compounds = selector.strip().split()
    if not compounds:
        return False

    if not _compound_matches(element, compounds[-1]):
        return False

    ancestor = element.parent
    for compound in reversed(compounds[:-1]):
        found = False
        while ancestor is not None:
            if isinstance(ancestor, Element) and _compound_matches(ancestor, compound):
                found = True
                ancestor = ancestor.parent
                break
            ancestor = getattr(ancestor, "parent", None)
        if not found:
            return False
    return True


def specificity_of(selector: str) -> Specificity:
    """Real CSS specificity: count ID selectors, class selectors, and
    type selectors ACROSS THE WHOLE SELECTOR (all compounds), not just
    the last one -- "div.a .b" is more specific than ".b" alone even
    though both ultimately select the same rightmost element shape."""
    ids = classes = types = 0
    for compound in selector.strip().split():
        parsed = _parse_compound(compound)
        if parsed["id"]:
            ids += 1
        classes += len(parsed["classes"])
        if parsed["type"]:
            types += 1
    return Specificity(ids, classes, types)
