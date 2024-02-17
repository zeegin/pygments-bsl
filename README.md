[![PyPI version](https://badge.fury.io/py/pygments-bsl.svg)](https://badge.fury.io/py/pygments-bsl)

pygments-bsl
=============

Pygments_ is a syntax highlighting tool that supports a wide range of
languages and data formats.

Made for MkDocs https://www.mkdocs.org.
Online example https://zeegin.github.io/pygments-bsl/

Syntax rools from https://github.com/1c-syntax.

Install
--------

```
$ pip install pygments-bsl
```

Install local
--------
```bash
pip install .
```

Build
------

```bash
python -m build
```

Test
------

```bash
pytest

```

Usage
-------

Pygment json highlighting is available without any further customization from code as well
as from the pygementize command:

```bash
pygmentize "C:\git\pygments-bsl\tests\examplefiles\bsl\samples.bsl"
pygmentize "C:\git\pygments-bsl\tests\examplefiles\bsl\samples.os"
pygmentize "C:\git\pygments-bsl\tests\examplefiles\sdbl\samples.sdbl"
```

- _Pygments: http://pygments.org/
- _pygments-bsl: https://github.com/zeegin/pygments-bsl
- _PyPI: http://pypi.python.org/pypi
- _pip: http://www.pip-installer.org/

Used:
- https://1c-syntax.github.io/bsl-language-server/
- https://pr-mex.github.io/vanessa-automation/
