"""
Module 17: origin_model_sop -- minimal local copy of Module 16's
response parsing (Content-Length path only -- this module's own toy
servers always send Content-Length, so the fuller parser including
chunked-decoding isn't needed here). Kept self-contained in this
module's directory per this course's per-module convention; see
Module 16 for the complete parser and its chunked-encoding handling.
"""

from dataclasses import dataclass


@dataclass
class HttpResponse:
    status_code: int
    headers: dict
    body: bytes


def parse_response(raw: bytes) -> HttpResponse:
    header_end = raw.index(b"\r\n\r\n")
    header_block = raw[:header_end]
    remainder = raw[header_end + 4:]

    lines = header_block.split(b"\r\n")
    status_code = int(lines[0].split(b" ")[1])

    headers = {}
    for line in lines[1:]:
        if not line:
            continue
        name, _, value = line.partition(b":")
        headers[name.decode().strip().lower()] = value.decode().strip()

    content_length = int(headers.get("content-length", len(remainder)))
    body = remainder[:content_length]
    return HttpResponse(status_code, headers, body)
