"""
Module 22: style_computation -- the actual cascade.

For every DOM element, find every CSS rule whose selector matches it,
then resolve, PER PROPERTY, which single declaration wins using CSS's
real, exact priority order:

    1. !important declarations beat non-!important ones, always,
       regardless of specificity.
    2. Among declarations of the same !important-ness, higher
       SPECIFICITY wins (more IDs beats more classes beats more types).
    3. Among declarations tied on both of the above, the one that
       appears LATER in source order wins.

This is real cascade resolution -- not "last rule wins" (wrong: an ID
selector defined first still beats a class selector defined after it,
unless !important is involved), and not "most specific always wins"
either (wrong: !important overrides specificity entirely).
"""

from dom_nodes import Document, Element
from selector_matcher import matches_selector, specificity_of


def _matching_declarations(element: Element, rules: list):
    """Yields (important, specificity_tuple, source_order, declaration)
    for every declaration of every rule that matches this element."""
    for order, rule in enumerate(rules):
        matched_selector = None
        for selector in rule.selectors:
            if matches_selector(element, selector):
                matched_selector = selector
                break
        if matched_selector is None:
            continue
        spec = specificity_of(matched_selector).as_tuple()
        for decl in rule.declarations:
            yield (decl.important, spec, order, decl)


def compute_element_style(element: Element, rules: list) -> dict:
    candidates = list(_matching_declarations(element, rules))
    # Ascending sort by (important, specificity, source_order): the
    # LAST-sorted entry for any given property is the real cascade
    # winner, so writing them in this order and letting later writes
    # overwrite earlier ones for the same property is exactly correct.
    candidates.sort(key=lambda c: (c[0], c[1], c[2]))

    style: dict = {}
    winning_reason: dict = {}
    for important, spec, order, decl in candidates:
        style[decl.property] = decl.value
        winning_reason[decl.property] = {
            "important": important,
            "specificity": spec,
            "source_order": order,
        }
    return style, winning_reason


def compute_styles(node, rules: list) -> None:
    """Walks the whole tree, setting `computed_style` on every Element."""
    if isinstance(node, Document):
        for child in node.children:
            compute_styles(child, rules)
    elif isinstance(node, Element):
        style, _reason = compute_element_style(node, rules)
        node.computed_style = style
        for child in node.children:
            compute_styles(child, rules)
