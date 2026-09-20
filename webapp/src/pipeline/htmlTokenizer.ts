/**
 * Ported from track2-applied-layer/phase6_parsing_dom/19_html_tokenizer/html_tokenizer.py
 * (Module 19: html_tokenizer) — a real state-machine HTML tokenizer.
 *
 * This is a genuine (if scoped-down) implementation of the shape of the
 * WHATWG HTML5 tokenization algorithm: an explicit state machine, one
 * character consumed at a time, with named states matching the real
 * spec's own state names. It is NOT a regex hack, and it is NOT "find
 * things between < and >" — both of those approaches fail on exactly the
 * malformed-input cases this module deliberately tests, which real
 * browsers are specified to recover from in precise, defined ways.
 *
 * Scope: covers start/end tags, attributes (quoted and unquoted),
 * comments, and the two "bogus comment" recovery paths real HTML5 parsing
 * defines for `<?...>` and invalid tag-open sequences. DOCTYPE is
 * recognized and skipped (not emitted as its own token type) — a scope
 * simplification noted in the course's own DECISIONS.md.
 */
import type { HtmlToken, StartTag, EndTag } from './htmlTokens';

const WHITESPACE = new Set([' ', '\t', '\n', '\r', '\f']);

type State =
  | 'DATA'
  | 'TAG_OPEN'
  | 'END_TAG_OPEN'
  | 'TAG_NAME'
  | 'BEFORE_ATTRIBUTE_NAME'
  | 'ATTRIBUTE_NAME'
  | 'AFTER_ATTRIBUTE_NAME'
  | 'BEFORE_ATTRIBUTE_VALUE'
  | 'ATTRIBUTE_VALUE_DOUBLE_QUOTED'
  | 'ATTRIBUTE_VALUE_SINGLE_QUOTED'
  | 'ATTRIBUTE_VALUE_UNQUOTED'
  | 'AFTER_ATTRIBUTE_VALUE_QUOTED'
  | 'SELF_CLOSING_START_TAG'
  | 'MARKUP_DECLARATION_OPEN'
  | 'DOCTYPE_SKIP'
  | 'COMMENT'
  | 'BOGUS_COMMENT'
  | 'EOF';

export class HtmlTokenizer {
  private html: string;
  private pos = 0;
  private state: State = 'DATA';
  tokens: HtmlToken[] = [];
  /** Not in the original Python — a side channel recording every state the
   * machine visited, purely so the webapp can show the trace. It changes
   * no tokenizer behavior. */
  stateTrace: State[] = [];
  private charBuffer = '';
  private tag: StartTag | EndTag | null = null;
  private attrName = '';
  private attrValue = '';
  private commentData = '';

  constructor(html: string) {
    this.html = html;
  }

  private current(): string | null {
    return this.pos < this.html.length ? this.html[this.pos] : null;
  }

  private advance(): void {
    this.pos += 1;
  }

  private flushCharBuffer(): void {
    if (this.charBuffer) {
      this.tokens.push({ kind: 'Character', data: this.charBuffer });
      this.charBuffer = '';
    }
  }

  /** The ONE place any non-Character token enters the stream. Flushing the
   * pending character buffer here — rather than at scattered call sites —
   * is what guarantees correct ordering regardless of which state path
   * produced the token: a Comment or tag is never allowed to appear
   * before text that preceded it in the source. */
  private emit(token: HtmlToken): void {
    this.flushCharBuffer();
    this.tokens.push(token);
  }

  private emitTag(): void {
    this.finalizeAttribute();
    this.emit(this.tag!);
    this.tag = null;
  }

  private finalizeAttribute(): void {
    if (this.attrName && this.tag?.kind === 'StartTag') {
      if (!(this.attrName in this.tag.attributes)) this.tag.attributes[this.attrName] = this.attrValue;
    }
    this.attrName = '';
    this.attrValue = '';
  }

  tokenize(): HtmlToken[] {
    while (this.state !== 'EOF') {
      this.stateTrace.push(this.state);
      this.step();
    }
    this.flushCharBuffer();
    this.tokens.push({ kind: 'EndOfFile' });
    return this.tokens;
  }

  private step(): void {
    switch (this.state) {
      case 'DATA':
        return this.stateData();
      case 'TAG_OPEN':
        return this.stateTagOpen();
      case 'END_TAG_OPEN':
        return this.stateEndTagOpen();
      case 'TAG_NAME':
        return this.stateTagName();
      case 'BEFORE_ATTRIBUTE_NAME':
        return this.stateBeforeAttributeName();
      case 'ATTRIBUTE_NAME':
        return this.stateAttributeName();
      case 'AFTER_ATTRIBUTE_NAME':
        return this.stateAfterAttributeName();
      case 'BEFORE_ATTRIBUTE_VALUE':
        return this.stateBeforeAttributeValue();
      case 'ATTRIBUTE_VALUE_DOUBLE_QUOTED':
        return this.stateAttributeValueDoubleQuoted();
      case 'ATTRIBUTE_VALUE_SINGLE_QUOTED':
        return this.stateAttributeValueSingleQuoted();
      case 'ATTRIBUTE_VALUE_UNQUOTED':
        return this.stateAttributeValueUnquoted();
      case 'AFTER_ATTRIBUTE_VALUE_QUOTED':
        return this.stateAfterAttributeValueQuoted();
      case 'SELF_CLOSING_START_TAG':
        return this.stateSelfClosingStartTag();
      case 'MARKUP_DECLARATION_OPEN':
        return this.stateMarkupDeclarationOpen();
      case 'DOCTYPE_SKIP':
        return this.stateDoctypeSkip();
      case 'COMMENT':
        return this.stateComment();
      case 'BOGUS_COMMENT':
        return this.stateBogusComment();
    }
  }

  private stateData(): void {
    const c = this.current();
    if (c === null) {
      this.state = 'EOF';
    } else if (c === '<') {
      this.advance();
      this.state = 'TAG_OPEN';
    } else {
      this.charBuffer += c;
      this.advance();
    }
  }

  private stateTagOpen(): void {
    const c = this.current();
    if (c !== null && /[a-zA-Z]/.test(c)) {
      this.tag = { kind: 'StartTag', name: '', attributes: {}, selfClosing: false };
      this.state = 'TAG_NAME';
    } else if (c === '/') {
      this.advance();
      this.state = 'END_TAG_OPEN';
    } else if (c === '!') {
      this.advance();
      this.state = 'MARKUP_DECLARATION_OPEN';
    } else if (c === '?') {
      // Real spec behavior: invalid first character after '<' that isn't a
      // letter, '/', or '!' — treated as a BOGUS COMMENT, not a syntax
      // error that aborts parsing.
      this.commentData = '';
      this.state = 'BOGUS_COMMENT';
    } else {
      // Real spec behavior: '<' not followed by anything tag-like is not
      // an error at all — it's just a literal '<' character in the data.
      // ("1 < 2" is valid HTML text.)
      this.charBuffer += '<';
      this.state = 'DATA'; // reconsume c in DATA
    }
  }

  private stateEndTagOpen(): void {
    const c = this.current();
    if (c !== null && /[a-zA-Z]/.test(c)) {
      this.tag = { kind: 'EndTag', name: '' };
      this.state = 'TAG_NAME';
    } else if (c === '>') {
      this.advance();
      this.state = 'DATA'; // malformed "</>" -- spec: parse error, emit nothing
    } else if (c === null) {
      this.charBuffer += '</';
      this.state = 'EOF';
    } else {
      this.commentData = '';
      this.state = 'BOGUS_COMMENT'; // reconsume c
    }
  }

  private stateTagName(): void {
    const c = this.current();
    if (c === null) {
      this.state = 'EOF'; // truncated tag at EOF -- dropped, like real browsers do for this case
    } else if (WHITESPACE.has(c)) {
      this.advance();
      this.state = 'BEFORE_ATTRIBUTE_NAME';
    } else if (c === '/') {
      this.advance();
      this.state = 'SELF_CLOSING_START_TAG';
    } else if (c === '>') {
      this.advance();
      this.emitTag();
      this.state = 'DATA';
    } else {
      // Tag names are ASCII case-INSENSITIVE -- <DIV> and <div> are the
      // same tag. Lowercasing here is that normalization.
      this.tag!.name += c.toLowerCase();
      this.advance();
    }
  }

  private stateBeforeAttributeName(): void {
    const c = this.current();
    if (c !== null && WHITESPACE.has(c)) {
      this.advance();
    } else if (c === '>' || c === '/' || c === null) {
      this.state = 'AFTER_ATTRIBUTE_NAME'; // reconsume
    } else {
      this.attrName = '';
      this.attrValue = '';
      this.state = 'ATTRIBUTE_NAME'; // reconsume
    }
  }

  private stateAttributeName(): void {
    const c = this.current();
    if (c === null || WHITESPACE.has(c) || c === '>' || c === '/') {
      this.state = 'AFTER_ATTRIBUTE_NAME'; // reconsume
    } else if (c === '=') {
      this.advance();
      this.state = 'BEFORE_ATTRIBUTE_VALUE';
    } else {
      this.attrName += c.toLowerCase();
      this.advance();
    }
  }

  private stateAfterAttributeName(): void {
    const c = this.current();
    if (c === null) {
      this.state = 'EOF';
    } else if (WHITESPACE.has(c)) {
      this.advance();
    } else if (c === '/') {
      this.advance();
      this.state = 'SELF_CLOSING_START_TAG';
    } else if (c === '=') {
      this.advance();
      this.state = 'BEFORE_ATTRIBUTE_VALUE';
    } else if (c === '>') {
      this.advance();
      this.emitTag();
      this.state = 'DATA';
    } else {
      this.finalizeAttribute();
      this.state = 'BEFORE_ATTRIBUTE_NAME'; // reconsume
    }
  }

  private stateBeforeAttributeValue(): void {
    const c = this.current();
    if (c !== null && WHITESPACE.has(c)) {
      this.advance();
    } else if (c === '"') {
      this.advance();
      this.state = 'ATTRIBUTE_VALUE_DOUBLE_QUOTED';
    } else if (c === "'") {
      this.advance();
      this.state = 'ATTRIBUTE_VALUE_SINGLE_QUOTED';
    } else {
      this.state = 'ATTRIBUTE_VALUE_UNQUOTED'; // reconsume, no quotes at all
    }
  }

  private stateAttributeValueDoubleQuoted(): void {
    const c = this.current();
    if (c === '"') {
      this.advance();
      this.finalizeAttribute();
      this.state = 'AFTER_ATTRIBUTE_VALUE_QUOTED';
    } else if (c === null) {
      this.state = 'EOF';
    } else {
      this.attrValue += c;
      this.advance();
    }
  }

  private stateAttributeValueSingleQuoted(): void {
    const c = this.current();
    if (c === "'") {
      this.advance();
      this.finalizeAttribute();
      this.state = 'AFTER_ATTRIBUTE_VALUE_QUOTED';
    } else if (c === null) {
      this.state = 'EOF';
    } else {
      this.attrValue += c;
      this.advance();
    }
  }

  private stateAttributeValueUnquoted(): void {
    const c = this.current();
    if (c === null) {
      this.state = 'EOF';
    } else if (WHITESPACE.has(c)) {
      this.advance();
      this.finalizeAttribute();
      this.state = 'BEFORE_ATTRIBUTE_NAME';
    } else if (c === '>') {
      this.advance();
      this.finalizeAttribute();
      this.emitTag();
      this.state = 'DATA';
    } else {
      this.attrValue += c;
      this.advance();
    }
  }

  private stateAfterAttributeValueQuoted(): void {
    const c = this.current();
    if (c !== null && WHITESPACE.has(c)) {
      this.advance();
      this.state = 'BEFORE_ATTRIBUTE_NAME';
    } else if (c === '/') {
      this.advance();
      this.state = 'SELF_CLOSING_START_TAG';
    } else if (c === '>') {
      this.advance();
      this.emitTag();
      this.state = 'DATA';
    } else if (c === null) {
      this.state = 'EOF';
    } else {
      this.state = 'BEFORE_ATTRIBUTE_NAME'; // reconsume; missing-whitespace recovery
    }
  }

  private stateSelfClosingStartTag(): void {
    const c = this.current();
    if (c === '>') {
      this.advance();
      if (this.tag?.kind === 'StartTag') this.tag.selfClosing = true;
      this.emitTag();
      this.state = 'DATA';
    } else if (c === null) {
      this.state = 'EOF';
    } else {
      this.state = 'BEFORE_ATTRIBUTE_NAME'; // reconsume; unexpected-solidus recovery
    }
  }

  private stateMarkupDeclarationOpen(): void {
    if (this.html.slice(this.pos, this.pos + 2) === '--') {
      this.pos += 2;
      this.commentData = '';
      this.state = 'COMMENT';
    } else if (this.html.slice(this.pos, this.pos + 7).toUpperCase() === 'DOCTYPE') {
      this.pos += 7;
      this.state = 'DOCTYPE_SKIP';
    } else {
      this.commentData = '';
      this.state = 'BOGUS_COMMENT';
    }
  }

  private stateDoctypeSkip(): void {
    // Scope simplification: we don't build a DOCTYPE token type, we just
    // consume up to '>' and discard it. Real browsers use a DOCTYPE token
    // to decide quirks-mode rendering — out of scope for this tokenizer.
    const c = this.current();
    if (c === null) {
      this.state = 'EOF';
    } else if (c === '>') {
      this.advance();
      this.state = 'DATA';
    } else {
      this.advance();
    }
  }

  private stateComment(): void {
    if (this.html.slice(this.pos, this.pos + 3) === '-->') {
      this.pos += 3;
      this.emit({ kind: 'Comment', data: this.commentData });
      this.state = 'DATA';
    } else if (this.current() === null) {
      this.emit({ kind: 'Comment', data: this.commentData }); // unterminated comment: emit what we have
      this.state = 'EOF';
    } else {
      this.commentData += this.current();
      this.advance();
    }
  }

  private stateBogusComment(): void {
    const c = this.current();
    if (c === '>') {
      this.advance();
      this.emit({ kind: 'Comment', data: this.commentData });
      this.state = 'DATA';
    } else if (c === null) {
      this.emit({ kind: 'Comment', data: this.commentData });
      this.state = 'EOF';
    } else {
      this.commentData += c;
      this.advance();
    }
  }
}

export function tokenize(html: string): HtmlToken[] {
  return new HtmlTokenizer(html).tokenize();
}
