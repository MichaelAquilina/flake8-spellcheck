# -*- coding: utf-8 -*-

import pytest
from flake8_spellcheck import is_number, parse_camel_case, parse_snake_case


@pytest.mark.parametrize(
    ["value", "col_offset", "tokens"],
    [
        ("bad_function", 0, [(0, "bad"), (4, "function")]),
        ("`pre_written`", 2, [(3, "pre"), (7, "written")]),
        ("foo_bar_baz", 4, [(4, "foo"), (8, "bar"), (12, "baz")]),
        ("__init__", 3, [(5, "init")]),
    ],
)
def test_parse_snake_case(value, col_offset, tokens):
    assert list(parse_snake_case(value, col_offset)) == tokens


@pytest.mark.parametrize(
    ["value", "col_offset", "tokens"],
    [
        ("FakeClass", 0, [(0, "Fake"), (4, "Class")]),
        ("don't", 0, [(0, "don't")]),
        ("coding:", 10, [(10, "coding")]),
        ("`FastCar`", 22, [(23, "Fast"), (27, "Car")]),
        ("pair-programming", 0, [(0, "pair"), (5, "programming")]),
        ("FooBarBaz", 4, [(4, "Foo"), (7, "Bar"), (10, "Baz")]),
    ],
)
def test_parse_camel_case(value, col_offset, tokens):
    assert list(parse_camel_case(value, col_offset)) == tokens


@pytest.mark.parametrize(["value", "result"], [("8", True), ("word8", False)])
def test_is_number(value, result):
    assert is_number(value) is result


def test_python_words(flake8dir):
    flake8dir.make_example_py(
        """
        id = str(4)
        if isinstance(id, int):
            dict(id=id)
    """
    )
    result = flake8dir.run_flake8()
    assert result.out_lines == []


class TestComments:
    def test_fail(self, flake8dir):
        flake8dir.make_example_py(
            """
            # this is a b4d c8omm3nt
            foo = "bar"
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == [
            "./example.py:1:1: SC100 Possibly misspelt word: 'b4d'",
            "./example.py:1:1: SC100 Possibly misspelt word: 'c8omm3nt'",
        ]

    def test_pass(self, flake8dir):
        flake8dir.make_example_py(
            """
            # this is a bad comment
            foo = "bar"
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == []


class TestFunctionDef:
    def test_ignore_symbols(self, flake8dir):
        flake8dir.make_example_py(
            """
            def dont_fail(a):
                return a + 2
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == []

    def test_fail(self, flake8dir):
        flake8dir.make_example_py(
            """
            def mispleled_function(a, b, c):
                pass
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == [
            "./example.py:1:5: SC100 Possibly misspelt word: 'mispleled'"
        ]

    def test_pass(self, flake8dir):
        flake8dir.make_example_py(
            """
            def misspelled_function(a, b, c):
                pass
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == []


class TestName:
    def test_fail(self, flake8dir):
        flake8dir.make_example_py(
            """
            my_varaible_namde = "something"
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == [
            "./example.py:1:4: SC100 Possibly misspelt word: 'varaible'",
            "./example.py:1:13: SC100 Possibly misspelt word: 'namde'",
        ]

    def test_pass(self, flake8dir):
        flake8dir.make_example_py(
            """
            my_variable_name = "something"
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == []


class TestClassDef:
    def test_fail(self, flake8dir):
        flake8dir.make_example_py(
            """
        class FackeClaessName:
            pass
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == [
            "./example.py:1:7: SC100 Possibly misspelt word: 'Facke'",
            "./example.py:1:12: SC100 Possibly misspelt word: 'Claess'",
        ]

    def test_pass(self, flake8dir):
        flake8dir.make_example_py(
            """
            class FakeClassName:
                pass
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == []
