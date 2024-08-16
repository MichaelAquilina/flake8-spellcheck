=================
Flake8 Spellcheck
=================

|CircleCI| |Black| |PyPi|

Flake8 Plugin that spellchecks variables, functions, classes and other bits of your python code.

You can create an allowlist for words that are specific to your project simply by adding them a ``.spellcheck-allowlist`` file
in the root of your project directory. Each word you add should be separated by a newline.

Spelling is assumed to be in en_US.

This plugin supports python 3.8+

Codes
-----

* SC100 - Spelling error in comments
* SC200 - Spelling error in name (e.g. variable, function, class)

Enable Django support
---------------------

You can enable support for a Django dictionary by adding the following to your
flake8 configuration (e.g. your ``.flake8`` file):

.. code-block:: ini

    [flake8]
    dictionaries = en_US,python,technical,django

Enable pandas support
---------------------

You can enable support for pandas DataFrames by adding the following to your
flake8 configuration (e.g. your ``.flake8`` file):

.. code-block:: ini

    [flake8]
    dictionaries = en_US,python,technical,pandas

Specify Targets
---------------

Both ``comments`` and ``names`` (variable names, function names...) are spellchecked by default.
You can specify what targets to spellcheck in your flake8 configuration (e.g. in your ``.flake8`` file):

.. code-block:: ini

   [flake8]
   spellcheck-targets = comments

The above configuration would only spellcheck comments

.. code-block:: ini

   [flake8]
   spellcheck-targets = names

The above configuration would only spellcheck names

Specify Allowlist
---------------

You can specify a list of allowed words - spellcheck will then not raise errors when those
words are encountered. You can define the list of allowed words either as a file or as a
configuration parameter.

By default, spellcheck will try to load a `.spellcheck-allowlist` file in the root of your
project. You can override the file name using the `--spellcheck-allowlist-file` CLI
parameter, or in your flake8 configuration (e.g. in your ``.flake8`` file):

.. code-block:: ini

   [flake8]
   spellcheck-allowlist-file = your-allowlist-file

You can also define the allowlist directly using the `--spellcheck-allowlist` CLI parameter
(this takes a comma-separated list of words to allow) or using the flake8 configuration
(e.g. in your ``.flake8`` file):

.. code-block:: ini

   [flake8]
   spellcheck-allowlist = your, allowed, words




Ignore Rules
------------

.. code-block:: ini

   [flake8]
   ignore = SC100, SC200

Contributing
------------

If you have found word(s) which are listed as a spelling error but are actually correct terms used
in python or in technical implementations (e.g. http), then you can very easily contribute by
adding those word(s) to the appropriate dictionaries:

* `python dictionary <flake8_spellcheck/python.txt>`_
* `technical dictionary <flake8_spellcheck/technical.txt>`_
* `django dictionary <flake8_spellcheck/django.txt>`_
* `pandas dictionary <flake8_spellcheck/pandas.txt>`_

Before you submit a PR, it is recommended to run ``check-sorting.sh`` in the root of this repository,
to verify that all the dictionary files are still sorted correctly. Sorting is enforced by CI, so
you'll need to make sure the files are sorted before your PR can be merged.

Development
-----------

* Install `poetry <https://github.com/python-poetry>`__
* Install `golang <https://go.dev/doc/install>`__ (required by some of our pre-commit hooks)
* Run ``poetry install``
* Run ``poetry run pre-commit install --install-hooks``

You can run tests with ``poetry run pytest``.


.. |CircleCI| image:: https://circleci.com/gh/MichaelAquilina/flake8-spellcheck.svg?style=svg
   :target: https://circleci.com/gh/MichaelAquilina/flake8-spellcheck

.. |PyPi| image:: https://badge.fury.io/py/flake8-spellcheck.svg
   :target: https://badge.fury.io/py/flake8-spellcheck

.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
