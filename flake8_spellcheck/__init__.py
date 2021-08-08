import enum
import logging
import re
import tokenize
from argparse import Namespace
from itertools import chain
from pathlib import Path
from string import ascii_lowercase, ascii_uppercase, digits
from typing import Any, FrozenSet, Iterable, Iterator, List, Optional, Tuple, Type

from flake8.options.manager import OptionManager

from .version import version as __version__

logger = logging.getLogger(__name__)


NOQA_REGEX = re.compile(r"#[\s]*noqa:[\s]*[\D]+[\d]+")

DICTIONARY_PATH = Path(__file__).parent
DEFAULT_DICTIONARY_NAMES = ("en_US", "python", "technical")


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
        raise ValueError("Unknown token_type {}".format(token_type))


def find_allowlist_path(options: Namespace) -> Optional[Path]:
    if options.spellcheck_allowlist:
        if options.spellcheck_allowlist.exists():
            return options.spellcheck_allowlist
        else:
            logger.error(
                "ERROR: Supplied allowlist file for flake8-spellcheck does not exist."
            )
            return None
    elif options.whitelist:
        logger.warning(
            "DEPRECATED: Support for '--whitelist' will be removed in future. Please use '--spellcheck-allowlist' instead."
        )
        whitelist_path = Path(options.whitelist)
        if whitelist_path.exists():
            return whitelist_path
        else:
            logger.error(
                "ERROR: Supplied allowlist file for flake8-spellcheck does not exist."
            )
            return None

    default_allowlist_path = Path("spellcheck-allowlist.txt")
    if default_allowlist_path.exists():
        return default_allowlist_path

    default_whitelist_path = Path("whitelist.txt")
    if default_whitelist_path.exists():
        logger.warning(
            "DEPRECATED: Support for 'whitelist.txt' will be removed in future. Please use 'spellcheck-allowlist.txt' instead."
        )
        return default_whitelist_path

    return None


def flatten_dictionary_add_list(options: Namespace) -> Iterator[str]:
    for identifier in options.spellcheck_add_dictionary:
        if isinstance(identifier, str):
            yield identifier
            continue

        for _id in identifier:
            yield _id


class SpellCheckPlugin:
    name = "flake8-spellcheck"
    version = __version__

    def __init__(
        self, tree, filename="(none)", file_tokens: Iterable[tokenize.TokenInfo] = None
    ):
        self.file_tokens: Iterable[tokenize.TokenInfo] = file_tokens

    @classmethod
    def load_dictionaries(
        cls, options: Namespace
    ) -> Tuple[FrozenSet[str], FrozenSet[str]]:
        words = set()

        dictionary_names: Iterable[str]
        if options.dictionaries:
            logger.warning(
                "DEPRECATED: Support for '--dictionaries' will be removed in future. Use '--spellcheck-add-dictionary' instead."
            )
            dictionary_names = options.dictionaries
        else:
            if options.spellcheck_disable_default_dictionaries:
                dictionary_names = flatten_dictionary_add_list(options)
            else:
                dictionary_names = chain(
                    DEFAULT_DICTIONARY_NAMES, flatten_dictionary_add_list(options)
                )

        for dictionary_name in dictionary_names:
            dictionary_path = DICTIONARY_PATH / "{}.txt".format(dictionary_name)
            if dictionary_path.exists():
                dictionary_data = dictionary_path.read_text()
                words |= set(word.lower() for word in dictionary_data.split("\n"))
            else:
                logger.error(
                    "ERROR: Supplied built-in dictionary '{}' does not exist.".format(
                        dictionary_name
                    )
                )

        allowlist_path: Optional[Path] = find_allowlist_path(options)
        if allowlist_path:
            allowlist_data = allowlist_path.read_text()
            words |= set(w.lower() for w in allowlist_data.split("\n"))

        # Hacky way of getting dictionary with symbols stripped
        no_symbols = set()
        for w in words:
            if w.endswith("'s"):
                no_symbols.add(w.replace("'s", ""))
            else:
                no_symbols.add(w.replace("'", ""))
        return frozenset(words), frozenset(no_symbols)

    @classmethod
    def add_options(cls, parser: OptionManager):
        parser.add_option(
            "--spellcheck-allowlist",
            help="Path to text file containing a custom list of allowed words.",
            type=Path,
            parse_from_config=True,
        )
        parser.add_option(
            "--whitelist",
            help="(deprecated) Path to text file containing a custom list of allowed words. Use '--spellcheck-allowlist' instead.",
            parse_from_config=True,
        )
        parser.add_option(
            "--spellcheck-disable-default-dictionaries",
            help="Don't use the default list of built-in dictionaries. You can still use '--spellcheck-add-dictionary' to select individual built-in dictionaries.",
            action="store_true",
            parse_from_config=True,
        )
        parser.add_option(
            "--spellcheck-add-dictionary",
            help="A built-in dictionary to enable. Pass this flag multiple times to enable multiple dictionaries.",
            action="append",
            default=[],
            parse_from_config=True,
            comma_separated_list=True,
        )
        parser.add_option(
            "--dictionaries",
            help="(deprecated) A comma-separated list of built-in dictionaries to enable. Use '--spellcheck-add-dictionary' instead.",
            comma_separated_list=True,
            parse_from_config=True,
        )
        # TODO: Convert this to use action=append
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
                    "{} Possibly misspelt word: '{}'".format(code, token),
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

        for error_tuple in self._detect_errors(tokens, use_symbols, token_info.type):
            yield error_tuple


__all__ = ("__version__", "SpellCheckPlugin")
