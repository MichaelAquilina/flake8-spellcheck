# -*- coding: utf-8 -*-
from __future__ import print_function

import ast
import pkg_resources
from string import ascii_lowercase, ascii_uppercase


def split_class_def(name):
    buffer = ""
    for c in name:
        if not buffer or c in ascii_lowercase:
            buffer += c
        elif c in ascii_uppercase:
            if buffer:
                yield buffer
            buffer = ""


def split_name_def(name):
    yield from name.split("_")


class SpellCheckPlugin(object):
    name = "flake8-spellcheck"
    version = "0.1.0"
    wadddd = "d"

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

        # TODO: this can definitely be simplified
        with open(pkg_resources.resource_filename(__name__, "words.txt"), "r") as fp:
           data = fp.read()

        self.words = set(w.lower() for w in data.split("\n"))

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                tokens = split_class_def(node.name)
            elif isinstance(node, ast.Name):
                tokens = split_name_def(node.id)
            else:
                continue

            for t in tokens:
                if t.lower() not in self.words:
                    yield (
                        node.lineno,
                        node.col_offset,
                        "SP1 Unknown word: {}".format(t),
                        type(self),
                    )
