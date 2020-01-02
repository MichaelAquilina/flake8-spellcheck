=================
Flake8 Spellcheck
=================

|CircleCI| |Black| |PyPi|

Flake8 Plugin that spellchecks variables, functions, classes and other bits of your python code.

You can whitelist words that are specific to your project simply by adding them to ``whitelist.txt``
in the root of your project directory. Each word you add  should be separated by a newline.

Spelling is assumed to be in en_US.

This plugin supports python 3.5+

Codes
-----

* SC100 - Spelling error in comments
* SC200 - Spelling error in name (e.g. variable, function, class)

Contributing
------------

If you have found word(s) which is listed as a spelling error but is actually a correct term used
in python or in technical implementations (e.g. http), then you can very easily contribute by
adding those word(s) to the appropriate dictionaries:

* `python dictionary <flake8_spellcheck/python.txt>`_
* `technical dictionary <flake8_spellcheck/technical.txt>`_
* `django dictionary <flake8_spellcheck/django.txt>`_

Enable Django support
---------------------

You can enable support for a Django dictionary by adding the following to your
flake8 configuration (e.g. your ``.flake8`` file):

.. code-block:: ini

    [flake8]
    dictionaries=en_US,python,technical,django

.. |CircleCI| image:: https://circleci.com/gh/MichaelAquilina/flake8-spellcheck.svg?style=svg
   :target: https://circleci.com/gh/MichaelAquilina/flake8-spellcheck

.. |PyPi| image:: https://badge.fury.io/py/flake8-spellcheck.svg
   :target: https://badge.fury.io/py/flake8-spellcheck

.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
