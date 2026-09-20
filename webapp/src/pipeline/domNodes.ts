/**
 * Ported from track2-applied-layer/phase6_parsing_dom/20_dom_tree_builder/dom_nodes.py
 * — a DOM tree is built from exactly these shapes: one root Document,
 * Element nodes (children + attributes), Text nodes, and Comment nodes.
 * Nothing here is tokenizer-shaped anymore — this is genuinely a tree,
 * with parent/child relationships, not a flat stream.
 */
export interface TextNode {
  kind: 'Text';
  data: string;
}
export interface CommentNode {
  kind: 'Comment';
  data: string;
}
export interface ElementNode {
  kind: 'Element';
  tag: string;
  attributes: Record<string, string>;
  children: DomNode[];
}
export interface DocumentNode {
  kind: 'Document';
  children: DomNode[];
}

export type DomNode = TextNode | CommentNode | ElementNode | DocumentNode;

/** A small pretty-printer — not part of a real DOM API, but useful for
 * actually seeing the tree shape this module builds. */
export function renderTreeText(node: DomNode, indent = 0): string {
  const pad = '  '.repeat(indent);
  const lines: string[] = [];
  if (node.kind === 'Document') {
    lines.push(`${pad}#document`);
    for (const child of node.children) lines.push(renderTreeText(child, indent + 1));
  } else if (node.kind === 'Element') {
    const attrs = Object.entries(node.attributes)
      .map(([k, v]) => ` ${k}="${v}"`)
      .join('');
    lines.push(`${pad}<${node.tag}${attrs}>`);
    for (const child of node.children) lines.push(renderTreeText(child, indent + 1));
  } else if (node.kind === 'Text') {
    lines.push(`${pad}#text ${JSON.stringify(node.data)}`);
  } else if (node.kind === 'Comment') {
    lines.push(`${pad}#comment ${JSON.stringify(node.data)}`);
  }
  return lines.join('\n');
}
