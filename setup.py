import setuptools

requires = ["flake8 > 3.0.0"]

setuptools.setup(
    name="flake8-spellcheck",
    license="MIT",
    version="0.2.0a",
    description="Spellcheck variables, comments and docstrings",
    author="Michael Aquilina",
    author_email="michaelaquilina@gmail.com",
    url="https://gitlab.com/MichaelAquilina/flake8-spellcheck",
    install_requires=requires,
    entry_points={"flake8.extension": ["SP = flake8_spellcheck:SpellCheckPlugin"]},
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    package_data={"flake8_spellcheck": ["*.txt"]},
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
