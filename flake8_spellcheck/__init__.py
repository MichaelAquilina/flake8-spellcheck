import os
import tokenize
from string import ascii_lowercase, ascii_uppercase, digits

import pkg_resources


# Really simple detection function
def detect_case(name):
    if name.startswith("http"):
        return "url"
    # ignore leading underscores when testing for snake case
    elif "_" in name.lstrip("_"):
        return "snake"
    elif name.isupper():
        return "snake"
    else:
        return "camel"


def parse_camel_case(name, position):
    index = position[1]
    start = index
    buffer = ""
    for c in name:
        index += 1
        if c in ascii_lowercase or c in digits or c in ("'"):
            buffer += c
        else:
            if buffer:
                yield (position[0], start), buffer
            if c in ascii_uppercase:
                buffer = c
                start = index - 1
            else:
                buffer = ""
                start = index

    if buffer:
        yield (position[0], start), buffer


def parse_snake_case(name, position):
    index = position[1]
    start = index
    buffer = ""
    for c in name:
        index += 1
        if c in ascii_lowercase or c in digits or c in ascii_uppercase:
            buffer += c
        else:
            if buffer:
                yield (position[0], start), buffer

            buffer = ""
            start = index

    if buffer:
        yield (position[0], start), buffer


def is_number(value):
    try:
        float(value)
    except ValueError:
        return False
    else:
        return True


def get_code(token_type):
    if token_type == tokenize.COMMENT:
        return "SC100"
    elif token_type == tokenize.NAME:
        return "SC200"
    else:
        raise ValueError("Unknown token_type {}".format(token_type))


class SpellCheckPlugin:
    name = "flake8-spellcheck"
    version = "0.12.1"

    def __init__(self, tree, filename="(none)", file_tokens=None):
        self.file_tokens = file_tokens

        self.words = set()
        for dictionary in self.dictionaries:
            data = pkg_resources.resource_string(__name__, dictionary)
            data = data.decode("utf8")
            self.words |= set(w.lower() for w in data.split("\n"))

        if os.path.exists(self.whitelist_path):
            with open(self.whitelist_path, "r") as fp:
                whitelist = fp.read()

            whitelist = set(w.lower() for w in whitelist.split("\n"))
            self.words |= whitelist

        # Hacky way of getting dictionary with symbols stripped
        self.no_symbols = set()
        for w in self.words:
            if w.endswith("'s"):
                self.no_symbols.add(w.replace("'s", ""))
            else:
                self.no_symbols.add(w.replace("'", ""))

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--whitelist",
            help="Path to text file containing whitelisted words",
            default="whitelist.txt",
            parse_from_config=True,
        )
        parser.add_option(
            "--dictionaries",
            # Unfortunately optparse does not support nargs="+" so we
            # need to use a command separated list to work round it
            help="Command separated list of dictionaries to enable",
            default="en_US,python,technical",
            comma_separated_list=True,
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options):
        cls.whitelist_path = options.whitelist
        cls.dictionaries = [d + ".txt" for d in options.dictionaries]

    def _detect_errors(self, tokens, use_symbols, token_type):
        code = get_code(token_type)

        for position, token in tokens:
            test_token = token.lower().strip("'").strip('"')

            if use_symbols:
                valid = test_token in self.words
            else:
                valid = test_token in self.no_symbols

            # Need a way of matching words without symbols
            if not valid and not is_number(token):
                yield (
                    position[0],
                    position[1],
                    "{} Possibly misspelt word: '{}'".format(code, token),
                    type(self),
                )

    def run(self):
        for token_info in self.file_tokens:
            yield from self._parse_token(token_info)

    def _parse_token(self, token_info):
        if token_info.type == tokenize.NAME:
            value = token_info.string
        elif token_info.type == tokenize.COMMENT:
            value = token_info.string.lstrip("#")
        else:
            return

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

        for error_tuple in self._detect_errors(tokens, use_symbols, token_info.type):
            yield error_tuple
