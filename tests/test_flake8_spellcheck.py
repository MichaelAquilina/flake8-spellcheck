# -*- coding: utf-8 -*-


class TestFunctionDef:
    def test_fail(self, flake8dir):
        flake8dir.make_example_py(
            """
            def mispleled_function(a, b, c):
                pass
        """
        )
        result = flake8dir.run_flake8()
        assert result.out_lines == [
            "./example.py:1:1: SP1 Unknown word: 'mispleled'",
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
            "./example.py:1:4: SP1 Unknown word: 'varaible'",
            "./example.py:1:13: SP1 Unknown word: 'namde'",
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
            "./example.py:1:1: SP1 Unknown word: 'Facke'",
            "./example.py:1:1: SP1 Unknown word: 'Claess'",
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
