from textwrap import dedent

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
        ("_ignoredValue", (20, 10), [((20, 11), "ignored"), ((20, 18), "Value")]),
    ],
)
def test_parse_camel_case(value, col_offset, tokens):
    assert list(parse_camel_case(value, col_offset)) == tokens


@pytest.mark.parametrize(["value", "result"], [("8", True), ("word8", False)])
def test_is_number(value, result):
    assert is_number(value) is result


def test_python_words(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """
            id = str(4)
            if isinstance(id, int):
                dict(id=id)
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


class TestComments:
    def test_fail(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                # dont "make" b4d c8omm3nts
                foo = "bar"
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == [
            "./example.py:2:1: SC100 Possibly misspelt word: 'dont'",
            "./example.py:2:1: SC100 Possibly misspelt word: 'b4d'",
            "./example.py:2:1: SC100 Possibly misspelt word: 'c8omm3nts'",
        ]

    def test_pass(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                # don't "make" 'bad' comments
                foo = "bar"
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.out_lines == []

    def test_disabled(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                # dont "make" b4d c8omm3nts
                foo = "bar"
                """
            )
        )
        result = flake8_path.run_flake8(["--spellcheck-targets=names"])
        assert result.exit_code == 0
        assert result.out_lines == []

    def test_flake8_pragma(self, flake8_path):
        (flake8_path / "example.py").write_text("foo = 'bar'  # noqa: W503\n")
        result = flake8_path.run_flake8()
        assert result.out_lines == []

    def test_flake8_pragma_spaces(self, flake8_path):
        (flake8_path / "example.py").write_text("foo = 'bar'  #    noqa: W503\n")
        result = flake8_path.run_flake8()
        assert result.out_lines == [
            "./example.py:1:14: E262 inline comment should start with '# '"
        ]

    # Regression test for github.com/MichaelAquilina/flake8-spellcheck/issues/34
    def test_empty_comment(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                # the empty comment below should not fail
                #
                # hello world
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.out_lines == []

    # Regression test for https://github.com/MichaelAquilina/flake8-spellcheck/issues/36
    def test_type_and_noqa(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                # the comment below should not fail on `W503` or `W504`  # noqa: SC100
                foo = []  # type: ignore  # noqa: W503  # noqa: W504
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.out_lines == []

    # Regression test for github.com/MichaelAquilina/flake8-spellcheck/issues/40
    def test_pure_number_char_comment(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                # the comment below should not fail
                ##########
                # hello world
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.out_lines == []


class TestFunctionDef:
    def test_apostrophe(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                def dont_fail(a):
                    return a + 2


                def cant_fail(b):
                    return b * 4
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 0
        assert result.out_lines == []

    def test_apostrophe_ending_with_s(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                def request_classs(a, b, c):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == [
            "./example.py:2:13: SC200 Possibly misspelt word: 'classs'"
        ]

    def test_fail(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                def mispleled_function(a, b, c):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == [
            "./example.py:2:5: SC200 Possibly misspelt word: 'mispleled'"
        ]

    def test_pass(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                def misspelled_function(a, b, c):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 0
        assert result.out_lines == []

    def test_disabled(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                def mispleled_function(a, b, c):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8(["--spellcheck-targets=comments"])
        assert result.exit_code == 0
        assert result.out_lines == []


class TestName:
    def test_fail(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                my_varaible_namde = "something"
                SOMETHIGN = "SOMETHING"
                SOMETHING_ELS = "SOMETHING"
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == [
            "./example.py:2:4: SC200 Possibly misspelt word: 'varaible'",
            "./example.py:2:13: SC200 Possibly misspelt word: 'namde'",
            "./example.py:3:1: SC200 Possibly misspelt word: 'SOMETHIGN'",
            "./example.py:4:11: SC200 Possibly misspelt word: 'ELS'",
        ]

    def test_pass(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                my_variable_name = "something"
                SOMETHING = "SOMETHING"
                SOMETHING_ELSE = "SOMETHING"
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 0
        assert result.out_lines == []

    def test_disabled(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                my_varaible_namde = "something"
                SOMETHIGN = "SOMETHING"
                SOMETHING_ELS = "SOMETHING"
                """
            )
        )
        result = flake8_path.run_flake8(["--spellcheck-targets=comments"])
        assert result.exit_code == 0
        assert result.out_lines == []


class TestClassDef:
    def test_fail(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                class FackeClaessName:
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == [
            "./example.py:2:7: SC200 Possibly misspelt word: 'Facke'",
            "./example.py:2:12: SC200 Possibly misspelt word: 'Claess'",
        ]

    def test_pass(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                class FakeClassName:
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.out_lines == []

    def test_disabled(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                class FackeClaessName:
                    pass
                """
            )
        )
        result = flake8_path.run_flake8(["--spellcheck-targets=comments"])
        assert result.exit_code == 0
        assert result.out_lines == []


class TestLeadingUnderscore:
    def test_fail(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                def _doSsomething(s):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == [
            "./example.py:2:8: SC200 Possibly misspelt word: 'Ssomething'"
        ]

    def test_pass(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                def _doSomething(s):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 0
        assert result.out_lines == []


class TestOptionalDictionaries:
    def test_fail(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                from django.http import HttpResponse
                from django.views.decorators.csrf import csrf_protect


                @csrf_protect
                def my_view(request):
                    return HttpResponse("hello world")
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == [
            "./example.py:3:30: SC200 Possibly misspelt word: 'csrf'",
            "./example.py:3:42: SC200 Possibly misspelt word: 'csrf'",
            "./example.py:6:2: SC200 Possibly misspelt word: 'csrf'",
        ]

    def test_success(self, flake8_path):
        (flake8_path / "example.py").write_text(
            dedent(
                """
                from django.http import HttpResponse
                from django.views.decorators.csrf import csrf_protect


                @csrf_protect
                def my_view(request):
                    return HttpResponse("hello world")
                """
            )
        )
        result = flake8_path.run_flake8(
            ["--dictionaries=python,technical,django,en_US"]
        )
        assert result.exit_code == 0
        assert result.out_lines == []
