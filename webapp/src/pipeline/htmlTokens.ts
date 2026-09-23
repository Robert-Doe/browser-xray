/**
 * Ported from track2-applied-layer/phase6_parsing_dom/19_html_tokenizer/tokens.py
 *, the five kinds of token a tokenizer emits. It never builds a tree
 * (that's the tree constructor's job, Module 20); its entire output is a
 * flat stream of these.
 */
export interface StartTag {
  kind: 'StartTag';
  name: string;
  attributes: Record<string, string>;
  selfClosing: boolean;
}
export interface EndTag {
  kind: 'EndTag';
  name: string;
}
export interface CommentToken {
  kind: 'Comment';
  data: string;
}
export interface CharacterToken {
  kind: 'Character';
  data: string;
}
export interface EndOfFileToken {
  kind: 'EndOfFile';
}

export type HtmlToken = StartTag | EndTag | CommentToken | CharacterToken | EndOfFileToken;
