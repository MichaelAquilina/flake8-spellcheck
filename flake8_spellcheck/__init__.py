import enum
import os
import re
import tokenize
from argparse import Namespace
from ast import AST
from pathlib import Path
from string import ascii_lowercase, ascii_uppercase, digits
from tokenize import TokenInfo
from typing import Any, FrozenSet, Iterable, Iterator, List, Optional, Tuple, Type

from flake8.options.manager import OptionManager

from .version import version as __version__

NOQA_REGEX = re.compile(r"#[\s]*noqa:[\s]*[\D]+[\d]+")
DICTIONARY_PATH = Path(__file__).parent


LintError = Tuple[int, int, str, Type["SpellCheckPlugin"]]
Position = Tuple[int, int]


class WordCase(enum.Enum):
    URL = enum.auto()
    SNAKE = enum.auto()
    CAMEL = enum.auto()


# Really simple detection function
def detect_case(word: str) -> WordCase:
    if word.startswith("http"):
        return WordCase.URL
    # ignore leading underscores when testing for snake case
    elif "_" in word.lstrip("_"):
        return WordCase.SNAKE
    elif word.isupper():
        return WordCase.SNAKE
    else:
        return WordCase.CAMEL


def parse_camel_case(name: str, position: Position) -> Iterator[Tuple[Position, str]]:
    index = position[1]
    start = index
    buffer = ""
    for c in name:
        index += 1
        if c in ascii_lowercase or c in digits or c in "'":
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


def parse_snake_case(name: str, position: Position) -> Iterator[Tuple[Position, str]]:
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


def is_number(value: Any) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    else:
        return True


def get_code(token_type: int) -> str:
    if token_type == tokenize.COMMENT:
        return "SC100"
    elif token_type == tokenize.NAME:
        return "SC200"
    else:
        raise ValueError(f"Unknown token_type {token_type}")


class SpellCheckPlugin:
    name = "flake8-spellcheck"
    version = __version__

    spellcheck_targets: FrozenSet[str] = frozenset()
    no_symbols: FrozenSet[str] = frozenset()
    words: FrozenSet[str] = frozenset()

    def __init__(
        self,
        tree: AST,
        filename: str = "(none)",
        file_tokens: Optional[Iterable[TokenInfo]] = None,
    ) -> None:
        if file_tokens is None:
            raise ValueError("Plugin requires file_tokens")
        else:
            self.file_tokens: Iterable[TokenInfo] = file_tokens

    @classmethod
    def load_dictionaries(
        cls, options: Namespace
    ) -> Tuple[FrozenSet[str], FrozenSet[str]]:
        words = set()
        for dictionary_name in options.dictionaries:
            dictionary_path = DICTIONARY_PATH / f"{dictionary_name}.txt"
            data = dictionary_path.read_text()
            words |= {w.lower() for w in data.split("\n")}

        if os.path.exists(options.whitelist):
            with open(options.whitelist) as fp:
                whitelist = fp.read()
            whitelist_data = {w.lower() for w in whitelist.split("\n")}
            words |= whitelist_data

        # Hacky way of getting dictionary with symbols stripped
        no_symbols = set()
        for w in words:
            if w.endswith("'s"):
                no_symbols.add(w.replace("'s", ""))
            else:
                no_symbols.add(w.replace("'", ""))
        return frozenset(words), frozenset(no_symbols)

    @classmethod
    def add_options(cls, parser: OptionManager) -> None:
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
        parser.add_option(
            "--spellcheck-targets",
            help="Specify the targets to spellcheck",
            default="names,comments",
            comma_separated_list=True,
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options: Namespace) -> None:
        cls.words, cls.no_symbols = cls.load_dictionaries(options)
        cls.spellcheck_targets = frozenset(options.spellcheck_targets)

    def _detect_errors(
        self, tokens: Iterable[Tuple[Position, str]], use_symbols: bool, token_type: int
    ) -> Iterator[LintError]:
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
                    f"{code} Possibly misspelt word: '{token}'",
                    type(self),
                )

    def run(self) -> Iterator[LintError]:
        for token_info in self.file_tokens:
            yield from self._parse_token(token_info)

    def _is_valid_comment(self, token_info: tokenize.TokenInfo) -> bool:
        return (
            token_info.type == tokenize.COMMENT
            and "comments" in self.spellcheck_targets
            # Ensure comment is neither empty nor a sequence of "#" characters
            # github.com/MichaelAquilina/flake8-spellcheck/issues/34
            and token_info.string.lstrip("#").strip() != ""
            # Ignore flake8 pragma comments
            and token_info.string.lstrip("#").split()[0] != "noqa:"
        )

    def _parse_token(self, token_info: tokenize.TokenInfo) -> Iterator[LintError]:
        if token_info.type == tokenize.NAME and "names" in self.spellcheck_targets:
            value = token_info.string
        elif self._is_valid_comment(token_info):
            # strip out all `noqa: [code]` style comments so they aren't erroneously checked
            # see https://github.com/MichaelAquilina/flake8-spellcheck/issues/36 for info
            value = NOQA_REGEX.sub("", token_info.string.lstrip("#"))
        else:
            return

        tokens: List[Tuple[Position, str]] = []
        for word in value.split(" "):
            case = detect_case(word)
            if case == WordCase.URL:
                # Nothing to do here
                continue
            elif case == WordCase.SNAKE:
                tokens.extend(parse_snake_case(word, token_info.start))
            elif case == WordCase.CAMEL:
                tokens.extend(parse_camel_case(word, token_info.start))

        if token_info.type == tokenize.NAME:
            use_symbols = False
        elif token_info.type == tokenize.COMMENT:
            use_symbols = True
        else:
            return

        yield from self._detect_errors(tokens, use_symbols, token_info.type)


__all__ = ("__version__", "SpellCheckPlugin")
