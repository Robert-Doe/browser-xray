/**
 * Draws the real DOM tree (produced by treeConstructor.ts, itself a port
 * of Module 20's tree_constructor.py) as an actual node-and-edge diagram,
 * using d3-hierarchy for layout. Plain SVG string output, no DOM binding.
 */
import { hierarchy, tree as d3tree, type HierarchyPointNode } from 'd3-hierarchy';
import type { DomNode } from './domNodes';

interface TreeDatum {
  label: string;
  detail: string;
  isText: boolean;
  children: TreeDatum[];
}

function toTreeDatum(node: DomNode): TreeDatum {
  switch (node.kind) {
    case 'Document':
      return { label: '#document', detail: '', isText: false, children: node.children.map(toTreeDatum) };
    case 'Element': {
      const attrs = Object.entries(node.attributes)
        .map(([k, v]) => `${k}="${v}"`)
        .join(' ');
      return { label: `<${node.tag}>`, detail: attrs, isText: false, children: node.children.map(toTreeDatum) };
    }
    case 'Text':
      return { label: '#text', detail: JSON.stringify(node.data), isText: true, children: [] };
    case 'Comment':
      return { label: '#comment', detail: JSON.stringify(node.data), isText: true, children: [] };
  }
}

const NODE_W = 120;
const NODE_H = 46;

export function renderDomTreeSvg(doc: DomNode): string {
  const root = hierarchy(toTreeDatum(doc), (d) => d.children);
  const layout = d3tree<TreeDatum>().nodeSize([NODE_W, NODE_H * 1.8]);
  const laidOut = layout(root);

  let minX = Infinity,
    maxX = -Infinity,
    maxY = -Infinity;
  laidOut.each((n) => {
    minX = Math.min(minX, n.x);
    maxX = Math.max(maxX, n.x);
    maxY = Math.max(maxY, n.y);
  });
  if (!isFinite(minX)) {
    minX = 0;
    maxX = 0;
    maxY = 0;
  }

  const pad = 60;
  const width = maxX - minX + pad * 2;
  const height = maxY + pad * 2;
  const ox = pad - minX;
  const oy = pad;

  const links = laidOut
    .links()
    .map((l: { source: HierarchyPointNode<TreeDatum>; target: HierarchyPointNode<TreeDatum> }) => {
      const sx = l.source.x + ox,
        sy = l.source.y + oy + NODE_H / 2;
      const tx = l.target.x + ox,
        ty = l.target.y + oy - NODE_H / 2;
      const my = (sy + ty) / 2;
      return `<path class="tree-link" d="M${sx},${sy} C${sx},${my} ${tx},${my} ${tx},${ty}"/>`;
    })
    .join('');

  const nodes = laidOut
    .descendants()
    .map((n: HierarchyPointNode<TreeDatum>) => {
      const x = n.x + ox,
        y = n.y + oy;
      const cls = n.data.isText ? 'text-node' : 'elem-node';
      const label = esc(n.data.label);
      const detail = n.data.detail ? esc(truncate(n.data.detail, 20)) : '';
      return `<g class="tree-node ${cls}" transform="translate(${x - NODE_W / 2},${y - NODE_H / 2})">
        <rect width="${NODE_W}" height="${NODE_H}" rx="8"/>
        <text x="${NODE_W / 2}" y="${detail ? 18 : NODE_H / 2 + 4}" text-anchor="middle" class="tree-label">${label}</text>
        ${detail ? `<text x="${NODE_W / 2}" y="34" text-anchor="middle" class="tree-detail">${detail}</text>` : ''}
      </g>`;
    })
    .join('');

  return `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
    <g>${links}${nodes}</g>
  </svg>`;
}

function truncate(s: string, n: number): string {
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
