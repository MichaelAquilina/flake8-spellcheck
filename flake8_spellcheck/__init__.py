# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import tokenize
from string import ascii_lowercase, ascii_uppercase, digits

import pkg_resources


# Really simple detection function
def detect_case(name):
    if name.startswith("http"):
        return "url"
    elif "_" in name:
        return "snake"
    else:
        return "camel"


def parse_camel_case(name, pos):
    index = pos[1]
    start = index
    buffer = ""
    for c in name:
        index += 1
        if c in ascii_lowercase or c in digits or c in ("'"):
            buffer += c
        else:
            if buffer:
                yield (pos[0], start), buffer
            if c in ascii_uppercase:
                buffer = c
                start = index - 1
            else:
                buffer = ""
                start = index

    if buffer:
        yield (pos[0], start), buffer


def parse_snake_case(name, pos):
    index = pos[1]
    start = index
    buffer = ""
    for c in name:
        index += 1
        if c in ascii_lowercase or c in digits or c in ascii_lowercase:
            buffer += c
        else:
            if buffer:
                yield (pos[0], start), buffer

            buffer = ""
            start = index

    if buffer:
        yield (pos[0], start), buffer


def is_number(value):
    try:
        float(value)
    except ValueError:
        return False
    else:
        return True


class SpellCheckPlugin(object):
    name = "flake8-spellcheck"
    version = "0.6.0"

    def __init__(self, tree, filename="(none)", file_tokens=None):
        self.file_tokens = file_tokens

        self.words = set()
        for dictionary in ("words.txt", "python.txt", "technical.txt"):
            data = pkg_resources.resource_string(__name__, dictionary)
            data = data.decode("utf8")
            self.words |= set(w.lower() for w in data.split("\n"))

        if os.path.exists(self.whitelist_path):
            with open(self.whitelist_path, "r") as fp:
                whitelist = fp.read()

            whitelist = set(w.lower() for w in whitelist.split("\n"))
            self.words |= whitelist

        # Hacky way of getting dictionary with symbols stripped
        self.no_symbols = set(w.replace("'", "") for w in self.words)

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

    def _detect_errors(self, tokens, use_symbols):
        for pos, token in tokens:
            if use_symbols:
                valid = token.lower() in self.words
            else:
                valid = token.lower() in self.no_symbols

            # Need a way of matching words without symbols
            if not valid and not is_number(token):
                yield (
                    pos[0],
                    pos[1],
                    "SC100 Possibly misspelt word: '{}'".format(token),
                    type(self),
                )

    def run(self):
        for token_info in self.file_tokens:
            if token_info.type == tokenize.NAME:
                value = token_info.string
            elif token_info.type == tokenize.COMMENT:
                value = token_info.string.lstrip("#")
            else:
                continue

            tokens = []
            for word in value.split(" "):
                case = detect_case(word)
                if case == "url":
                    # Nothing to do here
                    continue
                elif case == "snake":
                    tokens.extend(parse_snake_case(word, token_info.start))
                elif case == "camel":
                    tokens.extend(parse_camel_case(word, token_info.start))

            if token_info.type == tokenize.NAME:
                use_symbols = False
            elif token_info.type == tokenize.COMMENT:
                use_symbols = True

            yield from self._detect_errors(tokens, use_symbols)
