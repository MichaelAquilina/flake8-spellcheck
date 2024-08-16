from textwrap import dedent

import pytest

from flake8_spellcheck import is_number, parse_camel_case, parse_snake_case


@pytest.mark.parametrize(
    ["value", "col_offset", "tokens"],
    [
        ("bad_function", (0, 0), [((0, 0), "bad"), ((0, 4), "function")]),
        ("árvíztűrő_tükörfúrógép", (0, 0), [((0, 0), "árvíztűrő"), ((0, 10), "tükörfúrógép")]),
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
        ("ÁrvíztűrőTükörfúrógép", (0, 0), [((0, 0), "Árvíztűrő"), ((0, 9), "Tükörfúrógép")]),
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
    @pytest.mark.parametrize(
        ["comment_value", "expected_out_lines"],
        [
            # For ASCII character test
            (
                """dont "make" b4d c8omm3nts""",
                [
                    "./example.py:2:1: SC100 Possibly misspelt word: 'dont'",
                    "./example.py:2:1: SC100 Possibly misspelt word: 'b4d'",
                    "./example.py:2:1: SC100 Possibly misspelt word: 'c8omm3nts'",
                ],
            ),
            # For unicode character test
            (
                """árvíz1űrő 1ükörfúrógép""",
                [
                    "./example.py:2:1: SC100 Possibly misspelt word: 'árvíz1űrő'",
                    "./example.py:2:1: SC100 Possibly misspelt word: '1ükörfúrógép'",
                ],
            ),
        ],
    )
    def test_fail(self, flake8_path, comment_value, expected_out_lines):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                # {comment_value}
                foo = "bar"
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == expected_out_lines

    @pytest.mark.parametrize(
        ["comment_value", "allowlist_value"],
        [
            # For ASCII character test
            ("""don't "make" 'bad' comments""", ""),
            # For unicode character test
            ("""árvíztűrő tükörfúrógép""", "árvíztűrő\ntükörfúrógép"),
        ],
    )
    def test_pass_allowlist_file(self, flake8_path, comment_value, allowlist_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                # {comment_value}
                foo = "bar"
                """
            )
        )
        (flake8_path / ".spellcheck-allowlist").write_text(allowlist_value)
        result = flake8_path.run_flake8()
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["comment_value", "allowlist_value"],
        [
            # For ASCII character test
            ("""don't "make" 'bad' comments""", ""),
            # For unicode character test
            ("""árvíztűrő tükörfúrógép""", "árvíztűrő,tükörfúrógép"),
        ],
    )
    def test_pass_allowlist_param(self, flake8_path, comment_value, allowlist_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                # {comment_value}
                foo = "bar"
                """
            )
        )
        result = flake8_path.run_flake8([f"--spellcheck-allowlist={allowlist_value}"])
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["comment_value"],
        [
            # For ASCII character test
            ("""dont "make" b4d c8omm3nts""",),
            # For unicode character test
            ("""árvíz1űrő 1ükörfúrógép""",),
        ],
    )
    def test_disabled(self, flake8_path, comment_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                # {comment_value}
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
        assert result.out_lines == ["./example.py:2:13: SC200 Possibly misspelt word: 'classs'"]

    @pytest.mark.parametrize(
        ["function_name", "expected_out_lines"],
        [
            # For ASCII character test
            (
                "mispleled_function",
                ["./example.py:2:5: SC200 Possibly misspelt word: 'mispleled'"],
            ),
            # For unicode character test
            (
                "árvíz1űrő_1ükörfúrógép_function",
                [
                    "./example.py:2:5: SC200 Possibly misspelt word: 'árvíz1űrő'",
                    "./example.py:2:15: SC200 Possibly misspelt word: '1ükörfúrógép'",
                ],
            ),
        ],
    )
    def test_fail(self, flake8_path, function_name, expected_out_lines):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                def {function_name}(a, b, c):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == expected_out_lines

    @pytest.mark.parametrize(
        ["function_name", "allowlist_value"],
        [
            # For ASCII character test
            ("misspelled_function", ""),
            # For unicode character test
            ("árvíztűrő_tükörfúrógép_function", "árvíztűrő\ntükörfúrógép"),
        ],
    )
    def test_pass_allowlist_file(self, flake8_path, function_name, allowlist_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                def {function_name}(a, b, c):
                    pass
                """
            )
        )
        (flake8_path / ".spellcheck-allowlist").write_text(allowlist_value)
        result = flake8_path.run_flake8()
        assert result.exit_code == 0
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["function_name", "allowlist_value"],
        [
            # For ASCII character test
            ("misspelled_function", ""),
            # For unicode character test
            ("árvíztűrő_tükörfúrógép_function", "árvíztűrő,tükörfúrógép"),
        ],
    )
    def test_pass_allowlist_param(self, flake8_path, function_name, allowlist_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                def {function_name}(a, b, c):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8([f"--spellcheck-allowlist={allowlist_value}"])
        assert result.exit_code == 0
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["function_name"],
        [
            # For ASCII character test
            ("mispleled_function",),
            # For unicode character test
            ("árvíz1űrő_1ükörfúrógép_function",),
        ],
    )
    def test_disabled(self, flake8_path, function_name):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                def {function_name}(a, b, c):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8(["--spellcheck-targets=comments"])
        assert result.exit_code == 0
        assert result.out_lines == []


class TestName:
    @pytest.mark.parametrize(
        ["source_code", "expected_out_lines"],
        [
            # For ASCII character test
            (
                """
                my_varaible_namde = "something"
                SOMETHIGN = "SOMETHING"
                SOMETHING_ELS = "SOMETHING"
                """,
                [
                    "./example.py:2:4: SC200 Possibly misspelt word: 'varaible'",
                    "./example.py:2:13: SC200 Possibly misspelt word: 'namde'",
                    "./example.py:3:1: SC200 Possibly misspelt word: 'SOMETHIGN'",
                    "./example.py:4:11: SC200 Possibly misspelt word: 'ELS'",
                ],
            ),
            # For unicode character test
            (
                """
                árívztűrő_tüökrfúrógép = "flood-resistant mirror drill"
                ÁRÍVZTŰRŐ = "FLOOD-RESISTANT"
                ÁRÍVZTŰRŐ_TÜÖKRFÚRÓGÉP = "FLOOD-RESISTANT MIRROR DRILL"
                """,
                [
                    "./example.py:2:1: SC200 Possibly misspelt word: 'árívztűrő'",
                    "./example.py:2:11: SC200 Possibly misspelt word: 'tüökrfúrógép'",
                    "./example.py:3:1: SC200 Possibly misspelt word: 'ÁRÍVZTŰRŐ'",
                    "./example.py:4:1: SC200 Possibly misspelt word: 'ÁRÍVZTŰRŐ'",
                    "./example.py:4:11: SC200 Possibly misspelt word: 'TÜÖKRFÚRÓGÉP'",
                ],
            ),
        ],
    )
    def test_fail(self, flake8_path, source_code, expected_out_lines):
        (flake8_path / "example.py").write_text(dedent(source_code))
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == expected_out_lines

    @pytest.mark.parametrize(
        ["source_code", "allowlist_value"],
        [
            # For ASCII character test
            (
                """
                my_variable_name = "something"
                SOMETHING = "SOMETHING"
                SOMETHING_ELSE = "SOMETHING"
                """,
                "",
            ),
            # For unicode character test
            (
                """
                árvíztűrő_tükörfúrógép = "flood-resistant mirror drill"
                ÁRVÍZTŰRŐ = "FLOOD-RESISTANT"
                ÁRVÍZTŰRŐ_TÜKÖRFÚRÓGÉP = "FLOOD-RESISTANT MIRROR DRILL"
                """,
                "árvíztűrő\ntükörfúrógép",
            ),
        ],
    )
    def test_pass_allowlist_file(self, flake8_path, source_code, allowlist_value):
        (flake8_path / "example.py").write_text(dedent(source_code))
        (flake8_path / ".spellcheck-allowlist").write_text(allowlist_value)
        result = flake8_path.run_flake8()
        assert result.exit_code == 0
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["source_code", "allowlist_value"],
        [
            # For ASCII character test
            (
                """
                my_variable_name = "something"
                SOMETHING = "SOMETHING"
                SOMETHING_ELSE = "SOMETHING"
                """,
                "",
            ),
            # For unicode character test
            (
                """
                árvíztűrő_tükörfúrógép = "flood-resistant mirror drill"
                ÁRVÍZTŰRŐ = "FLOOD-RESISTANT"
                ÁRVÍZTŰRŐ_TÜKÖRFÚRÓGÉP = "FLOOD-RESISTANT MIRROR DRILL"
                """,
                "árvíztűrő,tükörfúrógép",
            ),
        ],
    )
    def test_pass_allowlist_param(self, flake8_path, source_code, allowlist_value):
        (flake8_path / "example.py").write_text(dedent(source_code))
        result = flake8_path.run_flake8([f"--spellcheck-allowlist={allowlist_value}"])
        assert result.exit_code == 0
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["source_code"],
        [
            # For ASCII character test
            (
                """
                my_varaible_namde = "something"
                SOMETHIGN = "SOMETHING"
                SOMETHING_ELS = "SOMETHING"
                """,
            ),
            # For unicode character test
            (
                """
                árvíztűrő_tükörfúrógép = "flood-resistant mirror drill"
                ÁRVÍZTŰRŐ = "FLOOD-RESISTANT"
                ÁRVÍZTŰRŐ_TÜKÖRFÚRÓGÉP = "FLOOD-RESISTANT MIRROR DRILL"
                """,
            ),
        ],
    )
    def test_disabled(self, flake8_path, source_code):
        (flake8_path / "example.py").write_text(dedent(source_code))
        result = flake8_path.run_flake8(["--spellcheck-targets=comments"])
        assert result.exit_code == 0
        assert result.out_lines == []


class TestClassDef:
    @pytest.mark.parametrize(
        ["class_name", "expected_out_lines"],
        [
            # For ASCII character test
            (
                "FackeClaessName",
                [
                    "./example.py:2:7: SC200 Possibly misspelt word: 'Facke'",
                    "./example.py:2:12: SC200 Possibly misspelt word: 'Claess'",
                ],
            ),
            # For unicode character test
            (
                "Árvíz1űrőTü4örfúrógépClassName",
                [
                    "./example.py:2:7: SC200 Possibly misspelt word: 'Árvíz1űrő'",
                    "./example.py:2:16: SC200 Possibly misspelt word: 'Tü4örfúrógép'",
                ],
            ),
        ],
    )
    def test_fail(self, flake8_path, class_name, expected_out_lines):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                class {class_name}:
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == expected_out_lines

    @pytest.mark.parametrize(
        ["class_name", "allowlist_value"],
        [
            # For ASCII character test
            ("FakeClassName", ""),
            # For unicode character test
            ("ÁrvíztűrőTükörfúrógépClassName", "árvíztűrő\ntükörfúrógép"),
        ],
    )
    def test_pass_allowlist_file(self, flake8_path, class_name, allowlist_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                class {class_name}:
                    pass
                """
            )
        )
        (flake8_path / ".spellcheck-allowlist").write_text(allowlist_value)
        result = flake8_path.run_flake8()
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["class_name", "allowlist_value"],
        [
            # For ASCII character test
            ("FakeClassName", ""),
            # For unicode character test
            ("ÁrvíztűrőTükörfúrógépClassName", "árvíztűrő,tükörfúrógép"),
        ],
    )
    def test_pass_allowlist_param(self, flake8_path, class_name, allowlist_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                class {class_name}:
                    pass
                """
            )
        )
        result = flake8_path.run_flake8([f"--spellcheck-allowlist={allowlist_value}"])
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["class_name"],
        [
            # For ASCII character test
            ("FackeClaessName",),
            # For unicode character test
            ("Árvíz1űrőTü4örfúrógépClassName",),
        ],
    )
    def test_disabled(self, flake8_path, class_name):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                class {class_name}:
                    pass
                """
            )
        )
        result = flake8_path.run_flake8(["--spellcheck-targets=comments"])
        assert result.exit_code == 0
        assert result.out_lines == []


class TestLeadingUnderscore:
    @pytest.mark.parametrize(
        ["function_name", "expected_out_lines"],
        [
            # For ASCII character test
            (
                "_doSsomething",
                ["./example.py:2:8: SC200 Possibly misspelt word: 'Ssomething'"],
            ),
            # For unicode character test
            (
                "_Árvíz1űrőTü4örfúrógépFunction",
                [
                    "./example.py:2:6: SC200 Possibly misspelt word: 'Árvíz1űrő'",
                    "./example.py:2:15: SC200 Possibly misspelt word: 'Tü4örfúrógép'",
                ],
            ),
        ],
    )
    def test_fail(self, flake8_path, function_name, expected_out_lines):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                def {function_name}(s):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8()
        assert result.exit_code == 1
        assert result.out_lines == expected_out_lines

    @pytest.mark.parametrize(
        ["function_name", "allowlist_value"],
        [
            # For ASCII character test
            ("_doSomething", ""),
            # For unicode character test
            ("_ÁrvíztűrőTükörfúrógépFunction", "árvíztűrő\ntükörfúrógép"),
        ],
    )
    def test_pass_allowlist_file(self, flake8_path, function_name, allowlist_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                def {function_name}(s):
                    pass
                """
            )
        )
        (flake8_path / ".spellcheck-allowlist").write_text(allowlist_value)
        result = flake8_path.run_flake8()
        assert result.exit_code == 0
        assert result.out_lines == []

    @pytest.mark.parametrize(
        ["function_name", "allowlist_value"],
        [
            # For ASCII character test
            ("_doSomething", ""),
            # For unicode character test
            ("_ÁrvíztűrőTükörfúrógépFunction", "árvíztűrő,tükörfúrógép"),
        ],
    )
    def test_pass_allowlist_param(self, flake8_path, function_name, allowlist_value):
        (flake8_path / "example.py").write_text(
            dedent(
                f"""
                def {function_name}(s):
                    pass
                """
            )
        )
        result = flake8_path.run_flake8([f"--spellcheck-allowlist={allowlist_value}"])
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
        result = flake8_path.run_flake8(["--dictionaries=python,technical,django,en_US"])
        assert result.exit_code == 0
        assert result.out_lines == []
