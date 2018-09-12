# -*- coding: utf-8 -*-
from __future__ import print_function

import ast
import os
from string import ascii_lowercase, ascii_uppercase

import pkg_resources


def parse_camel_case(name, col_offset):
    index = col_offset
    buffer = ""
    for c in name:
        if c in ascii_lowercase:
            buffer += c
        elif c in ascii_uppercase:
            if buffer:
                yield index - len(buffer), buffer
            buffer = c
        index += 1

    if buffer:
        yield index - len(buffer), buffer


def parse_snake_case(name, col_offset):
    index = col_offset
    for token in name.split("_"):
        if token:
            yield index, token
        index += len(token) + 1


class SpellCheckPlugin(object):
    name = "flake8-spellcheck"
    version = "0.3.0"

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

        self.words = set()
        for dictionary in ("words.txt", "python.txt"):
            data = pkg_resources.resource_string(__name__, dictionary)
            data = data.decode("utf8")
            self.words |= set(w.lower() for w in data.split("\n"))

        if os.path.exists(self.whitelist_path):
            with open(self.whitelist_path, "r") as fp:
                whitelist = fp.read()

            whitelist = set(w.lower() for w in whitelist.split("\n"))
            self.words |= whitelist

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--whitelist",
            help="Path to text file containing whitelisted words",
            default="whitelist.txt",
        )

    @classmethod
    def parse_options(cls, options):
        cls.whitelist_path = options.whitelist

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                tokens = parse_camel_case(node.name, node.col_offset + len("class "))
            elif isinstance(node, ast.FunctionDef):
                tokens = parse_snake_case(node.name, node.col_offset + len("def "))
            elif isinstance(node, ast.AsyncFunctionDef):
                tokens = parse_snake_case(
                    node.name, node.col_offset + len("async def ")
                )
            elif isinstance(node, ast.Name):
                tokens = parse_snake_case(node.id, node.col_offset)
            else:
                continue

            for index, token in tokens:
                if token.lower() not in self.words:
                    yield (
                        node.lineno,
                        index,
                        "SC100 Possibly misspelt word: '{}'".format(token),
                        type(self),
                    )
