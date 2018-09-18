import setuptools
from flake8_spellcheck import SpellCheckPlugin

requires = ["flake8 > 3.0.0"]

with open("README.rst") as fp:
    long_description = fp.read()

setuptools.setup(
    name="flake8-spellcheck",
    license="MIT",
    version=SpellCheckPlugin.version,
    description="Spellcheck variables, comments and docstrings",
    long_description=long_description,
    author="Michael Aquilina",
    author_email="michaelaquilina@gmail.com",
    url="https://github.com/MichaelAquilina/flake8-spellcheck",
    install_requires=requires,
    entry_points={"flake8.extension": ["SC = flake8_spellcheck:SpellCheckPlugin"]},
    packages=setuptools.find_packages("."),
    package_data={"flake8_spellcheck": ["*.txt"]},
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
