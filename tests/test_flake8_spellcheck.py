# -*- coding: utf-8 -*-

def test_class_name_pass(flake8dir):
    flake8dir.make_example_py("""
        class FakeClassName:
            pass
    """)
    result = flake8dir.run_flake8()
    assert result.out_lines == []
