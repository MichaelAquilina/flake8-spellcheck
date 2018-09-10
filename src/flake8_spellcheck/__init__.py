# -*- coding: utf-8 -*-
from __future__ import print_function

import ast
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

        # TODO: this can definitely be simplified
        with open(pkg_resources.resource_filename(__name__, "words.txt"), "r") as fp:
            data = fp.read()

        self.words = set(w.lower() for w in data.split("\n"))

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
