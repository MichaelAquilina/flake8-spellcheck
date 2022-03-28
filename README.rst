=================
Flake8 Spellcheck
=================

|CircleCI| |Black| |PyPi|

Flake8 Plugin that spellchecks variables, functions, classes and other bits of your python code.

Words specific to your project are supported by adding them to ``spellcheck-allowlist.txt`` in the root of your project directory. Each word you add should be separated by a newline.

Spelling is assumed to be in en_US.

This plugin supports python 3.8+

Codes
=====

* SC100 - Spelling error in comments
* SC200 - Spelling error in name (e.g. variable, function, class)

Configuration
=============

Enable non-default dictionaries
-------------------------------

This plugin comes with a couple of dictionary files that aren't enabled by default.

- ``django``
- ``pytest``

To enable a custom dictionary, you can use the ``--spellcheck-add-dictionary`` flag.

.. code-block::

    flake8 --spellcheck-add-dictionary django --spellcheck-add-dictionary pytest mypackage

Disable default dictionaries
----------------------------

The default dictionary list is as follows:

- ``en_US``
- ``technical``
- ``python``

You can disable the default dictionary list, if you want to be highly specific about the wordlist in use.

.. code-block::

    flake8 --spellcheck-disable-default-dictionaries mypackage

Or in your flake8 configuration (e.g. your ``.flake8`` file):

.. code-block:: ini

    spellcheck-disable-default-dictionaries = true

You can then enable built-in dictionaries one-by-one as necessary.

.. code-block::

    flake8 --spellcheck-disable-default-dictionaries --spellcheck-add-dictionary python --spellcheck-add-dictionary pytest --spellcheck-add-dictionary pandas mypackage

Or in your flake8 configuration file:

.. code-block:: ini

    spellcheck-add-dictionary = python,pytest,pandas

Specify Code Targets
--------------------

Both ``comments`` and ``names`` (variable names, function names...) are spellchecked by default.
You can specify what targets to spellcheck by specifying the ``--spellcheck-targets`` flag.

.. code-block::

    flake8 --spellcheck-targets comments mypackage

Or by setting the ``spellcheck-targets`` option in your flake8 configuration (e.g. in your ``.flake8`` file).

.. code-block:: ini

   [flake8]
   spellcheck-targets=comments

The above configuration would only spellcheck comments, while this configuration will only check symbol names.

.. code-block:: ini

   [flake8]
   spellcheck-targets=names

Contributing
============

If you have found word(s) which are listed as a spelling error but are actually correct terms used
in python or in technical implementations (e.g. http), then you can very easily contribute by
adding those word(s) to the appropriate dictionaries:

* `python dictionary <flake8_spellcheck/python.txt>`_
* `pytest dictionary <flake8_spellcheck/pytest.txt>`_
* `general technical dictionary <flake8_spellcheck/technical.txt>`_
* `django dictionary <flake8_spellcheck/django.txt>`_
* `pandas dictionary <flake8_spellcheck/pandas.txt>`_

Before you submit a PR, it is recommended to run ``check-sorting.sh`` in the root of this repository,
to verify that all the dictionary files are still sorted correctly. Sorting is enforced by CI, so
you'll need to make sure the files are sorted before your PR can be merged.

Development
-----------

* Install `poetry <https://github.com/python-poetry>`__
* Run ``poetry install``
* Run ``poetry run pre-commit install --install-hooks``

You can run tests with ``poetry run pytest``.


.. |CircleCI| image:: https://circleci.com/gh/MichaelAquilina/flake8-spellcheck.svg?style=svg
   :target: https://circleci.com/gh/MichaelAquilina/flake8-spellcheck

.. |PyPi| image:: https://badge.fury.io/py/flake8-spellcheck.svg
   :target: https://badge.fury.io/py/flake8-spellcheck

.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
