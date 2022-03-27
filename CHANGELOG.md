Flake8 Spellcheck Changelog
===========================

0.26.0
------
* Drop support for python 3.6
* Remove dependency on importlib
* General codebase improvements (Thanks @shaleh and @djmattyg007)
* Add type annotations
* Introduce pre-commit and mypy to codebase

0.25.0
------
* Add partial support for pandas dictionaries (Thanks @aaronzipp)
* Update python dictionary with missing words

0.24.0
------
* Speed up run for multiple files by loading once the dictionary, and using ``importlib.resources`` instead of
  ``pkg_resources`` - by @gaborbernat.

0.21.0 - 0.23.0
---------------
* Add more common words to technical and python dictionaries

0.20.1
------
* Fix crash on lines with only '#' characters (Thanks @paulovcmedeiros)

0.20.0
------
* Updated techincal and django dictionaries (Thanks @3n-k1)

0.19.1
------
* Fix bug where # noqa comments were incorrectly spellchecked if combined with typing comments (Thanks @3n-k1 for the fix)

0.19.0
------
* Updates to technical and python dictionaries

0.18.1
------
* Fix regression where plugin would crash on lines with empty comments (Issue #34)

0.18.0
------
* Do not report errors on `# noqa:` comments. Thanks @3n-k1!

0.17.0
------
* Update technical.txt

0.16.0
------
* Add support for specifying spellcheck targets in flake8 configuration

0.15.0
------
* Update technical and en_US

0.14.0
------
* Add "hardcode" to technical.txt

0.13.0
------
* Add more words to python, django and technical dictionaries (Thanks @pbelskiy)

0.12.1
------
* Fix bug where quotes in comments would result in spell errors

0.12.0
------
* Add more words to python dictionary
* Fully support optional django dictionary

0.11.0
------
* Add more words to python dictionary
* Add initial support for optional in-built dictionaries (e.g. Django)

0.10.0
------
* Handle special cases when spellchecking words ending with 's

0.9.1
-----
* Add `hasattr` to in-built python dictionary

0.9.0
-----
* Introduce Changelog
* Correctly detect fully UPPERCASE variables (thanks @gera)
* Correctly detect methods and variables with leading underscores (thanks @gera)
* Added new inbuilt words to python dictionary
