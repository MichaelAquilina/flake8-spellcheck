# -*- coding: utf-8 -*-
from __future__ import print_function

import ast
import os
import pkg_resources
from string import ascii_lowercase, ascii_uppercase


def split_class_def(name, col_offset):
    buffer = ""
    for c in name:
        if c in ascii_lowercase:
            buffer += c
        elif c in ascii_uppercase:
            if buffer:
                yield buffer, col_offset
            buffer = c


def split_name_def(name, col_offset):
    for token in name.split("_"):
        yield token, col_offset
        col_offset += len(token) + 1


class SpellCheckPlugin(object):
    name = "flake8-spellcheck"
    version = "0.1.0"

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

        data = pkg_resources.resource_string(__name__, "words.txt")
        data = data.decode("utf8")

        self.words = set(w.lower() for w in data.split("\n"))

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
                tokens = split_class_def(node.name, node.col_offset)
            elif isinstance(node, ast.Name):
                tokens = split_name_def(node.id, node.col_offset)
            else:
                continue

            for t, col_offset in tokens:
                if t.lower() not in self.words:
                    yield (
                        node.lineno,
                        col_offset,
                        "SP1 Unknown word: '{}'".format(t),
                        type(self),
                    )
