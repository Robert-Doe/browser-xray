"""
Module 19: html_tokenizer -- the token types the tokenizer produces.

These five kinds are all a tokenizer emits -- it never builds a tree
(that's the tree constructor's job, Module 20). A tokenizer's entire
output is a flat STREAM of these.
"""

from dataclasses import dataclass, field


@dataclass
class StartTag:
    name: str
    attributes: dict = field(default_factory=dict)
    self_closing: bool = False


@dataclass
class EndTag:
    name: str


@dataclass
class Comment:
    data: str


@dataclass
class Character:
    data: str


@dataclass
class EndOfFile:
    pass
