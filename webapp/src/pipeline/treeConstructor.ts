/**
 * Ported from track2-applied-layer/phase6_parsing_dom/20_dom_tree_builder/tree_constructor.py
 * (Module 20: dom_tree_builder), turning a flat token stream into a tree.
 *
 * The core idea this module proves: the tree is built INCREMENTALLY, using
 * a "stack of open elements" that tracks exactly where in the tree new
 * nodes currently get inserted, and specific, real HTML5 rules about
 * which tags implicitly close other currently-open tags, entirely
 * independent of the tokenizer (Module 19), which has no concept of a
 * tree at all.
 *
 * SCOPE SIMPLIFICATION (see the course's own DECISIONS.md): the real
 * HTML5 tree construction algorithm decides implicit closes using "scope"
 * checks that walk the ENTIRE open-elements stack against boundary
 * elements. This module checks only the IMMEDIATE top of the stack,
 * enough to correctly demonstrate the real, well-known <p>/<p> and
 * <li>/<li> auto-close behavior, without reproducing the full scope
 * algorithm.
 */
import type { HtmlToken } from './htmlTokens';
import type { DomNode, DocumentNode, ElementNode } from './domNodes';

const VOID_ELEMENTS = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr']);

// Real HTML5 rule (simplified to immediate-parent checking, see module
// docstring): opening tag X, while tag Y is the currently open element,
// implicitly closes Y first.
const AUTO_CLOSE_ON_OPEN: Record<string, Set<string>> = {
  p: new Set(['p']),
  li: new Set(['li']),
};

export function buildTree(tokens: HtmlToken[]): DocumentNode {
  const document: DocumentNode = { kind: 'Document', children: [] };
  const stack: (DocumentNode | ElementNode)[] = [document];

  const current = () => stack[stack.length - 1];

  for (const token of tokens) {
    if (token.kind === 'StartTag') {
      const top = stack[stack.length - 1];
      if (top.kind === 'Element' && AUTO_CLOSE_ON_OPEN[token.name]?.has(top.tag)) {
        stack.pop(); // the real, observable "auto-close" behavior
      }

      const element: ElementNode = { kind: 'Element', tag: token.name, attributes: { ...token.attributes }, children: [] };
      current().children.push(element);
      if (!VOID_ELEMENTS.has(token.name) && !token.selfClosing) {
        stack.push(element);
      }
      // Void/self-closing elements are appended as children but never
      // pushed, by definition they cannot contain anything, so there is
      // no "inside" to insert into.
    } else if (token.kind === 'EndTag') {
      // Scan DOWN the stack for a matching open element. If found, close
      // it AND everything still open above it, real spec behavior: an
      // ancestor's end tag implicitly closes any of its still-open
      // descendants too.
      for (let i = stack.length - 1; i > 0; i--) {
        const node = stack[i];
        if (node.kind === 'Element' && node.tag === token.name) {
          stack.length = i;
          break;
        }
      }
      // If no match exists anywhere in the stack, the end tag is simply
      // ignored, also real, spec-accurate behavior, not an error.
    } else if (token.kind === 'Character') {
      current().children.push({ kind: 'Text', data: token.data });
    } else if (token.kind === 'Comment') {
      current().children.push({ kind: 'Comment', data: token.data });
    } else if (token.kind === 'EndOfFile') {
      break;
    }
  }

  return document;
}
