# -*- coding: utf-8 -*-

import pytest
from flake8_spellcheck import is_number, parse_camel_case, parse_snake_case


@pytest.mark.parametrize(
    ["value", "col_offset", "tokens"],
    [
        ("bad_function", (0, 0), [((0, 0), "bad"), ((0, 4), "function")]),
        ("`pre_written`", (1, 2), [((1, 3), "pre"), ((1, 7), "written")]),
        (
            "foo_bar_baz",
            (30, 4),
            [((30, 4), "foo"), ((30, 8), "bar"), ((30, 12), "baz")],
        ),
        ("__init__", (0, 3), [((0, 5), "init")]),
    ],
)
def test_parse_snake_case(value, col_offset, tokens):
    assert list(parse_snake_case(value, col_offset)) == tokens


@pytest.mark.parametrize(
    ["value", "col_offset", "tokens"],
    [
        ("FakeClass", (0, 0), [((0, 0), "Fake"), ((0, 4), "Class")]),
        ("don't", (0, 0), [((0, 0), "don't")]),
        ("coding:", (20, 10), [((20, 10), "coding")]),
        ("`FastCar`", (1, 22), [((1, 23), "Fast"), ((1, 27), "Car")]),
        ("pair-programming", (5, 0), [((5, 0), "pair"), ((5, 5), "programming")]),
        ("FooBarBaz", (4, 4), [((4, 4), "Foo"), ((4, 7), "Bar"), ((4, 10), "Baz")]),
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
            # dont make b4d c8omm3nts
            # some 'quoted' words "shoul'd be" OK (also like `this`).
            foo = "bar"
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == [
            "./example.py:1:1: SC100 Possibly misspelt word: 'dont'",
            "./example.py:1:1: SC100 Possibly misspelt word: 'b4d'",
            "./example.py:1:1: SC100 Possibly misspelt word: 'c8omm3nts'",
            "./example.py:2:2: SC100 Possibly misspelt word: 'shoul'd'",
        ]

    def test_pass(self, flake8dir):
        flake8dir.make_example_py(
            """
            # don't make bad comments
            # some 'quoted' words "should be" OK (also like `this`).
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
            "./example.py:1:5: SC200 Possibly misspelt word: 'mispleled'"
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
            "./example.py:1:4: SC200 Possibly misspelt word: 'varaible'",
            "./example.py:1:13: SC200 Possibly misspelt word: 'namde'",
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
            "./example.py:1:7: SC200 Possibly misspelt word: 'Facke'",
            "./example.py:1:12: SC200 Possibly misspelt word: 'Claess'",
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
