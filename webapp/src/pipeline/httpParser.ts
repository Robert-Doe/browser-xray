/**
 * Ported from track2-applied-layer/phase5_networking/16_http_parsing/http_parser.py
 * (Module 16: http_parsing), a real, hand-rolled HTTP/1.1 response parser.
 * No fetch(), no framework: an HTTP response is just bytes with a
 * well-defined plain-text structure:
 *
 *   STATUS LINE \r\n
 *   Header-Name: value \r\n
 *   ...
 *   \r\n
 *   <body, framed EITHER by Content-Length OR by chunked encoding>
 *
 * A server MUST say which framing applies, because without one the client
 * has no way to know where the body ends short of the connection closing.
 */

export interface HttpResponse {
  version: string;
  statusCode: number;
  reason: string;
  headers: Record<string, string>;
  body: Uint8Array;
}

function indexOfBytes(hay: Uint8Array, needle: number[], from = 0): number {
  outer: for (let i = from; i <= hay.length - needle.length; i++) {
    for (let j = 0; j < needle.length; j++) if (hay[i + j] !== needle[j]) continue outer;
    return i;
  }
  return -1;
}

const CRLF = [0x0d, 0x0a];
const CRLFCRLF = [0x0d, 0x0a, 0x0d, 0x0a];

function splitOn(bytes: Uint8Array, sep: number[]): Uint8Array[] {
  const out: Uint8Array[] = [];
  let start = 0;
  while (true) {
    const idx = indexOfBytes(bytes, sep, start);
    if (idx === -1) {
      out.push(bytes.slice(start));
      break;
    }
    out.push(bytes.slice(start, idx));
    start = idx + sep.length;
  }
  return out;
}

const ascii = (b: Uint8Array) => new TextDecoder('ascii', { fatal: false }).decode(b);

function parseStatusLine(line: Uint8Array): [string, number, string] {
  const text = ascii(line);
  const parts = text.split(' ');
  const version = parts[0];
  const statusCode = parseInt(parts[1], 10);
  const reason = parts.slice(2).join(' ');
  return [version, statusCode, reason];
}

function parseHeaders(headerLines: Uint8Array[]): Record<string, string> {
  const headers: Record<string, string> = {};
  for (const line of headerLines) {
    if (line.length === 0) continue;
    const text = ascii(line);
    const colon = text.indexOf(':');
    if (colon === -1) continue;
    // HTTP header names are case-insensitive by spec -- normalizing to
    // lowercase here is what lets callers reliably look up
    // "content-length" regardless of how the server capitalized it.
    const name = text.slice(0, colon).trim().toLowerCase();
    const value = text.slice(colon + 1).trim();
    headers[name] = value;
  }
  return headers;
}

/** Reverse HTTP/1.1 chunked transfer encoding: each chunk is a hex length,
 * \r\n, that many bytes, \r\n, repeating until a zero-length chunk marks
 * the end. */
export function dechunk(chunkedBody: Uint8Array): Uint8Array {
  const result: number[] = [];
  let pos = 0;
  while (true) {
    const lineEnd = indexOfBytes(chunkedBody, CRLF, pos);
    const sizeField = ascii(chunkedBody.slice(pos, lineEnd)).split(';')[0]; // ignore chunk extensions
    const size = parseInt(sizeField.trim(), 16);
    pos = lineEnd + 2;
    if (size === 0) break;
    for (let i = 0; i < size; i++) result.push(chunkedBody[pos + i]);
    pos += size + 2; // skip the chunk's trailing \r\n
  }
  return new Uint8Array(result);
}

export function parseResponse(raw: Uint8Array): HttpResponse {
  const headerEnd = indexOfBytes(raw, CRLFCRLF);
  if (headerEnd === -1) throw new Error('no blank line found, response has no complete header block');
  const headerBlock = raw.slice(0, headerEnd);
  const remainder = raw.slice(headerEnd + 4);

  const lines = splitOn(headerBlock, CRLF);
  const [version, statusCode, reason] = parseStatusLine(lines[0]);
  const headers = parseHeaders(lines.slice(1));

  const transferEncoding = (headers['transfer-encoding'] ?? '').toLowerCase();
  let body: Uint8Array;
  if (transferEncoding === 'chunked') {
    body = dechunk(remainder);
  } else if ('content-length' in headers) {
    const contentLength = parseInt(headers['content-length'], 10);
    body = remainder.slice(0, contentLength);
  } else {
    // No framing header at all -- by spec, the body is "everything until
    // the connection closes." We've already read everything available, so
    // the remainder IS the whole body.
    body = remainder;
  }

  return { version, statusCode, reason, headers, body };
}
