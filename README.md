[![PyPI version](https://badge.fury.io/py/pygments-bsl.svg)](https://badge.fury.io/py/pygments-bsl)

pygments-bsl
=============

Pygments_ is a syntax highlighting tool that supports a wide range of
languages and data formats.

Made for MkDocs https://www.mkdocs.org.

Syntax rools from https://github.com/1c-syntax.

Install
--------

```
$ pip install pygments-bsl
```

Install local
--------
```
$ pip install .
```

Build
------

```
$ python -m build
```

Test
------

```
$ pytest
```

Usage
-------

Pygment json highlighting is available without any further customization from code as well
as from the pygementize command:

```
  $ pygmentize "C:\git\pygments-bsl\tests\samples.bsl"

   ... beautifully formatted bsl will flow here
```

- _Pygments: http://pygments.org/
- _pygments-bsl: https://github.com/zeegin/pygments-bsl
- _PyPI: http://pypi.python.org/pypi
- _pip: http://www.pip-installer.org/